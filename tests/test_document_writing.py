"""Writing-route and existing PRD-checker regressions, not model evaluations."""
from __future__ import annotations
import ast
import re
import runpy
import unittest
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parent.parent
OWNER = ROOT / "skills/senmu-build-engineering/references/technical-documentation-writing.md"
CHECK = runpy.run_path(str(ROOT / "skills/senmu-build-product/scripts/check_requirement_structure.py"))["check"]


def feature(identifier="FUN-001", version="V1.2.3"):
    return f"""## {identifier} 导出
需求对应版本号：`{version}`
### 1. 需求描述
管理员需要下载已有结果，通常在处理完成后操作。
### 2. 功能描述
仅管理员可以导出；文案修订不得扩展权限。
### 3. 功能逻辑
最多重试 3 次，每次间隔 5 秒；接口 `POST /api/export` 的 `task_id` 保持不变。
### 4. 前端交互描述
失败后保留选择；超时先查询任务状态，不假定没有副作用。
#### 关联原型／UI 设计稿
[设计 r7](design/export-r7.html)：部分采用布局，不采用示例价格；历史依据保留。
"""


class DocumentWritingRoutesTests(unittest.TestCase):
    def test_reusable_method_has_one_physical_owner(self):
        owners = list((ROOT / "skills").glob("*/references/technical-documentation-writing.md"))
        self.assertEqual(owners, [OWNER])

    def test_editing_entrypoints_resolve_to_the_same_method(self):
        consumers = (
            "skills/senmu-build-engineering/SKILL.md",
            "skills/senmu-build-product/references/interface-copy-and-content-design.md",
            "skills/senmu-build-workflow/references/workflow-materials-and-deliverables.md",
            "skills/senmu-build-delivery/references/collaboration-and-version-logs.md",
        )
        for relative in consumers:
            path = ROOT / relative
            targets = set()
            for link in re.findall(r"\[[^\]]+\]\(([^)]+)\)", path.read_text(encoding="utf-8")):
                parsed = urlsplit(link)
                if not parsed.scheme and parsed.path:
                    targets.add((path.parent / unquote(parsed.path)).resolve())
            with self.subTest(consumer=relative):
                self.assertIn(OWNER.resolve(), targets)

    def test_package_registers_the_actual_owner(self):
        tree = ast.parse((ROOT / "scripts/validate_package.py").read_text(encoding="utf-8"))
        assignments = [node for node in tree.body if isinstance(node, ast.Assign)
                       and any(isinstance(t, ast.Name) and t.id == "REFERENCE_OWNERS" for t in node.targets)]
        self.assertEqual(len(assignments), 1)
        owners = ast.literal_eval(assignments[0].value)
        self.assertEqual(owners[OWNER.name], "senmu-build-engineering")

    def test_existing_eight_skill_boundary_is_unchanged(self):
        self.assertEqual(len(list((ROOT / "skills").glob("*/SKILL.md"))), 8)


class DocumentWritingRequirementBoundaryTests(unittest.TestCase):
    def test_wording_change_preserves_per_feature_structure(self):
        source = feature() + feature("FUN-002", "V1.2.4")
        revised = source.replace("管理员需要下载已有结果", "管理员需要下载已生成的结果")
        result = CHECK(revised)
        self.assertEqual(result["status"], "pass", result)
        self.assertEqual(result["features"], 2)
        self.assertEqual(result["scope"], "structure_only")

    def test_document_summary_does_not_replace_local_versions(self):
        revised = "# V1.2.3 需求摘要\n" + feature().replace("需求对应版本号：`V1.2.3`\n", "")
        self.assertEqual(CHECK(revised)["status"], "fail")

    def test_design_reference_stays_nested_not_a_fifth_part(self):
        self.assertEqual(CHECK(feature())["status"], "pass")
        revised = feature().replace("#### 关联原型／UI 设计稿", "### 关联原型／UI 设计稿")
        self.assertEqual(CHECK(revised)["status"], "fail")

    def test_structural_success_does_not_certify_changed_facts(self):
        revised = feature().replace("最多重试 3 次", "最多重试 30 次").replace("仅管理员可以导出", "所有用户可以导出")
        result = CHECK(revised)
        self.assertEqual(result["status"], "pass")
        self.assertEqual(result["scope"], "structure_only")
        # Semantic preservation is intentionally outside this checker's contract.
        self.assertNotIn("accepted", result)


if __name__ == "__main__":
    unittest.main()
