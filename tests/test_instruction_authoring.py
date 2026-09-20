"""Structural/draft regressions, not claims of live model or host behavior."""
from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PROJECT = ROOT / "skills/senmu-build-project"
SPEC = importlib.util.spec_from_file_location(
    "instruction_initializer", PROJECT / "scripts/init_project_governance.py"
)
assert SPEC is not None and SPEC.loader is not None
initializer = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(initializer)


class InstructionAuthoringTests(unittest.TestCase):
    def draft(self, modules: set[str], project_type: str = "software") -> str:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            return initializer.render(
                PROJECT / "assets/project-governance-starter/AGENTS.template.md",
                "Example", root, root, "repository", "core", project_type,
                {"lifecycle_intent": "production", "delivery_model": "continuous_product",
                 "composition": "single_domain"},
                modules, "private_only", [], [],
            )

    def test_software_draft_has_useful_vendor_neutral_principles(self) -> None:
        text = self.draft({"code", "product"})
        for phrase in (
            "Reuse and extend", "Keep code clear",
            "framework and standard capabilities", "approved stack",
            "Keep necessary types, error handling and tests",
            "Trace consumers before deletion", "never weaken checks to pass",
        ):
            self.assertIn(phrase, text)
        self.assertNotIn("{{", text)
        self.assertNotIn("engineering-only:", text)
        self.assertNotIn("2.12.0", text)
        for vendor in ("Ant Design", "shadcn", "Element UI"):
            self.assertNotIn(vendor, text)

    def test_noncode_draft_omits_software_policy_not_general_working_agreements(self) -> None:
        text = self.draft({"workflow", "delivery"}, "media")
        for phrase in ("Reuse and extend", "framework and standard capabilities",
                       "approved stack", "Keep necessary types"):
            self.assertNotIn(phrase, text)
        for phrase in ("Judge independently", "Use evidence", "Ease the correct path",
                       "Protect existing work", "Act proportionately", "Use context well"):
            self.assertIn(phrase, text)
        self.assertNotIn("engineering-only:", text)

    def test_draft_rendering_is_repeatable_without_appending_principles(self) -> None:
        first, second = self.draft({"code"}), self.draft({"code"})
        self.assertEqual(first, second)
        self.assertEqual(first.count("## Adopted Working Principles"), 1)
        self.assertEqual(first.count("**Judge independently.**"), 1)
        self.assertEqual(first.count("**Reuse and extend.**"), 1)

    def test_english_structural_draft_does_not_claim_localization_or_activation(self) -> None:
        text = self.draft({"code", "poc"})
        self.assertIn("chosen project instruction language", text)
        self.assertIn("A draft is not an activated experiment area", text)
        self.assertIn("resolved at runtime", text)
        self.assertIn("remove placeholders before adoption", text)
        self.assertLessEqual(len(text), 2_300)
        contract = (PROJECT / "references/project-instruction-authoring.md").read_text(encoding="utf-8")
        self.assertIn("Claim runtime activation or token savings only with corresponding observations", contract)

    def test_authoring_contract_preserves_language_exceptions_and_existing_files(self) -> None:
        text = (PROJECT / "references/project-instruction-authoring.md").read_text(encoding="utf-8")
        for phrase in (
            "two parallel outcomes", "Explicitly adopted team working principles",
            "Repeated governance of unchanged facts must be a semantic no-op",
            "Audit-only remains read-only",
            "An explicit user instruction about document language takes precedence",
            "preserve its established language", "initialization request's language",
            "Use English only when there is no language signal",
            "Do not append bilingual copies by default",
            "Code-comment, product-content and response languages remain separate",
            "Existing projects are never reinitialized",
            "Structural fixtures do not prove an AI performed semantic reconciliation",
        ):
            self.assertIn(phrase.casefold(), text.casefold())

    def test_project_entry_routes_authoring_without_business_agent_confusion(self) -> None:
        text = (PROJECT / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("business runtime agents", text)
        self.assertIn("references/project-instruction-authoring.md", text)
        self.assertIn("Shared principles need not be unique", text)
        self.assertLessEqual(len(text), 3_600)

    def test_decision_principles_survive_all_module_selections(self) -> None:
        # Exercise the actual renderer: engineering clauses are conditional,
        # but independent judgment, evidence and source prevention are not.
        for modules in (set(), {"workflow"}, {"code"}, {"code", "poc"}, {"agents"}):
            with self.subTest(modules=modules):
                text = self.draft(modules)
                principles = text.split("## Adopted Working Principles", 1)[1].split(
                    "## Project Facts and Exceptions", 1
                )[0]
                for phrase in ("Judge independently", "Use evidence", "Ease the correct path"):
                    self.assertEqual(principles.count(phrase), 1)
                self.assertEqual("Reuse and extend" in principles, "code" in modules)
                self.assertNotIn("{{", text)
                self.assertNotIn("engineering-only:", text)

    def test_source_summary_retains_counterbalancing_boundaries(self) -> None:
        # This checks rendered source coverage, NOT whether a live model obeys it.
        text = self.draft({"code"})
        for phrase in (
            "yours and the user's", "informed choices", "reflexive opposition",
            "facts, inferences and unknowns", "Urgent containment may precede root repair",
            "unknown data", "others' work", "host permissions",
            "not whole documents or Skills", "security, privacy, cost, production",
        ):
            self.assertIn(phrase, text)
        scenarios = ROOT / "tests/behavior/core-working-principles.md"
        self.assertTrue(scenarios.is_file())


if __name__ == "__main__":
    unittest.main()
