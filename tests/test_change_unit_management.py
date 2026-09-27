from __future__ import annotations

import json
import subprocess
import sys
import time
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

    def test_resume_returns_to_registered_branch_without_creating_a_sibling(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            repo = self.make_repo(root)
            worktree = root / "continued-poc"
            self.command(
                "prepare",
                "--repo", str(repo),
                "--unit", "TASK-1006",
                "--slug", "continued-poc",
                "--worktree", str(worktree),
                cwd=ROOT,
            )
            (worktree / "checkpoint.txt").write_text("checkpoint\n", encoding="utf-8")
            run("git", "add", "checkpoint.txt", cwd=worktree)
            run("git", "commit", "-m", "checkpoint", cwd=worktree)
            run("git", "worktree", "remove", str(worktree), cwd=repo)

            report = json.loads(
                self.command(
                    "resume",
                    "--repo", str(repo),
                    "--unit", "TASK-1006",
                    cwd=ROOT,
                ).stdout
            )
            branches = run(
                "git", "for-each-ref", "--format=%(refname:short)", "refs/heads", cwd=repo
            ).stdout.splitlines()

            self.assertEqual(report["action"], "resumed")
            self.assertEqual(report["branch"], "codex/continued-poc")
            self.assertEqual(Path(report["worktree"]).resolve(), worktree.resolve())
            self.assertTrue((worktree / "checkpoint.txt").is_file())
            self.assertEqual(branches, ["codex/continued-poc", "main"])

    def test_resume_rejects_a_sealed_unit(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            repo = self.make_repo(root)
            worktree = root / "sealed-resume"
            self.command(
                "prepare",
                "--repo", str(repo),
                "--unit", "TASK-1007",
                "--slug", "sealed-resume",
                "--worktree", str(worktree),
                cwd=ROOT,
            )
            (worktree / "change.txt").write_text("change\n", encoding="utf-8")
            run("git", "add", "change.txt", cwd=worktree)
            run("git", "commit", "-m", "change", cwd=worktree)
            self.command("seal", "--repo", str(worktree), "--unit", "TASK-1007", cwd=ROOT)

            blocked = self.command(
                "resume",
                "--repo", str(repo),
                "--unit", "TASK-1007",
                cwd=ROOT,
                check=False,
            )

            self.assertNotEqual(blocked.returncode, 0)
            self.assertIn("sealed or closed work cannot be reused", blocked.stderr)

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
                self.command("list", "--repo", str(repo), "--format", "full", cwd=ROOT).stdout
            )["units"][0]
            self.assertEqual(pending["state"], "sealed")
            self.assertEqual(pending["derived_disposition"], "pending_integration")

            run("git", "merge", "--ff-only", sealed["head"], cwd=repo)
            integrated = json.loads(
                self.command("list", "--repo", str(repo), "--format", "full", cwd=ROOT).stdout
            )["units"][0]
            self.assertEqual(integrated["state"], "sealed")
            self.assertEqual(integrated["derived_disposition"], "pending_integration")
            self.assertTrue(integrated["candidate_reachable"])

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
            listed = json.loads(self.command("list", "--repo", str(repo), "--format", "full", cwd=ROOT).stdout)["units"][0]

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


    def make_sealed_fixture(self) -> tuple[Path, Path, dict]:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        root = Path(temporary.name)
        repo = self.make_repo(root)
        worktree = root / "unit"
        self.command(
            "prepare", "--repo", str(repo), "--unit", "TASK-4001",
            "--slug", "receipt-proof", "--worktree", str(worktree), cwd=ROOT,
        )
        (worktree / "base.txt").write_text("changed\n", encoding="utf-8")
        run("git", "commit", "-am", "change", cwd=worktree)
        sealed = json.loads(self.command("seal", "--repo", str(worktree), "--unit", "TASK-4001", cwd=ROOT).stdout)
        return repo, worktree, sealed

    def close_fixture(self, repo: Path, receipt: str, *extra: str) -> subprocess.CompletedProcess[str]:
        return self.command(
            "close", "--repo", str(repo), "--unit", "TASK-4001",
            "--disposition", "integrated", "--integration-commit", receipt,
            "--owner-ref", "TASK-4001#integration", *extra, cwd=ROOT, check=False,
        )

    def assert_rejected_without_mutation(self, repo: Path, sealed: dict, receipt: str, *extra: str) -> None:
        path = Path(sealed["record"])
        original = path.read_bytes()
        before = run("git", "status", "--porcelain", cwd=repo).stdout
        result = self.close_fixture(repo, receipt, *extra)
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertEqual(path.read_bytes(), original)
        self.assertEqual(run("git", "status", "--porcelain", cwd=repo).stdout, before)

    def test_close_rejects_baseline_as_receipt(self) -> None:
        repo, worktree, sealed = self.make_sealed_fixture()
        self.assert_rejected_without_mutation(repo, sealed, sealed["baseline"])
        self.assertEqual((repo / "base.txt").read_text(), "base\n")

    def test_close_rejects_unrelated_main_commit(self) -> None:
        repo, worktree, sealed = self.make_sealed_fixture()
        (repo / "unrelated.txt").write_text("another task\n")
        run("git", "add", ".", cwd=repo)
        run("git", "commit", "-m", "unrelated", cwd=repo)
        receipt = run("git", "rev-parse", "HEAD", cwd=repo).stdout.strip()
        self.assert_rejected_without_mutation(repo, sealed, receipt)
        self.assertEqual((repo / "base.txt").read_text(), "base\n")

    def test_close_proves_fast_forward_and_preserves_dirty_target_files(self) -> None:
        repo, worktree, sealed = self.make_sealed_fixture()
        run("git", "merge", "--ff-only", sealed["head"], cwd=repo)
        (repo / "do-not-touch.txt").write_text("local work\n")
        result = self.close_fixture(repo, sealed["head"])
        self.assertEqual(result.returncode, 0, result.stderr)
        closed = json.loads(result.stdout)
        self.assertEqual(closed["integration_proof"]["source_head"], sealed["head"])
        self.assertEqual((repo / "do-not-touch.txt").read_text(), "local work\n")

    def test_close_proves_normal_merge_with_target_changes(self) -> None:
        repo, worktree, sealed = self.make_sealed_fixture()
        (repo / "unrelated.txt").write_text("keep\n")
        run("git", "add", ".", cwd=repo)
        run("git", "commit", "-m", "target advanced", cwd=repo)
        run("git", "merge", "--no-ff", sealed["head"], "-m", "receive", cwd=repo)
        receipt = run("git", "rev-parse", "HEAD", cwd=repo).stdout.strip()
        result = self.close_fixture(repo, receipt)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["integration_proof"]["kind"], "tree_replay")
        self.assertEqual((repo / "base.txt").read_text(), "changed\n")
        self.assertEqual((repo / "unrelated.txt").read_text(), "keep\n")

    def test_ancestry_only_merge_cannot_claim_integration(self) -> None:
        repo, worktree, sealed = self.make_sealed_fixture()
        run("git", "merge", "--no-ff", "-s", "ours", sealed["head"], "-m", "discard source", cwd=repo)
        receipt = run("git", "rev-parse", "HEAD", cwd=repo).stdout.strip()
        self.assert_rejected_without_mutation(repo, sealed, receipt)
        listed = json.loads(self.command("list", "--repo", str(repo), "--format", "full", cwd=ROOT).stdout)["units"][0]
        self.assertEqual(listed["derived_disposition"], "pending_integration")
        self.assertTrue(listed["candidate_reachable"])
        self.assertEqual((repo / "base.txt").read_text(), "base\n")

    def test_close_rejects_source_branch_moved_after_seal(self) -> None:
        repo, worktree, sealed = self.make_sealed_fixture()
        run("git", "merge", "--ff-only", sealed["head"], cwd=repo)
        (worktree / "base.txt").write_text("not reviewed\n")
        run("git", "commit", "-am", "illegal post-seal edit", cwd=worktree)
        self.assert_rejected_without_mutation(repo, sealed, sealed["head"])

    def test_close_proves_squash_on_advanced_target(self) -> None:
        repo, worktree, sealed = self.make_sealed_fixture()
        (repo / "unrelated.txt").write_text("keep\n")
        run("git", "add", ".", cwd=repo)
        run("git", "commit", "-m", "target advanced", cwd=repo)
        run("git", "merge", "--squash", sealed["head"], cwd=repo)
        run("git", "commit", "-m", "squash", cwd=repo)
        receipt = run("git", "rev-parse", "HEAD", cwd=repo).stdout.strip()
        self.assertNotEqual(run("git", "merge-base", "--is-ancestor", sealed["head"], "HEAD", cwd=repo, check=False).returncode, 0)
        result = self.close_fixture(repo, receipt)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["integration_proof"]["kind"], "tree_replay")

    def test_close_rejects_partial_squash_and_unreviewed_extra_changes(self) -> None:
        for kind in ("partial", "extra"):
            with self.subTest(kind=kind):
                repo, worktree, sealed = self.make_sealed_fixture()
                if kind == "partial":
                    (repo / "base.txt").write_text("wrong\n")
                else:
                    (repo / "base.txt").write_text("changed\n")
                    (repo / "extra.txt").write_text("unreviewed\n")
                run("git", "add", ".", cwd=repo)
                run("git", "commit", "-m", kind, cwd=repo)
                self.assert_rejected_without_mutation(repo, sealed, "HEAD")

    def test_close_rejects_conflict_resolution_not_proven_equivalent(self) -> None:
        repo, worktree, sealed = self.make_sealed_fixture()
        (repo / "base.txt").write_text("conflicting target\n")
        run("git", "commit", "-am", "conflict", cwd=repo)
        run("git", "merge", "--no-ff", sealed["head"], cwd=repo, check=False)
        (repo / "base.txt").write_text("manually resolved\n")
        run("git", "add", ".", cwd=repo)
        run("git", "commit", "-m", "resolve", cwd=repo)
        self.assert_rejected_without_mutation(repo, sealed, "HEAD")

    def test_close_proves_multi_commit_cherry_pick_with_receiving_base(self) -> None:
        repo, worktree, sealed = self.make_sealed_fixture()
        # Build another fixture state before sealing, using the existing protocol.
        new_root = worktree.parent / "multi"
        self.command("prepare", "--repo", str(repo), "--unit", "TASK-4002", "--slug", "multi-pick", "--worktree", str(new_root), cwd=ROOT)
        (new_root / "base.txt").write_text("step one\n")
        run("git", "commit", "-am", "first", cwd=new_root)
        first = run("git", "rev-parse", "HEAD", cwd=new_root).stdout.strip()
        (new_root / "base.txt").write_text("step two\n")
        run("git", "commit", "-am", "second", cwd=new_root)
        second = run("git", "rev-parse", "HEAD", cwd=new_root).stdout.strip()
        frozen = json.loads(self.command("seal", "--repo", str(new_root), "--unit", "TASK-4002", cwd=ROOT).stdout)
        (repo / "target.txt").write_text("keep\n")
        run("git", "add", ".", cwd=repo)
        run("git", "commit", "-m", "advance", cwd=repo)
        before = run("git", "rev-parse", "HEAD", cwd=repo).stdout.strip()
        run("git", "cherry-pick", first, second, cwd=repo)
        result = self.command("close", "--repo", str(repo), "--unit", "TASK-4002", "--disposition", "integrated", "--integration-commit", "HEAD", "--integration-base", before, "--owner-ref", "TASK-4002#integration", cwd=ROOT, check=False)
        self.assertEqual(result.returncode, 0, result.stderr)
        proof = json.loads(result.stdout)["integration_proof"]
        self.assertEqual(proof["receiving_base"], before)
        self.assertEqual(proof["source_head"], frozen["head"])
        self.assertEqual((repo / "base.txt").read_text(), "step two\n")

    def test_close_rejects_receiving_base_equal_to_receipt(self) -> None:
        repo, worktree, sealed = self.make_sealed_fixture()
        run("git", "merge", "--ff-only", sealed["head"], cwd=repo)
        self.assert_rejected_without_mutation(repo, sealed, "HEAD", "--integration-base", "HEAD")

    def test_close_of_excluded_unit_needs_no_integration_proof(self) -> None:
        repo, worktree, sealed = self.make_sealed_fixture()
        result = self.command("close", "--repo", str(repo), "--unit", "TASK-4001", "--disposition", "excluded", "--owner-ref", "TASK-4001#scope", cwd=ROOT)
        self.assertEqual(json.loads(result.stdout)["state"], "excluded")


    def test_squash_proof_covers_rename_delete_binary_and_mode(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            repo = self.make_repo(root)
            (repo / "obsolete.txt").write_text("remove me\n")
            (repo / "data.bin").write_bytes(b"old\0data")
            run("git", "add", ".", cwd=repo)
            run("git", "commit", "-m", "seed files", cwd=repo)
            worktree = root / "unit"
            self.command("prepare", "--repo", str(repo), "--unit", "TASK-4001", "--slug", "receipt-proof", "--worktree", str(worktree), cwd=ROOT)
            run("git", "mv", "base.txt", "renamed file.txt", cwd=worktree)
            (worktree / "renamed file.txt").chmod(0o755)
            (worktree / "obsolete.txt").unlink()
            (worktree / "data.bin").write_bytes(b"new\0data\xff")
            run("git", "add", ".", cwd=worktree)
            run("git", "commit", "-m", "change files", cwd=worktree)
            sealed = json.loads(self.command("seal", "--repo", str(worktree), "--unit", "TASK-4001", cwd=ROOT).stdout)
            run("git", "merge", "--squash", sealed["head"], cwd=repo)
            run("git", "commit", "-m", "squash", cwd=repo)
            run("git", "worktree", "remove", str(worktree), cwd=repo)
            run("git", "branch", "-D", sealed["branch"], cwd=repo)
            result = self.close_fixture(repo, "HEAD")
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual((repo / "data.bin").read_bytes(), b"new\0data\xff")
            self.assertFalse((repo / "obsolete.txt").exists())
            self.assertFalse((repo / "base.txt").exists())
            self.assertTrue(run("git", "ls-tree", "HEAD", "renamed file.txt", cwd=repo).stdout.startswith("100755"))

    def test_missing_replay_capability_preserves_sealed_record(self) -> None:
        import argparse
        import importlib.util
        from unittest.mock import patch

        repo, worktree, sealed = self.make_sealed_fixture()
        run("git", "merge", "--squash", sealed["head"], cwd=repo)
        run("git", "commit", "-m", "squash", cwd=repo)
        spec = importlib.util.spec_from_file_location("unit_receipt_test", SCRIPT)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        original_run = subprocess.run
        def missing_merge_tree(command, **kwargs):
            if "merge-tree" in command:
                return subprocess.CompletedProcess(command, 129, "", "unsupported merge-tree option")
            return original_run(command, **kwargs)
        before = Path(sealed["record"]).read_bytes()
        args = argparse.Namespace(repo=repo, unit="TASK-4001", disposition="integrated", integration_commit="HEAD", integration_base=None, owner_ref="TASK-4001#integration")
        with patch.object(module.subprocess, "run", side_effect=missing_merge_tree):
            with self.assertRaisesRegex(SystemExit, "cannot prove clean integration replay"):
                module.close(args)
        self.assertEqual(Path(sealed["record"]).read_bytes(), before)



    def make_open_review_fixture(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        root = Path(temporary.name)
        repo = self.make_repo(root)
        worktree = root / "review unit"
        prepared = json.loads(self.command(
            "prepare", "--repo", str(repo), "--unit", "TASK-5001",
            "--slug", "open-review", "--worktree", str(worktree), cwd=ROOT,
        ).stdout)
        (worktree / "feature.txt").write_text("feature\n")
        run("git", "add", ".", cwd=worktree)
        run("git", "commit", "-m", "implement complete slice", cwd=worktree)
        return repo, worktree, prepared

    def test_inspect_finds_open_unit_from_main_without_creating_or_sealing(self):
        repo, worktree, prepared = self.make_open_review_fixture()
        before = Path(prepared["record"]).read_bytes()
        branches = run("git", "show-ref", cwd=repo).stdout
        report = json.loads(self.command(
            "inspect", "--repo", str(repo), "--unit", "TASK-5001", cwd=ROOT,
        ).stdout)
        self.assertEqual(report["worktree"], str(worktree.resolve()))
        self.assertEqual(report["repair_route"], "existing_unit")
        self.assertEqual(report["identity_issues"], [])
        self.assertEqual(report["head"], run("git", "rev-parse", "HEAD", cwd=worktree).stdout.strip())
        self.assertEqual(report["acceptance"], "not_assessed")
        self.assertEqual(Path(prepared["record"]).read_bytes(), before)
        self.assertEqual(run("git", "show-ref", cwd=repo).stdout, branches)

    def test_inspect_missing_worktree_preserves_commit_and_does_not_recreate(self):
        repo, worktree, prepared = self.make_open_review_fixture()
        head = run("git", "rev-parse", "HEAD", cwd=worktree).stdout.strip()
        run("git", "worktree", "remove", str(worktree), cwd=repo)
        before = Path(prepared["record"]).read_bytes()
        report = json.loads(self.command(
            "inspect", "--repo", str(repo), "--unit", "TASK-5001", cwd=ROOT,
        ).stdout)
        self.assertFalse(report["worktree_exists"])
        self.assertEqual(report["head"], head)
        self.assertIn("worktree_unavailable", report["identity_issues"])
        self.assertEqual(report["repair_route"], "reconcile_identity")
        self.assertFalse(worktree.exists())
        self.assertEqual(Path(prepared["record"]).read_bytes(), before)

    def test_review_then_repair_uses_one_open_unit_and_only_reports_delta(self):
        repo, worktree, prepared = self.make_open_review_fixture()
        before = Path(prepared["record"]).read_bytes()
        first = json.loads(self.command(
            "review", "--repo", str(worktree), "--unit", "TASK-5001", cwd=ROOT,
        ).stdout)
        self.assertEqual(first["state"], "in_progress")
        self.assertEqual(first["changed_paths"], ["feature.txt"])
        self.assertEqual(first["tests"], "not_run")
        self.assertEqual(first["acceptance"], "not_assessed")
        (worktree / "fixture with spaces.txt").write_text("GET only\n")
        run("git", "add", ".", cwd=worktree)
        run("git", "commit", "-m", "repair fixture in same batch", cwd=worktree)
        second = json.loads(self.command(
            "review", "--repo", str(worktree), "--unit", "TASK-5001",
            "--since", first["head"], cwd=ROOT,
        ).stdout)
        self.assertEqual(second["changed_paths"], ["fixture with spaces.txt"])
        self.assertEqual(second["review_base"], first["head"])
        self.assertEqual(second["scope"], "delta")
        self.assertEqual(Path(prepared["record"]).read_bytes(), before)
        self.assertTrue(json.loads(self.command("verify", "--repo", str(worktree), "--unit", "TASK-5001", cwd=ROOT).stdout)["verified"])
        self.assertEqual(len(run("git", "for-each-ref", "refs/heads", cwd=repo).stdout.splitlines()), 2)
        sealed = json.loads(self.command("seal", "--repo", str(worktree), "--unit", "TASK-5001", cwd=ROOT).stdout)
        self.assertEqual(sealed["head"], second["head"])

    def test_review_refuses_wrong_directory_and_dirty_source_without_mutation(self):
        repo, worktree, prepared = self.make_open_review_fixture()
        before = Path(prepared["record"]).read_bytes()
        wrong = self.command("review", "--repo", str(repo), "--unit", "TASK-5001", cwd=ROOT, check=False)
        self.assertNotEqual(wrong.returncode, 0)
        (worktree / "unfinished.txt").write_text("do not discard\n")
        dirty = self.command("review", "--repo", str(worktree), "--unit", "TASK-5001", cwd=ROOT, check=False)
        self.assertNotEqual(dirty.returncode, 0)
        self.assertIn("uncommitted", dirty.stderr)
        self.assertEqual((worktree / "unfinished.txt").read_text(), "do not discard\n")
        self.assertEqual(Path(prepared["record"]).read_bytes(), before)

    def test_review_rejects_unrelated_or_symbolic_previous_head(self):
        repo, worktree, prepared = self.make_open_review_fixture()
        (repo / "other.txt").write_text("unrelated\n")
        run("git", "add", ".", cwd=repo)
        run("git", "commit", "-m", "unrelated change", cwd=repo)
        other = run("git", "rev-parse", "HEAD", cwd=repo).stdout.strip()
        for previous in (other, "HEAD", "f" * 40):
            with self.subTest(previous=previous):
                result = self.command("review", "--repo", str(worktree), "--unit", "TASK-5001", "--since", previous, cwd=ROOT, check=False)
                self.assertNotEqual(result.returncode, 0)
        self.assertEqual(json.loads(Path(prepared["record"]).read_text())["state"], "in_progress")

    def test_review_does_not_reopen_sealed_unit_or_refresh_changed_sealed_head(self):
        repo, worktree, prepared = self.make_open_review_fixture()
        sealed = json.loads(self.command("seal", "--repo", str(worktree), "--unit", "TASK-5001", cwd=ROOT).stdout)
        before = Path(prepared["record"]).read_bytes()
        report = json.loads(self.command("review", "--repo", str(worktree), "--unit", "TASK-5001", cwd=ROOT).stdout)
        self.assertEqual(report["state"], "sealed")
        self.assertEqual(report["head"], sealed["head"])
        inspected = json.loads(self.command("inspect", "--repo", str(repo), "--unit", "TASK-5001", cwd=ROOT).stdout)
        self.assertEqual(inspected["repair_route"], "linked_repair")
        (worktree / "feature.txt").write_text("unauthorized post-seal change\n")
        run("git", "add", ".", cwd=worktree)
        run("git", "commit", "-m", "simulate sealed drift", cwd=worktree)
        blocked = self.command("review", "--repo", str(worktree), "--unit", "TASK-5001", cwd=ROOT, check=False)
        self.assertNotEqual(blocked.returncode, 0)
        self.assertIn("sealed_head_changed", blocked.stderr)
        self.assertEqual(Path(prepared["record"]).read_bytes(), before)

    def test_review_same_head_reports_no_delta_without_claiming_cached_tests(self):
        repo, worktree, prepared = self.make_open_review_fixture()
        head = run("git", "rev-parse", "HEAD", cwd=worktree).stdout.strip()
        report = json.loads(self.command("review", "--repo", str(worktree), "--unit", "TASK-5001", "--since", head, cwd=ROOT).stdout)
        self.assertEqual(report["changed_paths"], [])
        self.assertEqual(report["tests"], "not_run")
        self.assertEqual(report["acceptance"], "not_assessed")

    def test_inspect_preserves_missing_unit_as_unresolved_not_deleted(self):
        with tempfile.TemporaryDirectory() as raw:
            repo = self.make_repo(Path(raw))
            before = run("git", "status", "--porcelain", cwd=repo).stdout
            result = self.command("inspect", "--repo", str(repo), "--unit", "TASK-MISSING", cwd=ROOT, check=False)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("expected one Change Unit record", result.stderr)
            self.assertNotIn("deleted", result.stderr)
            self.assertEqual(run("git", "status", "--porcelain", cwd=repo).stdout, before)



    def test_inspect_closed_unit_does_not_require_retired_surface(self):
        repo, worktree, prepared = self.make_open_review_fixture()
        sealed = json.loads(self.command("seal", "--repo", str(worktree), "--unit", "TASK-5001", cwd=ROOT).stdout)
        run("git", "merge", "--ff-only", sealed["head"], cwd=repo)
        self.command("close", "--repo", str(repo), "--unit", "TASK-5001", "--disposition", "integrated", "--integration-commit", sealed["head"], "--owner-ref", "TASK-5001#accepted", cwd=ROOT)
        run("git", "worktree", "remove", str(worktree), cwd=repo)
        run("git", "branch", "-d", sealed["branch"], cwd=repo)
        report = json.loads(self.command("inspect", "--repo", str(repo), "--unit", "TASK-5001", cwd=ROOT).stdout)
        self.assertEqual(report["state"], "integrated")
        self.assertEqual(report["repair_route"], "current_target")
        self.assertEqual(report["identity_issues"], [])
        self.assertFalse(report["worktree_exists"])
        self.assertIsNone(report["head"])

    def test_review_rejects_previous_head_before_unit_baseline(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            repo = self.make_repo(root)
            old = run("git", "rev-parse", "HEAD", cwd=repo).stdout.strip()
            (repo / "later.txt").write_text("new target baseline\n")
            run("git", "add", ".", cwd=repo)
            run("git", "commit", "-m", "advance target", cwd=repo)
            worktree = root / "unit"
            self.command("prepare", "--repo", str(repo), "--unit", "TASK-5002", "--slug", "later-review", "--worktree", str(worktree), cwd=ROOT)
            result = self.command("review", "--repo", str(worktree), "--unit", "TASK-5002", "--since", old, cwd=ROOT, check=False)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("within this unit", result.stderr)



    def prepare_fixture(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        root = Path(temporary.name)
        repo = self.make_repo(root)
        worktree = root / "original"
        args = ("prepare", "--repo", str(repo), "--unit", "TASK-UNIQUE",
                "--slug", "original", "--worktree", str(worktree))
        prepared = json.loads(self.command(*args, cwd=ROOT).stdout)
        return root, repo, worktree, args, prepared

    def test_prepare_rejects_duplicate_id_before_creating_sibling(self):
        root, repo, worktree, args, prepared = self.prepare_fixture()
        before = Path(prepared["record"]).read_bytes()
        refs = run("git", "show-ref", cwd=repo).stdout
        for caller in (repo, worktree):
            with self.subTest(caller=caller):
                rejected = self.command(
                    "prepare", "--repo", str(caller), "--unit", "TASK-UNIQUE",
                    "--slug", "sibling", "--worktree", str(root / "sibling"),
                    cwd=ROOT, check=False,
                )
                self.assertNotEqual(rejected.returncode, 0)
                self.assertIn("already registered", rejected.stderr)
        self.assertFalse((root / "sibling").exists())
        self.assertEqual(run("git", "show-ref", cwd=repo).stdout, refs)
        self.assertEqual(Path(prepared["record"]).read_bytes(), before)
        self.assertEqual(len(list(Path(prepared["record"]).parent.glob("*.json"))), 1)
        resumed = json.loads(self.command("resume", "--repo", str(repo), "--unit", "TASK-UNIQUE", cwd=ROOT).stdout)
        self.assertEqual(resumed["worktree"], prepared["worktree"])

    def test_prepare_exact_retry_preserves_original_baseline_and_dirt(self):
        root, repo, worktree, args, prepared = self.prepare_fixture()
        before = Path(prepared["record"]).read_bytes()
        (worktree / "unfinished.txt").write_text("preserve me")
        (repo / "new-main.txt").write_text("advance main")
        run("git", "add", ".", cwd=repo)
        run("git", "commit", "-m", "advance target", cwd=repo)
        repeated = json.loads(self.command(*args, cwd=ROOT).stdout)
        self.assertEqual(repeated["action"], "resumed")
        self.assertEqual(repeated["baseline"], prepared["baseline"])
        self.assertEqual((worktree / "unfinished.txt").read_text(), "preserve me")
        self.assertEqual(Path(prepared["record"]).read_bytes(), before)
        self.assertEqual(len(list(Path(prepared["record"]).parent.glob("*.json"))), 1)

    def test_prepare_does_not_retarget_or_relocate_existing_id(self):
        root, repo, worktree, args, prepared = self.prepare_fixture()
        run("git", "branch", "alternate", cwd=repo)
        before = Path(prepared["record"]).read_bytes()
        for extra in (("--target", "alternate"), ("--worktree", str(root / "moved"))):
            with self.subTest(extra=extra):
                result = self.command(*args, *extra, cwd=ROOT, check=False)
                self.assertNotEqual(result.returncode, 0)
        self.assertFalse((root / "moved").exists())
        self.assertEqual(Path(prepared["record"]).read_bytes(), before)

    def test_prepare_reserves_id_after_sealing_and_retirement(self):
        root, repo, worktree, args, prepared = self.prepare_fixture()
        (worktree / "done.txt").write_text("done")
        run("git", "add", ".", cwd=worktree)
        run("git", "commit", "-m", "finish", cwd=worktree)
        sealed = json.loads(self.command("seal", "--repo", str(worktree), "--unit", "TASK-UNIQUE", cwd=ROOT).stdout)
        rejected = self.command(*args, "--slug", "new-name", "--worktree", str(root / "new-name"), cwd=ROOT, check=False)
        self.assertNotEqual(rejected.returncode, 0)
        self.assertIn("sealed or closed", rejected.stderr)
        run("git", "merge", "--ff-only", sealed["head"], cwd=repo)
        self.command("close", "--repo", str(repo), "--unit", "TASK-UNIQUE", "--disposition", "integrated",
                     "--integration-commit", sealed["head"], "--owner-ref", "TASK-UNIQUE#accepted", cwd=ROOT)
        run("git", "worktree", "remove", str(worktree), cwd=repo)
        run("git", "branch", "-d", sealed["branch"], cwd=repo)
        retired = Path(prepared["record"]).read_bytes()
        rejected = self.command(*args, "--slug", "new-name", "--worktree", str(root / "new-name"), cwd=ROOT, check=False)
        self.assertNotEqual(rejected.returncode, 0)
        self.assertFalse((root / "new-name").exists())
        self.assertEqual(Path(prepared["record"]).read_bytes(), retired)
        self.assertEqual(len(list(Path(prepared["record"]).parent.glob("*.json"))), 1)

    def test_prepare_legacy_duplicates_are_not_extended_or_auto_deleted(self):
        root, repo, worktree, args, prepared = self.prepare_fixture()
        record = Path(prepared["record"])
        extra = record.parent / "legacy-duplicate.json"
        extra.write_bytes(record.read_bytes())
        before = {p.name: p.read_bytes() for p in record.parent.glob("*.json")}
        result = self.command(*args, "--slug", "third", "--worktree", str(root / "third"), cwd=ROOT, check=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("found 2", result.stderr)
        self.assertFalse((root / "third").exists())
        self.assertEqual({p.name: p.read_bytes() for p in record.parent.glob("*.json")}, before)

    def test_prepare_invalid_record_cannot_silently_create_another_unit(self):
        root, repo, worktree, args, prepared = self.prepare_fixture()
        bad = Path(prepared["record"]).parent / "bad.json"
        bad.write_text("not-json")
        result = self.command(*args, "--slug", "third", "--worktree", str(root / "third"), cwd=ROOT, check=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("record is invalid", result.stderr)
        self.assertEqual(bad.read_text(), "not-json")
        self.assertFalse((root / "third").exists())

    def test_prepare_id_namespace_is_per_repository(self):
        root, repo, worktree, args, prepared = self.prepare_fixture()
        other = root / "other-project"
        other.mkdir()
        second = self.make_repo(other)
        result = json.loads(self.command(
            "prepare", "--repo", str(second), "--unit", "TASK-UNIQUE", "--slug", "original",
            "--worktree", str(other / "original"), cwd=ROOT,
        ).stdout)
        self.assertEqual(result["action"], "created")
        self.assertNotEqual(result["record"], prepared["record"])

    def test_prepare_failure_releases_registry_lock(self):
        root, repo, worktree, args, prepared = self.prepare_fixture()
        attempt = ("prepare", "--repo", str(repo), "--unit", "TASK-OTHER", "--slug", "other",
                   "--worktree", str(root / "other"))
        failed = self.command(*attempt, "--target", "missing-ref", cwd=ROOT, check=False)
        self.assertNotEqual(failed.returncode, 0)
        self.assertFalse((root / "other").exists())
        result = json.loads(self.command(*attempt, cwd=ROOT).stdout)
        self.assertEqual(result["action"], "created")

    def wait_marker(self, process, marker):
        deadline = time.monotonic() + 10
        while not marker.exists():
            if process.poll() is not None or time.monotonic() >= deadline:
                self.fail("fixture process did not reach the controlled race point")
            time.sleep(0.01)

    def stop_child(self, process):
        if process.poll() is None:
            process.kill()
        process.communicate(timeout=10)

    def test_prepare_concurrent_duplicate_is_blocked_before_git_creation(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        root = Path(temporary.name)
        repo = self.make_repo(root)
        marker = root / "before-worktree-add"
        child = r"""
import argparse, importlib.util, sys
from pathlib import Path
spec = importlib.util.spec_from_file_location('cu', sys.argv[1])
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
original = m.git
def paused_git(repo, *args, **kwargs):
    if args[:2] == ('worktree', 'add'):
        Path(sys.argv[4]).touch()
        sys.stdin.readline()
    return original(repo, *args, **kwargs)
m.git = paused_git
m.prepare(argparse.Namespace(repo=Path(sys.argv[2]), unit='TASK-RACE', slug='first',
    branch=None, worktree=Path(sys.argv[3]), target='main', target_role='integration-line', parent_unit=None))
"""
        first = subprocess.Popen([sys.executable, "-c", child, str(SCRIPT), str(repo), str(root / "first"), str(marker)],
                                 stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        self.addCleanup(self.stop_child, first)
        self.wait_marker(first, marker)
        # The first invocation holds the lock but has not written its record yet.
        args = ("prepare", "--repo", str(repo), "--unit", "TASK-RACE", "--slug", "second",
                "--worktree", str(root / "second"))
        second = self.command(*args, cwd=ROOT, check=False)
        self.assertNotEqual(second.returncode, 0)
        self.assertIn("preparation lock unavailable", second.stderr)
        self.assertFalse((root / "second").exists())
        out, err = first.communicate("continue\n", timeout=10)
        self.assertEqual(first.returncode, 0, err)
        retry = self.command(*args, cwd=ROOT, check=False)
        self.assertNotEqual(retry.returncode, 0)
        self.assertIn("already registered", retry.stderr)
        records = list((repo / ".git/senmu-buildos/change-units").glob("*.json"))
        self.assertEqual(len(records), 1)
        self.assertEqual(json.loads(records[0].read_text())["branch"], "codex/first")
        self.assertEqual(len(run("git", "for-each-ref", "refs/heads", cwd=repo).stdout.splitlines()), 2)

    def test_prepare_process_exit_releases_lock_without_deleting_marker(self):
        root, repo, worktree, args, prepared = self.prepare_fixture()
        marker = root / "lock-held"
        child = r"""
import importlib.util, sys
from pathlib import Path
spec = importlib.util.spec_from_file_location('cu', sys.argv[1])
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
with m.preparation_lock(Path(sys.argv[2])):
    Path(sys.argv[3]).touch()
    sys.stdin.readline()
"""
        holder = subprocess.Popen([sys.executable, "-c", child, str(SCRIPT), str(repo), str(marker)],
                                  stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        self.addCleanup(self.stop_child, holder)
        self.wait_marker(holder, marker)
        busy = self.command(*args, cwd=ROOT, check=False)
        self.assertNotEqual(busy.returncode, 0)
        holder.kill(); holder.communicate(timeout=10)
        self.assertTrue((repo / ".git/senmu-buildos/change-units.prepare.lock").exists())
        resumed = json.loads(self.command(*args, cwd=ROOT).stdout)
        self.assertEqual(resumed["action"], "resumed")



    # Cross-entrypoint regressions use the same corrupted fixture for observation,
    # recovery, verification and state writes. All mutations stay in temporary repos.
    def assert_entrypoints_reject(self, repo, worktree, prepared):
        path = Path(prepared["record"])
        before = {p.name: p.read_bytes() for p in path.parent.glob("*.json")}
        refs = run("git", "show-ref", cwd=repo).stdout
        calls = [
            ("prepare", "--repo", str(repo), "--unit", prepared["unit"],
             "--slug", "open-review", "--branch", prepared["branch"], "--worktree", str(worktree)),
            ("resume", "--repo", str(repo), "--unit", prepared["unit"]),
            ("verify", "--repo", str(worktree), "--unit", prepared["unit"]),
            ("review", "--repo", str(worktree), "--unit", prepared["unit"]),
            ("seal", "--repo", str(worktree), "--unit", prepared["unit"]),
            ("close", "--repo", str(repo), "--unit", prepared["unit"],
             "--disposition", "excluded", "--owner-ref", "fixture#decision"),
        ]
        for call in calls:
            with self.subTest(command=call[0]):
                result = self.command(*call, cwd=ROOT, check=False)
                self.assertNotEqual(result.returncode, 0, result.stdout)
                self.assertIn("[BLOCKED]", result.stderr)
                self.assertEqual({p.name: p.read_bytes() for p in path.parent.glob("*.json")}, before)
                self.assertEqual(run("git", "show-ref", cwd=repo).stdout, refs)

    def test_consistency_legacy_duplicate_blocks_all_entrypoints(self):
        repo, worktree, prepared = self.make_open_review_fixture()
        import hashlib
        duplicate = {**json.loads(Path(prepared["record"]).read_text()), "branch": "codex/legacy-copy"}
        name = hashlib.sha256(duplicate["branch"].encode()).hexdigest()[:20] + ".json"
        Path(prepared["record"]).with_name(name).write_text(json.dumps(duplicate))
        self.assert_entrypoints_reject(repo, worktree, prepared)
        result = self.command("inspect", "--repo", str(repo), "--unit", prepared["unit"], cwd=ROOT, check=False)
        self.assertIn("found 2", result.stderr)

    def test_consistency_divergent_history_blocks_all_entrypoints(self):
        repo, worktree, prepared = self.make_open_review_fixture()
        # A real unrelated commit, not a mock of Git's ancestry result.
        run("git", "checkout", "--orphan", "other-history", cwd=repo)
        (repo / "other.txt").write_text("unrelated root\n")
        run("git", "add", ".", cwd=repo)
        run("git", "commit", "-m", "unrelated root", cwd=repo)
        head = run("git", "rev-parse", "HEAD", cwd=repo).stdout.strip()
        run("git", "reset", "--hard", head, cwd=worktree)
        observed = json.loads(self.command("inspect", "--repo", str(repo), "--unit", prepared["unit"], cwd=ROOT).stdout)
        self.assertIn("baseline_not_ancestor", observed["identity_issues"])
        self.assert_entrypoints_reject(repo, worktree, prepared)

    def test_consistency_foreign_path_is_not_resumed_or_prepared(self):
        repo, worktree, prepared = self.make_open_review_fixture()
        import shutil
        shutil.rmtree(worktree)  # Only the disposable fixture created above.
        worktree.mkdir()
        run("git", "init", "-b", "main", cwd=worktree)
        run("git", "config", "user.name", "Foreign fixture", cwd=worktree)
        run("git", "config", "user.email", "fixture@example.test", cwd=worktree)
        (worktree / "preserve.txt").write_text("foreign content\n")
        run("git", "add", ".", cwd=worktree)
        run("git", "commit", "-m", "foreign root", cwd=worktree)
        observed = json.loads(self.command("inspect", "--repo", str(repo), "--unit", prepared["unit"], cwd=ROOT).stdout)
        self.assertIn("worktree_identity_mismatch", observed["identity_issues"])
        self.assert_entrypoints_reject(repo, worktree, prepared)
        self.assertEqual((worktree / "preserve.txt").read_text(), "foreign content\n")

    def test_consistency_mislocated_record_blocks_state_writes(self):
        repo, worktree, prepared = self.make_open_review_fixture()
        path = Path(prepared["record"])
        moved = path.with_name("legacy-mislocated.json")
        path.rename(moved)
        observed = json.loads(self.command("inspect", "--repo", str(repo), "--unit", prepared["unit"], cwd=ROOT).stdout)
        self.assertIn("record_location_mismatch", observed["identity_issues"])
        self.assert_entrypoints_reject(repo, worktree, {**prepared, "record": str(moved)})
        self.assertFalse(path.exists())

    def test_consistency_symbolic_baseline_does_not_follow_moving_refs(self):
        repo, worktree, prepared = self.make_open_review_fixture()
        path = Path(prepared["record"])
        record = json.loads(path.read_text())
        record["baseline"] = "main"
        path.write_text(json.dumps(record))
        self.assert_entrypoints_reject(repo, worktree, prepared)

    def test_consistency_excluded_close_does_not_hide_sealed_drift(self):
        repo, worktree, prepared = self.make_open_review_fixture()
        self.command("seal", "--repo", str(worktree), "--unit", prepared["unit"], cwd=ROOT)
        (worktree / "feature.txt").write_text("changed after seal\n")
        run("git", "add", ".", cwd=worktree)
        run("git", "commit", "-m", "simulate sealed drift", cwd=worktree)
        self.assert_entrypoints_reject(repo, worktree, prepared)

    def test_consistency_valid_missing_surface_recovers_without_sibling(self):
        for command in ("resume", "prepare"):
            with self.subTest(command=command):
                repo, worktree, prepared = self.make_open_review_fixture()
                before = Path(prepared["record"]).read_bytes()
                head = run("git", "rev-parse", "HEAD", cwd=worktree).stdout.strip()
                run("git", "worktree", "remove", str(worktree), cwd=repo)
                args = [command, "--repo", str(repo), "--unit", prepared["unit"]]
                if command == "prepare":
                    args += ["--slug", "open-review", "--worktree", str(worktree)]
                result = json.loads(self.command(*args, cwd=ROOT).stdout)
                self.assertEqual(result["action"], "resumed")
                self.assertEqual(run("git", "rev-parse", "HEAD", cwd=worktree).stdout.strip(), head)
                self.assertEqual(Path(prepared["record"]).read_bytes(), before)
                self.assertEqual(len(run("git", "for-each-ref", "refs/heads", cwd=repo).stdout.splitlines()), 2)

    def test_consistency_close_can_prove_retired_sealed_source(self):
        repo, worktree, prepared = self.make_open_review_fixture()
        sealed = json.loads(self.command("seal", "--repo", str(worktree), "--unit", prepared["unit"], cwd=ROOT).stdout)
        run("git", "merge", "--ff-only", sealed["head"], cwd=repo)
        run("git", "worktree", "remove", str(worktree), cwd=repo)
        run("git", "branch", "-d", prepared["branch"], cwd=repo)
        closed = json.loads(self.command(
            "close", "--repo", str(repo), "--unit", prepared["unit"],
            "--disposition", "integrated", "--integration-commit", sealed["head"],
            "--owner-ref", "fixture#accepted", cwd=ROOT).stdout)
        self.assertEqual(closed["integration_proof"]["kind"], "exact_commit")
        self.assertFalse(worktree.exists())

    def make_summary_fixture(self, count=120):
        repo, worktree, prepared = self.make_open_review_fixture()
        import hashlib
        path = Path(prepared["record"])
        base = json.loads(path.read_text())
        for i in range(count):
            item = {**base, "unit": f"TASK-HISTORY-{i:04d}", "branch": f"codex/history-{i:04d}",
                    "state": "superseded", "worktree": str(worktree.parent / f"retired-{i:04d}")}
            name = hashlib.sha256(item["branch"].encode()).hexdigest()[:20] + ".json"
            path.with_name(name).write_text(json.dumps(item))
        return repo, worktree, prepared

    def test_summary_default_bounds_history_without_hiding_counts(self):
        repo, worktree, prepared = self.make_summary_fixture()
        result = self.command("list", "--repo", str(repo), cwd=ROOT)
        report = json.loads(result.stdout)
        self.assertEqual(report["schema_version"], 2)
        self.assertEqual(report["total_records"], 121)
        self.assertEqual(report["counts_by_state"]["superseded"], 120)
        self.assertEqual(report["counts_by_state"]["in_progress"], 1)
        self.assertEqual(report["matching_records"], 1)
        self.assertEqual(len(report["units"]), 1)
        self.assertIsNone(report["next_offset"])
        self.assertLess(len(result.stdout.encode()), 8000)
        self.assertEqual(report["identity_checks"], "registration_only")

    def test_summary_pages_all_records_without_duplicates_or_loss(self):
        repo, worktree, prepared = self.make_summary_fixture(24)
        seen = []
        offset = 0
        while offset is not None:
            report = json.loads(self.command("list", "--repo", str(repo), "--state", "all",
                "--limit", "7", "--offset", str(offset), cwd=ROOT).stdout)
            self.assertEqual(report["matching_records"], 25)
            self.assertLessEqual(len(report["units"]), 7)
            seen.extend(item["unit"] for item in report["units"])
            offset = report["next_offset"]
        self.assertEqual(len(seen), 25)
        self.assertEqual(len(set(seen)), 25)
        report = json.loads(self.command("list", "--repo", str(repo), "--unit", "TASK-HISTORY-0001", cwd=ROOT).stdout)
        self.assertEqual(report["matching_records"], 1)
        self.assertEqual(report["units"][0]["unit"], "TASK-HISTORY-0001")

    def test_summary_reports_invalid_and_duplicate_registration_without_mutation(self):
        repo, worktree, prepared = self.make_summary_fixture(2)
        path = Path(prepared["record"])
        duplicate = json.loads(path.read_text())
        path.with_name("duplicate.json").write_text(json.dumps(duplicate))
        path.with_name("invalid.json").write_text("{not json")
        before = {p.name: p.read_bytes() for p in path.parent.glob("*.json")}
        report = json.loads(self.command("list", "--repo", str(repo), "--issues-only", cwd=ROOT).stdout)
        self.assertEqual(report["total_records"], 5)
        self.assertEqual(report["issue_records"], 3)
        self.assertEqual(len(report["units"]), 3)
        codes = {code for item in report["units"] for code in item["identity_issues"]}
        self.assertIn("duplicate_unit", codes)
        self.assertIn("record_unreadable", codes)
        self.assertEqual(before, {p.name: p.read_bytes() for p in path.parent.glob("*.json")})

    def test_summary_legacy_full_format_remains_explicit(self):
        repo, worktree, prepared = self.make_summary_fixture(3)
        result = json.loads(self.command("list", "--repo", str(repo), "--format", "full", cwd=ROOT).stdout)
        self.assertEqual(set(result), {"schema_version", "repository_root", "units"})
        self.assertEqual(result["schema_version"], 1)
        self.assertEqual(len(result["units"]), 4)
        self.assertIn("candidate_reachable", result["units"][0])
        self.assertIn("integration_proof", result["units"][0])

    def test_summary_rejects_invalid_paging_and_full_filter_combinations(self):
        repo, worktree, prepared = self.make_open_review_fixture()
        for extra in (("--limit", "0"), ("--limit", "101"), ("--offset", "-1"),
                      ("--format", "full", "--unit", prepared["unit"]),
                      ("--format", "full", "--limit", "2")):
            with self.subTest(extra=extra):
                result = self.command("list", "--repo", str(repo), *extra, cwd=ROOT, check=False)
                self.assertNotEqual(result.returncode, 0)

    def test_summary_anomaly_sample_is_bounded_and_expandable(self):
        repo, worktree, prepared = self.make_open_review_fixture()
        path = Path(prepared["record"])
        for i in range(30):
            path.with_name(f"invalid-{i:03d}.json").write_text("null")
        report = json.loads(self.command("list", "--repo", str(repo), cwd=ROOT).stdout)
        self.assertEqual(report["issue_records"], 30)
        self.assertLessEqual(len(report["issues"]), 10)
        self.assertTrue(report["issues_truncated"])
        page = json.loads(self.command("list", "--repo", str(repo), "--issues-only", "--offset", "10", cwd=ROOT).stdout)
        self.assertEqual(page["matching_records"], 30)
        self.assertEqual(page["next_offset"], 20)


if __name__ == "__main__":
    unittest.main()
