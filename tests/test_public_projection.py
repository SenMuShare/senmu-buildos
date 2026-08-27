import json
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
EXPORT = ROOT / "skills/senmu-build-delivery/scripts/export_public_projection.py"


class PublicProjectionTests(unittest.TestCase):
    def run_export(self, source: Path, target: Path, manifest: Path, *extra: str):
        return subprocess.run(
            ["python3", str(EXPORT), "--source", str(source), "--target", str(target), "--manifest", str(manifest), *extra],
            check=False,
            capture_output=True,
            text=True,
        )

    def write_manifest(self, path: Path, **overrides: object) -> None:
        data = {
            "schema_version": "1.0",
            "include": ["src", "README.md"],
            "exclude": [],
            "deny_terms": ["private-customer"],
        }
        data.update(overrides)
        path.write_text(json.dumps(data), encoding="utf-8")

    def test_plan_is_zero_write_and_apply_is_allowlist_only(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_root:
            base = Path(temporary_root)
            source = base / "private"
            target = base / "public"
            source.joinpath("src").mkdir(parents=True)
            source.joinpath("internal").mkdir()
            source.joinpath("src/main.py").write_text("print('public')\n", encoding="utf-8")
            source.joinpath("internal/worklog.md").write_text("private\n", encoding="utf-8")
            source.joinpath("README.md").write_text("# Public\n", encoding="utf-8")
            manifest = source / "publication.json"
            self.write_manifest(manifest)

            plan = self.run_export(source, target, manifest)
            self.assertEqual(plan.returncode, 0, plan.stderr or plan.stdout)
            self.assertFalse(target.exists())
            report = json.loads(plan.stdout)
            self.assertEqual(report["files"], ["README.md", "src/main.py"])

            applied = self.run_export(source, target, manifest, "--apply")
            self.assertEqual(applied.returncode, 0, applied.stderr or applied.stdout)
            self.assertTrue((target / "src/main.py").is_file())
            self.assertFalse((target / "internal").exists())
            marker = json.loads((target / ".senmu-public-projection.json").read_text(encoding="utf-8"))
            self.assertRegex(marker["projection_sha256"], r"^[0-9a-f]{64}$")

    def test_private_identity_and_absolute_home_path_block_projection(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_root:
            base = Path(temporary_root)
            source = base / "private"
            target = base / "public"
            source.joinpath("src").mkdir(parents=True)
            private_path = "/Users/" + "example/private-customer/project"
            source.joinpath("src/main.py").write_text(
                f"root = '{private_path}'\n",
                encoding="utf-8",
            )
            source.joinpath("README.md").write_text("# Public\n", encoding="utf-8")
            manifest = source / "publication.json"
            self.write_manifest(manifest)
            result = self.run_export(source, target, manifest, "--apply")
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("隐私门禁失败", result.stderr or result.stdout)
            self.assertFalse(target.exists())

    def test_existing_unmarked_target_is_not_overwritten(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_root:
            base = Path(temporary_root)
            source = base / "private"
            target = base / "public"
            source.joinpath("src").mkdir(parents=True)
            source.joinpath("src/main.py").write_text("pass\n", encoding="utf-8")
            source.joinpath("README.md").write_text("# Public\n", encoding="utf-8")
            manifest = source / "publication.json"
            self.write_manifest(manifest)
            target.mkdir()
            target.joinpath("owned.txt").write_text("do not replace\n", encoding="utf-8")
            result = self.run_export(source, target, manifest, "--apply")
            self.assertNotEqual(result.returncode, 0)
            self.assertTrue((target / "owned.txt").is_file())

    def test_target_cannot_be_source_parent(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_root:
            base = Path(temporary_root)
            source = base / "private"
            source.joinpath("src").mkdir(parents=True)
            source.joinpath("src/main.py").write_text("pass\n", encoding="utf-8")
            source.joinpath("README.md").write_text("# Public\n", encoding="utf-8")
            manifest = source / "publication.json"
            self.write_manifest(manifest)
            result = self.run_export(source, base, manifest, "--apply")
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("不得重叠", result.stderr or result.stdout)
            self.assertTrue((source / "src/main.py").is_file())


if __name__ == "__main__":
    unittest.main()
