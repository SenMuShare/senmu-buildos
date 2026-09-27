"""Render/validation contracts; semantic principles are reviewed in decision scenarios."""
from __future__ import annotations

import contextlib
import importlib.util
import io
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parent.parent
PROJECT = ROOT / "skills/senmu-build-project"
STARTER = PROJECT / "assets/project-governance-starter/AGENTS.template.md"
SPEC = importlib.util.spec_from_file_location(
    "instruction_initializer", PROJECT / "scripts/init_project_governance.py"
)
assert SPEC is not None and SPEC.loader is not None
initializer = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(initializer)
sys.path.insert(0, str(ROOT / "scripts"))
import validate_package as package_validator


class InstructionAuthoringTests(unittest.TestCase):
    def render(self, template: Path, root: Path, modules: set[str],
               name: str = "Example", profile: str = "core") -> str:
        return initializer.render(
            template, name, root, root, "repository", profile, "software",
            {"lifecycle_intent": "production", "delivery_model": "continuous_product",
             "composition": "single_domain"},
            modules, "private_only", [], [],
        )

    def draft(self, modules: set[str], **kwargs) -> str:
        with tempfile.TemporaryDirectory() as directory:
            return self.render(STARTER, Path(directory), modules, **kwargs)

    def test_actual_starter_preserves_shared_text_for_every_module_selection(self) -> None:
        # The template is the input, not an oracle for whether its advice is good.
        # This checks that the renderer never drops/duplicates its common body.
        source = STARTER.read_text(encoding="utf-8")
        body = source.split("## Adopted Working Principles", 1)[1].split(
            "## Project Facts and Exceptions", 1)[0]
        before, rest = body.split("<!-- engineering-only:start -->", 1)
        software, after = rest.split("<!-- engineering-only:end -->", 1)
        for modules in (set(), {"workflow"}, {"agents"}, {"code"}, {"code", "poc"}):
            with self.subTest(modules=modules):
                result = self.draft(modules).split("## Adopted Working Principles", 1)[1].split(
                    "## Project Facts and Exceptions", 1)[0]
                self.assertEqual(result, before + (software if "code" in modules else "") + after)
                self.assertNotIn("engineering-only:", result)

    def test_renderer_preserves_language_and_equivalent_layout(self) -> None:
        # A real passthrough test, not an English-heading requirement.
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            template = root / "input.md"
            template.write_text(
                "# {{PROJECT_NAME}}\n共通の合意：完成物を確認する。\n"
                "<!-- engineering-only:start -->\n代码约定：按影响测试。\n"
                "<!-- engineering-only:end -->\n`{{NAVIGATION_ENTRY}}`\n",
                encoding="utf-8",
            )
            noncode = self.render(template, root, {"workflow"}, name="制作项目")
            self.assertEqual(noncode, "# 制作项目\n共通の合意：完成物を確認する。\n\n`README.md`\n")
            code = self.render(template, root, {"code"}, name="制作项目", profile="standard")
            self.assertIn("代码约定：按影响测试。", code)
            self.assertIn("`governance/PROJECT_MAP.md`", code)
            self.assertIn("共通の合意：完成物を確認する。", code)

    def test_draft_resolves_real_routes_and_does_not_leak_local_path(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for profile, route in (("core", "README.md"), ("standard", "governance/PROJECT_MAP.md")):
                with self.subTest(profile=profile):
                    text = self.render(STARTER, root, {"code"}, profile=profile)
                    self.assertIn(f"`{route}`", text)
                    self.assertNotIn("{{", text)
                    self.assertNotIn(str(root), text)
                    self.assertIn("# Example", text)

    def test_repeat_rendering_is_read_only_and_does_not_append(self) -> None:
        before = STARTER.read_bytes()
        first, second = self.draft({"code"}), self.draft({"code"})
        self.assertEqual(first, second)
        self.assertEqual(STARTER.read_bytes(), before)
        self.assertEqual(first.count("## Adopted Working Principles"), 1)
        self.assertEqual(first.count("## Routing and Boundaries"), 1)

    def test_poc_draft_uses_registered_contract_not_activation(self) -> None:
        text = self.draft({"code", "poc"})
        self.assertIn("`poc_management`", text)
        self.assertIn("`contract_path`", text)
        self.assertIn("A draft is not an activated experiment area", text)
        self.assertNotIn("{{", text)
        self.assertNotIn("`poc_management`", self.draft({"code"}))

    def validate_layer(self, text: str, second_owner: bool = False) -> str:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target = root / "skills/senmu-build-project/assets/project-governance-starter/AGENTS.template.md"
            target.parent.mkdir(parents=True)
            target.write_text(text, encoding="utf-8")
            if second_owner:
                duplicate = root / "skills/senmu-build-engineering/assets/code-quality/AGENTS.template.md"
                duplicate.parent.mkdir(parents=True)
                duplicate.write_text(text, encoding="utf-8")
            output = io.StringIO()
            with patch.object(package_validator, "ROOT", root), contextlib.redirect_stdout(output):
                package_validator.validate_project_instruction_layer()
            return output.getvalue()

    def fixture(self) -> str:
        return ("# {{PROJECT_NAME}}\n{{PROJECT_TYPE}} {{PROJECT_ROOT}}\n"
                "共通の方針。\n<!-- engineering-only:start -->\nsoftware\n"
                "<!-- engineering-only:end -->\n{{NAVIGATION_ENTRY}}\n{{POC_ENTRY}}\n")

    def test_instruction_size_and_prose_are_review_signals_not_semantic_gates(self) -> None:
        text = self.fixture() + "reviewable context\n" * 140
        self.assertGreater(len(text), package_validator.PROJECT_AGENTS_REVIEW_CHARS)
        output = self.validate_layer(text)
        self.assertIn("[REVIEW]", output)
        self.validate_layer(self.fixture().replace("共通の方針。", "Working preferences."))

    def test_instruction_validator_rejects_broken_rendering_contracts(self) -> None:
        valid = self.fixture()
        mutations = {
            "missing route": valid.replace("{{NAVIGATION_ENTRY}}", "{{MISSPELLED_ROUTE}}"),
            "missing closing marker": valid.replace("<!-- engineering-only:end -->", ""),
            "empty code block": valid.replace("\nsoftware\n", ""),
            "duplicate opening marker": valid + "<!-- engineering-only:start -->",
            "reversed markers": valid.replace("engineering-only:start", "engineering-only:temp")
                                     .replace("engineering-only:end", "engineering-only:start")
                                     .replace("engineering-only:temp", "engineering-only:end"),
            "copied peer catalog": valid + "\nsenmu-build-product\n",
        }
        for case, text in mutations.items():
            with self.subTest(case=case), self.assertRaises(SystemExit):
                self.validate_layer(text)
        with self.assertRaises(SystemExit):
            self.validate_layer(valid, second_owner=True)


if __name__ == "__main__":
    unittest.main()
