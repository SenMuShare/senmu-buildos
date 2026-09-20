"""Exercise the real structural validator; no live-model quality claims."""
from __future__ import annotations

import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VALIDATOR = ROOT / "skills/senmu-build-workflow/scripts/validate_agents.py"
ROLES = (
    "role", "mission", "scope", "tasks", "input", "output", "tools",
    "workflow", "constraints", "quality", "exceptions", "continuity",
)
HEADINGS = (
    "Role", "Mission and Outcome", "Scope", "Tasks and Success", "Input Contract",
    "Output Contract", "Tools and Invocation", "Workflow and Decisions", "Constraints",
    "Quality and Acceptance", "Exceptions and Handoff", "Version and Continuity",
)


def definition(marked: bool = False, merged: bool = False) -> str:
    text = "# Example\n\n> Agent Key: `example`\n> Agent Version: `1.0.0`\n> Status: `active`\n\n"
    for key, heading in zip(ROLES, HEADINGS):
        if merged and key == "output":
            continue
        text += f"## {'節 ' + str(ROLES.index(key) + 1) if marked else heading}\n"
        if marked:
            text += f"<!-- agent-section: {key} -->\n"
        if merged and key == "input":
            text += "<!-- agent-section: output -->\n"
        text += "確認済みの契約。\n\n"
    return text


class AgentLanguageContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "project"
        self.agent = self.root / "agents/example/AGENT.md"
        self.agent.parent.mkdir(parents=True)
        self.register = self.root / "agents/AGENT_REGISTER.md"
        self.register.write_text(
            "# Agents\n\n| Agent Key | Name | Version | Status | Path | Owner | Runtime |\n"
            "| --- | --- | --- | --- | --- | --- | --- |\n"
            "| example | Example | 1.0.0 | active | agents/example/AGENT.md | Team | test |\n",
            encoding="utf-8",
        )

    def check_definition(self, text: str, valid: bool, strict: bool = True) -> str:
        self.agent.write_text(text, encoding="utf-8")
        before = (self.agent.read_bytes(), self.register.read_bytes())
        result = subprocess.run(
            ["python3", str(VALIDATOR), "--root", str(self.root), *(["--strict"] if strict else [])],
            capture_output=True, text=True, check=False,
        )
        self.assertEqual(result.returncode == 0, valid, result.stdout + result.stderr)
        self.assertEqual((self.agent.read_bytes(), self.register.read_bytes()), before)
        return result.stdout

    def test_english_headings_without_markers(self) -> None:
        self.check_definition(definition(), True)

    def test_japanese_headings_with_stable_roles(self) -> None:
        self.check_definition(definition(marked=True), True)

    def test_merged_sections_preserve_two_logical_contracts(self) -> None:
        self.check_definition(definition(marked=True, merged=True), True)

    def test_missing_role_is_rejected_regardless_of_language(self) -> None:
        self.check_definition(definition(marked=True).replace("<!-- agent-section: input -->\n", ""), False)

    def test_fenced_examples_do_not_supply_missing_sections(self) -> None:
        text = definition(marked=True).replace("<!-- agent-section: input -->\n", "")
        text += "```md\n## Input Contract\n<!-- agent-section: input -->\n```\n"
        self.check_definition(text, False)

    def test_tilde_examples_also_do_not_supply_missing_sections(self) -> None:
        text = definition(marked=True).replace("<!-- agent-section: output -->\n", "")
        self.check_definition(text + "~~~md\n## Output Contract\n~~~\n", False)

    def test_unknown_marker_is_not_silently_accepted(self) -> None:
        self.check_definition(definition(marked=True).replace("agent-section: input", "agent-section: invented"), False)

    def test_duplicate_roles_in_different_sections_are_rejected(self) -> None:
        self.check_definition(definition() + "## Input Contract\nConflicting second owner.\n", False)

    def test_marker_and_matching_heading_do_not_count_as_duplicates(self) -> None:
        self.check_definition(definition().replace("## Input Contract", "## Input Contract\n<!-- agent-section: input -->"), True)

    def test_conflicting_legacy_and_english_status_metadata_is_rejected(self) -> None:
        self.check_definition(definition().replace("> Status: `active`", "> Status: `active`\n> 状态: `retired`"), False)

    def test_same_legacy_status_is_compatible(self) -> None:
        self.check_definition(definition().replace("> Status: `active`", "> 状态: `active`"), True)

    def test_strict_placeholder_check_survives_marker_support(self) -> None:
        self.check_definition(definition(marked=True).replace("確認済みの契約。", "<unconfirmed>", 1), False)

    def test_code_sample_cannot_supply_required_metadata(self) -> None:
        text = definition().replace("> Agent Key: `example`\n", "")
        self.check_definition(text + "```md\n> Agent Key: `example`\n```\n", False)

    def test_symlink_definition_cannot_escape_project(self) -> None:
        outside = Path(self.temp.name) / "outside.md"
        outside.write_text(definition(), encoding="utf-8")
        self.agent.symlink_to(outside)
        result = subprocess.run(["python3", str(VALIDATOR), "--root", str(self.root)], capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("越出项目根", result.stdout)
        self.assertEqual(outside.read_text(encoding="utf-8"), definition())


    def test_legal_xml_html_and_code_delimiters_pass_strict(self) -> None:
        for sample in (
            '<result>approved-category</result>',
            '<result category="批准"><item /></result>',
            '<div class="result"><br/>Approved</div>',
            '```xml\n<result>approved-category</result>\n```',
            '~~~html\n<div>Approved</div>\n~~~',
            '<unconfirmed>literal output</unconfirmed>',
            '<confirm>outer<confirm>inner</confirm></confirm>',
            '<confirm value="literal"/>',
            'Map<Key, Value>',
            '<!-- ordinary comment -->',
        ):
            with self.subTest(sample=sample):
                self.check_definition(definition() + '\n' + sample, True)

    def test_declared_slots_fail_including_fenced_examples(self) -> None:
        for slot in (
            '<待确认>', '<待确认或不适用>', '<confirm>', '<unconfirmed>',
            '<confirmed owner>', '<Agent name>', '<agent-key>',
            '[[BUILDOS_TODO: output contract]]', '[[BUILDOS_TODO: ]]',
            '```xml\n<result>[[BUILDOS_TODO: result]]</result>\n```',
            '~~~md\n<待确认>\n~~~',
            '<confirm>literal</confirm>\n<confirm>',
        ):
            with self.subTest(slot=slot):
                output = self.check_definition(definition() + '\n' + slot, False)
                self.assertIn('未校准占位符', output)

    def test_runtime_variables_are_not_authoring_slots(self) -> None:
        self.check_definition(definition() + '\n{{user_text}} ${locale} {category}\n', True)

    def test_same_label_identity_conflicts_fail_in_both_modes(self) -> None:
        for label, value in (('Agent Key','other'), ('Agent Version','2.0.0'), ('Status','retired'), ('状态','retired')):
            for strict in (False, True):
                with self.subTest(label=label, strict=strict):
                    output = self.check_definition(definition() + f'\n> {label}: `{value}`\n', False, strict)
                    self.assertIn('Conflicting', output)

    def test_later_status_alias_conflict_cannot_hide_behind_matching_first_value(self) -> None:
        text = definition() + '\n> 状态: `active`\n> 状态: `retired`\n'
        self.check_definition(text, False)

    def test_identical_repeated_values_and_aliases_are_unambiguous(self) -> None:
        for label, value in (('Agent Key','example'), ('Agent Version','1.0.0'), ('Status','active'), ('状态','active')):
            with self.subTest(label=label):
                self.check_definition(definition() + f'\n> {label}: `{value}`\n', True)

    def test_empty_later_identity_is_rejected(self) -> None:
        for label in ('Agent Key','Agent Version','Status','状态'):
            for empty in ('', '  ', '``'):
                with self.subTest(label=label, empty=empty):
                    self.check_definition(definition() + f'\n> {label}: {empty}\n', False)

    def test_empty_first_value_does_not_consume_following_lines(self) -> None:
        self.check_definition(definition().replace('> Agent Key: `example`', '> Agent Key:\n> Agent Key: `example`'), False)

    def test_fenced_conflicting_metadata_is_only_an_example(self) -> None:
        sample = '\n> Agent Key: `other`\n> Agent Version: `2.0.0`\n> Status: `retired`\n'
        for fence in ('```','~~~'):
            with self.subTest(fence=fence):
                self.check_definition(definition() + '\n'+fence+'md'+sample+fence+'\n', True)

    def test_unfenced_conflict_after_a_fenced_example_is_detected(self) -> None:
        self.check_definition(definition() + '\n```md\n> Status: `active`\n```\n> Status: `retired`\n', False)

    def test_crlf_and_fullwidth_metadata_remain_compatible(self) -> None:
        text = definition().replace('> Status:', '> 状态：').replace('\n', '\r\n')
        self.check_definition(text, True)

    def test_conflicts_fail_when_the_wrong_value_comes_first(self) -> None:
        text = definition().replace('> Status: `active`', '> Status: `retired`\n> Status: `active`')
        self.check_definition(text, False)

    def test_registered_draft_still_reports_unfilled_new_starter(self) -> None:
        template = (ROOT / 'skills/senmu-build-workflow/assets/agent-governance/AGENT.template.md').read_text(encoding='utf-8')
        text = template.replace('[[BUILDOS_TODO: agent-key]]', 'example').replace('`0.1.0`', '`1.0.0`').replace('`draft`', '`active`')
        output = self.check_definition(text, False)
        self.assertIn('BUILDOS_TODO', output)

    def test_structure_only_mode_keeps_draft_placeholder_policy(self) -> None:
        self.check_definition(definition() + '\n[[BUILDOS_TODO: contract]]\n', True, strict=False)


if __name__ == "__main__":
    unittest.main()
