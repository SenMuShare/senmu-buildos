"""Real selector/adoption/loopback cases. These do not run or grade a model."""
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT/'skills/senmu-build-project'

def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    return module

selector = load('contract_selector', PROJECT/'scripts/prepare_task_context.py')
assessor = load('contract_assessor', PROJECT/'scripts/assess_project_governance.py')
fixture = load('contract_fixture', ROOT/'tests/behavior/contract_fixture.py')

class ContractNavigationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.root = Path(self.tmp.name)/'project'
        fixture.create(self.root)
    def tearDown(self): self.tmp.cleanup()
    def select(self, **kwargs):
        return selector.prepare(self.root, 'governance/PROJECT_MAP.md', 'Item creation', **kwargs)
    def replace_route(self, new):
        p = self.root/'governance/PROJECT_MAP.md'
        p.write_text(p.read_text().replace('../api/openapi.json#/paths/~1items/post', new))
    def test_default_retains_zero_body_reads_and_fragment(self):
        out = self.select()
        self.assertEqual(out['source_bodies_read'], 0)
        route = out['contract_context']['routes'][0]
        self.assertEqual(route['selector'], '/paths/~1items/post')
        self.assertNotIn('sha256', route)
    def test_opt_in_hashes_exact_file_without_runtime_claim(self):
        before = {p.relative_to(self.root): p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
        out = self.select(fingerprint_contracts=True)
        route = out['contract_context']['routes'][0]
        self.assertEqual(route['sha256'], hashlib.sha256(before[Path('api/openapi.json')]).hexdigest())
        self.assertEqual(out['source_bodies_read'], 1)
        self.assertEqual(out['commands_executed'], 0)
        self.assertFalse(out['semantic_route_verified'])
        self.assertFalse(out['contract_context']['baseline_verified'])
        self.assertEqual(before, {p.relative_to(self.root): p.read_bytes() for p in self.root.rglob('*') if p.is_file()})
    def test_changed_contract_is_distinguishable(self):
        old = self.select(fingerprint_contracts=True)['contract_context']['routes'][0]['sha256']
        p = self.root/'api/openapi.json'; p.write_text(p.read_text().replace('1.0.0', '1.1.0'))
        new = self.select(fingerprint_contracts=True)['contract_context']['routes'][0]['sha256']
        self.assertNotEqual(old, new)
    def test_referenced_schema_does_not_claim_whole_contract_hash(self):
        p = self.root/'api/openapi.json'; p.write_text('{"$ref":"types.json"}')
        (p.parent/'types.json').write_text('{"type":"string"}')
        a = self.select(fingerprint_contracts=True)
        (p.parent/'types.json').write_text('{"type":"integer"}')
        b = self.select(fingerprint_contracts=True)
        self.assertEqual(a['contract_context']['routes'], b['contract_context']['routes'])
        self.assertFalse(b['contract_context']['references_followed'])
        self.assertFalse(b['contract_context']['baseline_verified'])
    def test_external_reference_never_fetches(self):
        self.replace_route('https://example.invalid/openapi.json#/paths/items')
        out = self.select(fingerprint_contracts=True)
        self.assertEqual(out['source_bodies_read'], 0)
        self.assertNotIn('sha256', out['contract_context']['routes'][0])
    def test_missing_source_is_a_gap_not_a_new_file(self):
        (self.root/'api/openapi.json').unlink()
        out = self.select(fingerprint_contracts=True)
        self.assertEqual(out['status'], 'gaps')
        self.assertFalse((self.root/'api/openapi.json').exists())
    def test_oversized_target_is_explicit_and_unread(self):
        (self.root/'api/openapi.json').write_bytes(b'x'*(selector.MAX_CONTRACT_BYTES+1))
        out = self.select(fingerprint_contracts=True)
        self.assertEqual(out['status'], 'gaps'); self.assertEqual(out['source_bodies_read'], 0)
        self.assertEqual(out['contract_context']['routes'][0]['status'], 'oversized')
    def test_directory_is_not_read_as_a_contract(self):
        self.replace_route('../api')
        out = self.select(fingerprint_contracts=True)
        self.assertEqual(out['status'], 'gaps'); self.assertEqual(out['source_bodies_read'], 0)
    def test_external_symlink_is_not_read(self):
        p = self.root/'api/openapi.json'; p.unlink()
        outside = self.root.parent/'outside.json'; outside.write_text('do not read')
        p.symlink_to(outside)
        out = self.select(fingerprint_contracts=True)
        self.assertEqual(out['status'], 'gaps'); self.assertEqual(out['source_bodies_read'], 0)
    def test_code_declaration_source_is_supported_without_http_scaffold(self):
        (self.root/'model.py').write_text('class Item: pass\n')
        self.replace_route('../model.py#Item')
        out = self.select(fingerprint_contracts=True)
        self.assertEqual(out['contract_context']['routes'][0]['path'], 'model.py')
        self.assertFalse((self.root/'engineering/contracts').exists())
    def test_actual_cli_returns_bounded_contract_context(self):
        out = subprocess.run([sys.executable, str(PROJECT/'scripts/prepare_task_context.py'),
            '--root', str(self.root), '--map', 'governance/PROJECT_MAP.md', '--capability', 'Item creation',
            '--fingerprint-contracts'], capture_output=True, text=True, timeout=15)
        self.assertEqual(out.returncode, 0, out.stderr)
        self.assertEqual(json.loads(out.stdout)['source_bodies_read'], 1)
        self.assertNotIn('Synthetic item API', out.stdout)
    def test_candidate_inventory_never_promotes_authority(self):
        out = assessor.assess(self.root, 8, True)
        self.assertEqual(out['boundary_contract_review']['candidate_count'], 1)
        self.assertFalse(out['boundary_contract_review']['authority_confirmed'])
        self.assertEqual(out['boundary_contract_review']['required_actions'], [])
        self.assertEqual(out['write_operations'], [])
    def test_multiple_contract_versions_are_candidates_not_conflicts(self):
        p = self.root/'api/v2/openapi.yaml'; p.parent.mkdir(); p.write_text('openapi: 3.0.3\n')
        out = assessor.assess(self.root, 8, True)
        self.assertEqual(out['boundary_contract_review']['candidate_count'], 2)
        self.assertEqual(out['conflicts'], [])
    def test_legacy_and_generated_directories_do_not_become_authority(self):
        for directory in ('archive', 'dist'):
            p = self.root/directory/'openapi.json'; p.parent.mkdir(); p.write_text('{}')
        out = assessor.assess(self.root, 8, True)
        self.assertEqual(out['boundary_contract_review']['candidate_count'], 1)
    def test_absence_does_not_force_frontend_to_have_api(self):
        (self.root/'api/openapi.json').unlink()
        out = assessor.assess(self.root, 8, True)
        self.assertEqual(out['boundary_contract_review']['candidate_count'], 0)
        self.assertEqual(out['boundary_contract_review']['required_actions'], [])
    def test_native_protocol_candidates_need_no_http_conversion(self):
        for name in ('events.proto', 'schema.graphql', 'asyncapi.yaml'):
            p = self.root/name; p.write_text('synthetic')
        self.assertEqual(assessor.assess(self.root, 8, True)['boundary_contract_review']['candidate_count'], 4)
    def test_repeated_assessment_is_identical_and_read_only(self):
        a = assessor.assess(self.root, 8, True)
        self.assertEqual(a, assessor.assess(self.root, 8, True))

class ContractAdoptionTests(unittest.TestCase):
    def initialize(self, root, kind='software', mode='initialize-new'):
        result = subprocess.run([sys.executable, str(PROJECT/'scripts/init_project_governance.py'),
            '--mode', mode, '--root', str(root), '--project-name', 'Contract test', '--project-type', kind,
            '--profile', 'core'], capture_output=True, text=True, timeout=20)
        self.assertEqual(result.returncode, 0, result.stderr)
        return json.JSONDecoder().raw_decode(result.stdout[result.stdout.index('{'):])[0]
    def test_adoption_check_is_pending_not_invented_http(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)/'app'; out=self.initialize(root)
            self.assertIn('confirm_boundary_contract_source_and_checks_or_non_applicability', out['adoption_checks'])
            self.assertEqual(out['adoption_status'], 'unverified')
            self.assertFalse((root/'engineering/contracts/http').exists())
    def test_noncode_has_no_software_adoption(self):
        with tempfile.TemporaryDirectory() as tmp:
            out=self.initialize(Path(tmp)/'media', kind='media')
            self.assertEqual(out['adoption_checks'], [])
    def test_plan_does_not_write(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)/'app'; self.initialize(root, mode='plan-new'); self.assertFalse(root.exists())
    def test_second_initialization_preserves_adopted_exception(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)/'app'; self.initialize(root)
            path=root/'AGENTS.md'; path.write_text(path.read_text()+'\nKeep the current code-owned schema.\n')
            before=path.read_bytes(); self.initialize(root); self.assertEqual(before,path.read_bytes())

class ContractFixtureTests(unittest.TestCase):
    def run_checks(self, root):
        return subprocess.run([sys.executable, '-m', 'unittest', 'discover', '-s', 'tests', '-p', 'test_*.py'],
                              cwd=root, capture_output=True, text=True, timeout=20)
    def test_real_http_detects_bad_response_then_accepts_scoped_repair(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)/'app'; fixture.create(root)
            spec=(root/'api/openapi.json').read_bytes(); legacy=(root/'legacy.py').read_bytes()
            failed=self.run_checks(root); self.assertNotEqual(failed.returncode,0)
            self.assertIn('test_real_response_matches_agreed_identifier',failed.stderr)
            p=root/'server.py'; p.write_text(p.read_text().replace('"id": len(ITEMS)', '"id": item_id'))
            passed=self.run_checks(root); self.assertEqual(passed.returncode,0,passed.stderr)
            self.assertEqual(spec,(root/'api/openapi.json').read_bytes())
            self.assertEqual(legacy,(root/'legacy.py').read_bytes())
    def test_schema_correct_response_cannot_hide_missing_persistence(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)/'app'; fixture.create(root)
            p=root/'server.py'; p.write_text(p.read_text().replace('"id": len(ITEMS)', '"id": item_id')
                .replace('            ITEMS[item_id] = {"id": item_id, "name": request["name"]}\n',''))
            failed=self.run_checks(root); self.assertNotEqual(failed.returncode,0)
            self.assertIn('test_success_means_retrievable_data',failed.stderr)
    def test_fixture_refuses_existing_project(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); (root/'user.txt').write_text('preserve')
            with self.assertRaises(ValueError): fixture.create(root)
            self.assertEqual((root/'user.txt').read_text(),'preserve')

if __name__ == '__main__': unittest.main()
