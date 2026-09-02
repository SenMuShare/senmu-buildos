from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from validate_package import (
    extract_markdown_link_targets,
    local_markdown_target_error,
)


class MarkdownLinkParserTests(unittest.TestCase):
    def test_balanced_parentheses_angle_paths_and_fences(self) -> None:
        targets = extract_markdown_link_targets(
            """
[Parentheses](docs/design(v2).md#contract)
[Spaces](<docs/design notes.md>)

```markdown
[Example only](missing.md)
```

[External](https://example.com/spec) and [anchor](#section)
"""
        )

        self.assertEqual(
            targets,
            [
                "docs/design(v2).md#contract",
                "docs/design notes.md",
                "https://example.com/spec",
                "#section",
            ],
        )

    def test_local_resolution_distinguishes_missing_and_outside(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_root:
            root = Path(temporary_root)
            source = root / "docs/index.md"
            source.parent.mkdir()
            source.write_text("# Index\n", encoding="utf-8")
            target = root / "docs/design notes(v2).md"
            target.write_text("# Design\n", encoding="utf-8")

            self.assertIsNone(
                local_markdown_target_error(
                    source, "design%20notes(v2).md#contract", root
                )
            )
            self.assertIn(
                "broken local Markdown link",
                local_markdown_target_error(source, "missing.md", root) or "",
            )
            self.assertIn(
                "escapes the authority root",
                local_markdown_target_error(source, "../../outside.md", root) or "",
            )
            self.assertIsNone(
                local_markdown_target_error(source, "mailto:test@example.com", root)
            )


if __name__ == "__main__":
    unittest.main()
