from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills/senmu-build-delivery/scripts/verify_release_identity.py"


def run(*args: str, cwd: Path, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, cwd=cwd, check=check, capture_output=True, text=True)


class ReleaseIdentityTests(unittest.TestCase):
    def make_repo(self, root: Path) -> Path:
        repo = root / "repo"
        repo.mkdir()
        run("git", "init", "-b", "main", cwd=repo)
        run("git", "config", "user.name", "Test User", cwd=repo)
        run("git", "config", "user.email", "test@example.test", cwd=repo)
        (repo / "app.txt").write_text("v1\n", encoding="utf-8")
        run("git", "add", "app.txt", cwd=repo)
        run("git", "commit", "-m", "candidate", cwd=repo)
        run("git", "tag", "v1.0.0", cwd=repo)
        return repo

    def command(self, repo: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
        return run(sys.executable, str(SCRIPT), "--repo", str(repo), *args, cwd=ROOT, check=check)

    def test_matching_release_identities_pass(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            repo = self.make_repo(Path(raw))
            candidate = run("git", "rev-parse", "HEAD", cwd=repo).stdout.strip()
            report = json.loads(
                self.command(
                    repo,
                    "--source-ref", "main",
                    "--tested-commit", candidate,
                    "--reviewed-commit", candidate,
                    "--tag", "v1.0.0",
                    "--artifact-source", candidate,
                    "--require-clean",
                ).stdout
            )
            self.assertEqual(report["status"], "release_identity_verified")
            self.assertEqual(report["candidate_commit"], candidate)

    def test_source_advance_invalidates_a_frozen_candidate(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            repo = self.make_repo(Path(raw))
            frozen = run("git", "rev-parse", "HEAD", cwd=repo).stdout.strip()
            (repo / "app.txt").write_text("v2\n", encoding="utf-8")
            run("git", "commit", "-am", "advance source", cwd=repo)
            blocked = self.command(
                repo,
                "--source-ref", "main",
                "--tested-commit", frozen,
                "--tag", "v1.0.0",
                check=False,
            )
            self.assertNotEqual(blocked.returncode, 0)
            self.assertIn("release identity drift", blocked.stderr)

    def test_dirty_release_source_is_blocked_when_required(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            repo = self.make_repo(Path(raw))
            candidate = run("git", "rev-parse", "HEAD", cwd=repo).stdout.strip()
            (repo / "untracked.txt").write_text("dirty\n", encoding="utf-8")
            blocked = self.command(
                repo,
                "--source-ref", "main",
                "--tested-commit", candidate,
                "--require-clean",
                check=False,
            )
            self.assertNotEqual(blocked.returncode, 0)
            self.assertIn("not clean", blocked.stderr)

    def test_repo_must_be_the_release_source_worktree(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            repo = self.make_repo(Path(raw))
            frozen = run("git", "rev-parse", "main", cwd=repo).stdout.strip()
            run("git", "switch", "-c", "other", cwd=repo)
            (repo / "app.txt").write_text("other\n", encoding="utf-8")
            run("git", "commit", "-am", "other branch", cwd=repo)
            blocked = self.command(
                repo,
                "--source-ref", "main",
                "--tested-commit", frozen,
                check=False,
            )
            self.assertNotEqual(blocked.returncode, 0)
            self.assertIn("release_worktree_head", blocked.stderr)


if __name__ == "__main__":
    unittest.main()
