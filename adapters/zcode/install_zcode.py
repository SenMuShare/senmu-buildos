#!/usr/bin/env python3
"""Install Senmu BuildOS into ZCode as user- or project-level skills.

Copies the eight shared skills from skills/ (and optionally the ZCode kernel
bootstrap skill from adapters/zcode/kernel/), stripping Codex-only metadata,
then writes an install identity file. Deterministic and idempotent; only
writes under the target skills directory.

ZCode loads skills from `~/.zcode/skills/` or `~/.agents/skills/` (user level,
shared across projects) or `<repo>/.zcode/skills/` / `<repo>/.agents/skills/`
(project level). This installer defaults to `~/.agents/skills/` — the standard
cross-tool location shared with other agents — and creates it when missing.

Note: skills installed this way carry no lifecycle hook. For the full
experience (SessionStart governance-kernel injection), install the ZCode
plugin from the repository instead, or pass --with-kernel to also install the
`senmu-build-kernel` bootstrap skill.

Usage:
    python3 adapters/zcode/install_zcode.py --dry-run
    python3 adapters/zcode/install_zcode.py                          # user level
    python3 adapters/zcode/install_zcode.py --with-kernel            # + bootstrap skill
    python3 adapters/zcode/install_zcode.py --scope project --workspace <dir>
    python3 adapters/zcode/install_zcode.py --target <dir>           # explicit target
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent  # senmu-buildos-internal
KERNEL_SOURCE = ROOT / "adapters" / "zcode" / "kernel"
SKILLS_SOURCE = ROOT / "skills"
KERNEL_SKILL_NAME = "senmu-build-kernel"
INSTALL_IDENTITY_NAME = ".senmu-buildos-install.json"

ZCODE_SKILL_NAMES = [
    "senmu-build-project",
    "senmu-build-product",
    "senmu-build-design",
    "senmu-build-workflow",
    "senmu-build-engineering",
    "senmu-build-delivery",
    "senmu-build-assurance",
    "senmu-build-learning",
]

# Harness-specific files/folders that must not be copied into ZCode.
EXCLUDED_RELATIVE_NAMES = {"agents", "__pycache__"}


def user_skills() -> Path:
    """ZCode user-level skills directory (cross-tool standard location)."""
    return Path.home() / ".agents" / "skills"


def project_skills(workspace: Path) -> Path:
    """ZCode project-level skills directory inside the given repository."""
    return workspace / ".agents" / "skills"


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


def install(target: Path, scope: str, with_kernel: bool, dry_run: bool) -> list[str]:
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

    for name in ZCODE_SKILL_NAMES:
        place(name, SKILLS_SOURCE / name)
    if with_kernel:
        place(KERNEL_SKILL_NAME, KERNEL_SOURCE)

    identity = {
        "adapter": "zcode",
        "project": "Senmu BuildOS",
        "version": version(),
        "source_commit": source_commit(),
        "installed_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "scope": scope,
        "with_kernel": with_kernel,
        "skills": ZCODE_SKILL_NAMES + ([KERNEL_SKILL_NAME] if with_kernel else []),
    }
    if not dry_run:
        (target / INSTALL_IDENTITY_NAME).write_text(
            json.dumps(identity, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
    return installed


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Install Senmu BuildOS into ZCode skills directories"
    )
    parser.add_argument(
        "--scope", choices=("user", "project"), default="user",
        help="user installs into ~/.agents/skills; project installs into "
             "<workspace>/.agents/skills (default: user)",
    )
    parser.add_argument(
        "--workspace", type=Path, default=None,
        help="repository root for --scope project",
    )
    parser.add_argument(
        "--with-kernel", action="store_true",
        help="also install the senmu-build-kernel bootstrap skill (for "
             "script installs without the ZCode plugin's SessionStart hook)",
    )
    parser.add_argument(
        "--target", type=Path, default=None,
        help="Explicit skills directory (overrides --scope/--workspace)",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Report what would be installed without writing anything",
    )
    args = parser.parse_args()

    if args.target is not None:
        target = args.target
        scope = "target"
    elif args.scope == "user":
        target = user_skills()
        scope = "user"
    else:
        if args.workspace is None:
            raise SystemExit(
                "[ERROR] --scope project requires --workspace <repository-root>"
            )
        target = project_skills(args.workspace)
        scope = "project"

    if not args.dry_run:
        target.mkdir(parents=True, exist_ok=True)

    installed = install(target, scope, args.with_kernel, args.dry_run)
    verb = "would install" if args.dry_run else "installed"
    print(f"Senmu BuildOS v{version()} ({verb} into {target}, scope: {scope}):")
    for name in installed:
        print(f"  - {name}")
    if not args.dry_run:
        print(f"Install identity: {target / INSTALL_IDENTITY_NAME}")
    if not args.with_kernel:
        print(
            "Note: script installs carry no lifecycle hook. Install the ZCode "
            "plugin or rerun with --with-kernel for governance-kernel injection."
        )
    print("Done.")


if __name__ == "__main__":
    main()
