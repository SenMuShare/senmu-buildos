#!/usr/bin/env python3
"""Protect the packaged reference topology, not natural-language phrasing.

Semantic ownership and authority remain source-review subjects in
behavior/core-working-principles.md; these checks do not grade model behavior.
"""
from __future__ import annotations

from contextlib import contextmanager
import json
import re
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from validate_package import (  # noqa: E402
    EXPECTED_SKILLS,
    REFERENCE_OWNERS,
    extract_markdown_link_targets,
    parse_skill_name,
    reference_graph,
)

OWNER = "senmu-build-engineering"
DOMAIN_REFERENCES = (
    "frontend-engineering-contracts-and-validation.md",
    "backend-services-and-data-contracts.md",
)


@contextmanager
def copied_surface():
    """Mutate only a disposable copy of the actual packaged Skill surface."""
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        shutil.copytree(ROOT / "skills", root / "skills")
        for adapter in (".codex-plugin", ".claude-plugin", ".zcode-plugin"):
            shutil.copytree(ROOT / adapter, root / adapter)
        yield root


class EngineeringDomainReferenceTest(unittest.TestCase):
    def assert_domain_routes(self, root: Path) -> None:
        skill = root / "skills" / OWNER
        references = [skill / "references" / name for name in DOMAIN_REFERENCES]
        for reference in references:
            self.assertTrue(reference.is_file(), f"missing reference: {reference.name}")
            self.assertEqual(REFERENCE_OWNERS[reference.name], OWNER)
            owners = set((root / "skills").glob(f"*/references/**/{reference.name}"))
            self.assertEqual(owners, {reference}, f"duplicate/moved owner: {reference.name}")
        graph = reference_graph(skill, references)
        self.assertEqual(
            graph[(skill / "SKILL.md").resolve()],
            {reference.resolve() for reference in references},
            "both domain references need real links from the Engineering entry",
        )

    def assert_peer_layout(self, root: Path) -> None:
        skills = root / "skills"
        expected = {skills / name / "SKILL.md" for name in EXPECTED_SKILLS}
        self.assertEqual(set(skills.rglob("SKILL.md")), expected,
                         "packaged Skills must stay at the peer level")
        for entry in expected:
            self.assertEqual(parse_skill_name(entry.read_text(encoding="utf-8")), entry.parent.name)
        for adapter in (".codex-plugin", ".claude-plugin", ".zcode-plugin"):
            manifest = json.loads((root / adapter / "plugin.json").read_text(encoding="utf-8"))
            # Claude currently uses the conventional directory; other manifests
            # explicitly select it. This checks our package, not all host schemas.
            route = manifest.get("skills", "./skills/")
            self.assertIsInstance(route, str)
            self.assertEqual((root / route).resolve(), skills.resolve())

    def test_entry_routes_frontend_and_backend_as_references(self):
        self.assert_domain_routes(ROOT)

    def test_specialist_skills_remain_peer_capabilities(self):
        self.assert_peer_layout(ROOT)

    def test_backend_routes_to_owned_security_guidance(self):
        skill = ROOT / "skills" / OWNER
        backend = skill / "references" / DOMAIN_REFERENCES[1]
        security = skill / "references/application-security-and-abuse.md"
        self.assertTrue(security.is_file())
        self.assertEqual(REFERENCE_OWNERS[security.name], OWNER)
        graph = reference_graph(skill, [backend, security])
        self.assertIn(security.resolve(), graph[backend.resolve()])

    def test_editorial_rewrite_does_not_change_structural_contract(self):
        with copied_surface() as root:
            entry = root / "skills" / OWNER / "SKILL.md"
            text = entry.read_text(encoding="utf-8")
            frontmatter = text[:text.index("\n---\n", 4) + len("\n---\n")]
            links = extract_markdown_link_targets(text)
            # Deliberately replace prose and link labels. The test demonstrates
            # structural independence, NOT semantic equivalence of arbitrary text.
            entry.write_text(frontmatter + "\n# Reference navigation fixture\n\n" +
                             "\n".join(f"[Resource {i}]({target})" for i, target in enumerate(links)) + "\n",
                             encoding="utf-8")
            self.assert_domain_routes(root)
            self.assert_peer_layout(root)

    def test_filename_mention_or_code_example_is_not_a_route(self):
        name = DOMAIN_REFERENCES[0]
        for replacement in (name, f"```md\n[Example](references/{name})\n```"):
            with self.subTest(replacement=replacement), copied_surface() as root:
                entry = root / "skills" / OWNER / "SKILL.md"
                text = entry.read_text(encoding="utf-8")
                pattern = r"\[[^\]]+\]\(references/" + re.escape(name) + r"\)"
                changed, count = re.subn(pattern, lambda match: replacement, text)
                self.assertGreater(count, 0, "fixture must alter an existing link")
                entry.write_text(changed, encoding="utf-8")
                with self.assertRaisesRegex(AssertionError, "real links"):
                    self.assert_domain_routes(root)

    def test_missing_reference_is_rejected(self):
        with copied_surface() as root:
            (root / "skills" / OWNER / "references" / DOMAIN_REFERENCES[0]).unlink()
            with self.assertRaisesRegex(AssertionError, "missing reference"):
                self.assert_domain_routes(root)

    def test_duplicate_reference_owner_is_rejected(self):
        with copied_surface() as root:
            source = root / "skills" / OWNER / "references" / DOMAIN_REFERENCES[0]
            shutil.copy2(source, root / "skills/senmu-build-design/references" / source.name)
            with self.assertRaisesRegex(AssertionError, "duplicate/moved owner"):
                self.assert_domain_routes(root)

    def test_nested_skill_is_rejected_even_with_unchanged_prose(self):
        with copied_surface() as root:
            extra = root / "skills" / OWNER / "frontend/SKILL.md"
            extra.parent.mkdir()
            extra.write_text("---\nname: frontend\ndescription: Nested fixture.\n---\n", encoding="utf-8")
            with self.assertRaisesRegex(AssertionError, "peer level"):
                self.assert_peer_layout(root)

    def test_manifest_cannot_redirect_to_nested_skill_directory(self):
        with copied_surface() as root:
            path = root / ".codex-plugin/plugin.json"
            manifest = json.loads(path.read_text(encoding="utf-8"))
            manifest["skills"] = f"./skills/{OWNER}/"
            path.write_text(json.dumps(manifest), encoding="utf-8")
            with self.assertRaises(AssertionError):
                self.assert_peer_layout(root)


if __name__ == "__main__":
    unittest.main()
