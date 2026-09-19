#!/usr/bin/env python3
"""Validate the WorkBuddy adapter: kernel skill, installer, and shared skills."""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ADAPTER = ROOT / "adapters" / "workbuddy"
SKILLS = ROOT / "skills"


def load_installer():
    spec = importlib.util.spec_from_file_location(
        "workbuddy_installer", ADAPTER / "install_workbuddy.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


INSTALLER = load_installer()

WORKBUDDY_SKILL_NAMES = [
    "senmu-build-project",
    "senmu-build-product",
    "senmu-build-design",
    "senmu-build-workflow",
    "senmu-build-engineering",
    "senmu-build-delivery",
    "senmu-build-assurance",
    "senmu-build-learning",
]
KERNEL_NAME = "senmu-build-kernel"
ALL_NAMES = WORKBUDDY_SKILL_NAMES + [KERNEL_NAME]


class WorkBuddyAdapterTest(unittest.TestCase):
    def test_kernel_skill_exists_with_valid_frontmatter(self):
        kernel = ADAPTER / "kernel" / "SKILL.md"
        self.assertTrue(kernel.is_file(), "adapters/workbuddy/kernel/SKILL.md missing")
        text = kernel.read_text(encoding="utf-8")
        self.assertIn("name: senmu-build-kernel", text)
        self.assertIn("description:", text)
        self.assertIn("WorkBuddy", text)

    def test_kernel_routes_all_eight_skills(self):
        text = (ADAPTER / "kernel" / "SKILL.md").read_text(encoding="utf-8")
        for name in WORKBUDDY_SKILL_NAMES:
            self.assertIn(name, text, f"kernel routing table missing {name}")

    def test_kernel_keeps_context_effectiveness_boundary(self):
        text = (ADAPTER / "kernel" / "SKILL.md").read_text(encoding="utf-8")
        # Exact lifecycle/bootstrap parity is checked by the Hook transport test.
        self.assertEqual(text.count("<!-- kernel-contract:start -->"), 1)
        self.assertEqual(text.count("<!-- kernel-contract:end -->"), 1)

    def test_all_shared_skills_have_workbuddy_loadable_frontmatter(self):
        for name in WORKBUDDY_SKILL_NAMES:
            skill_md = SKILLS / name / "SKILL.md"
            self.assertTrue(skill_md.is_file(), f"skills/{name}/SKILL.md missing")
            text = skill_md.read_text(encoding="utf-8")
            self.assertIn(f"name: {name}", text)
            self.assertIn("description:", text)

    def test_installer_dry_run_lists_expected_skills(self):
        result = subprocess.run(
            [
                sys.executable,
                str(ADAPTER / "install_workbuddy.py"),
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
                    str(ADAPTER / "install_workbuddy.py"),
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
            identity_path = Path(tmp) / ".senmu-buildos-install.json"
            self.assertTrue(identity_path.is_file(), "install identity file missing")
            identity = json.loads(identity_path.read_text(encoding="utf-8"))
            self.assertEqual(identity["adapter"], "workbuddy")
            self.assertEqual(identity["skills"], ALL_NAMES)
            # Codex-only metadata must not leak into the WorkBuddy install.
            self.assertFalse((Path(tmp) / "senmu-build-project" / "agents").exists())

    def test_installer_rejects_project_scope_without_workspace(self):
        result = subprocess.run(
            [
                sys.executable,
                str(ADAPTER / "install_workbuddy.py"),
                "--scope", "project",
            ],
            capture_output=True, text=True,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("--workspace", result.stderr)

    def test_installer_project_scope_targets_workspace_skills(self):
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp) / "ws"
            (workspace / ".workbuddy" / "skills").mkdir(parents=True)
            result = subprocess.run(
                [
                    sys.executable,
                    str(ADAPTER / "install_workbuddy.py"),
                    "--scope", "project",
                    "--workspace", str(workspace),
                ],
                capture_output=True, text=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            for name in ALL_NAMES:
                self.assertTrue(
                    (workspace / ".workbuddy" / "skills" / name / "SKILL.md").is_file(),
                    f"{name}/SKILL.md not installed into project scope",
                )

    def test_skills_root_prefers_current_data_root_when_both_exist(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            (base / ".workbuddy-ai").mkdir()
            (base / ".workbuddy").mkdir()
            self.assertEqual(
                INSTALLER.skills_root(base), base / ".workbuddy-ai" / "skills"
            )

    def test_skills_root_falls_back_to_legacy_data_root(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            (base / ".workbuddy").mkdir()
            self.assertEqual(
                INSTALLER.skills_root(base), base / ".workbuddy" / "skills"
            )

    def test_skills_root_defaults_to_current_name_when_neither_exists(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            self.assertEqual(
                INSTALLER.skills_root(base), base / ".workbuddy-ai" / "skills"
            )

    def test_installer_project_scope_prefers_current_data_root(self):
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp) / "ws"
            (workspace / ".workbuddy-ai" / "skills").mkdir(parents=True)
            (workspace / ".workbuddy" / "skills").mkdir(parents=True)
            result = subprocess.run(
                [
                    sys.executable,
                    str(ADAPTER / "install_workbuddy.py"),
                    "--scope", "project",
                    "--workspace", str(workspace),
                ],
                capture_output=True, text=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            for name in ALL_NAMES:
                self.assertTrue(
                    (
                        workspace / ".workbuddy-ai" / "skills" / name / "SKILL.md"
                    ).is_file(),
                    f"{name}/SKILL.md not installed into the current data root",
                )
            # The stale root must not receive a second copy.
            self.assertFalse(
                (workspace / ".workbuddy" / "skills" / "senmu-build-project").exists()
            )


if __name__ == "__main__":
    unittest.main()
