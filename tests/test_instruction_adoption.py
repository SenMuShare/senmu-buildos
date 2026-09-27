"""Exercise persisted adoption definitions, real rendering and documented commands."""
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
INIT = ROOT / 'skills/senmu-build-project/scripts/init_project_governance.py'

class InstructionAdoptionTests(unittest.TestCase):
    def run_init(self, root, *extra, kind='software', profile='standard', mode='initialize-new'):
        result = subprocess.run([sys.executable, str(INIT), '--root', str(root), '--mode', mode,
            '--project-name', 'Instruction fixture', '--project-type', kind, '--profile', profile,
            *extra], capture_output=True, text=True, timeout=30)
        self.assertEqual(result.returncode, 0, result.stderr)
        return json.JSONDecoder().raw_decode(result.stdout[result.stdout.index('{'):])[0]

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

    def test_resuming_draft_preserves_user_instruction_bytes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)/'project'
            self.run_init(root)
            p = root/'AGENTS.md'
            original = p.read_bytes() + '\n项目已确认的独特例外。\n'.encode()
            p.write_bytes(original)
            self.run_init(root)
            self.assertEqual(p.read_bytes(), original)

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
