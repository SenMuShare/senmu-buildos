import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from scripts.manage_github_product_surface import (
    ProductSurfaceError,
    sync_remote_surface,
    validate_local_surface,
)


def write_surface(root: Path, *, version: str = "2.1.1") -> dict[str, object]:
    (root / "VERSION").write_text(f"{version}\n", encoding="utf-8")
    for relative in ("README.md", "README.en.md", "README.ja.md"):
        (root / relative).write_text(f"<!-- product-surface-review: {version} -->\n", encoding="utf-8")
    surface = {
        "schema_version": 1,
        "repository": "SenMuShare/senmu-buildos",
        "reviewed_for_version": version,
        "description": "AI-native BuildOS for reliable software engineering and releases.",
        "topics": ["agent-skills", "ai-agents", "ai-coding", "claude-code", "code-quality", "codex", "product-management", "software-engineering"],
        "readme_review": {
            "updated_sections": ["positioning"],
            "summary": {
                "zh": "重新审阅并更新当前产品定位、主要能力、设计理念和使用边界。",
                "en": "Review and update the current product positioning and capability boundaries.",
                "ja": "現在の製品位置付け、主要能力、利用境界を見直して更新します。"
            },
        },
        "readmes": {"zh": "README.md", "en": "README.en.md", "ja": "README.ja.md"},
    }
    (root / "GITHUB_PRODUCT_SURFACE.json").write_text(json.dumps(surface), encoding="utf-8")
    return surface


class GitHubProductSurfaceTests(unittest.TestCase):
    def test_accepts_reviewed_trilingual_product_surface(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            surface = write_surface(root)
            self.assertEqual(validate_local_surface(root)["description"], surface["description"])

    def test_rejects_version_and_readme_review_drift(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            write_surface(root)
            (root / "VERSION").write_text("2.1.2\n", encoding="utf-8")
            with self.assertRaisesRegex(ProductSurfaceError, "must match VERSION"):
                validate_local_surface(root)

    def test_remote_sync_updates_description_and_exact_topics_then_verifies(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            surface = write_surface(root)
            expected = json.dumps({"description": surface["description"], "topics": surface["topics"]})
            responses = [
                subprocess.CompletedProcess([], 0, stdout=json.dumps({"description": "old", "topics": ["old"]}), stderr=""),
                subprocess.CompletedProcess([], 0, stdout="{}", stderr=""),
                subprocess.CompletedProcess([], 0, stdout="{}", stderr=""),
                subprocess.CompletedProcess([], 0, stdout=expected, stderr=""),
            ]
            with mock.patch("scripts.manage_github_product_surface.run_gh", side_effect=responses) as run:
                report = sync_remote_surface(surface, root=root, apply=True)
            self.assertTrue(report["changed"])
            self.assertEqual(run.call_count, 4)


if __name__ == "__main__":
    unittest.main()
