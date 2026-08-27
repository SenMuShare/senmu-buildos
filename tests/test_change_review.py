import json
import subprocess
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
VALIDATOR = ROOT / "skills/senmu-build-delivery/scripts/validate_change_review.py"
TEMPLATE = ROOT / "skills/senmu-build-delivery/assets/delivery-governance/CHANGE_REVIEW_CONTROL.template.json"
FP = "sha256:" + "a" * 64


def approved_record() -> dict:
    return {
        "schema_version": 1,
        "review_id": "CR-0042",
        "status": "approved",
        "change": {
            "repository": "example",
            "integration_target": "main",
            "source_branch": "feature/example",
            "base_commit": "a" * 40,
            "head_commit": "b" * 40,
            "change_kind": "code",
            "governance_level": "G2",
        },
        "inventory": {
            "method": {
                "kind": "language_aware",
                "tools": ["python ast", "git diff"],
                "limitations": [],
            },
            "files": [
                {
                    "id": "FILE-0001",
                    "path": "app.py",
                    "classification": "first_party_source",
                    "change_type": "modified",
                    "scope_status": "included",
                    "exclusion_reason": None,
                    "review_status": "reviewed_pass",
                    "changed_line_ranges": [{"start": 1, "end": 3}],
                    "evidence_refs": ["review.md#file-0001"],
                    "changed_units": {
                        "status": "complete",
                        "empty_reason": None,
                        "items": [
                            {
                                "id": "UNIT-0001",
                                "kind": "function",
                                "qualified_name": "app.run",
                                "line_start": 1,
                                "line_end": 3,
                                "fingerprint": FP,
                                "review_status": "reviewed_pass",
                                "evidence_refs": ["review.md#unit-0001"],
                                "finding_ids": [],
                                "checks": {
                                    "responsibility": "pass",
                                    "abstraction": "pass",
                                    "inputs_outputs": "pass",
                                    "side_effects": "pass",
                                    "errors_resources": "pass",
                                    "dependencies_architecture": "pass",
                                    "duplication_economy": "pass",
                                    "tests": "pass",
                                    "comments_docs": "pass",
                                },
                            }
                        ],
                    },
                    "changed_comments": {
                        "status": "complete",
                        "empty_reason": "No changed comments or docstrings.",
                        "items": [],
                    },
                }
            ],
        },
        "findings": [],
        "quality_checks": [
            {
                "id": "QC-TEST",
                "status": "passed",
                "evidence_refs": ["tests:passed"],
                "not_applicable_reason": None,
            }
        ],
        "approval": {
            "author": "implementation-agent",
            "reviewer": "review-agent",
            "review_identity": "peer",
            "reviewed_head": "b" * 40,
            "outcome": "approved",
            "reviewed_at": "2026-08-27T12:00:00Z",
            "exception": None,
        },
    }


