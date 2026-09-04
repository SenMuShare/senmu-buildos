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
        self.assertIn("Frontend/backend are references, not child skills or job roles", text)

    def test_specialist_skills_remain_peer_capabilities(self):
        text = (ENGINEERING / "SKILL.md").read_text(encoding="utf-8")
        architecture = (ROOT / "docs" / "architecture" / "skill-boundaries.md").read_text(
            encoding="utf-8"
        )
        for specialist in ("React", "Ant Design", "shadcn", "GSAP", "Postgres"):
            self.assertIn(specialist, architecture)
        self.assertIn("not child skills or job roles", text)

    def test_frontend_and_backend_keep_adjacent_owner_boundaries(self):
        frontend = (
            ENGINEERING / "references" / "前端工程契约与验证规范.md"
        ).read_text(encoding="utf-8")
        backend = (
            ENGINEERING / "references" / "后端服务与数据契约规范.md"
        ).read_text(encoding="utf-8")
        self.assertIn("It does not redefine product capability, copy meaning, or visual direction", frontend)
        self.assertIn("Hidden UI", backend)
        self.assertIn("Production-data modification/deletion or irreversible migration requires separate authority", backend)


if __name__ == "__main__":
    unittest.main()
