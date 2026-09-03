import re
import stat
import tempfile
import unittest
from pathlib import Path

from scripts.bump_version import ReleaseError, apply_changes, prepare_changes, validate_current


PLUGIN = """{
  "name": "senmu-buildos",
  "version": "1.0.0"
}
"""

CLAUDE_PLUGIN = """{
  "name": "senmu-buildos",
  "version": "1.0.0"
}
"""

ZCODE_PLUGIN = """{
  "name": "senmu-buildos",
  "version": "1.0.0"
}
"""

MARKETPLACE = """{
  "name": "senmu-buildos",
  "plugins": [
    {
      "name": "senmu-buildos",
      "source": {
        "source": "url",
        "url": "https://github.com/SenMuShare/senmu-buildos.git",
        "ref": "v1.0.0"
      }
    }
  ]
}
"""

CLAUDE_MARKETPLACE = """{
  "name": "senmu-buildos",
  "plugins": [
    {
      "name": "senmu-buildos",
      "source": "./",
      "version": "1.0.0"
    }
  ]
}
"""

CHANGELOG = """# Changelog

## Unreleased

### Added

- Add release automation.

## [1.0.0] - 2026-08-25

### Added

- Initial release.
"""

READMES = {
    "README.md": "Senmu BuildOS 当前正式版本为 `v1.0.0`。\n",
    "README.en.md": "The current formal release is Senmu BuildOS `v1.0.0`.\n",
    "README.ja.md": "Senmu BuildOS の現行正式リリースは `v1.0.0` です。\n",
}


