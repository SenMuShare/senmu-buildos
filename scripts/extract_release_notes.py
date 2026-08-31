#!/usr/bin/env python3
"""Extract one concise, user-facing GitHub Release body."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
VERSION_HEADING = re.compile(r"^## \[(\d+\.\d+\.\d+)\](?: - \d{4}-\d{2}-\d{2})?$")
REQUIRED_SECTIONS = ("主要更新", "修复问题")


class ReleaseNotesError(ValueError):
    """Raised when user-facing release notes are missing or malformed."""


def extract_release_notes(text: str, version: str) -> str:
    """Return the two user-facing sections for one version."""
    lines = text.splitlines()
    start: int | None = None
    end = len(lines)
    for index, line in enumerate(lines):
        match = VERSION_HEADING.fullmatch(line)
        if not match:
            continue
        if start is not None:
            end = index
            break
        if match.group(1) == version:
            start = index + 1
    if start is None:
        raise ReleaseNotesError(f"RELEASE_NOTES.md has no section for {version}")

    body = lines[start:end]
    headings = [line.removeprefix("### ") for line in body if line.startswith("### ")]
    if tuple(headings) != REQUIRED_SECTIONS:
        raise ReleaseNotesError("release notes must contain only 主要更新 and 修复问题, in that order")

    rendered: list[str] = []
    for section in REQUIRED_SECTIONS:
        heading = f"### {section}"
        section_start = body.index(heading) + 1
        section_end = next(
            (index for index in range(section_start, len(body)) if body[index].startswith("### ")),
            len(body),
        )
        section_lines = body[section_start:section_end]
        bullets = [line for line in section_lines if line.startswith("- ") and line[2:].strip()]
        if not bullets:
            raise ReleaseNotesError(f"{section} must contain at least one concise bullet")
        rendered.extend((f"## {section}", "", *bullets, ""))
    return "\n".join(rendered).strip() + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--version", required=True, help="semantic version without the v prefix")
    parser.add_argument("--source", type=Path, default=ROOT / "RELEASE_NOTES.md")
    args = parser.parse_args()
    try:
        print(extract_release_notes(args.source.read_text(encoding="utf-8"), args.version), end="")
    except (OSError, ReleaseNotesError) as exc:
        raise SystemExit(f"[ERROR] {exc}") from exc


if __name__ == "__main__":
    main()
