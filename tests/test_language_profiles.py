import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
ENGINEERING = ROOT / "skills/senmu-build-engineering"
ENTRY = ENGINEERING / "SKILL.md"
COMMON = ENGINEERING / "references/源代码工程质量与AI协作规范.md"
BEHAVIOR = ROOT / "tests/behavior/senmu-buildos-trigger-matrix.md"

PROFILES = {
    "TypeScript工程编码规范.md": ("strict", "unknown", "稳定判别字段", "import type"),
    "Go工程编码规范.md": ("%w", "goroutine", "context.Context", "go test -race"),
    "Java工程编码规范.md": ("AutoCloseable", "try-with-resources", "suppressed exceptions", "Maven／Gradle"),
}


class LanguageProfileContractTests(unittest.TestCase):
    def test_behavior_invariant_identifiers_are_unique(self) -> None:
        behavior = (ROOT / "tests/behavior/skill-entry-invariants.md").read_text(encoding="utf-8")
        identifiers = [
            match.group(1)
            for line in behavior.splitlines()
            if (match := re.match(r"^\|\s*([A-Z]+-\d+)\s*\|", line))
        ]
        self.assertEqual(len(identifiers), len(set(identifiers)))

    def test_each_profile_has_one_direct_entry_route_and_unique_owner(self) -> None:
        entry = ENTRY.read_text(encoding="utf-8")
        validator = (ROOT / "scripts/validate_package.py").read_text(encoding="utf-8")
        for filename in PROFILES:
            with self.subTest(filename=filename):
                self.assertEqual(entry.count(f"references/{filename}"), 1)
                self.assertEqual(validator.count(f'"{filename}": "senmu-build-engineering"'), 1)

    def test_profiles_preserve_language_specific_decisions_without_source_library(self) -> None:
        forbidden = ("https://", "aws.amazon.com", "google.github.io", "go.dev/")
        for filename, required in PROFILES.items():
            with self.subTest(filename=filename):
                text = (ENGINEERING / "references" / filename).read_text(encoding="utf-8")
                for signal in required:
                    self.assertIn(signal, text)
                for source_locator in forbidden:
                    self.assertNotIn(source_locator, text)

    def test_language_and_retry_scenarios_are_behaviorally_discriminated(self) -> None:
        common = COMMON.read_text(encoding="utf-8")
        behavior = BEHAVIOR.read_text(encoding="utf-8")
        for signal in ("重试由一个层级", "封顶退避", "稳定意图键", "同键不同参数"):
            self.assertIn(signal, common)
        for scenario in ("TypeScript API", "goroutine 泄漏", "Java 服务", "五层服务链", "同一幂等键"):
            self.assertIn(scenario, behavior)


if __name__ == "__main__":
    unittest.main()
