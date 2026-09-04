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
            "skills/senmu-build-engineering/references/source-code-quality-and-ai-collaboration.md"
        )
        for phrase in ("short, stable failing loop", "rank hypotheses", "Change one observation/variable at a time", "remove debug logs"):
            self.assertIn(phrase, source)
        for axis in ("Requirement/Spec", "Engineering/Standards"):
            self.assertIn(axis, source)
        self.assertIn("A Finding names axis", source)

    def test_test_first_is_conditional_not_mandatory(self):
        engineering_entry = read("skills/senmu-build-engineering/SKILL.md")
        testing = read(
            "skills/senmu-build-engineering/references/software-testing-and-quality-verification.md"
        )
        self.assertIn("Not for routine fixes", engineering_entry)
        self.assertIn("visual or interaction direction or prototype validation", engineering_entry)
        self.assertIn("implementation review", engineering_entry)
        self.assertIn("implementation review", read("skills/senmu-build-product/SKILL.md"))
        self.assertIn("prototype validation", read("skills/senmu-build-design/SKILL.md"))
        self.assertIn("When behavior is expressible before implementation", testing)
        self.assertIn("Do not force test-first", testing)
        self.assertIn("not an approval ritual", testing)

    def test_project_planning_keeps_vertical_value_and_honest_unknowns(self):
        tasks = read(
            "skills/senmu-build-project/references/task-execution-and-state-management.md"
        )
        self.assertIn("vertical value slices", tasks)
        self.assertIn("Not yet specified", tasks)
        self.assertIn("Do not invent tasks", tasks)

    def test_architecture_and_poc_recipes_keep_safe_boundaries(self):
        architecture = read(
            "skills/senmu-build-engineering/references/architecture-constraints-and-technical-debt.md"
        )
        selection = read(
            "skills/senmu-build-engineering/references/technology-and-component-selection.md"
        )
        self.assertIn("expand -> migrate -> contract", architecture)
        for boundary in ("deployable", "verifiable", "recoverable"):
            self.assertIn(boundary, architecture)
        for phrase in ("logic prototype", "executable harness", "inputs, state, transitions, outputs, errors"):
            self.assertIn(phrase, selection)
        self.assertIn("Assurance freezes", selection)

    def test_human_operator_wizard_protects_secrets_and_irreversible_actions(self):
        entry = read("skills/senmu-build-workflow/SKILL.md")
        workflow = read(
            "skills/senmu-build-workflow/references/workflow-materials-and-deliverables.md"
        )
        self.assertIn("human-operator-guide", entry)
        self.assertIn("Not for executing workflows", entry)
        self.assertIn("Human-Operator Guide", workflow)
        self.assertIn("directly in trusted interfaces—not chat, logs, Git", workflow)
        self.assertIn("retries must be idempotent", workflow)
        self.assertIn("Before deletion, payment, review submission, notification, production switch", workflow)
        self.assertIn("not routine execution", workflow)

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
            "skills/senmu-build-design/references/prototype-exploration-and-interface-review.md"
        )
        self.assertIn("Offer two or three alternatives", prototype)
        self.assertIn("not only color, radius, and shadow", prototype)


if __name__ == "__main__":
    unittest.main()
