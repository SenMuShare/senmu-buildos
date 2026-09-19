"""Regression tests for truthful governance progress and resource disposition."""
import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "skills/senmu-build-project/scripts/validate_mature_project_governance.py"
spec = importlib.util.spec_from_file_location("governance_progress_validator", SOURCE)
assert spec is not None and spec.loader is not None
validator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validator)


def make_record(completed=False):
    done = "completed" if completed else "active"
    return {
        "schema_version": 1, "governance_id": "GOV-0042", "status": done,
        "authoritative_task_owner": {"kind": "existing", "locator": "issues/42", "task_id": "TASK-42"},
        "baseline": {"status": "frozen", "captured_at": "2026-09-17T00:00:00Z",
                     "target_identity": "repo@fixture", "release_units": ["app"], "evidence_refs": ["baseline"]},
        "implementation_authorization": {"status": "approved", "approved_by": "owner",
                                         "approved_at": "2026-09-17T00:00:00Z", "scope": ["FND-0042"]},
        "coverage": {"status": "assessed", "evidence_refs": ["audit"], "unassessed": []},
        "stages": [{"id": "repair", "status": done, "evidence_refs": []}],
        "findings": [{
            "id": "FND-0042", "severity": "P1",
            "status": "verified_resolved" if completed else "confirmed", "owner": "engineering",
            "evidence_refs": ["audit#finding"],
            "decision": {"status": "remediate", "approved_by": "owner", "approved_at": "2026-09-17T00:00:00Z"},
            "remediation": {"task_id": "TASK-43", "change_refs": ["commit:fixture"] if completed else []},
            "verification": {"status": "passed" if completed else "pending",
                             "evidence_refs": ["review#finding"] if completed else []},
        }],
        "remediation_waves": [{"id": "WAVE-01", "status": done, "finding_ids": ["FND-0042"]}],
        "final_review": {"status": "passed" if completed else "pending", "review_identity": "peer",
                         "reviewed_at": "2026-09-17T00:00:00Z", "frozen_target": "repo@fixture",
                         "evidence_refs": ["review"] if completed else []},
        "recovery": {"status": "verified", "evidence_refs": ["recovery"]},
        "cleanup": {"status": "archive", "location": "archive/task-42", "approved_by": "owner",
                    "approved_at": "2026-09-17T00:00:00Z", "evidence_refs": ["cleanup-decision"]},
    }


