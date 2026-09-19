#!/usr/bin/env python3
"""Install Senmu BuildOS into a WorkBuddy workspace as skills.

Copies the eight shared skills from skills/ and the WorkBuddy kernel bootstrap
skill from adapters/workbuddy/kernel/, stripping Codex-only metadata, then writes
an install identity file. Deterministic and idempotent; only writes under the
target skills directory.

WorkBuddy loads skills from `<data-root>/skills/` at user level (shared across
projects) or `<workspace>/<data-root>/skills/` at project level. Both use the
same `<skill-name>/SKILL.md` layout as the other adapters.

The WorkBuddy data root was renamed from `.workbuddy` to `.workbuddy-ai`. The
installer resolves whichever root exists under the chosen base so the payload
lands where the running app enumerates skills, and falls back to the current
name when neither exists.

Usage:
    python3 adapters/workbuddy/install_workbuddy.py --dry-run
    python3 adapters/workbuddy/install_workbuddy.py                          # user level
    python3 adapters/workbuddy/install_workbuddy.py --scope project --workspace <dir>
    python3 adapters/workbuddy/install_workbuddy.py --target <dir>           # explicit target
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent  # product root
KERNEL_SOURCE = ROOT / "adapters" / "workbuddy" / "kernel"
SKILLS_SOURCE = ROOT / "skills"
KERNEL_SKILL_NAME = "senmu-build-kernel"
INSTALL_IDENTITY_NAME = ".senmu-buildos-install.json"

WORKBUDDY_SKILL_NAMES = [
    "senmu-build-project",
    "senmu-build-product",
    "senmu-build-design",
    "senmu-build-workflow",
    "senmu-build-engineering",
    "senmu-build-delivery",
    "senmu-build-assurance",
    "senmu-build-learning",
]

# Harness-specific files/folders that must not be copied into WorkBuddy.
EXCLUDED_RELATIVE_NAMES = {"agents", "__pycache__"}

# WorkBuddy renamed its per-user and per-workspace data root. Resolve the root
# that exists instead of hardcoding one name: installing into a root the running
# app never enumerates looks successful but is never loaded.
DATA_ROOT_CURRENT = ".workbuddy-ai"
DATA_ROOT_LEGACY = ".workbuddy"


def skills_root(base: Path) -> Path:
    """Return the WorkBuddy skills directory under a user or workspace base."""
    current = base / DATA_ROOT_CURRENT
    legacy = base / DATA_ROOT_LEGACY
    if current.is_dir() or not legacy.is_dir():
        return current / "skills"
    return legacy / "skills"


def user_skills() -> Path:
    """WorkBuddy user-level skills directory (shared across projects)."""
    return skills_root(Path.home())


def project_skills(workspace: Path) -> Path:
    """WorkBuddy project-level skills directory inside the given workspace."""
    return skills_root(workspace)


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


def install(target: Path, scope: str, dry_run: bool) -> list[str]:
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

    for name in WORKBUDDY_SKILL_NAMES:
        place(name, SKILLS_SOURCE / name)
    place(KERNEL_SKILL_NAME, KERNEL_SOURCE)

    identity = {
        "adapter": "workbuddy",
        "project": "Senmu BuildOS",
        "version": version(),
        "source_commit": source_commit(),
        "installed_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "scope": scope,
        "skills": WORKBUDDY_SKILL_NAMES + [KERNEL_SKILL_NAME],
    }
    if not dry_run:
        (target / INSTALL_IDENTITY_NAME).write_text(
            json.dumps(identity, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
    return installed


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Install Senmu BuildOS into WorkBuddy skills"
    )
    parser.add_argument(
        "--scope", choices=("user", "project"), default="user",
        help="user installs into the user data root's skills directory; project "
             "installs into the workspace data root's skills directory "
             "(default: user)",
    )
    parser.add_argument(
        "--workspace", type=Path, default=None,
        help="WorkBuddy workspace root for --scope project",
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
                "[ERROR] --scope project requires --workspace <workbuddy-workspace>"
            )
        target = project_skills(args.workspace)
        scope = "project"

    if not target.is_dir() and not args.dry_run:
        raise SystemExit(
            f"[ERROR] WorkBuddy skills directory not found: {target}\n"
            "Pass an explicit target with --target, or use --scope user / "
            "--scope project --workspace <dir>. WorkBuddy loads user skills from\n"
            f"~/{DATA_ROOT_CURRENT}/skills/ (or the legacy ~/{DATA_ROOT_LEGACY}/skills/) "
            f"and project skills from <workspace>/{DATA_ROOT_CURRENT}/skills/ "
            f"(or the legacy <workspace>/{DATA_ROOT_LEGACY}/skills/)."
        )

    installed = install(target, scope, args.dry_run)
    verb = "would install" if args.dry_run else "installed"
    print(f"Senmu BuildOS v{version()} ({verb} into {target}, scope: {scope}):")
    for name in installed:
        print(f"  - {name}")
    if not args.dry_run:
        print(f"Install identity: {target / INSTALL_IDENTITY_NAME}")
    print("Done.")


if __name__ == "__main__":
    main()
