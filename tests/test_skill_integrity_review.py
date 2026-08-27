import tempfile
import unittest
from pathlib import Path

from scripts.validate_skill_integrity_review import surface_sha256, validate_record


class SkillIntegrityReviewTests(unittest.TestCase):
    def make_root(self) -> tuple[tempfile.TemporaryDirectory[str], Path, dict[str, object]]:
        temporary = tempfile.TemporaryDirectory()
        root = Path(temporary.name)
        (root / "skills/example").mkdir(parents=True)
        (root / "evidence/reviews/REV-test").mkdir(parents=True)
        (root / "skills/example/SKILL.md").write_text("---\nname: example\n---\n", encoding="utf-8")
        report = root / "evidence/reviews/REV-test/ASSURANCE_REVIEW.md"
        report.write_text("# Review\n\nREV-test\n", encoding="utf-8")
        record: dict[str, object] = {
            "schema_version": 1,
            "review_id": "REV-test",
            "reviewed_at": "2026-08-27",
            "review_identity": "evidence_based_self_review",
            "verdict": "supported",
            "surface_sha256": surface_sha256(root),
            "report": "evidence/reviews/REV-test/ASSURANCE_REVIEW.md",
            "findings": [],
            "conditions": [],
            "unassessed": [],
        }
        return temporary, root, record

    def test_accepts_current_releasable_review(self) -> None:
        temporary, root, record = self.make_root()
        self.addCleanup(temporary.cleanup)
        validate_record(record, require_current=True, release=True, root=root)

    def test_rejects_stale_surface(self) -> None:
        temporary, root, record = self.make_root()
        self.addCleanup(temporary.cleanup)
        (root / "skills/example/SKILL.md").write_text("changed\n", encoding="utf-8")
        with self.assertRaisesRegex(SystemExit, "stale"):
            validate_record(record, require_current=True, release=False, root=root)

    def test_release_rejects_unresolved_conditions(self) -> None:
        temporary, root, record = self.make_root()
        self.addCleanup(temporary.cleanup)
        record["conditions"] = ["run forward test"]
        with self.assertRaisesRegex(SystemExit, "unresolved release conditions"):
            validate_record(record, require_current=True, release=True, root=root)

    def test_release_rejects_open_blocking_finding(self) -> None:
        temporary, root, record = self.make_root()
        self.addCleanup(temporary.cleanup)
        record["findings"] = [{"id": "FND-1", "severity": "P1", "status": "confirmed"}]
        with self.assertRaisesRegex(SystemExit, "blocking Skill integrity finding"):
            validate_record(record, require_current=True, release=True, root=root)

    def test_schema_rejects_unknown_identity(self) -> None:
        temporary, root, record = self.make_root()
        self.addCleanup(temporary.cleanup)
        record["review_identity"] = "independent-ish"
        with self.assertRaisesRegex(SystemExit, "identity"):
            validate_record(record, require_current=False, release=False, root=root)


if __name__ == "__main__":
    unittest.main()
