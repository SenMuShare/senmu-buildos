#!/usr/bin/env python3
"""Read-only Git branch/worktree inventory for coaching and cleanup review."""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path
from typing import Any


def git(repo: Path, *args: str, check: bool = True) -> str:
    result = subprocess.run(
        ["git", "-C", str(repo), *args],
        check=False,
        capture_output=True,
        text=True,
    )
    if check and result.returncode != 0:
        detail = (result.stderr or result.stdout).strip()
        raise SystemExit(f"git {' '.join(args)} failed: {detail}")
    return result.stdout.rstrip("\n")


def parse_worktrees(raw: str) -> list[dict[str, str | bool | None]]:
    records: list[dict[str, str | bool | None]] = []
    for paragraph in raw.strip().split("\n\n") if raw.strip() else []:
        record: dict[str, str | bool | None] = {
            "path": None,
            "head": None,
            "branch_ref": None,
            "detached": False,
            "prunable": False,
        }
        for line in paragraph.splitlines():
            key, _, value = line.partition(" ")
            if key == "worktree":
                record["path"] = value
            elif key == "HEAD":
                record["head"] = value
            elif key == "branch":
                record["branch_ref"] = value
            elif key == "detached":
                record["detached"] = True
            elif key == "prunable":
                record["prunable"] = True
        if record["path"]:
            records.append(record)
    return records


def is_ancestor(repo: Path, ancestor: str, target: str) -> bool:
    result = subprocess.run(
        ["git", "-C", str(repo), "merge-base", "--is-ancestor", ancestor, target],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode not in (0, 1):
        raise SystemExit(result.stderr.strip() or "git merge-base failed")
    return result.returncode == 0


def classify_worktree(
    *,
    exists: bool,
    prunable: bool,
    primary: bool,
    target_branch: bool,
    dirty: bool,
    detached: bool,
    merged: bool,
) -> str:
    if prunable or not exists:
        return "stale_metadata_review_required"
    if dirty:
        return "dirty_review_required"
    if primary:
        return "primary_worktree"
    if target_branch:
        return "target_worktree"
    if detached:
        return "detached_review_required"
    if merged:
        return "merged_cleanup_candidate"
    return "unmerged_review_required"


def inspect(repo_arg: Path, target: str, protected: set[str]) -> dict[str, Any]:
    repo = Path(git(repo_arg, "rev-parse", "--show-toplevel")).resolve()
    target_head = git(repo, "rev-parse", "--verify", f"{target}^{{commit}}")
    worktrees = parse_worktrees(git(repo, "worktree", "list", "--porcelain"))
    primary_path = Path(str(worktrees[0]["path"])).resolve() if worktrees else repo
    branch_to_worktrees: dict[str, list[dict[str, Any]]] = {}
    inspected_worktrees: list[dict[str, Any]] = []

    for record in worktrees:
        path = Path(str(record["path"])).resolve()
        head = str(record["head"] or "")
        branch_ref = str(record["branch_ref"] or "")
        branch = branch_ref.removeprefix("refs/heads/") or None
        exists = path.is_dir()
        status = git(path, "status", "--porcelain", check=False) if exists else ""
        dirty = bool(status)
        merged = bool(head) and is_ancestor(repo, head, target_head)
        item: dict[str, Any] = {
            "path": str(path),
            "head": head or None,
            "branch": branch,
            "exists": exists,
            "dirty": dirty,
            "is_primary": path == primary_path,
            "is_target_branch": branch == target,
            "detached": bool(record["detached"]),
            "prunable": bool(record["prunable"]),
            "head_reachable_from_target": merged,
            "classification": classify_worktree(
                exists=exists,
                prunable=bool(record["prunable"]),
                primary=path == primary_path,
                target_branch=branch == target,
                dirty=dirty,
                detached=bool(record["detached"]),
                merged=merged,
            ),
        }
        inspected_worktrees.append(item)
        if branch:
            branch_to_worktrees.setdefault(branch, []).append(item)

    branches: list[dict[str, Any]] = []
    raw_branches = git(repo, "for-each-ref", "--format=%(refname:short)", "refs/heads")
    for branch in [line for line in raw_branches.splitlines() if line]:
        merged = is_ancestor(repo, branch, target_head)
        checked_out = branch_to_worktrees.get(branch, [])
        if branch == target or branch in protected:
            classification = "protected_branch"
        elif any(item["dirty"] for item in checked_out):
            classification = "dirty_review_required"
        elif merged:
            classification = "merged_cleanup_candidate"
        else:
            classification = "unmerged_review_required"
        branches.append(
            {
                "name": branch,
                "head": git(repo, "rev-parse", branch),
                "merged_into_target": merged,
                "unique_commit_count": int(git(repo, "rev-list", "--count", f"{target_head}..{branch}")),
                "checked_out_paths": [item["path"] for item in checked_out],
                "classification": classification,
            }
        )

    remotes = [line for line in git(repo, "remote").splitlines() if line]
    return {
        "schema_version": 1,
        "repository_root": str(repo),
        "primary_worktree": str(primary_path),
        "target": target,
        "target_head": target_head,
        "remotes": remotes,
        "worktrees": inspected_worktrees,
        "branches": branches,
        "caveats": [
            "Classifications are read-only coaching candidates, not deletion authorization.",
            "Git alone cannot prove that ignored assets, running processes, project owners, or release entrypoints are safe to remove.",
            "POC, successor-line, protected-branch, and retention intent must be confirmed from project authority sources.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=Path.cwd())
    parser.add_argument("--target", default="main")
    parser.add_argument("--protected", action="append", default=[])
    parser.add_argument("--compact", action="store_true")
    args = parser.parse_args()
    report = inspect(args.repo, args.target, set(args.protected))
    print(json.dumps(report, ensure_ascii=False, indent=None if args.compact else 2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
