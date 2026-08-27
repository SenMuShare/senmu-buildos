"""Generic fail-closed Git main-worktree authority check.

Copy and adapt this file into the project. Project-specific residue paths and
stateful commands must be registered by the project instead of being inferred.
Requires a Git executable on PATH and a Git worktree as the target directory.
"""

from __future__ import annotations

import argparse
import subprocess
from pathlib import Path


def git(*args: str, cwd: Path) -> str:
    result = subprocess.run(
        ["git", *args], cwd=cwd, check=True, capture_output=True, text=True
    )
    return result.stdout.strip()


def checkout_root(cwd: Path) -> Path:
    return Path(git("rev-parse", "--show-toplevel", cwd=cwd)).resolve()


def canonical_project_root(cwd: Path) -> Path:
    common_dir = Path(
        git("rev-parse", "--path-format=absolute", "--git-common-dir", cwd=cwd)
    ).resolve()
    if common_dir.name != ".git":
        raise RuntimeError(f"unexpected Git common directory: {common_dir}")
    return common_dir.parent


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("report", "require-canonical"))
    parser.add_argument("--cwd", type=Path, default=Path.cwd())
    args = parser.parse_args()

    current = checkout_root(args.cwd)
    canonical = canonical_project_root(args.cwd)
    if args.command == "report":
        print(f"current_checkout_root={current}")
        print(f"canonical_project_root={canonical}")
        print(f"is_external_worktree={str(current != canonical).lower()}")
        return
    if current != canonical:
        raise SystemExit(
            f"[ERROR] stateful operation rejected outside canonical root: {current}\n"
            f"canonical root: {canonical}"
        )
    print(f"[OK] canonical root: {canonical}")


if __name__ == "__main__":
    main()
