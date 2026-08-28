#!/usr/bin/env python3
"""Prepare, verify, and seal one task-specific Git Change Unit."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


UNIT_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{2,127}$")
SLUG_PATTERN = re.compile(r"^[a-z0-9][a-z0-9-]{1,63}$")


def git(repo: Path, *args: str, check: bool = True) -> str:
    result = subprocess.run(
        ["git", "-C", str(repo), *args],
        check=False,
        capture_output=True,
        text=True,
    )
    if check and result.returncode != 0:
        detail = (result.stderr or result.stdout).strip()
        raise SystemExit(f"[BLOCKED] git {' '.join(args)} failed: {detail}")
    return result.stdout.rstrip("\n")


def git_root(repo: Path) -> Path:
    return Path(git(repo, "rev-parse", "--show-toplevel")).resolve()


def common_git_dir(repo: Path) -> Path:
    root = git_root(repo)
    raw = Path(git(root, "rev-parse", "--git-common-dir"))
    return (root / raw).resolve() if not raw.is_absolute() else raw.resolve()


def record_path(repo: Path, branch: str) -> Path:
    digest = hashlib.sha256(branch.encode("utf-8")).hexdigest()[:20]
    return common_git_dir(repo) / "senmu-buildos" / "change-units" / f"{digest}.json"


def load_record(repo: Path, branch: str) -> dict[str, Any] | None:
    path = record_path(repo, branch)
    if not path.is_file():
        return None
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(f"[BLOCKED] Change Unit record is invalid: {path}: {exc}") from exc
    if not isinstance(value, dict) or value.get("branch") != branch:
        raise SystemExit(f"[BLOCKED] Change Unit record does not match branch {branch}")
    return value


def write_record(repo: Path, branch: str, payload: dict[str, Any]) -> Path:
    path = record_path(repo, branch)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(".tmp")
    temporary.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)
    return path


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def validate_identity(unit: str, slug: str | None = None) -> None:
    if not UNIT_PATTERN.fullmatch(unit):
        raise SystemExit("[BLOCKED] --unit must be a stable 3-128 character task/change-unit key")
    if slug is not None and not SLUG_PATTERN.fullmatch(slug):
        raise SystemExit("[BLOCKED] --slug must use 2-64 lowercase letters, digits, or hyphens")


def branch_exists(repo: Path, branch: str) -> bool:
    result = subprocess.run(
        ["git", "-C", str(repo), "show-ref", "--verify", "--quiet", f"refs/heads/{branch}"],
        check=False,
    )
    return result.returncode == 0


def worktree_for_branch(repo: Path, branch: str) -> Path | None:
    current_path: Path | None = None
    current_branch: str | None = None
    for line in git(repo, "worktree", "list", "--porcelain").splitlines() + [""]:
        if line.startswith("worktree "):
            current_path = Path(line.removeprefix("worktree ")).resolve()
            current_branch = None
        elif line.startswith("branch "):
            current_branch = line.removeprefix("branch refs/heads/")
        elif not line and current_path is not None:
            if current_branch == branch:
                return current_path
            current_path = None
            current_branch = None
    return None


def ensure_record_matches(record: dict[str, Any], *, branch: str, unit: str) -> None:
    if record.get("branch") != branch or record.get("unit") != unit:
        raise SystemExit(
            f"[BLOCKED] branch {branch} belongs to Change Unit {record.get('unit')!r}, not {unit!r}"
        )
    if record.get("state") != "in_progress":
        raise SystemExit(
            f"[BLOCKED] branch {branch} is {record.get('state')!r}; sealed or closed work cannot be reused"
        )


def prepare(args: argparse.Namespace) -> dict[str, Any]:
    validate_identity(args.unit, args.slug)
    repo = git_root(args.repo)
    target_head = git(repo, "rev-parse", "--verify", f"{args.target}^{{commit}}")
    branch = args.branch or f"codex/{args.slug}"
    worktree = args.worktree.expanduser().resolve()
    if worktree == repo:
        raise SystemExit("[BLOCKED] Change Unit worktree cannot be the current repository checkout")

    existing_record = load_record(repo, branch)
    checked_out = worktree_for_branch(repo, branch)
    if branch_exists(repo, branch):
        if existing_record is None:
            raise SystemExit(
                f"[BLOCKED] branch {branch} already exists without a matching Change Unit record; use a new branch"
            )
        ensure_record_matches(existing_record, branch=branch, unit=args.unit)
        expected = Path(str(existing_record["worktree"])).resolve()
        if worktree != expected:
            raise SystemExit(f"[BLOCKED] Change Unit {args.unit} is bound to worktree {expected}")
        if checked_out is None:
            if worktree.exists():
                raise SystemExit(f"[BLOCKED] requested worktree path already exists: {worktree}")
            git(repo, "worktree", "add", str(worktree), branch)
        elif checked_out != worktree:
            raise SystemExit(f"[BLOCKED] branch {branch} is already checked out at {checked_out}")
        return {**existing_record, "action": "resumed", "record": str(record_path(repo, branch))}

    if existing_record is not None:
        raise SystemExit(f"[BLOCKED] stale Change Unit record exists for missing branch {branch}; review it manually")
    if worktree.exists():
        raise SystemExit(f"[BLOCKED] requested worktree path already exists: {worktree}")
    git(repo, "worktree", "add", str(worktree), "-b", branch, target_head)
    payload = {
        "schema_version": 1,
        "unit": args.unit,
        "state": "in_progress",
        "branch": branch,
        "worktree": str(worktree),
        "target": args.target,
        "baseline": target_head,
        "prepared_at": now(),
    }
    path = write_record(repo, branch, payload)
    return {**payload, "action": "created", "record": str(path)}


def verify(args: argparse.Namespace) -> dict[str, Any]:
    validate_identity(args.unit)
    repo = git_root(args.repo)
    branch = git(repo, "branch", "--show-current")
    if not branch:
        raise SystemExit("[BLOCKED] detached HEAD is not a writable Change Unit")
    record = load_record(repo, branch)
    if record is None:
        raise SystemExit(f"[BLOCKED] branch {branch} has no prepared Change Unit record")
    ensure_record_matches(record, branch=branch, unit=args.unit)
    if Path(str(record["worktree"])).resolve() != repo:
        raise SystemExit(f"[BLOCKED] edit is running in {repo}, not the registered worktree {record['worktree']}")
    if worktree_for_branch(repo, branch) != repo:
        raise SystemExit(f"[BLOCKED] branch {branch} is not checked out in its registered worktree")
    return {**record, "verified": True, "record": str(record_path(repo, branch))}


def seal(args: argparse.Namespace) -> dict[str, Any]:
    payload = verify(args)
    repo = git_root(args.repo)
    branch = str(payload["branch"])
    dirty = git(repo, "status", "--porcelain")
    if dirty:
        raise SystemExit("[BLOCKED] Change Unit cannot be sealed with uncommitted files")
    head = git(repo, "rev-parse", "HEAD")
    unique_count = int(git(repo, "rev-list", "--count", f"{payload['baseline']}..{head}"))
    if unique_count < 1:
        raise SystemExit("[BLOCKED] Change Unit cannot be sealed without a commit after its baseline")
    sealed = {
        key: value
        for key, value in payload.items()
        if key not in {"verified", "record"}
    }
    sealed.update({"state": "sealed", "head": head, "sealed_at": now()})
    path = write_record(repo, branch, sealed)
    return {**sealed, "record": str(path)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    prepare_parser = subparsers.add_parser("prepare")
    prepare_parser.add_argument("--repo", type=Path, required=True)
    prepare_parser.add_argument("--target", default="main")
    prepare_parser.add_argument("--unit", required=True)
    prepare_parser.add_argument("--slug", required=True)
    prepare_parser.add_argument("--branch")
    prepare_parser.add_argument("--worktree", type=Path, required=True)

    for name in ("verify", "seal"):
        subparser = subparsers.add_parser(name)
        subparser.add_argument("--repo", type=Path, required=True)
        subparser.add_argument("--unit", required=True)

    args = parser.parse_args()
    if args.command == "prepare":
        report = prepare(args)
    elif args.command == "verify":
        report = verify(args)
    else:
        report = seal(args)
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
