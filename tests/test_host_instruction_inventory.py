"""Host-file discovery is read-only and is not a claim of runtime activation."""
import importlib.util
from pathlib import Path
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'skills/senmu-build-project/scripts/assess_project_governance.py'
SPEC = importlib.util.spec_from_file_location('host_instruction_assessment', SCRIPT)
ASSESS = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(ASSESS)


class HostInstructionInventoryTests(unittest.TestCase):
    def test_claude_only_project_is_not_reported_as_missing_instructions(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp).resolve(); (root / 'CLAUDE.md').write_text('project rule')
            report = ASSESS.assess(root, 4, False)
            review = report['instruction_layering_review']
            self.assertEqual(review['status'], 'semantic_review_required')
            self.assertEqual(review['entrypoints'], ['CLAUDE.md'])
            self.assertIn('CLAUDE.md', report['authority_evidence']['project_entrypoints'])
            self.assertEqual(review['inventory'][0]['load_status'], 'not_verified')
            self.assertEqual(report['write_operations'], [])

    def test_mixed_nested_scoped_local_and_override_files_keep_their_scope(self):
        fixtures = {
            'AGENTS.md': 'shared', 'CLAUDE.md': '@AGENTS.md\n',
            'CLAUDE.local.md': 'local', '.claude/CLAUDE.md': 'claude',
            '.claude/AGENTS.md': 'shared-candidate', '.claude/rules/ui.md': '---\npaths: src/**\n---\nUI rule',
            'api/.claude/rules/auth.md': 'api rule', 'api/AGENTS.override.md': 'codex override',
            'node_modules/pkg/CLAUDE.md': 'vendor', 'archive/CLAUDE.md': 'historical',
        }
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp).resolve()
            for name, text in fixtures.items():
                p = root / name; p.parent.mkdir(parents=True, exist_ok=True); p.write_text(text)
            before = {str(p.relative_to(root)): p.read_bytes() for p in root.rglob('*') if p.is_file()}
            report = ASSESS.assess(root, 8, False)
            items = {item['path']: item for item in report['instruction_layering_review']['inventory']}
            self.assertEqual(len(items), 8)
            self.assertEqual(items['.claude/CLAUDE.md']['scope'], '.')
            self.assertEqual(items['api/.claude/rules/auth.md']['scope'], 'api')
            self.assertEqual(items['api/AGENTS.override.md']['host'], 'codex')
            self.assertEqual(items['.claude/rules/ui.md']['kind'], 'scoped_rule')
            self.assertEqual(items['CLAUDE.md']['import_candidates'], ['AGENTS.md'])
            self.assertTrue(all(item['load_status'] == 'not_verified' for item in items.values()))
            self.assertEqual(before, {str(p.relative_to(root)): p.read_bytes() for p in root.rglob('*') if p.is_file()})

    def test_import_is_only_a_locator_and_external_or_linked_files_are_not_read(self):
        with tempfile.TemporaryDirectory() as temp:
            top = Path(temp).resolve(); root = top / 'project'; root.mkdir()
            (top / 'private.txt').write_text('must-not-enter-inventory')
            (root / 'CLAUDE.md').write_text('@../private.txt\n')
            try:
                (root / 'AGENTS.md').symlink_to(top / 'private.txt')
            except OSError:
                pass
            items = ASSESS.assess(root, 2, False)['instruction_layering_review']['inventory']
            self.assertEqual(len(items), 1)
            self.assertEqual(items[0]['import_candidates'], ['../private.txt'])
            self.assertNotIn('must-not-enter-inventory', str(items))

    def test_depth_limit_does_not_become_loaded_scope(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp).resolve(); nested = root / 'api/deep'; nested.mkdir(parents=True)
            (nested / 'CLAUDE.md').write_text('deep')
            review = ASSESS.assess(root, 1, False)['instruction_layering_review']
            self.assertEqual(review['inventory'], [])
            self.assertEqual(review['coverage']['depth_limited_directories'], ['api/deep/'])
            self.assertEqual(review['coverage']['host_configuration_and_effective_loading'], 'not_verified')


if __name__ == '__main__':
    unittest.main()
