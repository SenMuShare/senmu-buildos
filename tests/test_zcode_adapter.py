#!/usr/bin/env python3
"""Validate the ZCode adapter: plugin manifest, kernel skill, installer, shared skills."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ADAPTER = ROOT / "adapters" / "zcode"
SKILLS = ROOT / "skills"
ZCODE_SKILL_NAMES = [
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
ALL_NAMES = ZCODE_SKILL_NAMES + [KERNEL_NAME]


class ZCodePluginManifestTest(unittest.TestCase):
    def test_manifest_declares_skills_route_and_matches_version(self):
        manifest = json.loads((ROOT / ".zcode-plugin" / "plugin.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["name"], "senmu-buildos")
        self.assertEqual(manifest["skills"], "./skills/")
        self.assertNotIn("hooks", manifest, "ZCode uses the default hooks/hooks.json discovery path")
        version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
        self.assertEqual(manifest["version"], version)

    def test_root_hooks_resolve_plugin_root_without_platform_variable(self):
        hooks = json.loads((ROOT / "hooks" / "hooks.json").read_text(encoding="utf-8"))
        serialized = json.dumps(hooks)
        self.assertIn("CLAUDE_PLUGIN_ROOT", serialized)
        self.assertIn("ZCODE_PLUGIN_ROOT", serialized)
        self.assertIn("${PLUGIN_ROOT}", serialized)
        self.assertIn("/hooks/session-start.js", serialized)
        session = hooks["hooks"]["SessionStart"][0]["hooks"][0]
        self.assertEqual(session["type"], "command")
        self.assertEqual(session["timeout"], 5)

    def test_shared_session_start_script_emits_lifecycle_json(self):
        result = subprocess.run(
            ["node", str(ROOT / "hooks" / "session-start.js")],
            capture_output=True, text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        output = json.loads(result.stdout)
        self.assertEqual(output["hookSpecificOutput"]["hookEventName"], "SessionStart")
        self.assertTrue(output["hookSpecificOutput"]["additionalContext"])


class ZCodeAdapterTest(unittest.TestCase):
    def test_kernel_skill_exists_with_valid_frontmatter(self):
        kernel = ADAPTER / "kernel" / "SKILL.md"
        self.assertTrue(kernel.is_file(), "adapters/zcode/kernel/SKILL.md missing")
        text = kernel.read_text(encoding="utf-8")
        self.assertIn("name: senmu-build-kernel", text)
        self.assertIn("description:", text)
        self.assertIn("ZCode", text)

    def test_kernel_routes_all_eight_skills(self):
        text = (ADAPTER / "kernel" / "SKILL.md").read_text(encoding="utf-8")
        for name in ZCODE_SKILL_NAMES:
            self.assertIn(name, text, f"kernel routing table missing {name}")

    def test_kernel_keeps_context_effectiveness_boundary(self):
        text = (ADAPTER / "kernel" / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("项目／框架／平台现有能力", text)
        self.assertIn("复用仍有效证据", text)
        self.assertIn("不拼接可能截断的长输出", text)

    def test_all_shared_skills_have_zcode_loadable_frontmatter(self):
        for name in ZCODE_SKILL_NAMES:
            skill_md = SKILLS / name / "SKILL.md"
            self.assertTrue(skill_md.is_file(), f"skills/{name}/SKILL.md missing")
            text = skill_md.read_text(encoding="utf-8")
            self.assertIn(f"name: {name}", text)
            self.assertIn("description:", text)

    def test_installer_dry_run_lists_expected_skills(self):
        result = subprocess.run(
            [
                sys.executable,
                str(ADAPTER / "install_zcode.py"),
                "--dry-run",
                "--target", str(ROOT),
            ],
            capture_output=True, text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        for name in ZCODE_SKILL_NAMES:
            self.assertIn(name, result.stdout)
        self.assertNotIn(KERNEL_NAME, result.stdout)

    def test_installer_dry_run_with_kernel_lists_bootstrap_skill(self):
        result = subprocess.run(
            [
                sys.executable,
                str(ADAPTER / "install_zcode.py"),
                "--dry-run",
                "--with-kernel",
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
                    str(ADAPTER / "install_zcode.py"),
                    "--with-kernel",
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
            self.assertEqual(identity["adapter"], "zcode")
            self.assertTrue(identity["with_kernel"])
            self.assertEqual(identity["skills"], ALL_NAMES)
            # Codex-only metadata must not leak into the ZCode install.
            self.assertFalse((Path(tmp) / "senmu-build-project" / "agents").exists())

    def test_installer_rejects_project_scope_without_workspace(self):
        result = subprocess.run(
            [
                sys.executable,
                str(ADAPTER / "install_zcode.py"),
                "--scope", "project",
            ],
            capture_output=True, text=True,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("--workspace", result.stderr)

    def test_installer_project_scope_creates_workspace_skills(self):
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp) / "repo"
            result = subprocess.run(
                [
                    sys.executable,
                    str(ADAPTER / "install_zcode.py"),
                    "--scope", "project",
                    "--workspace", str(workspace),
                ],
                capture_output=True, text=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            for name in ZCODE_SKILL_NAMES:
                self.assertTrue(
                    (workspace / ".agents" / "skills" / name / "SKILL.md").is_file(),
                    f"{name}/SKILL.md not installed into project scope",
                )


if __name__ == "__main__":
    unittest.main()