class GovernanceProgressAndRetentionTests(unittest.TestCase):
    def assert_valid(self, record):
        self.assertEqual(validator.validate_record(record), [])

    def assert_invalid(self, record, message):
        errors = validator.validate_record(record)
        self.assertTrue(any(message in error for error in errors), errors)

    def test_authorized_pending_remediation_is_valid(self):
        self.assert_valid(make_record())

    def test_partial_failed_remediation_is_valid(self):
        record = make_record()
        finding = record["findings"][0]
        finding["remediation"]["change_refs"] = ["commit:partial"]
        finding["verification"] = {"status": "failed", "evidence_refs": ["failure-log"]}
        self.assert_valid(record)

    def test_verified_resolution_needs_changes_and_pass(self):
        for missing in ("changes", "pass", "evidence"):
            with self.subTest(missing=missing):
                record = make_record(True)
                record["status"] = "active"
                finding = record["findings"][0]
                if missing == "changes":
                    finding["remediation"]["change_refs"] = []
                    message = "has no change_refs"
                elif missing == "pass":
                    finding["verification"]["status"] = "pending"
                    message = "has not passed verification"
                else:
                    finding["verification"]["evidence_refs"] = []
                    message = "verification has no evidence_refs"
                self.assert_invalid(record, message)

    def test_any_passed_claim_requires_evidence(self):
        record = make_record()
        record["findings"][0]["verification"]["status"] = "passed"
        self.assert_invalid(record, "verification has no evidence_refs")

    def test_complete_cannot_hide_pending_remediation(self):
        record = make_record(True)
        finding = record["findings"][0]
        finding["status"] = "confirmed"
        finding["verification"]["status"] = "pending"
        self.assert_invalid(record, "not verified_resolved")

    def test_existing_complete_record_remains_valid(self):
        self.assert_valid(make_record(True))

    def test_unauthorized_remediation_is_rejected(self):
        record = make_record()
        record["implementation_authorization"]["status"] = "pending"
        self.assert_invalid(record, "without approved implementation authorization")

    def test_empty_authorization_scope_is_rejected(self):
        record = make_record()
        record["implementation_authorization"]["scope"] = []
        self.assert_invalid(record, "nonempty implementation authorization scope")

    def test_pending_decision_does_not_hide_actual_changes(self):
        record = make_record()
        record["findings"][0]["decision"] = {"status": "pending"}
        record["findings"][0]["remediation"]["change_refs"] = ["commit:unapproved"]
        record["implementation_authorization"]["status"] = "pending"
        self.assert_invalid(record, "without approved implementation authorization")

    def test_pending_candidate_without_changes_is_valid(self):
        record = make_record()
        record["findings"][0]["decision"] = {"status": "pending"}
        record["implementation_authorization"]["status"] = "pending"
        self.assert_valid(record)

    def test_final_claim_cannot_use_an_unrelated_decision(self):
        record = make_record(True)
        record["status"] = "active"
        record["findings"][0]["decision"]["status"] = "accept_risk"
        self.assert_invalid(record, "resolved status requires a remediate decision")

    def test_policy_retention_does_not_need_invented_approval(self):
        record = make_record(True)
        record["cleanup"] = {"status": "retain", "location": "work/task-42",
                             "evidence_refs": ["policy#retention"], "reason": "Needed for approved recovery",
                             "revisit_condition": "After the documented recovery window"}
        self.assert_valid(record)

    def test_policy_retention_needs_complete_basis(self):
        for key in ("location", "evidence_refs", "reason", "revisit_condition"):
            with self.subTest(key=key):
                record = make_record(True)
                record["cleanup"] = {"status": "retain", "location": "work/task-42",
                                     "evidence_refs": ["policy#retention"], "reason": "Recovery",
                                     "revisit_condition": "Recovery closed"}
                del record["cleanup"][key]
                self.assert_invalid(record, "retain requires")

    def test_legacy_approved_retention_remains_valid(self):
        record = make_record(True)
        record["cleanup"]["status"] = "retain"
        self.assert_valid(record)

    def test_archive_and_delete_still_need_approval(self):
        for action in ("archive", "delete_authorized"):
            with self.subTest(action=action):
                record = make_record(True)
                record["cleanup"]["status"] = action
                record["cleanup"]["approved_by"] = None
                self.assert_invalid(record, "terminal cleanup decision lacks approver or time")

    def test_no_resources_can_be_not_applicable(self):
        record = make_record(True)
        record["cleanup"] = {"status": "not_applicable", "location": None,
                             "reason": "This task created no temporary materials requiring disposition", "evidence_refs": []}
        self.assert_valid(record)
        record["cleanup"]["location"] = "work/existing-material"
        self.assert_invalid(record, "must not identify a resource location")
        record["cleanup"]["location"] = None
        record["cleanup"]["reason"] = ""
        self.assert_invalid(record, "requires a reason")

    def test_cleanup_pending_cannot_be_completed(self):
        record = make_record(True)
        record["cleanup"]["status"] = "pending_user_decision"
        self.assert_invalid(record, "cannot leave cleanup pending user decision")

    def test_critical_deferral_remains_rejected(self):
        record = make_record(True)
        record["findings"][0]["decision"]["status"] = "defer"
        record["findings"][0]["status"] = "accepted_risk"
        self.assert_invalid(record, "blocking finding cannot be deferred")


if __name__ == "__main__":
    unittest.main()
