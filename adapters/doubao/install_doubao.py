#!/usr/bin/env python3
"""Install Senmu BuildOS into a Doubao workspace as user skills.

Copies the seven shared skills from skills/ and the Doubao kernel bootstrap
skill from adapters/doubao/kernel/, stripping Codex-only metadata, then writes
an install identity file. Deterministic and idempotent; only writes under the
target .user_skills directory.

Usage:
    python3 adapters/doubao/install_doubao.py --dry-run
    python3 adapters/doubao/install_doubao.py                 # auto-detect Doubao .user_skills
    python3 adapters/doubao/install_doubao.py --target <dir>  # explicit target
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent  # senmu-buildos-internal
KERNEL_SOURCE = ROOT / "adapters" / "doubao" / "kernel"
SKILLS_SOURCE = ROOT / "skills"
KERNEL_SKILL_NAME = "senmu-build-kernel"
INSTALL_IDENTITY_NAME = ".senmu-buildos-install.json"

DOUBAO_SKILL_NAMES = [
    "senmu-build-project",
    "senmu-build-product",
    "senmu-build-workflow",
    "senmu-build-engineering",
    "senmu-build-delivery",
    "senmu-build-assurance",
    "senmu-build-learning",
]

# Harness-specific files/folders that must not be copied into Doubao.
EXCLUDED_RELATIVE_NAMES = {"agents", "__pycache__"}


def default_user_skills() -> Path:
    """Common Doubao .user_skills locations across macOS / Linux / Windows."""
    home = Path.home()
    candidates = [
        home / "Library/Application Support/Doubao/Default/.doubao/agent_mode/workspace/.user_skills",
        home / ".doubao/agent_mode/workspace/.user_skills",
        home / "Library/Application Support/Doubao/workspace/.user_skills",
        home / ".config/Doubao/workspace/.user_skills",
        home / "workspace/.user_skills",
    ]
    if sys.platform.startswith("win"):
        candidates.insert(0, Path(os.environ.get("USERPROFILE", str(home))) / "Doubao/workspace/.user_skills")
    for candidate in candidates:
        if candidate.is_dir():
            return candidate
    return candidates[0]


def version() -> str:
    version_path = ROOT / "VERSION"
    if version_path.is_file():
        return version_path.read_text(encoding="utf-8").strip()
    return "unknown"


def source_commit() -> str:
    try:
        return subprocess.check_output(
            ["git", "-C", str(ROOT), "rev-parse", "HEAD"], text=True
        ).strip()
    except Exception:
        return "unknown"


def _ignore_harness_specific(directory: str, names: list[str]) -> set[str]:
    return {name for name in names if name in EXCLUDED_RELATIVE_NAMES}


def copy_tree(src: Path, dst: Path) -> None:
    dst.mkdir(parents=True, exist_ok=True)
    shutil.copytree(
        src,
        dst,
        dirs_exist_ok=True,
        ignore=_ignore_harness_specific,
    )


def install(target: Path, dry_run: bool) -> list[str]:
    installed: list[str] = []

    def place(name: str, src: Path) -> None:
        if not (src / "SKILL.md").is_file():
            raise SystemExit(f"[ERROR] missing SKILL.md source: {src}")
        dst = target / name
        if dry_run:
            installed.append(name)
            return
        if dst.exists():
            shutil.rmtree(dst)
        copy_tree(src, dst)
        installed.append(name)

    for name in DOUBAO_SKILL_NAMES:
        place(name, SKILLS_SOURCE / name)
    place(KERNEL_SKILL_NAME, KERNEL_SOURCE)

    identity = {
        "adapter": "doubao",
        "project": "Senmu BuildOS",
        "version": version(),
        "source_commit": source_commit(),
        "installed_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "skills": DOUBAO_SKILL_NAMES + [KERNEL_SKILL_NAME],
    }
    if not dry_run:
        (target / INSTALL_IDENTITY_NAME).write_text(
            json.dumps(identity, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
    return installed


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Install Senmu BuildOS into Doubao .user_skills"
    )
    parser.add_argument(
        "--target", type=Path, default=None,
        help="Doubao .user_skills directory (default: auto-detect)",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Report what would be installed without writing anything",
    )
    args = parser.parse_args()

    target = args.target or default_user_skills()
    if not target.is_dir():
        raise SystemExit(
            f"[ERROR] Doubao .user_skills directory not found: {target}\n"
            "Pass an explicit target with --target. In Doubao, user skills live under\n"
            "the <Doubao-workspace>/.user_skills directory (the same folder the built-in\n"
            "Skills use). If you do not know it, ask Doubao to show the workspace path."
        )

    installed = install(target, args.dry_run)
    verb = "would install" if args.dry_run else "installed"
    print(f"Senmu BuildOS v{version()} ({verb} into {target}):")
    for name in installed:
        print(f"  - {name}")
    if not args.dry_run:
        print(f"Install identity: {target / INSTALL_IDENTITY_NAME}")
    print("Done.")


if __name__ == "__main__":
    main()
