#!/usr/bin/env python3
"""Fail when a public source tree contains private project-state boundaries."""

from __future__ import annotations

import argparse
import re
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
FORBIDDEN_PREFIXES = (
    Path(".senmu-buildos"),
    Path("governance/tasks"),
    Path("governance/logs"),
    Path("evidence/releases"),
    Path("evidence/reviews"),
)
TEXT_SUFFIXES = {".md", ".json", ".yaml", ".yml", ".py", ".js", ".sh", ".env", ".txt"}
ABSOLUTE_PRIVATE_PATH = re.compile(
    r"(?:/Users/[A-Za-z0-9._-]+/|/home/[A-Za-z0-9._-]+/|[A-Za-z]:\\Users\\[A-Za-z0-9._-]+\\)"
)


def tracked_files(root: Path) -> list[Path]:
    result = subprocess.run(
        ["git", "-C", str(root), "ls-files", "-z"],
        check=False,
        capture_output=True,
    )
    if result.returncode == 0:
        return [Path(item.decode("utf-8")) for item in result.stdout.split(b"\0") if item]
    return sorted(path.relative_to(root) for path in root.rglob("*") if path.is_file() and ".git" not in path.parts)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--deny-term", action="append", default=[])
    args = parser.parse_args()
    root = args.root.expanduser().resolve()
    errors = []
    files = tracked_files(root)
    for relative in files:
        if any(relative == prefix or prefix in relative.parents for prefix in FORBIDDEN_PREFIXES):
            errors.append(f"禁止公开的内部 owner：{relative.as_posix()}")
            continue
        path = root / relative
        if path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        if ABSOLUTE_PRIVATE_PATH.search(text):
            errors.append(f"包含本机绝对路径：{relative.as_posix()}")
        for term in args.deny_term:
            if term and term in text:
                errors.append(f"包含私有实例标识 {term!r}：{relative.as_posix()}")
    if errors:
        raise SystemExit("[ERROR] 公开源码面校验失败：\n" + "\n".join(errors))
    print(f"[OK] public source surface is clean: {len(files)} tracked files")


if __name__ == "__main__":
    main()
