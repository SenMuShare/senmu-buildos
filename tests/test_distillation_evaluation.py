import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
VALIDATOR = ROOT / "scripts" / "validate_distillation_evaluation.py"


def valid_receipt() -> dict:
    cases = []
    for index, (role, verdict) in enumerate(
        (("target", "improved"), ("non_trigger", "unchanged"),
         ("exception", "improved"), ("adversarial", "improved")),
        start=1,
    ):
        cases.append(
            {
                "case_id": f"E-{index:03d}",
                "roles": [role],
                "prompt": f"realistic prompt for {role}",
                "success_criteria": "Makes the intended decision without expanding authority.",
                "baseline_observation": "The baseline missed or preserved the relevant behavior.",
                "candidate_observation": "The candidate made the expected observable decision.",
                "verdict": verdict,
                "evidence": f"outputs/{role}.json",
            }
        )
    return {
        "schema_version": 1,
        "evaluation_id": "KDE-20260831-001",
        "scope": "Distilled rule changes Skill behavior",
        "candidate_ids": ["C-001"],
        "baseline": {
            "identity": "main@abc123",
            "skill_surface": "sha256:baseline",
            "isolation_probe": "No candidate rule was loaded.",
        },
        "candidate": {
            "identity": "task@def456",
            "skill_surface": "sha256:candidate",
            "isolation_probe": "Candidate rule was loaded only in this group.",
        },
        "environment": {
            "model": "model-snapshot-2026-08-31",
            "reasoning": "medium",
            "harness": "codex-desktop-2026-08-31",
            "tools": "filesystem and shell, no network writes",
            "budget": "one run per case, bounded task context",
            "repeat_count": 1,
        },
        "cases": cases,
        "conclusion": {
            "status": "accept",
            "review_identity": "evidence_based_self_review",
            "rationale": "Target behavior improved without non-trigger regressions.",
        },
    }


class DistillationEvaluationTests(unittest.TestCase):
    def run_validator(self, receipt: dict) -> subprocess.CompletedProcess[str]:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "receipt.json"
            path.write_text(json.dumps(receipt, ensure_ascii=False), encoding="utf-8")
            return subprocess.run(
                [sys.executable, str(VALIDATOR), str(path)],
                cwd=ROOT,
                check=False,
                capture_output=True,
                text=True,
            )

    def test_valid_accept_receipt_passes(self) -> None:
        result = self.run_validator(valid_receipt())
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn("conclusion=accept", result.stdout)
        self.assertIn("repeat_count=1", result.stdout)

    def test_missing_non_trigger_role_fails(self) -> None:
        receipt = valid_receipt()
        receipt["cases"] = [
            case for case in receipt["cases"] if "non_trigger" not in case["roles"]
        ]
        result = self.run_validator(receipt)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("non_trigger", result.stderr)

    def test_same_skill_surface_fails(self) -> None:
        receipt = valid_receipt()
        receipt["candidate"]["skill_surface"] = receipt["baseline"]["skill_surface"]
        result = self.run_validator(receipt)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("skill_surface", result.stderr)

    def test_accept_with_regression_fails(self) -> None:
        receipt = valid_receipt()
        receipt["cases"][1]["verdict"] = "regressed"
        result = self.run_validator(receipt)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("accept cannot contain", result.stderr)

    def test_accept_without_improvement_fails(self) -> None:
        receipt = valid_receipt()
        for case in receipt["cases"]:
            case["verdict"] = "unchanged"
        result = self.run_validator(receipt)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("at least one improved", result.stderr)

    def test_invalidated_case_requires_invalidated_conclusion(self) -> None:
        receipt = valid_receipt()
        receipt["cases"][0]["verdict"] = "invalidated"
        result = self.run_validator(receipt)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("conclusion.status=invalidated", result.stderr)


if __name__ == "__main__":
    unittest.main()
