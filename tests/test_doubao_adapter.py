#!/usr/bin/env python3
"""Validate the Doubao adapter: kernel skill, installer, and shared skills."""

from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ADAPTER = ROOT / "adapters" / "doubao"
SKILLS = ROOT / "skills"
DOUBAO_SKILL_NAMES = [
    "senmu-build-project",
    "senmu-build-product",
    "senmu-build-workflow",
    "senmu-build-engineering",
    "senmu-build-delivery",
    "senmu-build-assurance",
    "senmu-build-learning",
]
KERNEL_NAME = "senmu-build-kernel"
ALL_NAMES = DOUBAO_SKILL_NAMES + [KERNEL_NAME]


class DoubaoAdapterTest(unittest.TestCase):
    def test_kernel_skill_exists_with_valid_frontmatter(self):
        kernel = ADAPTER / "kernel" / "SKILL.md"
        self.assertTrue(kernel.is_file(), "adapters/doubao/kernel/SKILL.md missing")
        text = kernel.read_text(encoding="utf-8")
        self.assertIn("name: senmu-build-kernel", text)
        self.assertIn("description:", text)

    def test_kernel_routes_all_seven_skills(self):
        text = (ADAPTER / "kernel" / "SKILL.md").read_text(encoding="utf-8")
        for name in DOUBAO_SKILL_NAMES:
            self.assertIn(name, text, f"kernel routing table missing {name}")

    def test_all_shared_skills_have_doubao_loadable_frontmatter(self):
        for name in DOUBAO_SKILL_NAMES:
            skill_md = SKILLS / name / "SKILL.md"
            self.assertTrue(skill_md.is_file(), f"skills/{name}/SKILL.md missing")
            text = skill_md.read_text(encoding="utf-8")
            self.assertIn(f"name: {name}", text)
            self.assertIn("description:", text)

    def test_installer_dry_run_lists_expected_skills(self):
        result = subprocess.run(
            [
                sys.executable,
                str(ADAPTER / "install_doubao.py"),
                "--dry-run",
                "--target", str(ROOT),
            ],
            capture_output=True, text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        for name in ALL_NAMES:
            self.assertIn(name, result.stdout)

    def test_installer_real_install_roundtrip(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = subprocess.run(
                [
                    sys.executable,
                    str(ADAPTER / "install_doubao.py"),
                    "--target", tmp,
                ],
                capture_output=True, text=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            for name in ALL_NAMES:
                self.assertTrue(
                    (Path(tmp) / name / "SKILL.md").is_file(),
                    f"{name}/SKILL.md not installed",
                )
            identity = Path(tmp) / ".senmu-buildos-install.json"
            self.assertTrue(identity.is_file(), "install identity file missing")
            # Codex-only metadata must not leak into the Doubao install.
            self.assertFalse((Path(tmp) / "senmu-build-project" / "agents").exists())


if __name__ == "__main__":
    unittest.main()