class ReleaseVersioningTests(unittest.TestCase):
    def test_workflows_pin_actions_and_limit_release_write_scope(self) -> None:
        root = Path(__file__).resolve().parent.parent
        validate_workflow = (root / ".github/workflows/validate.yml").read_text(encoding="utf-8")
        release_workflow = (root / ".github/workflows/release.yml").read_text(encoding="utf-8")
        for workflow in (validate_workflow, release_workflow):
            references = re.findall(r"uses:\s*actions/[^@]+@([^\s]+)", workflow)
            self.assertTrue(references)
            self.assertTrue(all(re.fullmatch(r"[0-9a-f]{40}", reference) for reference in references))
        self.assertIn('branches:\n      - "**"', validate_workflow)
        self.assertIn("permissions:\n  contents: read", release_workflow)
        self.assertIn("publish:\n    needs: validate", release_workflow)
        self.assertIn("permissions:\n      contents: write", release_workflow)

    def make_repo(self) -> tuple[tempfile.TemporaryDirectory[str], Path]:
        temporary = tempfile.TemporaryDirectory()
        root = Path(temporary.name)
        (root / ".codex-plugin").mkdir()
        (root / ".claude-plugin").mkdir()
        (root / ".zcode-plugin").mkdir()
        (root / ".agents/plugins").mkdir(parents=True)
        (root / "VERSION").write_text("1.0.0\n", encoding="utf-8")
        (root / ".codex-plugin/plugin.json").write_text(PLUGIN, encoding="utf-8")
        (root / ".claude-plugin/plugin.json").write_text(CLAUDE_PLUGIN, encoding="utf-8")
        (root / ".zcode-plugin/plugin.json").write_text(ZCODE_PLUGIN, encoding="utf-8")
        (root / ".claude-plugin/marketplace.json").write_text(CLAUDE_MARKETPLACE, encoding="utf-8")
        (root / ".agents/plugins/marketplace.json").write_text(MARKETPLACE, encoding="utf-8")
        (root / "CHANGELOG.md").write_text(CHANGELOG, encoding="utf-8")
        for relative, text in READMES.items():
            (root / relative).write_text(text, encoding="utf-8")
        return temporary, root

    def test_prepare_and_apply_updates_all_release_owners(self) -> None:
        temporary, root = self.make_repo()
        self.addCleanup(temporary.cleanup)

        changes = prepare_changes(root, "1.1.0", "2026-08-26")
        self.assertEqual((root / "VERSION").read_text(encoding="utf-8"), "1.0.0\n")
        modes = {path: stat.S_IMODE(path.stat().st_mode) for path in changes}
        apply_changes(changes)

        self.assertEqual(validate_current(root, "v1.1.0"), "1.1.0")
        self.assertIn('"version": "1.1.0"', (root / ".codex-plugin/plugin.json").read_text())
        self.assertIn('"version": "1.1.0"', (root / ".claude-plugin/plugin.json").read_text())
        self.assertIn('"version": "1.1.0"', (root / ".zcode-plugin/plugin.json").read_text())
        self.assertIn('"version": "1.1.0"', (root / ".claude-plugin/marketplace.json").read_text())
        self.assertIn('"ref": "v1.1.0"', (root / ".agents/plugins/marketplace.json").read_text())
        changelog = (root / "CHANGELOG.md").read_text(encoding="utf-8")
        self.assertIn("## Unreleased\n\n## [1.1.0] - 2026-08-26", changelog)
        for relative in READMES:
            self.assertIn("`v1.1.0`", (root / relative).read_text(encoding="utf-8"))
        self.assertEqual({path: stat.S_IMODE(path.stat().st_mode) for path in changes}, modes)

    def test_rejects_downgrade(self) -> None:
        temporary, root = self.make_repo()
        self.addCleanup(temporary.cleanup)
        with self.assertRaisesRegex(ReleaseError, "must be newer"):
            prepare_changes(root, "0.9.0", "2026-08-26")

    def test_rejects_inconsistent_marketplace_ref(self) -> None:
        temporary, root = self.make_repo()
        self.addCleanup(temporary.cleanup)
        marketplace = root / ".agents/plugins/marketplace.json"
        marketplace.write_text(MARKETPLACE.replace("v1.0.0", "v0.9.0"), encoding="utf-8")
        with self.assertRaisesRegex(ReleaseError, "marketplace release ref"):
            validate_current(root)

    def test_rejects_inconsistent_claude_marketplace_version(self) -> None:
        temporary, root = self.make_repo()
        self.addCleanup(temporary.cleanup)
        marketplace = root / ".claude-plugin/marketplace.json"
        marketplace.write_text(CLAUDE_MARKETPLACE.replace('"version": "1.0.0"', '"version": "0.9.0"'), encoding="utf-8")
        with self.assertRaisesRegex(ReleaseError, "Claude Code marketplace version"):
            validate_current(root)

    def test_rejects_inconsistent_zcode_plugin_version(self) -> None:
        temporary, root = self.make_repo()
        self.addCleanup(temporary.cleanup)
        plugin = root / ".zcode-plugin/plugin.json"
        plugin.write_text(ZCODE_PLUGIN.replace('"version": "1.0.0"', '"version": "0.9.0"'), encoding="utf-8")
        with self.assertRaisesRegex(ReleaseError, "ZCode plugin manifest version"):
            validate_current(root)

    def test_rejects_stale_public_readme_version(self) -> None:
        temporary, root = self.make_repo()
        self.addCleanup(temporary.cleanup)
        readme = root / "README.md"
        readme.write_text(readme.read_text(encoding="utf-8").replace("v1.0.0", "v0.9.0"), encoding="utf-8")
        with self.assertRaisesRegex(ReleaseError, "README.md current release"):
            validate_current(root)

    def test_rejects_tag_mismatch(self) -> None:
        temporary, root = self.make_repo()
        self.addCleanup(temporary.cleanup)
        with self.assertRaisesRegex(ReleaseError, "does not match"):
            validate_current(root, "v1.0.1")

    def test_rejects_empty_unreleased_section(self) -> None:
        temporary, root = self.make_repo()
        self.addCleanup(temporary.cleanup)
        changelog = root / "CHANGELOG.md"
        changelog.write_text(CHANGELOG.replace("### Added\n\n- Add release automation.\n\n", ""), encoding="utf-8")
        with self.assertRaisesRegex(ReleaseError, "no releasable entries"):
            prepare_changes(root, "1.1.0", "2026-08-26")


if __name__ == "__main__":
    unittest.main()
