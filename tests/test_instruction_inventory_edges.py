"""Observe real instruction files without claiming native loading or edit authority."""
import importlib.util
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

SCRIPT = Path(__file__).resolve().parents[1] / 'skills/senmu-build-project/scripts/assess_project_governance.py'
SPEC = importlib.util.spec_from_file_location('instruction_edges', SCRIPT)
ASSESS = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(ASSESS)


class InstructionInventoryEdges(unittest.TestCase):
    def review(self, root):
        return ASSESS.assess(root, 6, False)['instruction_layering_review']

    def test_internal_link_is_an_entry_with_scoped_content(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp).resolve()
            (root / 'docs').mkdir()
            (root / 'docs/rules.md').write_text('Commands: @docs/checks.md\n')
            (root / 'CLAUDE.md').symlink_to('docs/rules.md')
            report = ASSESS.assess(root, 6, False)
            review = report['instruction_layering_review']
            self.assertIn('CLAUDE.md', review['entrypoints'])
            self.assertIn('CLAUDE.md', report['authority_evidence']['project_entrypoints'])
            item = review['inventory'][0]
            self.assertEqual(item['link_status'], 'inside_root')
            self.assertEqual(item['read_status'], 'readable')
            self.assertEqual(item['import_candidates'], ['docs/checks.md'])
            self.assertEqual(item['load_status'], 'not_verified')
            self.assertTrue((root / 'CLAUDE.md').is_symlink())

    def test_external_target_is_recorded_without_stat_or_read(self):
        with tempfile.TemporaryDirectory() as temp:
            top = Path(temp).resolve(); root = top / 'project'; root.mkdir()
            private = top / 'private.md'; private.write_text('SECRET-NOT-FOR-INVENTORY')
            (root / 'AGENTS.md').symlink_to('../private.md')
            original_read = Path.read_bytes
            original_stat = Path.stat
            def read(path):
                self.assertNotEqual(path, private)
                return original_read(path)
            def stat(path, *args, **kwargs):
                self.assertNotEqual(path, private)
                return original_stat(path, *args, **kwargs)
            with patch.object(Path, 'read_bytes', read), patch.object(Path, 'stat', stat):
                item = self.review(root)['inventory'][0]
            self.assertEqual(item['link_status'], 'outside_root_not_read')
            self.assertEqual(item['read_status'], 'not_read')
            self.assertNotIn('sha256', item)
            self.assertNotIn('import_candidates', item)
            self.assertNotIn('SECRET-NOT-FOR-INVENTORY', json.dumps(item))

    def test_chained_link_cannot_hide_external_target(self):
        with tempfile.TemporaryDirectory() as temp:
            top = Path(temp).resolve(); root = top / 'project'; root.mkdir()
            (top / 'private.md').write_text('SECRET')
            (root / 'pointer').symlink_to('../private.md')
            (root / 'CLAUDE.md').symlink_to('pointer')
            item = self.review(root)['inventory'][0]
            self.assertEqual(item['link_status'], 'outside_root_not_read')
            self.assertNotIn('sha256', item)

    def test_parent_segments_follow_resolved_directory_links(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp).resolve()
            (root / 'a').mkdir(); (root / 'b/c').mkdir(parents=True)
            (root / 'a/link').symlink_to('../b/c')
            (root / 'a/rules.md').write_text('@wrong.md')
            (root / 'b/rules.md').write_text('@correct.md')
            (root / 'CLAUDE.md').symlink_to('a/link/../rules.md')
            item = self.review(root)['inventory'][0]
            self.assertEqual(item['import_candidates'], ['correct.md'])
            self.assertEqual(item['link_status'], 'inside_root')

    def test_parent_segments_cannot_hide_an_external_directory_link(self):
        with tempfile.TemporaryDirectory() as temp:
            top = Path(temp).resolve(); root = top / 'repo'; root.mkdir()
            (top / 'external/nested').mkdir(parents=True)
            (root / 'link').symlink_to('../external/nested')
            (root / 'rules.md').write_text('@misleading.md')
            (root / 'CLAUDE.md').symlink_to('link/../rules.md')
            item = self.review(root)['inventory'][0]
            self.assertEqual(item['link_status'], 'outside_root_not_read')
            self.assertNotIn('sha256', item)

    def test_broken_and_cyclic_links_are_not_missing_entrypoints(self):
        for target in ('missing.md', 'CLAUDE.md'):
            with self.subTest(target=target), tempfile.TemporaryDirectory() as temp:
                root = Path(temp).resolve(); (root / 'CLAUDE.md').symlink_to(target)
                review = self.review(root)
                self.assertEqual(review['entrypoints'], ['CLAUDE.md'])
                self.assertEqual(review['status'], 'semantic_review_required')
                self.assertIn(review['inventory'][0]['link_status'], ('broken', 'cycle_or_limit'))
                self.assertNotIn('sha256', review['inventory'][0])

    def test_directory_link_is_not_recursively_scanned(self):
        with tempfile.TemporaryDirectory() as temp:
            top = Path(temp).resolve(); root = top / 'project'; root.mkdir()
            outside = top / 'outside'; outside.mkdir(); (outside / 'CLAUDE.md').write_text('SECRET')
            (root / 'linked').symlink_to(outside, target_is_directory=True)
            report = ASSESS.assess(root, 6, True)
            self.assertEqual(report['instruction_layering_review']['inventory'], [])
            self.assertIn('linked/', report['full_excluded_inventory']['symlink_directory_not_followed'])

    def test_import_candidates_ignore_code_and_preserve_inline_paths(self):
        text = '''Read @README.md and @docs/rules.md.
`@not-an-import.md` and ``some ` @also-not.md``.
```md
@fenced-example.md
```
~~~text
@tilde-example.md
~~~
    @indented-code.md
Contact name@example.com; escaped \\@literal.md.
Include @../shared.md, @./local.md and @~/team.md.
Read @README.md again.
'''
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp).resolve(); (root / 'CLAUDE.md').write_text(text)
            item = self.review(root)['inventory'][0]
            self.assertEqual(item['import_candidates'], ['README.md', 'docs/rules.md', '../shared.md', './local.md', '~/team.md'])
            self.assertEqual(item['import_parse_status'], 'candidates_only')

    def test_long_fence_and_multiline_inline_code_do_not_leak(self):
        text = '````markdown\n```\n@hidden.md\n```\n````\n`line\n@hidden-too.md`\n@visible.md\n'
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp).resolve(); (root / 'CLAUDE.md').write_text(text)
            self.assertEqual(self.review(root)['inventory'][0]['import_candidates'], ['visible.md'])

    def test_inventory_does_not_require_deletion_or_rewriting(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp).resolve(); entry = root / 'AGENTS.md'
            original = b'Keep the approved compatibility exception.\n'
            entry.write_bytes(original)
            first = self.review(root); second = self.review(root)
            self.assertEqual(first, second)
            self.assertEqual(first['required_actions'], [])
            self.assertEqual(first['change_recommendations'], [])
            self.assertIn('preserve_effective_principles_commands_and_exceptions', first['review_dimensions'])
            self.assertEqual(entry.read_bytes(), original)

    @unittest.skipUnless(hasattr(os, 'mkfifo'), 'POSIX FIFO')
    def test_nonregular_instruction_file_is_not_opened(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp).resolve(); os.mkfifo(root / 'AGENTS.md')
            item = self.review(root)['inventory'][0]
            self.assertEqual(item['read_status'], 'not_regular_file')

if __name__ == '__main__':
    unittest.main()
