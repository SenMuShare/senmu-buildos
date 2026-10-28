from __future__ import annotations

import argparse
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import test_change_unit_management as existing_fixture


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills/senmu-build-delivery/scripts/manage_change_unit.py"


class NoChangesCloseoutTests(unittest.TestCase):
    """Exercise lifecycle decisions against real temporary Git repositories."""

    def setUp(self) -> None:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name).resolve()
        self.repo = existing_fixture.ChangeUnitManagementTests().make_repo(self.root)

    def git(self, *args: str, cwd: Path | None = None) -> str:
        return existing_fixture.run("git", *args, cwd=cwd or self.repo).stdout.strip()

    def cli(self, *args: str) -> subprocess.CompletedProcess[str]:
        return existing_fixture.run(sys.executable, str(SCRIPT), *args, cwd=ROOT, check=False)

    def good(self, *args: str) -> dict:
        result = self.cli(*args)
        self.assertEqual(result.returncode, 0, result.stderr)
        return json.loads(result.stdout)

    def prepare(self, slug: str, *extra: str) -> dict:
        return self.good("prepare", "--repo", str(self.repo), "--unit", "TASK-" + slug.upper(),
                         "--slug", slug, "--worktree", str(self.root / slug), *extra)

    def owner(self, slug: str, status: str) -> Path:
        path = self.root / (slug + "-task-run.json")
        path.write_text(json.dumps({"kind": "task-run", "synthetic": True, "status": status}))
        return path

    def close(self, unit: dict, owner: Path | str, *extra: str) -> subprocess.CompletedProcess[str]:
        return self.cli("close", "--repo", str(self.repo), "--unit", unit["unit"],
                        "--disposition", "no_changes", "--owner-ref", str(owner), *extra)

    def reject_unchanged(self, unit: dict, owner: Path | str, *extra: str) -> None:
        record = Path(unit["record"])
        before = record.read_bytes()
        refs = self.git("show-ref")
        result = self.close(unit, owner, *extra)
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn("[BLOCKED]", result.stderr)
        self.assertNotIn("Traceback", result.stderr)
        self.assertEqual(record.read_bytes(), before)
        self.assertEqual(self.git("show-ref"), refs)

    def test_unchanged_named_and_frozen_units_close_without_claiming_task_success(self) -> None:
        baseline = self.git("rev-parse", "HEAD")
        cases = [
            ("failed-run", "failed", ()),
            ("cancelled-run", "cancelled", ("--target", baseline, "--target-role", "frozen-commit")),
            ("no-edit-needed", "no_change_needed", ()),
        ]
        for slug, outcome, extra in cases:
            with self.subTest(outcome=outcome):
                unit = self.prepare(slug, *extra)
                original = json.loads(Path(unit["record"]).read_text())
                owner = self.owner(slug, outcome)
                owner_before = owner.read_bytes()
                result = self.close(unit, owner)
                self.assertEqual(result.returncode, 0, result.stderr)
                closed = json.loads(result.stdout)
                self.assertEqual(closed["state"], "no_changes")
                self.assertEqual(closed["owner_ref"], str(owner))
                self.assertEqual(closed["head"], baseline)
                self.assertIsNone(closed["integration_commit"])
                self.assertNotIn("integration_proof", closed)
                self.assertTrue(closed["closed_at"])
                stored = json.loads(Path(unit["record"]).read_text())
                for key, value in original.items():
                    self.assertEqual(stored[key], "no_changes" if key == "state" else value)
                self.assertEqual(owner.read_bytes(), owner_before)
                observed = self.good("inspect", "--repo", str(self.repo), "--unit", unit["unit"])
                self.assertEqual(observed["identity_issues"], [])
                self.assertEqual(observed["acceptance"], "not_assessed")
                self.assertTrue(Path(unit["worktree"]).is_dir())
                self.assertEqual(self.git("rev-parse", unit["branch"]), baseline)

    def test_ignored_run_output_is_preserved_when_git_unit_closes(self) -> None:
        (self.repo / ".gitignore").write_text("runtime-output.bin\n")
        self.git("add", ".gitignore")
        self.git("commit", "-m", "declare disposable execution output boundary")
        unit = self.prepare("ignored-output")
        worktree = Path(unit["worktree"])
        output = worktree / "runtime-output.bin"
        output.write_bytes(b"retained failed-run output\x00")
        before = output.read_bytes()
        self.assertEqual(self.git("status", "--porcelain", cwd=worktree), "")
        result = self.close(unit, self.owner("ignored-output", "failed"))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["state"], "no_changes")
        self.assertTrue(worktree.is_dir())
        self.assertEqual(output.read_bytes(), before)

    def test_target_can_advance_while_source_remains_at_its_original_baseline(self) -> None:
        unit = self.prepare("target-advance")
        (self.repo / "other-task.txt").write_text("another task advances main\n")
        self.git("add", "other-task.txt")
        self.git("commit", "-m", "advance receiving line independently")
        target_head = self.git("rev-parse", "HEAD")
        self.assertNotEqual(target_head, unit["baseline"])
        result = self.close(unit, self.owner("target-advance", "failed"))
        self.assertEqual(result.returncode, 0, result.stderr)
        closed = json.loads(result.stdout)
        self.assertEqual(closed["head"], unit["baseline"])
        self.assertEqual(closed["target"], "main")
        self.assertEqual(self.git("rev-parse", "HEAD"), target_head)

    def test_dirty_tracked_staged_and_untracked_work_is_preserved(self) -> None:
        for kind in ("tracked", "staged", "untracked"):
            with self.subTest(kind=kind):
                unit = self.prepare("dirty-" + kind)
                worktree = Path(unit["worktree"])
                path = worktree / ("scratch.txt" if kind == "untracked" else "base.txt")
                path.write_text("unfinished work must survive\n")
                if kind == "staged":
                    self.git("add", "base.txt", cwd=worktree)
                before = self.git("status", "--porcelain", cwd=worktree)
                self.reject_unchanged(unit, "task:unfinished")
                self.assertEqual(path.read_text(), "unfinished work must survive\n")
                self.assertEqual(self.git("status", "--porcelain", cwd=worktree), before)

    def test_empty_commit_and_reverted_changes_cannot_hide_source_history(self) -> None:
        for kind in ("empty", "reverted"):
            with self.subTest(kind=kind):
                unit = self.prepare("history-" + kind)
                worktree = Path(unit["worktree"])
                if kind == "empty":
                    self.git("commit", "--allow-empty", "-m", "not a no-source-change unit", cwd=worktree)
                else:
                    (worktree / "base.txt").write_text("changed\n")
                    self.git("commit", "-am", "make a real change", cwd=worktree)
                    self.git("revert", "--no-edit", "HEAD", cwd=worktree)
                self.assertEqual(self.git("diff", unit["baseline"], "HEAD", cwd=worktree), "")
                self.assertNotEqual(self.git("rev-parse", "HEAD", cwd=worktree), unit["baseline"])
                self.reject_unchanged(unit, "task:net-zero-is-not-no-changes")

    def test_sealing_and_existing_sealed_dispositions_keep_their_boundaries(self) -> None:
        unit = self.prepare("seal-boundary")
        record = Path(unit["record"])
        before = record.read_bytes()
        blocked = self.cli("seal", "--repo", unit["worktree"], "--unit", unit["unit"])
        self.assertNotEqual(blocked.returncode, 0)
        self.assertEqual(record.read_bytes(), before)
        worktree = Path(unit["worktree"])
        (worktree / "feature.txt").write_text("a real candidate\n")
        self.git("add", "feature.txt", cwd=worktree)
        self.git("commit", "-m", "candidate", cwd=worktree)
        self.good("seal", "--repo", str(worktree), "--unit", unit["unit"])
        self.reject_unchanged(unit, "task:sealed-cannot-become-no-changes")
        closed = self.good("close", "--repo", str(self.repo), "--unit", unit["unit"],
                           "--disposition", "excluded", "--owner-ref", "task:scope-decision")
        self.assertEqual(closed["state"], "excluded")

    def test_no_changes_cannot_receive_integration_arguments_or_blank_owner(self) -> None:
        unit = self.prepare("reject-reception")
        for extra in (("--integration-commit", unit["baseline"]),
                      ("--integration-base", unit["baseline"]),
                      ("--integration-target", "main"),
                      ("--target-authorization-ref", "task:receiving-line")):
            with self.subTest(argument=extra[0]):
                self.reject_unchanged(unit, "task:no-integration", *extra)
        self.reject_unchanged(unit, "  ")

    def test_live_registered_source_is_required_before_closeout(self) -> None:
        for kind in ("moved", "detached", "missing-worktree", "missing-branch"):
            with self.subTest(kind=kind):
                unit = self.prepare("identity-" + kind)
                worktree = Path(unit["worktree"])
                if kind == "moved":
                    self.git("worktree", "move", str(worktree), str(self.root / "moved-source"))
                elif kind == "detached":
                    self.git("switch", "--detach", cwd=worktree)
                else:
                    self.git("worktree", "remove", str(worktree))
                    if kind == "missing-branch":
                        self.git("branch", "-d", unit["branch"])
                self.reject_unchanged(unit, "task:identity-unresolved")

    def test_closed_unit_is_retired_but_remains_inspectable_after_native_retirement(self) -> None:
        unit = self.prepare("retired-record")
        result = self.close(unit, self.owner("retired-record", "cancelled"))
        self.assertEqual(result.returncode, 0, result.stderr)
        record = Path(unit["record"])
        closed_bytes = record.read_bytes()
        active = self.good("list", "--repo", str(self.repo))
        self.assertEqual(active["units"], [])
        self.assertEqual(active["counts_by_state"]["no_changes"], 1)
        for extra in (("--unit", unit["unit"]), ("--state", "no_changes"), ("--format", "full")):
            with self.subTest(list_arguments=extra):
                listed = self.good("list", "--repo", str(self.repo), *extra)
                self.assertEqual(listed["units"][0]["state"], "no_changes")
        for args in (
            ("resume", "--repo", str(self.repo), "--unit", unit["unit"]),
            ("verify", "--repo", unit["worktree"], "--unit", unit["unit"]),
            ("review", "--repo", unit["worktree"], "--unit", unit["unit"]),
            ("prepare", "--repo", str(self.repo), "--unit", unit["unit"],
             "--slug", "retired-record", "--worktree", unit["worktree"]),
            ("prepare", "--repo", str(self.repo), "--unit", unit["unit"],
             "--slug", "new-sibling", "--worktree", str(self.root / "new-sibling")),
        ):
            with self.subTest(command=args[0]):
                rejected = self.cli(*args)
                self.assertNotEqual(rejected.returncode, 0, rejected.stdout)
                self.assertEqual(record.read_bytes(), closed_bytes)
        self.assertFalse((self.root / "new-sibling").exists())
        self.git("worktree", "remove", unit["worktree"])
        self.git("branch", "-d", unit["branch"])
        observed = self.good("inspect", "--repo", str(self.repo), "--unit", unit["unit"])
        self.assertEqual(observed["state"], "no_changes")
        self.assertEqual(observed["identity_issues"], [])
        self.assertFalse(observed["worktree_exists"])
        self.assertIsNone(observed["head"])
        self.assertEqual(observed["acceptance"], "not_assessed")
        full = self.good("list", "--repo", str(self.repo), "--format", "full")
        self.assertEqual(full["units"][0]["derived_disposition"], "no_changes")
        self.assertIsNone(full["units"][0]["candidate_reachable"])
        self.assertEqual(record.read_bytes(), closed_bytes)

    def test_release_control_cannot_receive_no_changes_as_included_source(self) -> None:
        fixture = existing_fixture.FeedbackLifecycleTests()
        self.addCleanup(fixture.doCleanups)
        fixture.setUp()
        integrated = fixture.integrated_unit()
        data = fixture.release_record(integrated)
        result, report = fixture.check_release(data)
        self.assertEqual(result.returncode, 0, report)

        prepared = fixture.prepare("no-source")
        closed = fixture.good("manage_change_unit.py", "close", "--repo", fixture.repo,
                              "--unit", prepared["unit"], "--disposition", "no_changes",
                              "--owner-ref", "task:failed-run")
        record = Path(closed["record"])
        before = record.read_bytes()
        # Only the proposed release sheet claims inclusion; the real ledger remains no_changes.
        data["change_units"].append({
            "unit": closed["unit"], "branch": closed["branch"], "source_commit": closed["head"],
            "integration_commit": integrated["integration_commit"], "disposition": "include",
            "evidence_refs": ["task:proposed-inclusion"], "test_refs": ["test:structure-only"],
        })
        data["cleanup"].append({**data["cleanup"][0], "unit": closed["unit"],
                                "branch": closed["branch"], "worktree": closed["worktree"]})
        result, report = fixture.check_release(data)
        self.assertNotEqual(result.returncode, 0, report)
        self.assertTrue(report["structure_valid"], report)
        self.assertTrue(report["git_state_checked"], report)
        self.assertIn(closed["unit"] + ": included unit is not registered integrated", report["errors"])
        self.assertEqual(next(item for item in report["units"] if item["unit"] == closed["unit"])["state"],
                         "no_changes")
        self.assertEqual(record.read_bytes(), before)

    def test_closed_source_drift_and_inconsistent_frozen_head_remain_visible(self) -> None:
        unit = self.prepare("closed-drift")
        result = self.close(unit, self.owner("closed-drift", "failed"))
        self.assertEqual(result.returncode, 0, result.stderr)
        record = Path(unit["record"])
        closed_bytes = record.read_bytes()
        self.git("commit", "--allow-empty", "-m", "simulate post-close branch drift",
                 cwd=Path(unit["worktree"]))
        observed = self.good("inspect", "--repo", str(self.repo), "--unit", unit["unit"])
        self.assertIn("no_changes_head_changed", observed["identity_issues"])
        self.assertEqual(record.read_bytes(), closed_bytes)

        # Rebinding the receipt to the new branch head must not erase the anomaly.
        forged = json.loads(closed_bytes)
        forged["head"] = self.git("rev-parse", unit["branch"])
        record.write_text(json.dumps(forged))
        forged_bytes = record.read_bytes()
        observed = self.good("inspect", "--repo", str(self.repo), "--unit", unit["unit"])
        self.assertIn("no_changes_baseline_mismatch", observed["identity_issues"])
        summary = self.good("list", "--repo", str(self.repo), "--unit", unit["unit"])
        self.assertIn("no_changes_baseline_mismatch", summary["units"][0]["identity_issues"])
        self.assertEqual(record.read_bytes(), forged_bytes)

    def test_close_reobserves_real_source_changes_before_writing_the_record(self) -> None:
        for kind in ("dirty", "head"):
            with self.subTest(kind=kind):
                unit = self.prepare("close-race-" + kind)
                worktree = Path(unit["worktree"])
                record = Path(unit["record"])
                before = record.read_bytes()
                spec = importlib.util.spec_from_file_location("no_changes_race", SCRIPT)
                assert spec and spec.loader
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                original_observe = module.observe_unit
                observations = 0

                def change_before_reobservation(repo: Path, unit_id: str):
                    nonlocal observations
                    observations += 1
                    if observations == 2:
                        if kind == "dirty":
                            (worktree / "concurrent.txt").write_text("preserve another writer's work\n")
                        else:
                            self.git("commit", "--allow-empty", "-m", "concurrent writer", cwd=worktree)
                    return original_observe(repo, unit_id)

                # Only schedule an actual filesystem/Git change; use every real identity check.
                module.observe_unit = change_before_reobservation
                args = argparse.Namespace(repo=self.repo, unit=unit["unit"], disposition="no_changes",
                                          owner_ref="task:failed-race-run", integration_commit=None,
                                          integration_base=None, integration_target=None,
                                          target_authorization_ref=None)
                with self.assertRaisesRegex(SystemExit, "changed during closeout"):
                    module.close(args)
                self.assertEqual(observations, 2)
                self.assertEqual(record.read_bytes(), before)
                if kind == "dirty":
                    self.assertEqual((worktree / "concurrent.txt").read_text(), "preserve another writer's work\n")
                else:
                    self.assertNotEqual(self.git("rev-parse", "HEAD", cwd=worktree), unit["baseline"])


if __name__ == "__main__":
    unittest.main()
