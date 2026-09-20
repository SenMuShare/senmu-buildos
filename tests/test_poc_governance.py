"""POC adoption paths and generated contracts, using disposable projects only."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT / 'skills/senmu-build-project'
TEMPLATES = ROOT / 'skills/senmu-build-assurance/assets/poc-experiment-governance'
SPEC = importlib.util.spec_from_file_location('poc_project_validator', PROJECT / 'scripts/validate_project_governance.py')
VALIDATOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VALIDATOR)


class RegistrationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.workspace = Path(self.temp.name).resolve()
        self.root = self.workspace / 'project'
        self.root.mkdir()
        (self.root / 'EXPERIMENT_REGISTER.md').write_text('Adopted experiment route\n')
        (self.workspace / 'experiments').mkdir()
        (self.workspace / 'records').mkdir()
        (self.workspace / 'active-development').mkdir()
        self.registration = {
            'owner_kind': 'project_policy', 'contract_path': 'EXPERIMENT_REGISTER.md',
            'activation_status': 'active', 'poc_root': 'experiments',
            'tracking_mode': 'untracked', 'record_root': None,
            'protected_roots': ['project', 'active-development'],
            'retention_policy': 'Retain report, relevant patches and representative evidence; cache is regenerable.',
            'backup_policy': 'Retained evidence has a verified external backup reference in the report.',
        }
        self.policy = {'selected_modules': ['poc'], 'workspace_root': '..', 'poc_management': self.registration}

    def validate(self, strict=True):
        errors, warnings = [], []
        VALIDATOR.validate_poc_registration(self.root, self.policy, strict, errors, warnings)
        return errors, warnings

    def test_non_git_sibling_poc_is_valid_and_no_files_are_written(self):
        before = {p.relative_to(self.workspace): p.read_bytes() for p in self.workspace.rglob('*') if p.is_file()}
        self.assertEqual(self.validate(), ([], []))
        after = {p.relative_to(self.workspace): p.read_bytes() for p in self.workspace.rglob('*') if p.is_file()}
        self.assertEqual(before, after)

    def test_no_poc_module_adds_no_requirements(self):
        self.policy = {'selected_modules': ['code']}
        with mock.patch.object(VALIDATOR.subprocess, 'run') as run:
            self.assertEqual(self.validate(), ([], []))
        run.assert_not_called()

    def test_legacy_enabled_poc_is_not_silently_certified(self):
        del self.policy['poc_management']
        errors, warnings = self.validate(strict=False)
        self.assertFalse(errors)
        self.assertEqual(warnings[0]['code'], 'poc.unconfigured')
        self.assertTrue(self.validate(strict=True)[0])

    def test_draft_is_inventory_warning_not_active_storage(self):
        self.registration['activation_status'] = 'draft'
        self.registration['poc_root'] = None
        self.assertFalse(self.validate(strict=False)[0])
        self.assertTrue(self.validate(strict=True)[0])

    def test_existing_contract_is_not_copied_or_executed(self):
        self.policy['poc_management'] = {
            'owner_kind': 'existing_contract', 'contract_path': 'EXPERIMENT_REGISTER.md',
            'activation_status': 'active',
        }
        with mock.patch.object(VALIDATOR.subprocess, 'run') as run:
            errors, warnings = self.validate()
        run.assert_not_called()
        self.assertFalse(errors)
        self.assertEqual(warnings[0]['code'], 'poc.existing_contract_requires_semantic_check')

    def test_native_owner_needs_reachable_pointer(self):
        self.policy['poc_management'] = {
            'owner_kind': 'existing_contract', 'contract_path': 'missing.md', 'activation_status': 'active',
        }
        self.assertTrue(self.validate()[0])

    def test_unfilled_package_template_is_not_project_owner(self):
        p = self.root / '.senmu-buildos/templates/experiment.md'
        p.parent.mkdir(parents=True); p.write_text('template')
        self.registration['contract_path'] = p.relative_to(self.root).as_posix()
        self.assertTrue(self.validate()[0])

    def test_foreign_absolute_and_escaping_paths_are_rejected(self):
        for raw in ('/other-project', 'C:\\data\\poc', 'C:/data/poc', '//server/share', '../outside'):
            with self.subTest(raw=raw):
                self.registration['poc_root'] = raw
                self.assertTrue(self.validate()[0])

    def test_paths_may_use_existing_unicode_and_spaces(self):
        (self.workspace / '实验 材料').mkdir()
        self.registration['poc_root'] = '实验 材料'
        self.assertEqual(self.validate()[0], [])

    def test_malformed_state_and_mode_return_findings_not_exceptions(self):
        for field in ('activation_status', 'tracking_mode'):
            previous = self.registration[field]
            self.registration[field] = []
            self.assertTrue(self.validate()[0])
            self.registration[field] = previous

    def test_git_metadata_cannot_be_record_storage(self):
        hidden = self.workspace / '.git/records'
        hidden.mkdir(parents=True)
        self.registration.update(tracking_mode='split', record_root='.git/records')
        self.assertTrue(self.validate()[0])

    def test_whole_workspace_is_not_an_experiment_root(self):
        self.registration['poc_root'] = '.'
        self.assertTrue(self.validate()[0])

    def test_missing_root_is_not_created(self):
        self.registration['poc_root'] = 'missing'
        self.assertTrue(self.validate()[0])
        self.assertFalse((self.workspace / 'missing').exists())

    def test_active_development_or_release_overlap_is_rejected(self):
        for raw in ('project', 'active-development'):
            with self.subTest(raw=raw):
                self.registration['poc_root'] = raw
                self.assertTrue(self.validate()[0])

    def test_parent_overlap_is_rejected(self):
        nested = self.workspace / 'experiments/development'
        nested.mkdir()
        self.registration['protected_roots'] = ['experiments/development']
        self.assertTrue(self.validate()[0])

    def test_protection_must_be_explicit_not_unknown(self):
        self.registration['protected_roots'] = None
        self.assertTrue(self.validate()[0])
        self.registration['protected_roots'] = []
        self.assertEqual(self.validate()[0], [])

    @unittest.skipUnless(hasattr(Path, 'symlink_to'), 'symlink support required')
    def test_symlink_cannot_hide_physical_development_overlap(self):
        link = self.workspace / 'alias'
        link.symlink_to(self.workspace / 'project', target_is_directory=True)
        self.registration['poc_root'] = 'alias'
        self.assertTrue(self.validate()[0])

    def test_split_has_distinct_registered_record_owner(self):
        self.registration.update(tracking_mode='split', record_root='records')
        self.assertEqual(self.validate()[0], [])
        self.registration['record_root'] = 'experiments'
        self.assertTrue(self.validate()[0])

    def test_split_record_root_cannot_live_in_development(self):
        self.registration.update(tracking_mode='split', record_root='active-development')
        self.assertTrue(self.validate()[0])

    def test_untracked_does_not_create_second_record_owner(self):
        self.registration['record_root'] = 'records'
        self.assertTrue(self.validate()[0])

    def test_retention_and_backup_are_not_implied_by_ignore(self):
        for field in ('retention_policy', 'backup_policy'):
            value = self.registration[field]
            self.registration[field] = None
            self.assertTrue(self.validate()[0])
            self.registration[field] = value

    def git(self, *args):
        return subprocess.check_output(['git', '-C', str(self.workspace), *args], text=True, stderr=subprocess.PIPE)

    def test_untracked_storage_checks_ignore_and_real_index(self):
        self.git('init', '-q')
        self.assertTrue(self.validate()[0])
        (self.workspace / '.gitignore').write_text('experiments/\n')
        self.assertEqual(self.validate()[0], [])
        record = self.workspace / 'experiments/result.md'; record.write_text('unique result')
        self.git('add', '-f', '--', 'experiments/result.md')
        self.assertTrue(self.validate()[0])
        self.assertEqual(record.read_text(), 'unique result')

    def test_git_failures_do_not_look_like_untracked_success(self):
        result = subprocess.CompletedProcess([], 42, stdout='', stderr='synthetic permission failure')
        with mock.patch.object(VALIDATOR.subprocess, 'run', return_value=result):
            self.assertTrue(self.validate()[0])
        with mock.patch.object(VALIDATOR.subprocess, 'run', side_effect=FileNotFoundError):
            self.assertTrue(self.validate()[0])

    def test_literal_git_path_does_not_interpret_glob_characters(self):
        self.git('init', '-q')
        (self.workspace / 'exp[1]').mkdir()
        (self.workspace / 'exp1').mkdir()
        (self.workspace / 'exp1/keep.txt').write_text('tracked unrelated file')
        self.git('add', 'exp1/keep.txt')
        (self.workspace / '.gitignore').write_text('exp\\[1\\]/\n')
        self.registration['poc_root'] = 'exp[1]'
        self.assertEqual(self.validate()[0], [])

    def test_records_survive_disposal_of_separate_fixture_execution_surface(self):
        self.registration.update(tracking_mode='split', record_root='records')
        report = self.workspace / 'records/decision.md'
        report.write_text('Rejected A: failure run 2. Adopt B with stated limits.\n')
        execution = self.workspace / 'experiments/runtime'
        execution.mkdir(); (execution / 'cache.bin').write_bytes(b'regenerable fixture')
        before = report.read_bytes()
        self.assertEqual(self.validate()[0], [])
        # This deletes only a disposable fixture, not user or project resources.
        shutil.rmtree(execution)
        self.assertEqual(report.read_bytes(), before)
        self.assertEqual(self.validate()[0], [])


class InitializationTests(unittest.TestCase):
    def initialize(self, target, profile='standard', mode='initialize-new', extra=()):
        return subprocess.run([sys.executable, str(PROJECT/'scripts/init_project_governance.py'),
                               '--mode', mode, '--root', str(target), '--project-name', 'POC fixture',
                               '--project-type', 'poc', '--profile', profile, *extra],
                              capture_output=True, text=True, check=False, timeout=30)

    def test_core_has_short_route_without_five_mandatory_documents(self):
        with tempfile.TemporaryDirectory() as temp:
            result = self.initialize(Path(temp)/'workspace', profile='core')
            self.assertEqual(result.returncode, 0, result.stderr)
            root = Path(temp)/'workspace/00-project-system'
            policy = json.loads((root/'.senmu-buildos/config.json').read_text())
            self.assertEqual(policy['poc_management']['contract_path'], 'README.md')
            self.assertEqual(policy['poc_management']['activation_status'], 'draft')
            self.assertIsNone(policy['poc_management']['poc_root'])
            self.assertFalse((root/'experiments').exists())
            self.assertIn('poc_management', (root/'AGENTS.md').read_text())
            self.assertIn('poc_management', (root/'README.md').read_text())

    def test_standard_generates_one_register_and_keeps_existing_files(self):
        with tempfile.TemporaryDirectory() as temp:
            workspace=Path(temp)/'workspace'
            result=self.initialize(workspace)
            self.assertEqual(result.returncode, 0, result.stderr)
            root=workspace/'00-project-system'
            path=root/'.senmu-buildos/config.json'
            policy=json.loads(path.read_text())
            self.assertEqual(policy['poc_management']['contract_path'], 'experiments/EXPERIMENT_REGISTER.md')
            self.assertIsNone(policy['poc_management']['protected_roots'])
            register=root/policy['poc_management']['contract_path']
            register.write_text('Preserve original decisions.\n')
            policy['poc_management']={'owner_kind':'existing_contract','contract_path':'experiments/EXPERIMENT_REGISTER.md','activation_status':'active'}
            path.write_text(json.dumps(policy))
            old=path.read_bytes()
            result=self.initialize(workspace)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(path.read_bytes(), old)
            self.assertEqual(register.read_text(), 'Preserve original decisions.\n')

    def test_planning_does_not_create_or_enable_poc_storage(self):
        with tempfile.TemporaryDirectory() as temp:
            target=Path(temp)/'missing'
            result=self.initialize(target,mode='plan-new')
            self.assertEqual(result.returncode,0,result.stderr)
            self.assertFalse(target.exists())

    def test_generated_validator_reports_poc_calibration_gap(self):
        with tempfile.TemporaryDirectory() as temp:
            result=self.initialize(Path(temp)/'workspace',profile='core')
            self.assertEqual(result.returncode,0,result.stderr)
            root=Path(temp)/'workspace/00-project-system'
            result=subprocess.run([sys.executable,str(root/'.senmu-buildos/validate.py'),
                                   '--root',str(root),'--json'],capture_output=True,text=True,check=False,timeout=30)
            self.assertEqual(result.returncode,0,result.stdout+result.stderr)
            report=json.loads(result.stdout)
            self.assertTrue(any(w['code']=='poc.unconfigured' for w in report['warnings']))

    def test_optional_manifest_preserves_legacy_locator_without_promoting_it(self):
        manifest=json.loads((TEMPLATES/'experiment-package/experiment-manifest.template.json').read_text())
        self.assertIn('external_workspace',manifest)
        self.assertIsNone(manifest['external_workspace'])
        self.assertIsNone(manifest['project_contract'])
        self.assertEqual(manifest['runs'],[])
        self.assertEqual(manifest['retained_evidence'],[])
        self.assertEqual(manifest['resource_closeout']['status'],'not_started')
        for name in ('EXPERIMENT','PLAN','RESULTS','DECISION'):
            self.assertTrue((TEMPLATES/f'experiment-package/{name}.template.md').is_file())


if __name__=='__main__':
    unittest.main()
