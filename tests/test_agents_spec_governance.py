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
            "skills/senmu-build-project/references/治理强度分级与门禁规范.md"
        )
        chinese = read("README.md")

        self.assertIn("## 核心治理顺序：宜疏不宜堵", architecture)
        self.assertIn("先减少生产过程制造错误的机会", architecture)
        self.assertIn("## 0. 宜疏不宜堵：源头治理优先，门禁兜底", project_gate)
        self.assertIn("**宜疏不宜堵。**", chinese)

    def test_project_rule_admission_and_index_semantics_remain_distinct(self) -> None:
        discovery = read(
            "skills/senmu-build-project/references/项目规范发现与按需加载规范.md"
        )

        for phrase in (
            "使用两种不同准入标准",
            "现行工程约束只要当前有效、稳定、面向实现且可验证即可成立",
            "不要求先有失败历史",
            "同一权威正文可以有多个不同的适用信号或入口",
            "不要求所有 Markdown 都进入索引",
            "警告用于完全重复索引行",
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
