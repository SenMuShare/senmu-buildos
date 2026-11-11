"""Exercise persisted adoption definitions, real rendering and documented commands."""
import json
import hashlib
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
INIT = ROOT / 'skills/senmu-build-project/scripts/init_project_governance.py'
ASSESS = INIT.with_name('assess_project_governance.py')
CONTEXT = INIT.with_name('prepare_task_context.py')
VALIDATE = INIT.with_name('validate_project_governance.py')
UI_CHECK = 'confirm_ui_basis_and_implementation_routes_with_rendered_evidence'
UI_BASIS = 'design/UI_SPECIFICATION.md'
UI_TEMPLATE = ROOT/'skills/senmu-build-design/assets/design-governance/UI_SPECIFICATION.template.md'

class InstructionAdoptionTests(unittest.TestCase):
    def run_init(self, root, *extra, kind='software', profile='standard', mode='initialize-new', scope='none'):
        result = subprocess.run([sys.executable, str(INIT), '--root', str(root), '--mode', mode,
            '--project-name', 'Instruction fixture', '--project-type', kind, '--profile', profile,
            *(['--ui-scope', scope] if scope is not None else []),
            *extra], capture_output=True, text=True, timeout=30)
        self.assertEqual(result.returncode, 0, result.stderr)
        return json.JSONDecoder().raw_decode(result.stdout[result.stdout.index('{'):])[0]

    def legacy_ui(self, root, owner):
        """Represent an existing 2.31 project, not a new custom-owner initializer."""
        self.run_init(root, '--ui-scope', 'persistent')
        target = root/owner
        target.parent.mkdir(parents=True, exist_ok=True)
        (root/UI_BASIS).rename(target)
        policy_path = root/'.senmu-buildos/config.json'
        policy = json.loads(policy_path.read_text())
        policy['ui_management']['basis_path'] = owner
        for field in ('required_paths', 'placeholder_scan_paths'):
            policy[field] = [owner if path == UI_BASIS else path for path in policy[field]]
        policy_path.write_text(json.dumps(policy, ensure_ascii=False, indent=2) + '\n')
        for name in ('AGENTS.md', 'README.md'):
            path = root/name
            path.write_text(path.read_text().replace(UI_BASIS, owner))
        path = root/'governance/PROJECT_MAP.md'
        link = quote(Path(os.path.relpath(target, path.parent)).as_posix(), safe='/')
        path.write_text(path.read_text().replace('../' + UI_BASIS, link))

    def test_adoption_definitions_survive_initialization_and_point_to_existing_owner(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)/'project'
            out = self.run_init(root, '--release-channel', 'managed_service')
            policy = json.loads((root/'.senmu-buildos/config.json').read_text())
            self.assertEqual(policy['adoption_checks'], out['adoption_checks'])
            self.assertIn('establish_actual_exposure_and_security_evidence', policy['adoption_checks'])
            self.assertTrue((root/policy['adoption_record_owner']).is_file())
            self.assertEqual(policy['initialization_status'], 'draft')
            self.assertEqual(out['adoption_status'], 'unverified')

    def test_quality_template_reaches_project_and_preserves_its_local_policy(self):
        template = ROOT/'skills/senmu-build-engineering/assets/code-quality/CODE_QUALITY.template.md'
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)/'project'
            self.run_init(root)
            owner = root/'engineering/CODE_QUALITY.md'
            self.assertEqual(template.read_bytes(), owner.read_bytes())
            adopted = owner.read_bytes() + b"\nLocal exception: keep public SDK examples in English.\n"
            owner.write_bytes(adopted)
            self.run_init(root)
            self.assertEqual(adopted, owner.read_bytes())

    def test_noncode_core_has_no_software_or_security_adoption_and_no_extra_ledger(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)/'project'
            out = self.run_init(root, kind='media', profile='core')
            actual = Path(out['root'])
            policy = json.loads((actual/'.senmu-buildos/config.json').read_text())
            self.assertEqual(policy['adoption_checks'], [])
            self.assertEqual(policy['adoption_record_owner'], 'README.md')
            self.assertFalse((actual/'governance/tasks').exists())
            text = (actual/'AGENTS.md').read_text()
            self.assertNotIn('<!-- engineering-only:', text)
            self.assertNotIn('For unfamiliar or cross-module work', text)

    def test_plan_persists_nothing(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)/'project'
            out = self.run_init(root, mode='plan-new')
            self.assertFalse(root.exists())
            self.assertEqual(out['adoption_status'], 'unverified')
            self.assertEqual(out['adoption_record_owner'], 'governance/tasks/TASK_REGISTER.md')

    def test_missing_ui_classification_is_unassessed_and_initialize_writes_nothing(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)/'project'
            plan = self.run_init(root, mode='plan-new', scope=None)
            self.assertEqual(plan['ui_management'], {'scope': 'unassessed', 'basis_path': None})
            self.assertIn('classify_ui_scope_from_project_capability', plan['adoption_checks'])
            self.assertFalse(root.exists())
            result = subprocess.run([sys.executable, str(INIT), '--root', str(root),
                '--mode', 'initialize-new', '--project-name', 'fixture', '--project-type', 'software',
                '--profile', 'core'], capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('UI 范围尚未评估', result.stderr)
            self.assertFalse(root.exists())
            completed = self.run_init(root, '--ui-scope', 'persistent', profile='core')
            self.assertEqual(completed['ui_management'], {'scope': 'persistent', 'basis_path': UI_BASIS})

    def test_explicit_none_remains_a_saved_choice(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)/'project'
            self.run_init(root, profile='core')
            original = (root/'.senmu-buildos/config.json').read_bytes()
            resumed = self.run_init(root, scope=None, profile='core')
            self.assertEqual(resumed['ui_management'], {'scope': 'none', 'basis_path': None})
            changed = subprocess.run([sys.executable, str(INIT), '--root', str(root),
                '--mode', 'initialize-new', '--project-name', 'fixture', '--project-type', 'software',
                '--profile', 'core', '--ui-scope', 'persistent'], capture_output=True, text=True)
            self.assertNotEqual(changed.returncode, 0)
            self.assertEqual(original, (root/'.senmu-buildos/config.json').read_bytes())
            self.assertFalse((root/'design').exists())

    def test_resuming_draft_preserves_user_instruction_bytes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)/'project'
            self.run_init(root)
            p = root/'AGENTS.md'
            original = p.read_bytes() + '\n项目已确认的独特例外。\n'.encode()
            p.write_bytes(original)
            self.run_init(root)
            self.assertEqual(p.read_bytes(), original)

    def test_persistent_ui_renders_reachable_basis_without_inventing_implementation(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)/'ui'
            out = self.run_init(root, '--ui-scope', 'persistent')
            policy = json.loads((root/'.senmu-buildos/config.json').read_text())
            self.assertEqual(policy['ui_management'], out['ui_management'])
            basis = policy['ui_management']['basis_path']
            self.assertEqual(basis, UI_BASIS)
            self.assertTrue((root/basis).is_file())
            self.assertIn(UI_CHECK, policy['adoption_checks'])
            self.assertIn(f'`{basis}`', (root/'AGENTS.md').read_text())
            self.assertEqual(out['adoption_status'], 'unverified')
            self.assertFalse((root/'DESIGN.md').exists())
            self.assertFalse((root/'src').exists())
            self.assertEqual(UI_TEMPLATE.read_bytes(), (root/basis).read_bytes())
            self.assertIn(f'`{basis}`', (root/'README.md').read_text())
            self.assertNotIn(UI_TEMPLATE.read_text(), (root/'product/PRODUCT_SPECIFICATION.md').read_text())
            selected = subprocess.run([sys.executable, str(CONTEXT), '--root', str(root),
                '--map', 'governance/PROJECT_MAP.md', '--capability', '持续维护的用户界面'],
                capture_output=True, text=True, timeout=30)
            self.assertEqual(selected.returncode, 0, selected.stderr)
            route = json.loads(selected.stdout)
            self.assertIn({'field': 'contract', 'target': basis, 'status': 'present'}, route['targets'])
            lines = (root/'governance/PROJECT_MAP.md').read_text().splitlines()
            row_index = next(index for index, line in enumerate(lines)
                             if line.startswith('| ' + route['row']['capability'] + ' |'))
            self.assertTrue(lines[row_index - 1].startswith('|'))
            self.assertEqual(route['status'], 'gaps')
            self.assertFalse(route['semantic_route_verified'])
            validation = subprocess.run([sys.executable, str(VALIDATE), '--root', str(root)],
                capture_output=True, text=True, timeout=30)
            self.assertEqual(validation.returncode, 0, validation.stdout + validation.stderr)

    def test_core_ui_uses_canonical_spec_and_keeps_task_in_readme(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)/'ui'
            out = self.run_init(root, '--ui-scope', 'persistent', profile='core')
            self.assertEqual(out['ui_management']['basis_path'], UI_BASIS)
            self.assertEqual(out['adoption_record_owner'], 'README.md')
            self.assertEqual(UI_TEMPLATE.read_bytes(), (root/UI_BASIS).read_bytes())
            self.assertNotIn(UI_TEMPLATE.read_text(), (root/'README.md').read_text())
            self.assertIn(f'`{UI_BASIS}`', (root/'README.md').read_text())
            self.assertFalse((root/'governance/tasks').exists())
            self.assertFalse((root/'product').exists())

    def test_backend_and_one_off_render_no_persistent_ui_routes_or_new_files(self):
        starter = INIT.parent.parent/'assets/project-governance-starter'
        with tempfile.TemporaryDirectory() as tmp:
            for scope in ('none', 'one_off'):
                with self.subTest(scope=scope):
                    root = Path(tmp)/scope
                    out = self.run_init(root, '--modules', 'code', '--ui-scope', scope)
                    policy = json.loads((root/'.senmu-buildos/config.json').read_text())
                    self.assertEqual(policy['ui_management'], {'scope': scope, 'basis_path': None})
                    self.assertNotIn(UI_CHECK, policy['adoption_checks'])
                    for name, target in (('AGENTS', 'AGENTS.md'), ('PROJECT_MAP', 'governance/PROJECT_MAP.md')):
                        template = (starter/f'{name}.template.md').read_text()
                        blocks = re.findall(r'<!-- persistent-ui-only:start -->(.*?)<!-- persistent-ui-only:end -->', template, re.S)
                        self.assertTrue(blocks)
                        rendered = (root/target).read_text()
                        for block in blocks:
                            disabled = re.sub(r'\{\{UI_(?:MAP_)?BASIS_PATH\}\}', '', block).strip()
                            self.assertNotIn(disabled, rendered)
                        self.assertNotIn('<!-- persistent-ui-only:', rendered)
                    self.assertNotIn(UI_TEMPLATE.read_text().strip(), (root/'README.md').read_text())
                    self.assertFalse((root/'design').exists())
                    self.assertFalse((root/'product').exists())
                    baseline = self.run_init(Path(tmp)/('default-' + scope), '--modules', 'code')
                    self.assertEqual(set(out['generated']), set(baseline['generated']))
            lightweight = self.run_init(Path(tmp)/'one-off-core', '--ui-scope', 'one_off', profile='core')
            self.assertEqual(len(lightweight['generated']), 6)

    def test_custom_ui_owner_and_existing_approved_contents_survive_resume(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)/'project'
            owner = 'docs/interface/approved basis.md'
            self.legacy_ui(root, owner)
            approved = '# Approved UI\nTheme: src/theme.css\nComponent: src/components/Button.tsx\nLocal exception: compact records.\n'
            (root/owner).write_text(approved)
            for relative in ('src/theme.css', 'src/components/Button.tsx'):
                target = root/relative
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text('/* adopted implementation */\n')
            before = {p.relative_to(root).as_posix(): p.read_bytes() for p in root.rglob('*')
                      if p.is_file() and '.git' not in p.relative_to(root).parts}
            out = self.run_init(root, scope=None)
            self.assertEqual(out['generated'], [])
            self.assertEqual(out['ui_management']['basis_path'], owner)
            self.assertEqual(before, {p.relative_to(root).as_posix(): p.read_bytes() for p in root.rglob('*')
                             if p.is_file() and '.git' not in p.relative_to(root).parts})
            context = subprocess.run([sys.executable, str(CONTEXT), '--root', str(root),
                '--map', 'governance/PROJECT_MAP.md', '--capability', '持续维护的用户界面'],
                capture_output=True, text=True, timeout=30)
            self.assertEqual(context.returncode, 0, context.stderr)
            self.assertIn({'field': 'contract', 'target': owner, 'status': 'present'}, json.loads(context.stdout)['targets'])
            scan = subprocess.run([sys.executable, str(ASSESS), '--root', str(root)],
                capture_output=True, text=True, timeout=30)
            self.assertEqual(scan.returncode, 0, scan.stderr)
            review = json.loads(scan.stdout)['ui_adoption_review']
            self.assertEqual(review['declared_capabilities'][0]['basis_path'], owner)
            self.assertEqual(review['declared_capabilities'][0]['standardization'], 'migration_required')
            self.assertEqual(review['candidate_counts']['theme_token_candidate'], 1)
            self.assertEqual(review['candidate_counts']['ui_component_candidate'], 1)
            self.assertFalse(review['authority_confirmed'])

    def test_ui_plan_is_zero_write_and_conflicting_resume_changes_nothing(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)/'project'
            plan = self.run_init(root, '--ui-scope', 'persistent', mode='plan-new')
            self.assertFalse(root.exists())
            self.assertIn(UI_BASIS, plan['planned'])
            self.run_init(root, '--ui-scope', 'persistent')
            before = (root/'.senmu-buildos/config.json').read_bytes()
            result = subprocess.run([sys.executable, str(INIT), '--root', str(root), '--mode', 'initialize-new',
                '--project-name', 'fixture', '--project-type', 'software', '--profile', 'standard',
                '--ui-scope', 'persistent', '--ui-owner', 'docs/replacement.md'], capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(before, (root/'.senmu-buildos/config.json').read_bytes())
            self.assertFalse((root/'docs/replacement.md').exists())

    def test_ui_validator_checks_declared_path_and_optional_legacy_declaration(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)/'project'
            self.run_init(root, '--ui-scope', 'persistent', profile='core')
            config = root/'.senmu-buildos/config.json'
            policy = json.loads(config.read_text())
            for declaration in ({'scope': 'persistent', 'basis_path': '../external.md'},
                                {'scope': 'persistent', 'basis_path': 'missing.md'},
                                {'scope': 'persistent', 'basis_path': 'C:/external.md'},
                                {'scope': [], 'basis_path': None},
                                {'scope': 'one_off', 'basis_path': 'README.md'}, None):
                with self.subTest(declaration=declaration):
                    policy['ui_management'] = declaration
                    config.write_text(json.dumps(policy))
                    result = subprocess.run([sys.executable, str(VALIDATE), '--root', str(root)],
                        capture_output=True, text=True, timeout=30)
                    self.assertEqual(result.returncode == 0, declaration is None, result.stdout + result.stderr)
                    self.assertNotIn('Traceback', result.stderr)

    def test_new_ui_owner_rejects_custom_or_conflicting_roles_without_writes(self):
        with tempfile.TemporaryDirectory() as tmp:
            for i, owner in enumerate(('AGENTS.md', 'docs/../AGENTS.md', 'README.md',
                    'governance/PROJECT_MAP.md', 'governance/tasks/TASK_REGISTER.md',
                    'design/archive/UI_SPECIFICATION.md', 'docs/visual.md', '../outside.md')):
                root = Path(tmp)/str(i)
                result = subprocess.run([sys.executable, str(INIT), '--root', str(root),
                    '--mode', 'initialize-new', '--project-name', 'fixture', '--project-type', 'software',
                    '--profile', 'core', '--ui-scope', 'persistent', '--ui-owner', owner],
                    capture_output=True, text=True)
                self.assertNotEqual(result.returncode, 0, owner)
                self.assertFalse(root.exists(), owner)

    def test_legacy_migration_is_reported_and_reserved_or_external_paths_are_errors(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)/'project'
            owner = 'docs/approved-ui.md'
            self.legacy_ui(root, owner)
            before = (root/owner).read_bytes()
            result = subprocess.run([sys.executable, str(VALIDATE), '--root', str(root), '--json'],
                capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn('ui.migration_required', {w['code'] for w in json.loads(result.stdout)['warnings']})
            strict = subprocess.run([sys.executable, str(VALIDATE), '--root', str(root), '--strict', '--json'],
                capture_output=True, text=True)
            self.assertNotEqual(strict.returncode, 0)
            self.assertTrue(any('UI 依据尚未规范化' in e['message'] for e in json.loads(strict.stdout)['errors']))
            self.assertEqual(before, (root/owner).read_bytes())
            policy_path = root/'.senmu-buildos/config.json'
            policy = json.loads(policy_path.read_text())
            for basis in ('AGENTS.md', 'governance/PROJECT_MAP.md', 'governance/tasks/TASK_REGISTER.md'):
                policy['ui_management']['basis_path'] = basis
                policy_path.write_text(json.dumps(policy))
                invalid = subprocess.run([sys.executable, str(VALIDATE), '--root', str(root), '--json'],
                    capture_output=True, text=True)
                self.assertEqual(invalid.returncode, 1, invalid.stdout + invalid.stderr)
                self.assertTrue(any('角色冲突' in e['message'] for e in json.loads(invalid.stdout)['errors']))
            policy['ui_management']['basis_path'] = UI_BASIS
            policy_path.write_text(json.dumps(policy))
            (root/UI_BASIS).symlink_to(root/'AGENTS.md')
            invalid = subprocess.run([sys.executable, str(VALIDATE), '--root', str(root)],
                capture_output=True, text=True)
            self.assertEqual(invalid.returncode, 1)
            self.assertIn('角色冲突', invalid.stdout)
            (root/UI_BASIS).unlink()
            outside = Path(tmp)/'external.md'
            outside.write_text('# Private external basis\n')
            (root/UI_BASIS).symlink_to(outside)
            invalid = subprocess.run([sys.executable, str(VALIDATE), '--root', str(root)],
                capture_output=True, text=True)
            self.assertEqual(invalid.returncode, 1)
            self.assertIn('越出项目根', invalid.stdout)

    def test_missing_legacy_declaration_is_unassessed_and_not_overwritten(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)/'project'
            self.run_init(root, profile='core')
            config = root/'.senmu-buildos/config.json'
            policy = json.loads(config.read_text())
            policy.pop('ui_management')
            config.write_text(json.dumps(policy))
            before = config.read_bytes()
            assessed = subprocess.run([sys.executable, str(ASSESS), '--root', str(root)],
                capture_output=True, text=True)
            self.assertEqual(assessed.returncode, 0, assessed.stderr)
            declaration = json.loads(assessed.stdout)['ui_adoption_review']['declared_capabilities'][0]
            self.assertEqual(declaration['scope'], 'unassessed')
            self.assertEqual(declaration['status'], 'unassessed')
            result = subprocess.run([sys.executable, str(INIT), '--root', str(root),
                '--mode', 'initialize-new', '--project-name', 'fixture', '--project-type', 'software',
                '--profile', 'core'], capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(config.read_bytes(), before)
            plan = self.run_init(root, profile='core', mode='plan-new', scope=None)
            self.assertEqual(plan['ui_management']['scope'], 'unassessed')

    def test_canonical_migration_updates_routes_and_preserves_archived_decisions(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)/'project'
            old = 'docs/approved-ui.md'
            self.legacy_ui(root, old)
            approved = b'# Approved UI\nUse shared components. Compact table is a permitted variant.\n'
            (root/old).write_bytes(approved)
            archive = root/'design/archive/approved-ui.md'
            archive.parent.mkdir(parents=True)
            (root/old).rename(archive)
            (root/UI_BASIS).write_bytes(approved)
            policy_path = root/'.senmu-buildos/config.json'
            policy = json.loads(policy_path.read_text())
            policy['ui_management']['basis_path'] = UI_BASIS
            for field in ('required_paths', 'placeholder_scan_paths'):
                policy[field] = [UI_BASIS if p == old else p for p in policy[field]]
            policy_path.write_text(json.dumps(policy))
            for name in ('README.md', 'AGENTS.md', 'governance/PROJECT_MAP.md'):
                path = root/name
                path.write_text(path.read_text().replace(old, UI_BASIS))
            result = subprocess.run([sys.executable, str(VALIDATE), '--root', str(root), '--json'],
                capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertNotIn('ui.migration_required', {w['code'] for w in json.loads(result.stdout)['warnings']})
            selected = subprocess.run([sys.executable, str(CONTEXT), '--root', str(root),
                '--map', 'governance/PROJECT_MAP.md', '--capability', '持续维护的用户界面',
                '--fingerprint-contracts'], capture_output=True, text=True)
            self.assertEqual(selected.returncode, 0, selected.stderr)
            route = json.loads(selected.stdout)['contract_context']['routes'][0]
            self.assertEqual(route['path'], UI_BASIS)
            self.assertEqual(route['sha256'], hashlib.sha256(approved).hexdigest())
            self.assertEqual(archive.read_bytes(), approved)
            self.assertFalse((root/old).exists())
            assessed = subprocess.run([sys.executable, str(ASSESS), '--root', str(root), '--verbose'],
                capture_output=True, text=True)
            self.assertEqual(assessed.returncode, 0, assessed.stderr)
            review = json.loads(assessed.stdout)['ui_adoption_review']
            self.assertEqual(review['declared_capabilities'][0]['standardization'], 'canonical_path_pending_confirmation')
            self.assertEqual(review['candidate_counts']['design_basis_candidate'], 1)
            self.assertFalse(review['authority_confirmed'])

    def test_canonical_alias_preserves_saved_ui_and_instruction_bytes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)/'project'
            out = self.run_init(root, '--ui-scope', 'persistent', '--ui-owner', 'docs/../' + UI_BASIS)
            self.assertEqual(out['ui_management']['basis_path'], UI_BASIS)
            starter = INIT.parent.parent/'assets/project-governance-starter/AGENTS.template.md'
            common = starter.read_text().split('## Adopted Working Principles', 1)[1].split('## Project Facts and Exceptions', 1)[0]
            common = common.replace('<!-- engineering-only:start -->', '').replace('<!-- engineering-only:end -->', '')
            self.assertIn(common, (root/'AGENTS.md').read_text())
            original = (root/'AGENTS.md').read_bytes() + b'\nApproved project exception.\n'
            (root/'AGENTS.md').write_bytes(original)
            (root/'aliases').symlink_to(root, target_is_directory=True)
            resumed = self.run_init(root, '--ui-owner', 'aliases/docs/../' + UI_BASIS, scope=None)
            self.assertEqual(resumed['ui_management']['basis_path'], UI_BASIS)
            self.assertEqual(resumed['generated'], [])
            self.assertEqual((root/'AGENTS.md').read_bytes(), original)

    def test_encoded_ui_owner_routes_resolve_exact_identity_despite_decoys(self):
        cases = (
            ('docs/guide%20literal.md', 'docs/guide literal.md'),
            ('docs/guide?locale.md', 'docs/guide'),
            ('docs/guide (approved).md', 'docs/guide%20(approved).md'),
        )
        with tempfile.TemporaryDirectory() as tmp:
            for index, (owner, decoy) in enumerate(cases):
                with self.subTest(owner=owner):
                    root = Path(tmp)/str(index)
                    self.legacy_ui(root, owner)
                    (root/owner).write_text('# Exact approved basis\n' + owner)
                    (root/decoy).write_text('# Decoy must not be selected\n')
                    context = subprocess.run([sys.executable, str(CONTEXT), '--root', str(root),
                        '--map', 'governance/PROJECT_MAP.md', '--capability', '持续维护的用户界面',
                        '--fingerprint-contracts'], capture_output=True, text=True, timeout=30)
                    self.assertEqual(context.returncode, 0, context.stderr)
                    route = json.loads(context.stdout)['contract_context']['routes'][0]
                    self.assertEqual(route['path'], owner)
                    self.assertEqual(route['sha256'], hashlib.sha256((root/owner).read_bytes()).hexdigest())
                    self.assertNotEqual(route['sha256'], hashlib.sha256((root/decoy).read_bytes()).hexdigest())

    def test_documented_selector_command_runs_from_product_root(self):
        guide = ROOT/'skills/senmu-build-engineering/references/stack-and-file-role-guidance.md'
        block = re.search(r'```sh\n(.*?)\n```', guide.read_text(), re.S)
        self.assertIsNotNone(block)
        result = subprocess.run(block.group(1), shell=True, cwd=ROOT, capture_output=True,
            text=True, timeout=30)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIsInstance(json.loads(result.stdout), dict)

    def test_language_and_file_role_endpoints_are_direct_reachable_links(self):
        skill = ROOT/'skills/senmu-build-engineering'
        entry = (skill/'SKILL.md').read_text()
        targets = re.findall(r'\]\(([^)]+)\)', entry)
        profiles = list((skill/'references/stack-profiles').glob('*.md'))
        self.assertGreater(len(profiles), 0)
        for profile in profiles:
            self.assertIn(profile.relative_to(skill).as_posix(), targets)
            self.assertTrue(profile.is_file())

if __name__ == '__main__':
    unittest.main()
