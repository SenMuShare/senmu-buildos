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

    def test_task_branch_cannot_silently_become_an_integration_line(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            repo = self.make_repo(root)
            parent_worktree = root / "parent"
            self.command(
                "prepare",
                "--repo", str(repo),
                "--unit", "TASK-2001",
                "--slug", "parent-unit",
                "--worktree", str(parent_worktree),
                cwd=ROOT,
            )
            (parent_worktree / "parent.txt").write_text("parent\n", encoding="utf-8")
            run("git", "add", "parent.txt", cwd=parent_worktree)
            run("git", "commit", "-m", "parent", cwd=parent_worktree)
            self.command("seal", "--repo", str(parent_worktree), "--unit", "TASK-2001", cwd=ROOT)

            blocked = self.command(
                "prepare",
                "--repo", str(repo),
                "--target", "codex/parent-unit",
                "--unit", "TASK-2002",
                "--slug", "child-unit",
                "--worktree", str(root / "child"),
                cwd=ROOT,
                check=False,
            )

            self.assertNotEqual(blocked.returncode, 0)
            self.assertIn("task-on-task branching requires", blocked.stderr)

    def test_explicit_stack_requires_matching_sealed_parent(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            repo = self.make_repo(root)
            parent_worktree = root / "parent"
            self.command(
                "prepare",
                "--repo", str(repo),
                "--unit", "TASK-2003",
                "--slug", "sealed-parent",
                "--worktree", str(parent_worktree),
                cwd=ROOT,
            )
            (parent_worktree / "parent.txt").write_text("parent\n", encoding="utf-8")
            run("git", "add", "parent.txt", cwd=parent_worktree)
            run("git", "commit", "-m", "parent", cwd=parent_worktree)
            self.command("seal", "--repo", str(parent_worktree), "--unit", "TASK-2003", cwd=ROOT)

            report = json.loads(
                self.command(
                    "prepare",
                    "--repo", str(repo),
                    "--target", "codex/sealed-parent",
                    "--target-role", "stacked-unit",
                    "--parent-unit", "TASK-2003",
                    "--unit", "TASK-2004",
                    "--slug", "dependent-child",
                    "--worktree", str(root / "child"),
                    cwd=ROOT,
                ).stdout
            )

            self.assertEqual(report["target_role"], "stacked-unit")
            self.assertEqual(report["parent_unit"], "TASK-2003")
            self.assertEqual(report["baseline"], run("git", "rev-parse", "codex/sealed-parent", cwd=repo).stdout.strip())

    def test_stack_cannot_start_from_an_in_progress_parent(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            repo = self.make_repo(root)
            self.command(
                "prepare",
                "--repo", str(repo),
                "--unit", "TASK-2005",
                "--slug", "open-parent",
                "--worktree", str(root / "parent"),
                cwd=ROOT,
            )
            blocked = self.command(
                "prepare",
                "--repo", str(repo),
                "--target", "codex/open-parent",
                "--target-role", "stacked-unit",
                "--parent-unit", "TASK-2005",
                "--unit", "TASK-2006",
                "--slug", "premature-child",
                "--worktree", str(root / "child"),
                cwd=ROOT,
                check=False,
            )

            self.assertNotEqual(blocked.returncode, 0)
            self.assertIn("must be sealed", blocked.stderr)

    def test_list_derives_pending_and_integrated_without_a_second_task_state(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            repo = self.make_repo(root)
            worktree = root / "unit"
            self.command(
                "prepare",
                "--repo", str(repo),
                "--unit", "TASK-3001",
                "--slug", "pending-view",
                "--worktree", str(worktree),
                cwd=ROOT,
            )
            (worktree / "change.txt").write_text("change\n", encoding="utf-8")
            run("git", "add", "change.txt", cwd=worktree)
            run("git", "commit", "-m", "change", cwd=worktree)
            sealed = json.loads(
                self.command("seal", "--repo", str(worktree), "--unit", "TASK-3001", cwd=ROOT).stdout
            )

            pending = json.loads(
                self.command("list", "--repo", str(repo), cwd=ROOT).stdout
            )["units"][0]
            self.assertEqual(pending["state"], "sealed")
            self.assertEqual(pending["derived_disposition"], "pending_integration")

            run("git", "merge", "--ff-only", sealed["head"], cwd=repo)
            integrated = json.loads(
                self.command("list", "--repo", str(repo), cwd=ROOT).stdout
            )["units"][0]
            self.assertEqual(integrated["state"], "sealed")
            self.assertEqual(integrated["derived_disposition"], "integrated")

    def test_close_records_non_ancestry_integration_with_owner_receipt(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            repo = self.make_repo(root)
            worktree = root / "unit"
            self.command(
                "prepare", "--repo", str(repo), "--unit", "TASK-3002",
                "--slug", "squashed-view", "--worktree", str(worktree), cwd=ROOT,
            )
            (worktree / "change.txt").write_text("change\n", encoding="utf-8")
            run("git", "add", "change.txt", cwd=worktree)
            run("git", "commit", "-m", "change", cwd=worktree)
            self.command("seal", "--repo", str(worktree), "--unit", "TASK-3002", cwd=ROOT)
            run("git", "merge", "--squash", "codex/squashed-view", cwd=repo)
            run("git", "commit", "-m", "squashed", cwd=repo)
            integration_commit = run("git", "rev-parse", "HEAD", cwd=repo).stdout.strip()

            closed = json.loads(
                self.command(
                    "close", "--repo", str(repo), "--unit", "TASK-3002",
                    "--disposition", "integrated", "--integration-commit", integration_commit,
                    "--owner-ref", "governance/tasks/TASK-3002.md#integration", cwd=ROOT,
                ).stdout
            )
            listed = json.loads(self.command("list", "--repo", str(repo), cwd=ROOT).stdout)["units"][0]

            self.assertEqual(closed["state"], "integrated")
            self.assertEqual(closed["integration_commit"], integration_commit)
            self.assertEqual(listed["derived_disposition"], "integrated")
            self.assertEqual(listed["owner_ref"], "governance/tasks/TASK-3002.md#integration")

    def test_close_requires_owner_and_integration_commit(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            repo = self.make_repo(root)
            worktree = root / "unit"
            self.command(
                "prepare", "--repo", str(repo), "--unit", "TASK-3003",
                "--slug", "missing-receipt", "--worktree", str(worktree), cwd=ROOT,
            )
            (worktree / "change.txt").write_text("change\n", encoding="utf-8")
            run("git", "add", "change.txt", cwd=worktree)
            run("git", "commit", "-m", "change", cwd=worktree)
            self.command("seal", "--repo", str(worktree), "--unit", "TASK-3003", cwd=ROOT)
            blocked = self.command(
                "close", "--repo", str(repo), "--unit", "TASK-3003",
                "--disposition", "integrated", "--owner-ref", "TASK-3003#integration",
                cwd=ROOT, check=False,
            )
            self.assertNotEqual(blocked.returncode, 0)
            self.assertIn("requires --integration-commit", blocked.stderr)

            unrelated = run("git", "rev-parse", "codex/missing-receipt", cwd=repo).stdout.strip()
            unreachable = self.command(
                "close", "--repo", str(repo), "--unit", "TASK-3003",
                "--disposition", "integrated", "--integration-commit", unrelated,
                "--owner-ref", "TASK-3003#integration", cwd=ROOT, check=False,
            )
            self.assertNotEqual(unreachable.returncode, 0)
            self.assertIn("not reachable from the registered target line", unreachable.stderr)


if __name__ == "__main__":
    unittest.main()
