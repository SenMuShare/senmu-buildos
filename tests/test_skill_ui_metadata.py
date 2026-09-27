"""Validate the official authoring bounds without changing Skill triggers."""
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


class SkillUIMetadataTests(unittest.TestCase):
    def test_each_short_description_has_25_to_64_characters(self):
        paths = sorted((ROOT / 'skills').glob('*/agents/openai.yaml'))
        self.assertEqual(len(paths), 8)
        for path in paths:
            with self.subTest(skill=path.parent.parent.name):
                match = re.search(r'^  short_description:\s*"([^"\n]+)"\s*$', path.read_text(), re.MULTILINE)
                self.assertIsNotNone(match)
                self.assertGreaterEqual(len(match.group(1)), 25)
                self.assertLessEqual(len(match.group(1)), 64)

    def test_invocation_prompt_resolves_its_own_skill(self):
        for path in (ROOT / 'skills').glob('*/agents/openai.yaml'):
            with self.subTest(skill=path.parent.parent.name):
                match = re.search(r'^  default_prompt: (.+)$', path.read_text(), re.MULTILINE)
                self.assertIsNotNone(match)
                prompt = json.loads(match.group(1))
                self.assertIsInstance(prompt, str)
                self.assertIn('$' + path.parent.parent.name, prompt)


if __name__ == '__main__':
    unittest.main()
