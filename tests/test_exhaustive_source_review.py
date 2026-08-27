import json
import subprocess
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
VALIDATOR = ROOT / "skills/senmu-build-assurance/scripts/validate_exhaustive_source_review.py"
TEMPLATE = ROOT / "skills/senmu-build-assurance/assets/review-governance/EXHAUSTIVE_SOURCE_REVIEW_CONTROL.template.json"
FP = "sha256:" + "a" * 64


def completed_record() -> dict:
    return {
        "schema_version": 1,
        "review_id": "REV-SOURCE-0042",
        "status": "verified_complete",
        "conclusion": "supported",
        "review_identity": "peer",
        "target": {
            "baseline_identity": "commit:abc123",
            "current_identity": "commit:def456",
            "captured_at": "2026-08-27T12:00:00Z",
        },
        "scope": {
            "release_units": ["api"],
            "systems": ["billing"],
            "included_roots": ["src"],
            "exclusions": [],
        },
        "inventory": {
            "method": {
                "kind": "language_aware",
                "tools": ["python ast"],
                "limitations": [],
            },
            "files": [
                {
                    "id": "SRC-0001",
                    "path": "src/billing.py",
                    "release_unit": "api",
                    "system": "billing",
                    "module": "payments",
                    "classification": "first_party_source",
                    "scope_status": "included",
                    "exclusion_reason": None,
                    "inventory_status": "complete",
                    "review_status": "reviewed_with_findings",
                    "evidence_refs": ["review.md#src-0001"],
                    "symbol_scan": {
                        "status": "complete",
                        "empty_reason": None,
                        "units": [
                            {
                                "id": "UNIT-0001",
                                "kind": "function",
                                "qualified_name": "billing.charge",
                                "line_start": 10,
                                "line_end": 30,
                                "fingerprint": FP,
                                "status": "reviewed_with_findings",
                                "evidence_refs": ["review.md#unit-0001"],
                                "finding_ids": ["FND-0001"],
                                "checks": {
                                    "responsibility": "pass",
                                    "abstraction": "pass",
                                    "inputs_outputs": "pass",
                                    "side_effects": "pass",
                                    "errors_resources": "finding",
                                    "dependencies_architecture": "pass",
                                    "duplication_economy": "pass",
                                    "tests": "pass",
                                    "comments_docs": "pass",
                                },
                            }
                        ],
                    },
                    "comment_scan": {
                        "status": "complete",
                        "empty_reason": None,
                        "comments": [
                            {
                                "id": "COMMENT-0001",
                                "kind": "docstring",
                                "qualified_name": "billing.charge.__doc__",
                                "line_start": 11,
                                "line_end": 12,
                                "fingerprint": FP,
                                "status": "reviewed_pass",
                                "evidence_refs": ["review.md#comment-0001"],
                                "finding_ids": [],
                                "checks": {
                                    "accuracy": "pass",
                                    "necessity": "pass",
                                    "currency": "pass",
                                    "safety": "pass",
                                },
                            }
                        ],
                    },
                }
            ],
        },
        "findings": [
            {
                "id": "FND-0001",
                "severity": "P2",
                "status": "verified_resolved",
                "location_ids": ["UNIT-0001"],
                "evidence_refs": ["review.md#fnd-0001"],
                "verification_refs": ["recheck.md#fnd-0001"],
            }
        ],
        "verification": {
            "status": "passed",
            "frozen_target": "commit:def456",
            "evidence_refs": ["recheck.md", "tests:passed"],
        },
    }


class ExhaustiveSourceReviewValidatorTests(unittest.TestCase):
    def validate(self, record: dict) -> subprocess.CompletedProcess[str]:
        with tempfile.TemporaryDirectory() as temporary_root:
            record_path = Path(temporary_root) / "review.json"
            record_path.write_text(json.dumps(record, ensure_ascii=False), encoding="utf-8")
            return subprocess.run(
                ["python3", str(VALIDATOR), "--record", str(record_path)],
                check=False,
                capture_output=True,
                text=True,
            )

    def test_active_template_is_valid(self) -> None:
        result = self.validate(json.loads(TEMPLATE.read_text(encoding="utf-8")))
        self.assertEqual(result.returncode, 0, result.stdout or result.stderr)

    def test_verified_complete_record_passes(self) -> None:
        result = self.validate(completed_record())
        self.assertEqual(result.returncode, 0, result.stdout or result.stderr)
        self.assertIn("files=1, units=1, comments=1", result.stdout)

    def test_complete_review_rejects_unfinished_function(self) -> None:
        record = completed_record()
        record["inventory"]["files"][0]["symbol_scan"]["status"] = "blocked"
        result = self.validate(record)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("symbol_scan must be complete", result.stdout)

    def test_complete_review_rejects_unfinished_comment_inventory(self) -> None:
        record = completed_record()
        record["inventory"]["files"][0]["comment_scan"]["status"] = "pending"
        result = self.validate(record)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("comment_scan must be complete", result.stdout)

    def test_function_requires_every_review_dimension(self) -> None:
        record = completed_record()
        del record["inventory"]["files"][0]["symbol_scan"]["units"][0]["checks"]["side_effects"]
        result = self.validate(record)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("checks mismatch", result.stdout)

    def test_findings_and_units_must_cross_reference(self) -> None:
        record = completed_record()
        record["findings"][0]["location_ids"] = ["SRC-0001"]
        result = self.validate(record)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("do not reference each other", result.stdout)

    def test_unit_and_findings_must_reverse_cross_reference(self) -> None:
        record = completed_record()
        record["inventory"]["files"][0]["symbol_scan"]["units"][0]["finding_ids"] = []
        record["inventory"]["files"][0]["symbol_scan"]["units"][0]["status"] = "reviewed_pass"
        record["inventory"]["files"][0]["symbol_scan"]["units"][0]["checks"]["errors_resources"] = "pass"
        result = self.validate(record)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("do not reference each other", result.stdout)

    def test_file_review_status_must_match_findings(self) -> None:
        record = completed_record()
        record["inventory"]["files"][0]["review_status"] = "reviewed_pass"
        result = self.validate(record)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("reviewed_pass cannot reference findings", result.stdout)

    def test_scope_exclusions_must_be_a_list(self) -> None:
        record = completed_record()
        record["scope"]["exclusions"] = "vendor"
        result = self.validate(record)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("scope.exclusions must be a list", result.stdout)

    def test_supported_cannot_hide_accepted_risk(self) -> None:
        record = completed_record()
        finding = record["findings"][0]
        finding["status"] = "accepted_risk"
        finding["acceptance"] = {
            "owner": "maintainer",
            "accepted_at": "2026-08-27T13:00:00Z",
            "condition": "replace before next release",
        }
        result = self.validate(record)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("supported conclusion cannot contain accepted_risk", result.stdout)

    def test_supported_with_conditions_requires_real_accepted_risk(self) -> None:
        record = deepcopy(completed_record())
        record["conclusion"] = "supported_with_conditions"
        result = self.validate(record)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("requires an accepted_risk finding", result.stdout)


if __name__ == "__main__":
    unittest.main()
