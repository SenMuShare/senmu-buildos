#!/usr/bin/env python3
"""Protect the Design Skill's owner, routing, and progressive-disclosure boundaries."""

from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
DESIGN = ROOT / "skills" / "senmu-build-design"


class DesignSkillTest(unittest.TestCase):
    def test_entry_routes_distinct_design_results(self):
        text = (DESIGN / "SKILL.md").read_text(encoding="utf-8")
        for reference in (
            "visual-systems-and-design-language.md",
            "reference-interface-analysis-and-reconstruction.md",
            "interaction-motion-and-accessibility.md",
            "prototype-exploration-and-interface-review.md",
        ):
            self.assertIn(reference, text)

    def test_entry_preserves_adjacent_owner_boundaries(self):
        text = (DESIGN / "SKILL.md").read_text(encoding="utf-8")
        for owner in ("Product", "Engineering", "Assurance", "Delivery"):
            self.assertIn(owner, text)
        self.assertIn("specialist skills for current APIs/methods only", text)

    def test_reference_analysis_routes_progressively_to_design_library(self):
        analysis = (DESIGN / "references" / "reference-interface-analysis-and-reconstruction.md").read_text(
            encoding="utf-8"
        )
        index = (
            DESIGN / "references" / "design-library" / "INDEX.md"
        ).read_text(encoding="utf-8")
        self.assertIn("design-library/INDEX.md", analysis)
        self.assertIn("page-structures-and-visual-directions.md", index)
        self.assertIn("component-design-patterns.md", index)
        self.assertIn("not project brand facts or frontend code", index)

    def test_reference_analysis_preserves_project_owner_and_unknowns(self):
        analysis = (DESIGN / "references" / "reference-interface-analysis-and-reconstruction.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("observations, inferences, conflicts, unknowns", analysis)
        self.assertIn("Reference analysis does not become the design owner", analysis)

    def test_runtime_guidance_does_not_embed_source_products(self):
        runtime = "\n".join(
            path.read_text(encoding="utf-8")
            for path in sorted(DESIGN.rglob("*.md"))
        ).casefold()
        for source_name in (
            "ui-ux-pro-max",
            "website-design-brief",
            "emil",
            "apple-design",
            "motionsites",
        ):
            self.assertNotIn(source_name, runtime)

    def test_behavior_matrix_distinguishes_design_from_neighbors(self):
        matrix = (ROOT / "tests/behavior/senmu-buildos-trigger-matrix.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("`senmu-build-design`", matrix)
        self.assertIn("设计稿、Token 和交互规格已经批准", matrix)
        self.assertIn("Ant Design 的这个组件当前版本", matrix)


if __name__ == "__main__":
    unittest.main()
