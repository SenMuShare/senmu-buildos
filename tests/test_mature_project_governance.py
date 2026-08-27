import json
import subprocess
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
VALIDATOR = ROOT / "skills/senmu-build-project/scripts/validate_mature_project_governance.py"
TEMPLATE = ROOT / "skills/senmu-build-project/assets/mature-project-governance/GOVERNANCE_CONTROL.template.json"


def completed_record() -> dict:
    return {
        "schema_version": 1,
        "governance_id": "GOV-0042",
        "status": "completed",
        "authoritative_task_owner": {
            "kind": "project_existing_owner",
            "locator": "issues/42",
            "task_id": "TASK-42",
        },
        "baseline": {
            "status": "frozen",
            "captured_at": "2026-08-27T12:00:00Z",
            "target_identity": "repo@example-commit",
            "release_units": ["web"],
            "evidence_refs": ["evidence/baseline.json"],
        },
        "implementation_authorization": {
            "status": "approved",
            "approved_by": "project-owner",
            "approved_at": "2026-08-27T13:00:00Z",
            "scope": ["FND-0042"],
        },
        "coverage": {
            "status": "assessed",
            "evidence_refs": ["reviews/audit.md#coverage"],
            "unassessed": ["third-party billing environment"],
        },
        "stages": [
            {"id": "baseline", "status": "completed", "evidence_refs": ["evidence/baseline.json"]},
            {"id": "audit", "status": "completed", "evidence_refs": ["reviews/audit.md"]},
            {"id": "decision", "status": "completed", "evidence_refs": ["issues/42"]},
            {"id": "remediation", "status": "completed", "evidence_refs": ["commit:abc123"]},
            {"id": "final_review", "status": "completed", "evidence_refs": ["reviews/recheck.md"]},
        ],
        "findings": [
            {
                "id": "FND-0042",
                "severity": "P1",
                "status": "verified_resolved",
                "owner": "engineering",
                "evidence_refs": ["reviews/audit.md#fnd-0042"],
                "decision": {
                    "status": "remediate",
                    "approved_by": "project-owner",
                    "approved_at": "2026-08-27T13:00:00Z",
                },
                "remediation": {"task_id": "TASK-43", "change_refs": ["commit:abc123"]},
                "verification": {
                    "status": "passed",
                    "evidence_refs": ["reviews/recheck.md#fnd-0042"],
                },
            }
        ],
        "remediation_waves": [
            {"id": "WAVE-01", "status": "completed", "finding_ids": ["FND-0042"]}
        ],
        "final_review": {
            "status": "passed",
            "review_identity": "peer",
            "reviewed_at": "2026-08-27T14:00:00Z",
            "frozen_target": "repo@example-commit-after",
            "evidence_refs": ["reviews/recheck.md"],
        },
        "recovery": {
            "status": "verified",
            "evidence_refs": ["delivery/rollback-check.md"],
        },
        "cleanup": {
            "status": "archive",
            "location": "archive/governance-42",
            "approved_by": "project-owner",
            "approved_at": "2026-08-27T15:00:00Z",
            "evidence_refs": ["issues/42#cleanup"],
        },
    }


class MatureProjectGovernanceValidatorTests(unittest.TestCase):
    def validate(self, record: dict) -> subprocess.CompletedProcess[str]:
        with tempfile.TemporaryDirectory() as temporary_root:
            path = Path(temporary_root) / "record.json"
            path.write_text(json.dumps(record, ensure_ascii=False), encoding="utf-8")
            return subprocess.run(
                ["python3", str(VALIDATOR), "--record", str(path)],
                check=False,
                capture_output=True,
                text=True,
            )

    def test_active_template_allows_pending_user_decisions(self) -> None:
        record = json.loads(TEMPLATE.read_text(encoding="utf-8"))
        result = self.validate(record)
        self.assertEqual(result.returncode, 0, result.stdout or result.stderr)

    def test_completed_record_requires_full_trace_and_passes(self) -> None:
        result = self.validate(completed_record())
        self.assertEqual(result.returncode, 0, result.stdout or result.stderr)

    def test_completed_record_rejects_open_blocking_finding(self) -> None:
        record = completed_record()
        finding = record["findings"][0]
        finding["status"] = "confirmed"
        finding["decision"] = {"status": "pending", "approved_by": None, "approved_at": None}
        result = self.validate(record)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("has no user or owner decision", result.stdout)
        self.assertIn("is not closed or accepted", result.stdout)

    def test_completed_record_rejects_resolved_but_unreviewed_finding(self) -> None:
        record = completed_record()
        record["findings"][0]["status"] = "resolved_unverified"
        result = self.validate(record)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("is resolved but not re-reviewed", result.stdout)

    def test_remediation_requires_explicit_implementation_authorization(self) -> None:
        record = completed_record()
        record["implementation_authorization"] = {
            "status": "pending",
            "approved_by": None,
            "approved_at": None,
            "scope": [],
        }
        result = self.validate(record)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("remediation exists without approved implementation authorization", result.stdout)

    def test_completed_record_requires_cleanup_disposition(self) -> None:
        record = deepcopy(completed_record())
        record["cleanup"]["status"] = "pending_user_decision"
        result = self.validate(record)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("cannot leave cleanup pending user decision", result.stdout)

    def test_cleanup_disposition_requires_recorded_user_or_owner_decision(self) -> None:
        record = completed_record()
        record["cleanup"]["approved_by"] = None
        record["cleanup"]["approved_at"] = None
        result = self.validate(record)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("terminal cleanup decision lacks approver or time", result.stdout)

    def test_completed_record_discloses_coverage_and_review_identity(self) -> None:
        record = completed_record()
        record["coverage"] = {"status": "pending", "evidence_refs": [], "unassessed": []}
        record["final_review"]["review_identity"] = None
        result = self.validate(record)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("requires assessed coverage", result.stdout)
        self.assertIn("requires final_review.review_identity", result.stdout)

    def test_blocking_finding_cannot_be_deferred(self) -> None:
        record = completed_record()
        finding = record["findings"][0]
        finding["status"] = "accepted_risk"
        finding["decision"] = {
            "status": "defer",
            "approved_by": "project-owner",
            "approved_at": "2026-08-27T13:00:00Z",
        }
        result = self.validate(record)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("blocking finding cannot be deferred", result.stdout)


if __name__ == "__main__":
    unittest.main()
