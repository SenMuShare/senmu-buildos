"""Scaffold safety only; these tests do not invoke a native host or model."""
import importlib.util
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("contract_pipeline_workspace", ROOT / "tests/behavior/claude-evals/contract_pipeline_workspace.py")
fixture = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fixture)


class ContractPipelineWorkspaceTests(unittest.TestCase):
    def test_both_cases_copy_real_examples_and_keep_source_identity(self):
        original = ROOT / "skills/senmu-build-engineering/assets/contract-examples"
        with tempfile.TemporaryDirectory() as temporary:
            for case in ("contract-generated", "contract-baseline"):
                target = Path(temporary) / case
                fixture.create(target, case)
                for path in original.rglob("*"):
                    if path.is_file() and not {"node_modules", ".venv", "__pycache__"} & set(path.parts):
                        self.assertEqual(path.read_bytes(), (target / "example" / path.relative_to(original)).read_bytes())
                self.assertEqual((target / "CLAUDE.md").read_text(), "@AGENTS.md\n")

    def test_nonempty_workspace_is_not_overwritten(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            path = root / "user.txt"
            path.write_text("preserve")
            with self.assertRaises(ValueError):
                fixture.create(root, "contract-generated")
            self.assertEqual(path.read_text(), "preserve")
            self.assertEqual(len(list(root.iterdir())), 1)

    def test_unknown_case_creates_nothing(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "unused"
            with self.assertRaises(ValueError):
                fixture.create(root, "unknown")
            self.assertFalse(root.exists())