class ChangeReviewValidatorTests(unittest.TestCase):
    def validate(self, record: dict, *extra: str) -> subprocess.CompletedProcess[str]:
        with tempfile.TemporaryDirectory() as temporary_root:
            record_path = Path(temporary_root) / "review.json"
            record_path.write_text(json.dumps(record, ensure_ascii=False), encoding="utf-8")
            return subprocess.run(
                ["python3", str(VALIDATOR), "--record", str(record_path), *extra],
                check=False,
                capture_output=True,
                text=True,
            )

    def make_repo(self) -> tuple[tempfile.TemporaryDirectory[str], Path, str, str]:
        temporary = tempfile.TemporaryDirectory()
        repo = Path(temporary.name)
        subprocess.run(["git", "init", "-b", "main", str(repo)], check=True, capture_output=True)
        subprocess.run(["git", "-C", str(repo), "config", "user.name", "Test"], check=True)
        subprocess.run(["git", "-C", str(repo), "config", "user.email", "test@example.com"], check=True)
        (repo / "app.py").write_text("def run():\n    return 1\n", encoding="utf-8")
        subprocess.run(["git", "-C", str(repo), "add", "app.py"], check=True)
        subprocess.run(["git", "-C", str(repo), "commit", "-m", "base"], check=True, capture_output=True)
        base = subprocess.check_output(["git", "-C", str(repo), "rev-parse", "HEAD"], text=True).strip()
        (repo / "app.py").write_text("def run():\n    return 2\n", encoding="utf-8")
        subprocess.run(["git", "-C", str(repo), "commit", "-am", "change"], check=True, capture_output=True)
        head = subprocess.check_output(["git", "-C", str(repo), "rev-parse", "HEAD"], text=True).strip()
        return temporary, repo, base, head

    def test_draft_template_is_valid(self) -> None:
        result = self.validate(json.loads(TEMPLATE.read_text(encoding="utf-8")))
        self.assertEqual(result.returncode, 0, result.stdout or result.stderr)

    def test_approved_change_review_passes(self) -> None:
        result = self.validate(approved_record())
        self.assertEqual(result.returncode, 0, result.stdout or result.stderr)
        self.assertIn("files=1, units=1, comments=0", result.stdout)

    def test_code_change_rejects_self_review(self) -> None:
        record = approved_record()
        record["approval"]["review_identity"] = "evidence_based_self_review"
        record["approval"]["reviewer"] = record["approval"]["author"]
        result = self.validate(record)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("requires peer or independent reviewer", result.stdout)

    def test_g4_code_change_requires_independent_review(self) -> None:
        record = approved_record()
        record["change"]["governance_level"] = "G4"
        result = self.validate(record)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("G4 code merge review requires independent identity", result.stdout)

    def test_reviewed_head_must_match_candidate(self) -> None:
        record = approved_record()
        record["approval"]["reviewed_head"] = "c" * 40
        result = self.validate(record)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("reviewed_head must match", result.stdout)

    def test_changed_unit_requires_all_review_dimensions(self) -> None:
        record = approved_record()
        del record["inventory"]["files"][0]["changed_units"]["items"][0]["checks"]["side_effects"]
        result = self.validate(record)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("checks mismatch", result.stdout)

    def test_failed_quality_check_blocks_approval(self) -> None:
        record = approved_record()
        record["quality_checks"][0]["status"] = "failed"
        result = self.validate(record)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("unfinished quality checks", result.stdout)

    def test_open_finding_blocks_approval(self) -> None:
        record = approved_record()
        file_entry = record["inventory"]["files"][0]
        unit = file_entry["changed_units"]["items"][0]
        file_entry["review_status"] = "reviewed_with_findings"
        unit["review_status"] = "reviewed_with_findings"
        unit["checks"]["responsibility"] = "finding"
        unit["finding_ids"] = ["FND-0001"]
        record["findings"] = [
            {
                "id": "FND-0001",
                "severity": "P2",
                "status": "confirmed",
                "location_ids": ["UNIT-0001"],
                "evidence_refs": ["review.md#fnd-0001"],
            }
        ]
        result = self.validate(record)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("approved review has open findings", result.stdout)

    def test_accepted_p1_cannot_pass_merge_gate(self) -> None:
        record = approved_record()
        file_entry = record["inventory"]["files"][0]
        unit = file_entry["changed_units"]["items"][0]
        file_entry["review_status"] = "reviewed_with_findings"
        unit["review_status"] = "reviewed_with_findings"
        unit["checks"]["responsibility"] = "finding"
        unit["finding_ids"] = ["FND-0001"]
        record["findings"] = [
            {
                "id": "FND-0001",
                "severity": "P1",
                "status": "accepted_risk",
                "location_ids": ["UNIT-0001"],
                "evidence_refs": ["review.md#fnd-0001"],
                "acceptance": {
                    "owner": "maintainer",
                    "accepted_at": "2026-08-27T13:00:00Z",
                    "condition": "temporary exception",
                },
            }
        ]
        record["approval"]["outcome"] = "approved_with_conditions"
        result = self.validate(record)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("cannot accept P0/P1 risk", result.stdout)

    def test_git_diff_and_current_head_can_be_verified(self) -> None:
        temporary, repo, base, head = self.make_repo()
        self.addCleanup(temporary.cleanup)
        record = approved_record()
        record["change"]["repository"] = str(repo)
        record["change"]["base_commit"] = base
        record["change"]["head_commit"] = head
        record["approval"]["reviewed_head"] = head
        result = self.validate(record, "--repo", str(repo), "--require-current-head")
        self.assertEqual(result.returncode, 0, result.stdout or result.stderr)

    def test_git_diff_rejects_uninventoried_file(self) -> None:
        temporary, repo, base, head = self.make_repo()
        self.addCleanup(temporary.cleanup)
        record = approved_record()
        record["change"]["repository"] = str(repo)
        record["change"]["base_commit"] = base
        record["change"]["head_commit"] = head
        record["approval"]["reviewed_head"] = head
        record["inventory"]["files"][0]["path"] = "other.py"
        result = self.validate(record, "--repo", str(repo))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("inventory paths do not match git diff", result.stdout)

    def test_new_commit_invalidates_previous_approval(self) -> None:
        temporary, repo, base, head = self.make_repo()
        self.addCleanup(temporary.cleanup)
        record = approved_record()
        record["change"]["repository"] = str(repo)
        record["change"]["base_commit"] = base
        record["change"]["head_commit"] = head
        record["approval"]["reviewed_head"] = head
        (repo / "README.md").write_text("new\n", encoding="utf-8")
        subprocess.run(["git", "-C", str(repo), "add", "README.md"], check=True)
        subprocess.run(["git", "-C", str(repo), "commit", "-m", "after review"], check=True, capture_output=True)
        result = self.validate(record, "--repo", str(repo), "--require-current-head")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("current HEAD does not match reviewed head", result.stdout)


if __name__ == "__main__":
    unittest.main()
