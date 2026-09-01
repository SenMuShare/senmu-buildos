#!/usr/bin/env python3
"""Verify recursive Skill reference discovery and progressive route accounting."""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from validate_package import (  # noqa: E402
    REFERENCE_OWNERS,
    largest_reference_chain,
    reachable_references,
    reference_graph,
)


class PackageReferenceRoutingTest(unittest.TestCase):
    def test_design_library_resources_have_explicit_owner(self) -> None:
        for relative in (
            "design-library/INDEX.md",
            "design-library/页面结构与视觉方向.md",
            "design-library/组件设计模式.md",
        ):
            self.assertEqual(REFERENCE_OWNERS[relative], "senmu-build-design")

    def test_nested_references_are_reachable_and_counted_as_a_chain(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            skill = Path(directory) / "example-skill"
            nested = skill / "references" / "library"
            nested.mkdir(parents=True)
            entry = skill / "SKILL.md"
            index = nested / "INDEX.md"
            leaf = nested / "leaf.md"
            entry.write_text("读取 [索引](references/library/INDEX.md)。", encoding="utf-8")
            index.write_text("读取 [条目](leaf.md)。", encoding="utf-8")
            leaf.write_text("条目。", encoding="utf-8")

            references = [index, leaf]
            graph = reference_graph(skill, references)
            self.assertEqual(reachable_references(entry, graph), {index.resolve(), leaf.resolve()})

            units = {entry.resolve(): 10, index.resolve(): 20, leaf.resolve(): 30}
            total, path = largest_reference_chain(entry, graph, units)
            self.assertEqual(total, 60)
            self.assertEqual(path, [entry.resolve(), index.resolve(), leaf.resolve()])

    def test_unlinked_nested_reference_is_not_reachable(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            skill = Path(directory) / "example-skill"
            references_root = skill / "references"
            references_root.mkdir(parents=True)
            entry = skill / "SKILL.md"
            hidden = references_root / "hidden.md"
            entry.write_text("没有 reference 路由。", encoding="utf-8")
            hidden.write_text("隐藏内容。", encoding="utf-8")

            graph = reference_graph(skill, [hidden])
            self.assertNotIn(hidden.resolve(), reachable_references(entry, graph))

    def test_reference_routing_cycle_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            skill = Path(directory) / "example-skill"
            references_root = skill / "references"
            references_root.mkdir(parents=True)
            entry = skill / "SKILL.md"
            first = references_root / "first.md"
            second = references_root / "second.md"
            entry.write_text("读取 [一](references/first.md)。", encoding="utf-8")
            first.write_text("读取 [二](second.md)。", encoding="utf-8")
            second.write_text("返回 [一](first.md)。", encoding="utf-8")

            graph = reference_graph(skill, [first, second])
            units = {entry.resolve(): 10, first.resolve(): 20, second.resolve(): 30}
            with self.assertRaisesRegex(ValueError, "routing cycle"):
                largest_reference_chain(entry, graph, units)


if __name__ == "__main__":
    unittest.main()
