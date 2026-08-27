import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
VALIDATE = ROOT / "scripts/validate_public_surface.py"


class PublicSurfaceTests(unittest.TestCase):
    def validate(self, root: Path, *extra: str):
        return subprocess.run(
            ["python3", str(VALIDATE), "--root", str(root), *extra],
            check=False,
            capture_output=True,
            text=True,
        )

    def test_accepts_minimal_public_tree(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_root:
            root = Path(temporary_root)
            (root / "README.md").write_text("# Public\n", encoding="utf-8")
            result = self.validate(root)
            self.assertEqual(result.returncode, 0, result.stderr or result.stdout)

    def test_rejects_internal_owner_and_private_term(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_root:
            root = Path(temporary_root)
            (root / "governance/tasks").mkdir(parents=True)
            (root / "governance/tasks/TASK-0001-private.md").write_text("private-client\n", encoding="utf-8")
            (root / "README.md").write_text("private-client\n", encoding="utf-8")
            result = self.validate(root, "--deny-term", "private-client")
            self.assertNotEqual(result.returncode, 0)
            output = result.stderr or result.stdout
            self.assertIn("禁止公开的内部 owner", output)
            self.assertIn("私有实例标识", output)

    def test_rejects_sensitive_file_types_and_concrete_tokens(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_root:
            root = Path(temporary_root)
            (root / "runtime.log").write_text("local execution\n", encoding="utf-8")
            token = "ghp_" + "12345678901234567890"
            (root / "README.md").write_text(f"token={token}\n", encoding="utf-8")
            result = self.validate(root)
            self.assertNotEqual(result.returncode, 0)
            output = result.stderr or result.stdout
            self.assertIn("敏感文件类型", output)
            self.assertIn("高置信度凭据形态", output)


if __name__ == "__main__":
    unittest.main()
