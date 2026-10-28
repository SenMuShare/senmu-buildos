from __future__ import annotations

import copy
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills/senmu-build-delivery/scripts/validate_release_control.py"
TEMPLATE = ROOT / "skills/senmu-build-delivery/assets/delivery-governance/RELEASE_CONTROL.template.json"
SPEC = importlib.util.spec_from_file_location("validate_release_control", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class ReleaseControlTests(unittest.TestCase):
    def valid_closed_record(self) -> dict:
        record = json.loads(TEMPLATE.read_text(encoding="utf-8"))
        # Legacy source-only releases do not opt into resource closeout.
        record.pop("resource_closeout", None)
        record["release"].update(
            {
                "candidate_commit": "abc123",
                "authorization_ref": "user-request-2026-09-02",
                "release_record_ref": "governance/releases/REL-0001.md",
                "status": "closed",
            }
        )
        record["requirements"] = [
            {"id": "REQ-1", "disposition": "include", "evidence_refs": ["task:REQ-1"], "reason": None}
        ]
        record["change_units"] = [
            {
                "unit": "TASK-1",
                "branch": "codex/task-1",
                "source_commit": "source123",
                "disposition": "include",
                "evidence_refs": ["change-unit:TASK-1"],
                "test_refs": ["test:unit"],
                "integration_commit": "integrated123",
                "reason": None,
            }
        ]
        for gate in record["gates"]:
            gate.update({"status": "passed", "evidence_refs": [f"evidence:{gate['id']}"]})
        record["cleanup"] = [
            {
                "unit": "TASK-1",
                "branch": "codex/task-1",
                "worktree": "/tmp/task-1",
                "disposition": "removed",
                "evidence_refs": ["git:worktree-list"],
                "owner": None,
                "exit_condition": None,
            }
        ]
        return record

    def test_valid_closed_record_is_accepted(self) -> None:
        self.assertEqual(MODULE.validate_record(self.valid_closed_record()), [])

    def test_later_gate_cannot_close_before_an_earlier_gate(self) -> None:
        record = self.valid_closed_record()
        record["release"]["status"] = "candidate"
        record["gates"][1].update({"status": "pending", "evidence_refs": []})
        errors = MODULE.validate_record(record)
        self.assertTrue(any("cannot close before an earlier unfinished gate" in error for error in errors))

    def test_scope_gate_rejects_unaccounted_requirement(self) -> None:
        record = self.valid_closed_record()
        record["release"]["status"] = "planning"
        record["requirements"][0].update({"disposition": "pending", "evidence_refs": []})
        errors = MODULE.validate_record(record)
        self.assertIn("scope_accounted cannot pass while requirements are pending or blocked", errors)

    def test_git_closeout_requires_cleanup_for_each_included_unit(self) -> None:
        record = self.valid_closed_record()
        record["cleanup"] = []
        errors = MODULE.validate_record(record)
        self.assertTrue(any("missing cleanup rows" in error for error in errors))

    def test_retained_cleanup_requires_owner_and_exit_condition(self) -> None:
        record = copy.deepcopy(self.valid_closed_record())
        record["cleanup"][0].update({"disposition": "retained", "owner": None, "exit_condition": None})
        errors = MODULE.validate_record(record)
        self.assertTrue(any("requires owner and exit_condition" in error for error in errors))

    def test_git_closeout_rejects_any_unfinished_cleanup_row(self) -> None:
        record = self.valid_closed_record()
        record["cleanup"].append(
            {
                "unit": "TASK-2",
                "branch": "codex/task-2",
                "worktree": "/tmp/task-2",
                "disposition": "pending",
                "evidence_refs": [],
                "owner": None,
                "exit_condition": None,
            }
        )
        errors = MODULE.validate_record(record)
        self.assertTrue(any("unfinished cleanup rows" in error for error in errors))

    def resource_record(self) -> dict:
        record = self.valid_closed_record()
        group_ids = ["images", "dependencies", "historical_directories"]
        record["resource_closeout"] = {
            "scope_ref": "policy:release-assets",
            "required_groups": group_ids,
            "status": "complete",
            "groups": [
                {
                    "id": group_id,
                    "scope": "synthetic application only",
                    "surface": f"inventory:{group_id}",
                    "status": "completed",
                    "evidence_refs": [f"receipt:{group_id}"],
                    "owner": "release owner",
                    "retention_ref": f"policy:{group_id}",
                }
                for group_id in group_ids
            ],
        }
        return record

    def test_resource_complete_accepts_exact_accounted_scope(self) -> None:
        record = self.resource_record()
        record["resource_closeout"]["groups"][1]["status"] = "no_candidates"
        self.assertEqual(MODULE.validate_record(record), [])

    def test_resource_complete_rejects_held_directories_and_disabled_groups(self) -> None:
        for status in ("pending", "planned", "disabled", "blocked", "failed", "unknown"):
            with self.subTest(status=status):
                record = self.resource_record()
                record["resource_closeout"]["groups"][2].update(
                    status=status, reason="held for reconciliation", next_action="identify consumers"
                )
                errors = MODULE.validate_record(record)
                self.assertTrue(any("cannot be complete" in error for error in errors), errors)

    def test_resource_closed_rejects_partial_but_released_can_resume(self) -> None:
        record = self.resource_record()
        record["resource_closeout"]["status"] = "partial"
        record["resource_closeout"]["groups"][2].update(
            status="pending", reason="consumer identity unresolved", next_action="inspect consumer identity"
        )
        errors = MODULE.validate_record(record)
        self.assertTrue(any("closed requires resource_closeout" in error for error in errors), errors)
        record["release"]["status"] = "released"
        self.assertEqual(MODULE.validate_record(record), [])

    def test_resource_complete_rejects_missing_duplicate_extra_or_invalid_groups(self) -> None:
        mutations = {
            "missing": lambda block: block["groups"].pop(),
            "duplicate": lambda block: block["groups"].append(copy.deepcopy(block["groups"][0])),
            "extra": lambda block: block["groups"].append(dict(block["groups"][0], id="undeclared")),
            "invalid": lambda block: block["groups"].append("not an object"),
            "empty": lambda block: block.update(groups=[]),
        }
        for case, mutate in mutations.items():
            with self.subTest(case=case):
                record = self.resource_record()
                mutate(record["resource_closeout"])
                self.assertTrue(MODULE.validate_record(record))

    def test_resource_required_groups_must_be_nonempty_unique_strings(self) -> None:
        for required_groups in ([], ["images", "images"], [""], [7], "images", ["images", []]):
            with self.subTest(required_groups=required_groups):
                record = self.resource_record()
                record["resource_closeout"]["required_groups"] = required_groups
                self.assertTrue(MODULE.validate_record(record))

    def test_resource_complete_requires_scope_policy_owner_and_evidence(self) -> None:
        for field in ("scope", "surface", "owner", "retention_ref", "evidence_refs"):
            with self.subTest(field=field):
                record = self.resource_record()
                record["resource_closeout"]["groups"][0][field] = [] if field == "evidence_refs" else ""
                self.assertTrue(MODULE.validate_record(record))
        record = self.resource_record()
        record["resource_closeout"]["scope_ref"] = ""
        self.assertTrue(MODULE.validate_record(record))

    def test_resource_retained_requires_declared_policy_basis_and_exit(self) -> None:
        for basis in ("current", "rollback", "pin", "recovery", "evidence", "approved_policy"):
            with self.subTest(basis=basis):
                record = self.resource_record()
                group = record["resource_closeout"]["groups"][0]
                group.update(status="retained", retention_basis=basis, reason="policy protection",
                             exit_condition="protection expires after review", next_action="review protection")
                self.assertEqual(MODULE.validate_record(record), [])
                for field in ("reason", "exit_condition", "next_action", "retention_basis"):
                    with self.subTest(missing=field):
                        malformed = copy.deepcopy(record)
                        malformed["resource_closeout"]["groups"][0].pop(field)
                        self.assertTrue(MODULE.validate_record(malformed))
        record["resource_closeout"]["groups"][0]["retention_basis"] = "held"
        self.assertTrue(MODULE.validate_record(record))

    def test_resource_unfinished_groups_require_recovery_fields(self) -> None:
        for status in ("pending", "planned", "disabled", "blocked", "failed", "unknown"):
            record = self.resource_record()
            record["release"]["status"] = "released"
            block = record["resource_closeout"]
            block["status"] = "partial"
            block["groups"][0].update(status=status, reason="awaiting assessment", next_action="inspect inventory")
            self.assertEqual(MODULE.validate_record(record), [])
            for field in ("reason", "next_action", "owner"):
                with self.subTest(status=status, field=field):
                    malformed = copy.deepcopy(record)
                    malformed["resource_closeout"]["groups"][0].pop(field)
                    self.assertTrue(MODULE.validate_record(malformed))

    def test_resource_not_applicable_requires_full_reasoned_coverage(self) -> None:
        record = self.resource_record()
        block = record["resource_closeout"]
        block["status"] = "not_applicable"
        for group in block["groups"]:
            group.update(status="not_applicable", reason="this surface is not produced")
            group.pop("retention_ref")
        self.assertEqual(MODULE.validate_record(record), [])
        for case in ("missing_reason", "missing_evidence", "missing_group", "non_na_group"):
            with self.subTest(case=case):
                malformed = copy.deepcopy(record)
                broken = malformed["resource_closeout"]
                if case == "missing_reason":
                    broken["groups"][0].pop("reason")
                elif case == "missing_evidence":
                    broken["groups"][0]["evidence_refs"] = []
                elif case == "missing_group":
                    broken["groups"].pop()
                else:
                    broken["groups"][0].update(status="completed", retention_ref="policy:images")
                self.assertTrue(MODULE.validate_record(malformed))

    def test_resource_malformed_values_are_diagnostic(self) -> None:
        malformed_blocks = [None, [], "invalid", {"status": []}, {"groups": [None]}]
        for block in malformed_blocks:
            with self.subTest(block=block):
                record = self.resource_record()
                record["resource_closeout"] = block
                self.assertTrue(MODULE.validate_record(record))
        for field in ("id", "status", "retention_basis", "evidence_refs"):
            with self.subTest(field=field):
                record = self.resource_record()
                record["resource_closeout"]["groups"][0][field] = {"unexpected": "object"}
                self.assertTrue(MODULE.validate_record(record))

    def test_source_only_legacy_requires_resource_block_only_when_requested(self) -> None:
        record = self.valid_closed_record()
        self.assertEqual(MODULE.validate_record(record), [])
        errors = MODULE.validate_record(record, require_resource_closeout=True)
        self.assertTrue(any("resource_closeout is required" in error for error in errors), errors)
        self.assertEqual(MODULE.validate_record(self.resource_record(), require_resource_closeout=True), [])

    def test_resource_requirement_cli_and_json_keep_declarations_read_only(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            record_path = Path(temp) / "release.json"
            for record, required, expected in (
                (self.valid_closed_record(), False, 0),
                (self.valid_closed_record(), True, 1),
                (self.resource_record(), True, 0),
            ):
                with self.subTest(required=required, expected=expected):
                    before = json.dumps(record).encode()
                    record_path.write_bytes(before)
                    args = [sys.executable, str(SCRIPT), str(record_path), "--json"]
                    if required:
                        args.append("--require-resource-closeout")
                    result = subprocess.run(args, capture_output=True, text=True, check=False)
                    self.assertEqual(result.returncode, expected, result.stderr)
                    self.assertNotIn("Traceback", result.stderr)
                    report = json.loads(result.stdout)
                    self.assertFalse(report["git_state_checked"])
                    self.assertIn("Resource closeout declarations", report["limits"])
                    self.assertEqual(record_path.read_bytes(), before)


class LiveReleaseControlReviewTests(unittest.TestCase):
    def setUp(self) -> None:
        # Reuse the real-Git fixture without inheriting or rerunning its test cases.
        spec = importlib.util.spec_from_file_location(
            "buildos_closeout_fixture", Path(__file__).with_name("test_change_unit_management.py"))
        assert spec and spec.loader
        fixture_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(fixture_module)
        self.fixture = fixture_module.FeedbackLifecycleTests()
        self.addCleanup(self.fixture.doCleanups)
        self.fixture.setUp()
        self.git_run = fixture_module.run
        self.unit = self.fixture.integrated_unit()
        self.data = self.fixture.release_record(self.unit)
        self.record_path = Path(self.unit["record"])
        self.original = json.loads(self.record_path.read_text(encoding="utf-8"))
        result, report = self.fixture.check_release(self.data)
        self.assertEqual(result.returncode, 0, report)

    def save_record(self, record: dict) -> bytes:
        self.record_path.write_text(json.dumps(record), encoding="utf-8")
        return self.record_path.read_bytes()

    def test_stored_receiving_target_cannot_be_rebound_by_top_level_record(self) -> None:
        self.git_run("git", "branch", "alternate", cwd=self.fixture.repo)
        record = copy.deepcopy(self.original)
        record["integration_target"] = "refs/heads/alternate"
        before = self.save_record(record)
        self.data["release"]["target_line"] = "alternate"
        result, report = self.fixture.check_release(self.data)
        self.assertNotEqual(result.returncode, 0, report)
        self.assertTrue(any("proof receiving target" in error for error in report["errors"]), report)
        self.assertEqual(self.record_path.read_bytes(), before)

    def test_equivalent_and_legacy_proof_targets_remain_read_only(self) -> None:
        for target in ("main", "refs/heads/main", None):
            with self.subTest(target=target):
                record = copy.deepcopy(self.original)
                if target is None:
                    record["integration_proof"].pop("receiving_target")
                else:
                    record["integration_proof"]["receiving_target"] = target
                before = self.save_record(record)
                result, report = self.fixture.check_release(self.data)
                self.assertEqual(result.returncode, 0, report)
                self.assertEqual(self.record_path.read_bytes(), before)
        for target in (None, "", 7):
            with self.subTest(invalid_present_target=target):
                record = copy.deepcopy(self.original)
                record["integration_proof"]["receiving_target"] = target
                before = self.save_record(record)
                result, report = self.fixture.check_release(self.data)
                self.assertNotEqual(result.returncode, 0, report)
                self.assertTrue(any("proof receiving target" in error for error in report["errors"]), report)
                self.assertEqual(self.record_path.read_bytes(), before)

    def test_retained_worktree_reports_actual_moved_path_and_rejects_stale_path(self) -> None:
        moved = self.fixture.root / "moved worktree"
        self.git_run("git", "worktree", "move", self.unit["worktree"], str(moved), cwd=self.fixture.repo)
        before = self.record_path.read_bytes()
        result, report = self.fixture.check_release(self.data)
        self.assertNotEqual(result.returncode, 0, report)
        facts = report["units"][0]
        self.assertIn("worktree_registration_mismatch", facts["identity_issues"])
        self.assertEqual(facts["worktree_registrations"], [
            {"path": str(moved), "branch": "refs/heads/" + self.unit["branch"]}])
        self.assertTrue(facts["physical"]["worktree_registered"])
        self.assertFalse(facts["physical"]["worktree_path_present"])
        self.assertEqual(self.record_path.read_bytes(), before)
        self.assertTrue(moved.is_dir())

    def test_retained_registered_path_does_not_hide_a_different_checkout(self) -> None:
        self.git_run("git", "switch", "--detach", cwd=Path(self.unit["worktree"]))
        result, report = self.fixture.check_release(self.data)
        self.assertNotEqual(result.returncode, 0, report)
        facts = report["units"][0]
        self.assertIn("worktree_registration_mismatch", facts["identity_issues"])
        self.assertEqual(facts["worktree_registrations"], [
            {"path": self.unit["worktree"], "branch": None}])

    def test_missing_original_target_is_diagnostic_with_or_without_final_target(self) -> None:
        for keep_final_target in (True, False):
            with self.subTest(keep_final_target=keep_final_target):
                record = copy.deepcopy(self.original)
                record.pop("target")
                if not keep_final_target:
                    record.pop("integration_target")
                before = self.save_record(record)
                inspected = self.fixture.good("inspect_git_workspace.py", "--repo", self.fixture.repo,
                                              "--unit", self.unit["unit"], "--intent", "read")
                self.assertIn("target_identity_missing", inspected["change_unit"]["identity_issues"])
                result, report = self.fixture.check_release(self.data)
                self.assertNotEqual(result.returncode, 0, report)
                self.assertNotIn("Traceback", result.stderr)
                self.assertTrue(any("target_identity_missing" in error for error in report["errors"]), report)
                self.assertEqual(self.record_path.read_bytes(), before)


    def test_included_units_cannot_skip_live_closeout_as_not_applicable(self) -> None:
        gate = next(item for item in self.data["gates"] if item["id"] == "git_execution_closed")
        gate.update(status="not_applicable", reason="synthetic attempted bypass")
        self.data["change_units"][0]["integration_commit"] = self.unit["baseline"]
        self.data["cleanup"] = []
        result, report = self.fixture.check_release(self.data)
        self.assertNotEqual(result.returncode, 0, report)
        self.assertTrue(any("cannot be not_applicable" in error for error in report["errors"]), report)
        # A release with no included code units may still have a genuine N/A closeout.
        self.data["change_units"] = []
        result, report = self.fixture.check_release(self.data)
        self.assertEqual(result.returncode, 0, report)

    def test_json_mode_keeps_read_and_parse_errors_machine_readable(self) -> None:
        missing = self.fixture.root / "missing.json"
        directory = self.fixture.root / "directory"
        directory.mkdir()
        malformed = self.fixture.root / "malformed.json"
        malformed.write_text("{broken", encoding="utf-8")
        invalid_utf8 = self.fixture.root / "invalid-utf8.json"
        invalid_utf8.write_bytes(b"\xff")
        for source in (missing, directory, malformed, invalid_utf8):
            with self.subTest(source=source.name):
                result = self.fixture.cli("validate_release_control.py", source,
                                          "--repo", self.fixture.repo, "--json")
                self.assertNotEqual(result.returncode, 0)
                self.assertNotIn("Traceback", result.stderr)
                report = json.loads(result.stdout)
                self.assertEqual(report["kind"], "release_control_check")
                self.assertFalse(report["structure_valid"])
                self.assertFalse(report["git_state_checked"])
                self.assertEqual(report["units"], [])
                self.assertTrue(report["errors"])


if __name__ == "__main__":
    unittest.main()
