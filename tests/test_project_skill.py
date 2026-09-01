#!/usr/bin/env python3
"""Protect the Project Skill's user-facing governance identity and peer boundary."""

from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
PROJECT = ROOT / "skills" / "senmu-build-project"


class ProjectSkillTest(unittest.TestCase):
    def test_user_facing_identity_is_governance_while_slug_stays_stable(self):
        entry = (PROJECT / "SKILL.md").read_text(encoding="utf-8")
        ui = (PROJECT / "agents/openai.yaml").read_text(encoding="utf-8")

        self.assertIn("name: senmu-build-project", entry)
        self.assertIn("# Project Governance", entry)
        self.assertIn('display_name: "Senmu Build Project Governance"', ui)
        self.assertNotIn("Project Management", entry + ui)

    def test_architecture_keeps_project_as_a_peer_governance_skill(self):
        boundaries = (
            ROOT / "docs/architecture/skill-boundaries.md"
        ).read_text(encoding="utf-8")

        self.assertIn("Project Governance（项目治理）", boundaries)
        self.assertIn("不是其他专业 Skill 的父级", boundaries)
        self.assertIn("不设置第九个“总导演”Skill", boundaries)

    def test_assurance_identity_does_not_equate_self_review_with_independence(self):
        boundaries = (
            ROOT / "docs/architecture/skill-boundaries.md"
        ).read_text(encoding="utf-8")
        assurance = (
            ROOT / "skills/senmu-build-assurance/SKILL.md"
        ).read_text(encoding="utf-8")

        for identity in ("independent", "peer", "evidence-based self-review"):
            self.assertIn(identity, boundaries)
            self.assertIn(identity, assurance)
        self.assertIn("无法证明职责分离时不得称独立审查", boundaries)


if __name__ == "__main__":
    unittest.main()
