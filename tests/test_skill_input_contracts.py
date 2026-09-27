"""Skill metadata and real reference/template input contracts, not model behavior."""
import contextlib
import io
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import validate_package as validator


class SkillInputContractTests(unittest.TestCase):
    def document(self, fields):
        return "---\n" + fields + "\n---\n# Instructions\n"

    def test_required_scalar_does_not_consume_following_field(self):
        for value in ("", "   ", "\"\"", "''"):
            with self.subTest(value=value), self.assertRaises(SystemExit):
                validator.parse_skill_description(self.document(
                    "name: example\ndescription: " + value + "\nlicense: MIT"))
        with self.assertRaises(SystemExit):
            validator.parse_skill_name(self.document("name:\ndescription: Example"))

    def test_duplicate_identity_or_trigger_is_not_silently_selected(self):
        for key, parser in (("name", validator.parse_skill_name),
                            ("description", validator.parse_skill_description)):
            with self.subTest(key=key), self.assertRaises(SystemExit):
                parser(self.document(f"{key}: first\n{key}: second"))

    def test_simple_scalar_values_remain_compatible(self):
        for value in ('Example scope.', '"Example scope."', "'Example scope.'"):
            self.assertEqual(validator.parse_skill_description(
                self.document("name: example\ndescription: " + value)), "Example scope.")
        self.assertEqual(validator.parse_skill_name(self.document(
            'name: "example-skill"\ndescription: Example')), 'example-skill')

    def test_fenced_examples_are_not_effective_reference_routes(self):
        with tempfile.TemporaryDirectory() as directory:
            skill=Path(directory); refs=skill/'references'; refs.mkdir()
            leaf=refs/'rules.md'; leaf.write_text('# Rules\n',encoding='utf-8')
            entry=skill/'SKILL.md'
            for fence in ('```', '~~~'):
                with self.subTest(fence=fence):
                    entry.write_text(f'{fence}md\n[Example](references/rules.md)\n{fence}\n',encoding='utf-8')
                    graph=validator.reference_graph(skill,[leaf])
                    self.assertEqual(validator.reachable_references(entry,graph),set())
            entry.write_text('[Actual](<references/rules.md#section> "Context")\n',encoding='utf-8')
            graph=validator.reference_graph(skill,[leaf])
            self.assertEqual(validator.reachable_references(entry,graph),{leaf.resolve()})

    def test_encoded_link_and_title_resolve_consistently(self):
        with tempfile.TemporaryDirectory() as directory:
            skill=Path(directory); refs=skill/'references'; refs.mkdir()
            leaf=refs/'rules.md'; leaf.write_text('# Rules\n',encoding='utf-8')
            entry=skill/'SKILL.md'
            entry.write_text('[Actual](references/%72ules.md "Read as needed")\n',encoding='utf-8')
            graph=validator.reference_graph(skill,[leaf])
            self.assertEqual(validator.reachable_references(entry,graph),{leaf.resolve()})

    def test_unknown_renderer_placeholder_is_rejected(self):
        original=(ROOT/'skills/senmu-build-project/assets/project-governance-starter/AGENTS.template.md').read_text(encoding='utf-8')
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            path=root/'skills/senmu-build-project/assets/project-governance-starter/AGENTS.template.md'
            path.parent.mkdir(parents=True)
            path.write_text(original+'\n{{UNKNOWN_ROUTE}}\n',encoding='utf-8')
            with patch.object(validator,'ROOT',root), contextlib.redirect_stdout(io.StringIO()):
                with self.assertRaises(SystemExit):
                    validator.validate_project_instruction_layer()


if __name__ == '__main__':
    unittest.main()
