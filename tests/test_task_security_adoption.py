"""Real initializer and selected-route fixtures; no live deployment or model claim."""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
INIT = ROOT / "skills/senmu-build-project/scripts/init_project_governance.py"
ENTRY = ROOT / "skills/senmu-build-project/scripts/prepare_task_context.py"

class TaskSecurityAdoptionTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.root = Path(self.tmp.name)/"project"
    def tearDown(self): self.tmp.cleanup()
    def init(self, mode="initialize-new", kind="software", extra=()):
        return subprocess.run([sys.executable, str(INIT), "--mode", mode, "--root", str(self.root),
            "--project-name", "Synthetic task fixture", "--project-type", kind,
            "--profile", "standard", *extra], capture_output=True, text=True, timeout=30)
    def output(self, result):
        self.assertEqual(result.returncode, 0, result.stderr)
        return json.JSONDecoder().raw_decode(result.stdout[result.stdout.index("{"):])[0]
    def test_plan_is_read_only_and_never_claims_adoption(self):
        out = self.output(self.init("plan-new", extra=("--release-channel", "managed_service")))
        self.assertFalse(self.root.exists())
        self.assertEqual(out["adoption_status"], "unverified")
        self.assertIn("operations/DEPLOYMENT.md", out["planned"])
    def test_managed_service_receives_unverified_security_controls(self):
        out = self.output(self.init(extra=("--release-channel", "managed_service")))
        text = (self.root/"operations/DEPLOYMENT.md").read_text()
        rows = [line.split("|") for line in text.splitlines() if line.startswith("| ")]
        expected = {"network", "edge-origin", "tls-proxy", "application", "resource-cost",
                    "host-container", "secrets-supply", "detection", "recovery"}
        controls = {row[1].strip(): row[-2].strip() for row in rows if row[1].strip() in expected}
        self.assertEqual(set(controls), expected)
        self.assertEqual(set(controls.values()), {"unverified"})
        self.assertIn("establish_actual_exposure_and_security_evidence", out["adoption_checks"])
        self.assertFalse((self.root/"nginx.conf").exists())
        self.assertFalse((self.root/"Dockerfile").exists())
    def test_offline_script_does_not_acquire_deployment(self):
        out = self.output(self.init(kind="script"))
        self.assertFalse((self.root/"operations/DEPLOYMENT.md").exists())
        self.assertNotIn("establish_actual_exposure_and_security_evidence", out["adoption_checks"])
    def test_noncode_project_does_not_acquire_code_adoption(self):
        out = self.output(self.init(kind="media"))
        self.assertNotIn("confirm_stack_and_shared_capability_owner", out["adoption_checks"])
    def test_existing_project_is_preserved(self):
        self.root.mkdir(); p=self.root/"README.md"; p.write_text("user-owned project\n")
        before=p.read_bytes(); out=self.init()
        self.assertNotEqual(out.returncode,0)
        self.assertEqual(p.read_bytes(),before)
        self.assertFalse((self.root/"operations").exists())
    def test_initialized_map_reaches_real_implementation_and_test(self):
        self.output(self.init())
        (self.root/"src").mkdir(); (self.root/"tests").mkdir()
        (self.root/"src/__init__.py").write_text("")
        (self.root/"src/orders.py").write_text("def total(unit, quantity):\n    return unit * quantity\n")
        (self.root/"tests/test_orders.py").write_text("import unittest\nfrom src.orders import total\nclass OrderTests(unittest.TestCase):\n    def test_total(self):\n        self.assertEqual(total(7, 3), 21)\n")
        (self.root/"engineering/contracts.md").write_text("Integer unit price times quantity; no external effects.\n")
        nav=self.root/"governance/PROJECT_MAP.md"; original=nav.read_text()
        lines=original.splitlines()
        found=[i for i,line in enumerate(lines) if line.startswith("| `<实际业务能力>`")]
        self.assertEqual(len(found),1)
        lines[found[0]]="| Order checkout | compute order total | `src/orders.py` | [contract](../engineering/contracts.md) | `tests/test_orders.py` | pure calculation/application |"
        nav.write_text("\n".join(lines)+"\n")
        result=subprocess.run([sys.executable,str(ENTRY),"--root",str(self.root),"--map","governance/PROJECT_MAP.md","--capability","Order checkout"],capture_output=True,text=True,timeout=30)
        out=self.output(result)
        self.assertEqual(out["status"],"selected")
        self.assertEqual(out["source_bodies_read"],0)
        target=[x["target"] for x in out["targets"] if x["field"]=="verification"]
        self.assertEqual(target,["tests/test_orders.py"])
        run=subprocess.run([sys.executable,"-m","unittest","discover","-s","tests","-p",Path(target[0]).name],cwd=self.root,capture_output=True,text=True,timeout=30)
        self.assertEqual(run.returncode,0,run.stderr)
        self.assertIn("Ran 1 test",run.stderr)

if __name__ == "__main__": unittest.main()
