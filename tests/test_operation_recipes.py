#!/usr/bin/env python3
"""Protect the distilled operation recipes and their owner boundaries."""

from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent


def read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


class OperationRecipeContractTest(unittest.TestCase):
    def test_debugging_and_review_have_observable_structure(self):
        source = read(
            "skills/senmu-build-engineering/references/源代码工程质量与AI协作规范.md"
        )
        for phrase in ("能稳定失败", "假设排序", "一次只增加一个观测点", "删除临时日志"):
            self.assertIn(phrase, source)
        for axis in ("Requirement／Spec", "Engineering／Standards"):
            self.assertIn(axis, source)
        self.assertIn("Finding 写明所属轴", source)

    def test_test_first_is_conditional_not_mandatory(self):
        engineering_entry = read("skills/senmu-build-engineering/SKILL.md")
        testing = read(
            "skills/senmu-build-engineering/references/软件测试与质量验证规范.md"
        )
        self.assertIn("Not for routine fixes", engineering_entry)
        self.assertIn("visual or interaction direction or prototype validation", engineering_entry)
        self.assertIn("implementation review", engineering_entry)
        self.assertIn("implementation review", read("skills/senmu-build-product/SKILL.md"))
        self.assertIn("prototype validation", read("skills/senmu-build-design/SKILL.md"))
        self.assertIn("行为契约能在实现前清楚表达", testing)
        self.assertIn("不强制测试先行", testing)
        self.assertIn("不是所有修改的审批仪式", testing)

    def test_project_planning_keeps_vertical_value_and_honest_unknowns(self):
        tasks = read(
            "skills/senmu-build-project/references/任务执行与状态管理规范.md"
        )
        self.assertIn("纵向价值切片", tasks)
        self.assertIn("Not yet specified", tasks)
        self.assertIn("不得为看起来完整而提前编造", tasks)

    def test_architecture_and_poc_recipes_keep_safe_boundaries(self):
        architecture = read(
            "skills/senmu-build-engineering/references/架构约束与技术债治理规范.md"
        )
        selection = read(
            "skills/senmu-build-engineering/references/技术路线与组件选型.md"
        )
        self.assertIn("expand → migrate → contract", architecture)
        for boundary in ("可部署", "可验证", "可恢复"):
            self.assertIn(boundary, architecture)
        for phrase in ("逻辑原型", "可执行 harness", "输入、状态、转换、输出、错误"):
            self.assertIn(phrase, selection)
        self.assertIn("由 Assurance 冻结 POC", selection)

    def test_human_operator_wizard_protects_secrets_and_irreversible_actions(self):
        entry = read("skills/senmu-build-workflow/SKILL.md")
        workflow = read(
            "skills/senmu-build-workflow/references/工作流、物料与交付物治理规范.md"
        )
        self.assertIn("human-operator-guide", entry)
        self.assertIn("Not for executing workflows", entry)
        self.assertIn("人机操作向导", workflow)
        self.assertIn("不要求粘贴进聊天、日志、Git", workflow)
        self.assertIn("重复执行必须幂等", workflow)
        self.assertIn("不可逆动作前单独展示", workflow)
        self.assertIn("不接管现有向导的日常执行", workflow)

    def test_skill_text_and_readme_expose_recipes_without_new_skills(self):
        boundaries = read("docs/architecture/skill-boundaries.md")
        readme = read("README.md")
        self.assertIn("同域高频方法在现有 reference 中形成短操作配方", boundaries)
        self.assertIn("每步可检查的完成判断", boundaries)
        self.assertIn("优先写希望执行的正向动作", boundaries)
        for phrase in (
            "把这个 Bug 查到底",
            "分别按需求是否做对、代码质量是否过关来审查",
            "设计成可恢复的操作向导",
        ):
            self.assertIn(phrase, readme)

    def test_ui_prototype_already_requires_real_alternatives(self):
        prototype = read(
            "skills/senmu-build-design/references/原型探索与界面评审规范.md"
        )
        self.assertIn("通常提供二至三个候选", prototype)
        self.assertIn("不能只换颜色、圆角和阴影假装多个方案", prototype)


if __name__ == "__main__":
    unittest.main()
