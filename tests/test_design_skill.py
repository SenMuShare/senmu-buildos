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
            "界面视觉与设计系统规范.md",
            "参考界面解析与还原规范.md",
            "交互动效与可访问性规范.md",
            "原型探索与界面评审规范.md",
        ):
            self.assertIn(reference, text)

    def test_entry_preserves_adjacent_owner_boundaries(self):
        text = (DESIGN / "SKILL.md").read_text(encoding="utf-8")
        for owner in ("Product", "Engineering", "Assurance", "Delivery"):
            self.assertIn(owner, text)
        self.assertIn("Ant Design、shadcn、GSAP", text)

    def test_reference_analysis_routes_progressively_to_design_library(self):
        analysis = (DESIGN / "references" / "参考界面解析与还原规范.md").read_text(
            encoding="utf-8"
        )
        index = (
            DESIGN / "references" / "design-library" / "INDEX.md"
        ).read_text(encoding="utf-8")
        self.assertIn("design-library/INDEX.md", analysis)
        self.assertIn("页面结构与视觉方向.md", index)
        self.assertIn("组件设计模式.md", index)
        self.assertIn("不是前端组件代码包", index)

    def test_reference_analysis_preserves_project_owner_and_unknowns(self):
        analysis = (DESIGN / "references" / "参考界面解析与还原规范.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("已观察、推断、冲突和未知", analysis)
        self.assertIn("不会自动成为项目设计 owner", analysis)

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
