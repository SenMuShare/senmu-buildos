#!/usr/bin/env python3
"""Protect Engineering domain references without creating role-shaped Skills."""

from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
ENGINEERING = ROOT / "skills" / "senmu-build-engineering"


class EngineeringDomainReferenceTest(unittest.TestCase):
    def test_entry_routes_frontend_and_backend_as_references(self):
        text = (ENGINEERING / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("前端工程契约与验证规范.md", text)
        self.assertIn("后端服务与数据契约规范.md", text)
        self.assertIn("不是父子 Skill 或岗位映射", text)

    def test_specialist_skills_remain_peer_capabilities(self):
        text = (ENGINEERING / "SKILL.md").read_text(encoding="utf-8")
        architecture = (ROOT / "docs" / "architecture" / "skill-boundaries.md").read_text(
            encoding="utf-8"
        )
        for specialist in ("React", "Ant Design", "shadcn", "GSAP", "Postgres"):
            self.assertIn(specialist, architecture)
        self.assertIn("保持平级", text)

    def test_frontend_and_backend_keep_adjacent_owner_boundaries(self):
        frontend = (
            ENGINEERING / "references" / "前端工程契约与验证规范.md"
        ).read_text(encoding="utf-8")
        backend = (
            ENGINEERING / "references" / "后端服务与数据契约规范.md"
        ).read_text(encoding="utf-8")
        self.assertIn("不重新决定产品功能、文案语义或视觉方向", frontend)
        self.assertIn("前端隐藏", backend)
        self.assertIn("生产数据修改、删除或不可逆迁移需要独立授权", backend)


if __name__ == "__main__":
    unittest.main()
