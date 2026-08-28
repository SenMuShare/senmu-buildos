from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills/senmu-build-delivery/scripts/manage_change_unit.py"


def run(*args: str, cwd: Path, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, cwd=cwd, check=check, capture_output=True, text=True)


class ChangeUnitManagementTests(unittest.TestCase):
    def make_repo(self, root: Path) -> Path:
        repo = root / "repo"
        repo.mkdir()
        run("git", "init", "-b", "main", cwd=repo)
        run("git", "config", "user.name", "Test User", cwd=repo)
        run("git", "config", "user.email", "test@example.test", cwd=repo)
        (repo / "base.txt").write_text("base\n", encoding="utf-8")
        run("git", "add", "base.txt", cwd=repo)
        run("git", "commit", "-m", "base", cwd=repo)
        return repo

    def command(self, *args: str, cwd: Path, check: bool = True) -> subprocess.CompletedProcess[str]:
        return run(sys.executable, str(SCRIPT), *args, cwd=cwd, check=check)

    def test_prepare_creates_isolated_branch_and_verifiable_worktree(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            repo = self.make_repo(root)
            worktree = root / "unit-one"
            report = json.loads(
                self.command(
                    "prepare",
                    "--repo", str(repo),
                    "--unit", "TASK-1001",
                    "--slug", "fix-preview-speed",
                    "--worktree", str(worktree),
                    cwd=ROOT,
                ).stdout
            )
            verified = json.loads(
                self.command(
                    "verify",
                    "--repo", str(worktree),
                    "--unit", "TASK-1001",
                    cwd=ROOT,
                ).stdout
            )

            self.assertEqual(report["action"], "created")
            self.assertEqual(report["branch"], "codex/fix-preview-speed")
            self.assertEqual(run("git", "branch", "--show-current", cwd=worktree).stdout.strip(), report["branch"])
            self.assertTrue(verified["verified"])
            self.assertEqual(run("git", "status", "--porcelain", cwd=repo).stdout, "")

    def test_existing_unowned_branch_is_not_reused(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            repo = self.make_repo(root)
            run("git", "branch", "codex/existing", cwd=repo)
            blocked = self.command(
                "prepare",
                "--repo", str(repo),
                "--unit", "TASK-1002",
                "--slug", "existing",
                "--worktree", str(root / "existing"),
                cwd=ROOT,
                check=False,
            )

            self.assertNotEqual(blocked.returncode, 0)
            self.assertIn("already exists without a matching Change Unit record", blocked.stderr)

    def test_sealed_branch_cannot_be_reused_by_same_or_different_unit(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            repo = self.make_repo(root)
            worktree = root / "sealed"
            self.command(
                "prepare",
                "--repo", str(repo),
                "--unit", "TASK-1003",
                "--slug", "sealed-unit",
                "--worktree", str(worktree),
                cwd=ROOT,
            )
            (worktree / "change.txt").write_text("change\n", encoding="utf-8")
            run("git", "add", "change.txt", cwd=worktree)
            run("git", "commit", "-m", "change", cwd=worktree)
            sealed = json.loads(
                self.command(
                    "seal",
                    "--repo", str(worktree),
                    "--unit", "TASK-1003",
                    cwd=ROOT,
                ).stdout
            )
            same_unit = self.command(
                "prepare",
                "--repo", str(repo),
                "--unit", "TASK-1003",
                "--slug", "sealed-unit",
                "--worktree", str(worktree),
                cwd=ROOT,
                check=False,
            )
            different_unit = self.command(
                "prepare",
                "--repo", str(repo),
                "--unit", "TASK-1004",
                "--slug", "sealed-unit",
                "--worktree", str(worktree),
                cwd=ROOT,
                check=False,
            )

            self.assertEqual(sealed["state"], "sealed")
            self.assertNotEqual(same_unit.returncode, 0)
            self.assertIn("cannot be reused", same_unit.stderr)
            self.assertNotEqual(different_unit.returncode, 0)
            self.assertIn("belongs to Change Unit", different_unit.stderr)

    def test_verify_blocks_unprepared_branch(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            repo = self.make_repo(root)
            run("git", "switch", "-c", "codex/manual", cwd=repo)
            blocked = self.command(
                "verify",
                "--repo", str(repo),
                "--unit", "TASK-1005",
                cwd=ROOT,
                check=False,
            )
            self.assertNotEqual(blocked.returncode, 0)
            self.assertIn("has no prepared Change Unit record", blocked.stderr)


if __name__ == "__main__":
    unittest.main()
