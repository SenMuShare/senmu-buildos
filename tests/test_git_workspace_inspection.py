from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills/senmu-build-delivery/scripts/inspect_git_workspace.py"


def run(*args: str, cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, cwd=cwd, check=True, capture_output=True, text=True)


class GitWorkspaceInspectionTests(unittest.TestCase):
    def test_clean_write_defaults_to_isolation_unless_exclusive_writer_is_guaranteed(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            repo = Path(raw) / "repo"
            repo.mkdir()
            run("git", "init", "-b", "main", cwd=repo)
            run("git", "config", "user.name", "Test User", cwd=repo)
            run("git", "config", "user.email", "test@example.com", cwd=repo)
            (repo / "base.txt").write_text("base\n", encoding="utf-8")
            run("git", "add", "base.txt", cwd=repo)
            run("git", "commit", "-m", "base", cwd=repo)

            default_report = json.loads(
                run(
                    sys.executable,
                    str(SCRIPT),
                    "--repo",
                    str(repo),
                    "--intent",
                    "write",
                    cwd=ROOT,
                ).stdout
            )
            exclusive_report = json.loads(
                run(
                    sys.executable,
                    str(SCRIPT),
                    "--repo",
                    str(repo),
                    "--intent",
                    "write",
                    "--exclusive-writer",
                    cwd=ROOT,
                ).stdout
            )

            self.assertEqual(
                default_report["execution_recommendation"]["mode"],
                "isolated_short_branch_worktree",
            )
            self.assertTrue(default_report["execution_recommendation"]["requires_isolation"])
            self.assertEqual(
                exclusive_report["execution_recommendation"]["mode"],
                "short_branch_current_worktree",
            )
            self.assertFalse(exclusive_report["execution_recommendation"]["requires_isolation"])

    def test_recommends_parallel_isolation_without_mutating_repository(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            repo = Path(raw) / "repo"
            repo.mkdir()
            run("git", "init", "-b", "main", cwd=repo)
            run("git", "config", "user.name", "Test User", cwd=repo)
            run("git", "config", "user.email", "test@example.com", cwd=repo)
            (repo / "base.txt").write_text("base\n", encoding="utf-8")
            run("git", "add", "base.txt", cwd=repo)
            run("git", "commit", "-m", "base", cwd=repo)

            before = run("git", "status", "--porcelain", cwd=repo).stdout
            result = run(
                sys.executable,
                str(SCRIPT),
                "--repo",
                str(repo),
                "--intent",
                "parallel-write",
                cwd=ROOT,
            )
            report = json.loads(result.stdout)
            after = run("git", "status", "--porcelain", cwd=repo).stdout

            self.assertEqual(before, after)
            self.assertEqual(
                report["execution_recommendation"]["mode"],
                "isolated_short_branch_worktree",
            )
            self.assertTrue(report["execution_recommendation"]["requires_isolation"])

    def test_dirty_write_is_preserved_and_release_does_not_merge_all(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            repo = Path(raw) / "repo"
            repo.mkdir()
            run("git", "init", "-b", "main", cwd=repo)
            run("git", "config", "user.name", "Test User", cwd=repo)
            run("git", "config", "user.email", "test@example.com", cwd=repo)
            (repo / "base.txt").write_text("base\n", encoding="utf-8")
            run("git", "add", "base.txt", cwd=repo)
            run("git", "commit", "-m", "base", cwd=repo)
            (repo / "dirty.txt").write_text("user work\n", encoding="utf-8")

            write_report = json.loads(
                run(
                    sys.executable,
                    str(SCRIPT),
                    "--repo",
                    str(repo),
                    "--intent",
                    "write",
                    cwd=ROOT,
                ).stdout
            )
            release_report = json.loads(
                run(
                    sys.executable,
                    str(SCRIPT),
                    "--repo",
                    str(repo),
                    "--intent",
                    "release-closeout",
                    cwd=ROOT,
                ).stdout
            )

            self.assertEqual(
                write_report["execution_recommendation"]["mode"],
                "preserve_dirty_owner_then_isolate_or_handoff",
            )
            self.assertEqual(
                release_report["execution_recommendation"]["mode"],
                "release_intake_then_clean_release_source",
            )
            self.assertIn("never merge every branch mechanically", release_report["execution_recommendation"]["reason"])
            self.assertTrue((repo / "dirty.txt").is_file())

    def test_classifies_without_mutating_repository(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            repo = root / "repo"
            repo.mkdir()
            run("git", "init", "-b", "main", cwd=repo)
            run("git", "config", "user.name", "Test User", cwd=repo)
            run("git", "config", "user.email", "test@example.com", cwd=repo)
            (repo / "base.txt").write_text("base\n", encoding="utf-8")
            run("git", "add", "base.txt", cwd=repo)
            run("git", "commit", "-m", "base", cwd=repo)

            run("git", "switch", "-c", "feature/merged", cwd=repo)
            (repo / "merged.txt").write_text("merged\n", encoding="utf-8")
            run("git", "add", "merged.txt", cwd=repo)
            run("git", "commit", "-m", "merged feature", cwd=repo)
            run("git", "switch", "main", cwd=repo)
            run("git", "merge", "--ff-only", "feature/merged", cwd=repo)
            merged_worktree = root / "merged-worktree"
            run("git", "worktree", "add", str(merged_worktree), "feature/merged", cwd=repo)

            run("git", "branch", "feature/unmerged", cwd=repo)
            unmerged_worktree = root / "unmerged-worktree"
            run("git", "worktree", "add", str(unmerged_worktree), "feature/unmerged", cwd=repo)
            (unmerged_worktree / "dirty.txt").write_text("dirty\n", encoding="utf-8")

            run("git", "branch", "feature/unmerged-clean", cwd=repo)
            unmerged_clean_worktree = root / "unmerged-clean-worktree"
            run(
                "git",
                "worktree",
                "add",
                str(unmerged_clean_worktree),
                "feature/unmerged-clean",
                cwd=repo,
            )
            (unmerged_clean_worktree / "new.txt").write_text("new\n", encoding="utf-8")
            run("git", "add", "new.txt", cwd=unmerged_clean_worktree)
            run("git", "commit", "-m", "unmerged feature", cwd=unmerged_clean_worktree)

            (repo / "primary-dirty.txt").write_text("dirty primary\n", encoding="utf-8")

            before = run("git", "status", "--porcelain", cwd=repo).stdout
            result = run(
                sys.executable,
                str(SCRIPT),
                "--repo",
                str(repo),
                "--target",
                "main",
                cwd=ROOT,
            )
            report = json.loads(result.stdout)
            after = run("git", "status", "--porcelain", cwd=repo).stdout

            worktrees = {item["branch"]: item for item in report["worktrees"]}
            branches = {item["name"]: item for item in report["branches"]}
            self.assertEqual(before, after)
            self.assertEqual(
                worktrees["feature/merged"]["classification"],
                "merged_cleanup_candidate",
            )
            self.assertEqual(
                worktrees["feature/unmerged"]["classification"],
                "dirty_review_required",
            )
            self.assertEqual(
                worktrees["feature/unmerged-clean"]["classification"],
                "unmerged_review_required",
            )
            self.assertTrue(worktrees["main"]["is_primary"])
            self.assertEqual(
                worktrees["main"]["classification"],
                "dirty_review_required",
            )
            self.assertEqual(branches["main"]["classification"], "protected_branch")
            self.assertEqual(
                branches["feature/merged"]["classification"],
                "merged_cleanup_candidate",
            )
            self.assertEqual(
                branches["feature/unmerged"]["classification"],
                "dirty_review_required",
            )
            self.assertEqual(
                branches["feature/unmerged-clean"]["classification"],
                "unmerged_review_required",
            )
            self.assertIn("not deletion authorization", report["caveats"][0])


if __name__ == "__main__":
    unittest.main()
