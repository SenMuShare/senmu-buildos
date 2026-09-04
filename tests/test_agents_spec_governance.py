from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


class AgentsSpecGovernanceTests(unittest.TestCase):
    def test_source_first_principle_has_one_architecture_owner_and_public_routes(self) -> None:
        architecture = read("docs/architecture/system-overview.md")
        project_gate = read(
            "skills/senmu-build-project/references/governance-levels-and-gates.md"
        )
        chinese = read("README.md")

        self.assertIn("## 核心治理顺序：宜疏不宜堵", architecture)
        self.assertIn("先减少生产过程制造错误的机会", architecture)
        self.assertIn("## 0. Govern at the Source; Use Gates as a Backstop", project_gate)
        self.assertIn("**宜疏不宜堵。**", chinese)

    def test_project_rule_admission_and_index_semantics_remain_distinct(self) -> None:
        discovery = read(
            "skills/senmu-build-project/references/project-standard-discovery-and-on-demand-loading.md"
        )

        for phrase in (
            "Apply two admission tests",
            "Current engineering constraints need only be valid, stable, implementation-relevant, and verifiable",
            "prior failure is unnecessary",
            "Several triggers may point to one authority",
            "neither require every Markdown file in the index",
            "warnings for exact duplicate entries",
        ):
            self.assertIn(phrase, discovery)

    def test_three_readmes_explain_cross_session_memory_and_five_layer_route(self) -> None:
        expectations = {
            "README.md": ("注意力会随着上下文变长而衰减", "项目入口"),
            "README.en.md": ("attention thins as context grows", "Project entrypoint"),
            "README.ja.md": ("文脈が長くなるほど注意は薄れます", "プロジェクト入口"),
        }
        for relative, phrases in expectations.items():
            with self.subTest(relative=relative):
                text = read(relative)
                for phrase in phrases:
                    self.assertIn(phrase, text)
                closing_phrase = (
                    "production evidence"
                    if relative.endswith(".en.md")
                    else "証拠"
                    if relative.endswith(".ja.md")
                    else "生产证据"
                )
                self.assertIn(closing_phrase, text)


if __name__ == "__main__":
    unittest.main()
