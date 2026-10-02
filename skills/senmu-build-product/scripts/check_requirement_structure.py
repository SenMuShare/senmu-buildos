#!/usr/bin/env python3
"""Read-only structural check for BuildOS's default per-feature four-part PRD.

Use only for documents adopting this format, not arbitrary user templates.
This does not verify business meaning, exception coverage or asset custody.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

SECTIONS = ("1. 需求描述", "2. 功能描述", "3. 功能逻辑", "4. 前端交互描述")
FEATURE = re.compile(r"^(?:FUN|CAP)-[A-Za-z0-9_-]+(?:\s|$)")
VERSION = re.compile(r"^\s*(?:>\s*)?需求对应版本号[：:]\s*(.*?)\s*$")
UNKNOWN = re.compile(r"待确认|待定|未确定|待规划|未排期|TBD|UNKNOWN|\{\{|\$\{[^}]+\}|<[^>]+>|[xX]\.[xX]", re.I)


def visible_lines(text: str) -> list[str]:
    """Preserve line positions while ignoring comments and fenced examples."""
    text = re.sub(r"<!--[\s\S]*?-->", lambda m: "\n" * m.group().count("\n"), text)
    result: list[str] = []
    fence_char, fence_length = "", 0
    for line in text.splitlines():
        fence = re.match(r"^ {0,3}(`{3,}|~{3,})(.*)$", line)
        if fence_char:
            if fence and fence.group(1)[0] == fence_char and len(fence.group(1)) >= fence_length and not fence.group(2).strip():
                fence_char, fence_length = "", 0
            result.append("")
        elif fence:
            fence_char, fence_length = fence.group(1)[0], len(fence.group(1))
            result.append("")
        else:
            result.append(line)
    return result


def has_content(line: str) -> bool:
    """Ignore empty Markdown list/quote prefixes, retaining actual item text."""
    text = line.strip()
    while text:
        remainder = re.sub(r"^(?:>\s*|(?:[-+*]|[0-9]+[.)])(?:\s+|$)|\[[ xX]\](?:\s+|$))", "", text, count=1).strip()
        if remainder == text:
            break
        text = remainder
    return re.fullmatch(r"[\s>*_`.-]*", text) is None


def check(text: str, *, draft: bool = False) -> dict[str, object]:
    lines = visible_lines(text)
    headings: list[dict[str, object]] = []
    stack: list[int] = []
    for number, line in enumerate(lines):
        match = re.match(r"^ {0,3}(#{1,6})\s+(.+?)\s*#*\s*$", line)
        if not match:
            continue
        level, title = len(match.group(1)), match.group(2).strip()
        while stack and int(headings[stack[-1]]["level"]) >= level:
            headings[stack.pop()]["end"] = number
        headings.append({"line": number, "end": len(lines), "level": level,
                         "title": title, "parent": stack[-1] if stack else None})
        stack.append(len(headings) - 1)
    children: dict[int, list[int]] = {}
    for index, heading in enumerate(headings):
        parent = heading["parent"]
        if isinstance(parent, int):
            children.setdefault(parent, []).append(index)
    features = {i for i, h in enumerate(headings) if FEATURE.match(str(h["title"]))}
    for index, heading in enumerate(headings):
        child_ids = children.get(index, [])
        # Metadata belongs only to this heading's preamble, never its descendants.
        stop = int(headings[child_ids[0]]["line"]) if child_ids else int(heading["end"])
        has_version = any(VERSION.match(line) for line in lines[int(heading["line"]) + 1:stop])
        if has_version or any(headings[child]["title"] in SECTIONS for child in child_ids):
            features.add(index)
    errors: list[str] = []
    if not features:
        errors.append("No feature blocks found; use the adopted four-part template, not a whole-document summary.")
    for index in sorted(features):
        feature = headings[index]
        label = f"line {int(feature['line']) + 1}: {feature['title']}"
        child_ids = children.get(index, [])
        titles = [headings[child]["title"] for child in child_ids]
        if titles != list(SECTIONS):
            errors.append(f"{label}: require exactly four ordered sections: {', '.join(SECTIONS)}")
        stop = int(headings[child_ids[0]]["line"]) if child_ids else int(feature["end"])
        versions = [m.group(1).strip("`* ") for line in lines[int(feature["line"]) + 1:stop]
                    if (m := VERSION.match(line))]
        if len(versions) != 1 or not versions[0]:
            errors.append(f"{label}: require one nonempty 需求对应版本号 before the four sections")
        elif not draft and UNKNOWN.search(versions[0]):
            errors.append(f"{label}: unresolved version is allowed only in a draft")
        for child in child_ids:
            section = headings[child]
            if section["title"] not in SECTIONS:
                continue
            body = [line for line in lines[int(section["line"]) + 1:int(section["end"])]
                    if line.strip() and not re.match(r"^\s*#{1,6}\s", line)]
            if not any(has_content(line) for line in body):
                errors.append(f"{label}: {section['title']} has no content; explain genuine non-applicability")
    return {"status": "fail" if errors else "pass", "scope": "structure_only",
            "features": len(features), "errors": errors,
            "agentHint": "修复结构问题；仍需核对需求语义、前后端一致性、异常及原型归档关联。结构通过不代表需求已确认或已验收。"}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--document", required=True, type=Path)
    parser.add_argument("--draft", action="store_true", help="allow an explicitly unresolved version in a draft")
    args = parser.parse_args()
    try:
        result = check(args.document.read_text(encoding="utf-8"), draft=args.draft)
    except (OSError, UnicodeError) as exc:
        result = {"status": "fail", "scope": "structure_only", "features": 0,
                  "errors": [f"Cannot read document: {exc}"],
                  "agentHint": "提供可读的需求文档路径；读取失败不代表文档已检查。"}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 1 if result["status"] == "fail" else 0


if __name__ == "__main__":
    raise SystemExit(main())
