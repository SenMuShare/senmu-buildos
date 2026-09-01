#!/usr/bin/env python3
"""Prepare, resume, verify, seal, and close one task-specific Git Change Unit."""

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


def records_dir(repo: Path) -> Path:
    return common_git_dir(repo) / "senmu-buildos" / "change-units"


def record_for_unit(repo: Path, unit: str) -> tuple[Path, dict[str, Any]]:
    matches: list[tuple[Path, dict[str, Any]]] = []
    directory = records_dir(repo)
    for path in sorted(directory.glob("*.json")) if directory.is_dir() else []:
        try:
            value = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise SystemExit(f"[BLOCKED] Change Unit record is invalid: {path}: {exc}") from exc
        if isinstance(value, dict) and value.get("unit") == unit:
            matches.append((path, value))
    if len(matches) != 1:
        raise SystemExit(f"[BLOCKED] expected one Change Unit record for {unit}, found {len(matches)}")
    return matches[0]


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


def is_ancestor(repo: Path, ancestor: str, descendant: str) -> bool:
    result = subprocess.run(
        ["git", "-C", str(repo), "merge-base", "--is-ancestor", ancestor, descendant],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode not in {0, 1}:
        detail = (result.stderr or result.stdout).strip()
        raise SystemExit(f"[BLOCKED] cannot compare Change Unit ancestry: {detail}")
    return result.returncode == 0


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


def local_branch_for_ref(repo: Path, ref: str) -> str | None:
    symbolic = git(repo, "rev-parse", "--symbolic-full-name", ref)
    prefix = "refs/heads/"
    return symbolic.removeprefix(prefix) if symbolic.startswith(prefix) else None


def validate_target_topology(
    repo: Path,
    *,
    target: str,
    target_head: str,
    target_role: str,
    parent_unit: str | None,
) -> dict[str, str | None]:
    target_branch = local_branch_for_ref(repo, target)
    target_record = load_record(repo, target_branch) if target_branch else None

    if target_role == "integration-line":
        if parent_unit:
            raise SystemExit("[BLOCKED] --parent-unit is valid only with --target-role stacked-unit")
        if target_branch is None:
            raise SystemExit(
                "[BLOCKED] integration-line targets must be named local branches; "
                "use --target-role frozen-commit for an exact commit"
            )
        if target_record is not None:
            raise SystemExit(
                f"[BLOCKED] target {target_branch} belongs to Change Unit "
                f"{target_record.get('unit')!r}; task-on-task branching requires "
                "--target-role stacked-unit --parent-unit <unit>"
            )
    elif target_role == "stacked-unit":
        if not parent_unit:
            raise SystemExit("[BLOCKED] stacked-unit targets require --parent-unit")
        if target_branch is None or target_record is None:
            raise SystemExit("[BLOCKED] stacked-unit target must be a registered Change Unit branch")
        if target_record.get("unit") != parent_unit:
            raise SystemExit(
                f"[BLOCKED] stacked parent is {target_record.get('unit')!r}, not {parent_unit!r}"
            )
        if target_record.get("state") != "sealed":
            raise SystemExit("[BLOCKED] stacked-unit target must be sealed before a dependent unit starts")
        if target_record.get("head") != target_head:
            raise SystemExit("[BLOCKED] stacked-unit target has moved after its recorded sealed head")
    elif parent_unit:
        raise SystemExit("[BLOCKED] --parent-unit is valid only with --target-role stacked-unit")

    return {"target_branch": target_branch, "parent_unit": parent_unit}


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


def resume(args: argparse.Namespace) -> dict[str, Any]:
    """Restore the registered execution surface without creating a new branch."""
    validate_identity(args.unit)
    repo = git_root(args.repo)
    path, record = record_for_unit(repo, args.unit)
    branch = str(record.get("branch") or "")
    ensure_record_matches(record, branch=branch, unit=args.unit)
    if not branch_exists(repo, branch):
        raise SystemExit(f"[BLOCKED] registered branch {branch} no longer exists; reconcile the owner record")
    registered_worktree = record.get("worktree")
    if not isinstance(registered_worktree, str) or not registered_worktree.strip():
        raise SystemExit(f"[BLOCKED] Change Unit {args.unit} has no registered worktree")
    expected = Path(registered_worktree).expanduser().resolve()
    checked_out = worktree_for_branch(repo, branch)
    if checked_out is None:
        if expected.exists():
            raise SystemExit(f"[BLOCKED] registered worktree path exists but is not attached: {expected}")
        git(repo, "worktree", "add", str(expected), branch)
    elif checked_out != expected:
        raise SystemExit(f"[BLOCKED] branch {branch} is checked out at {checked_out}, not {expected}")
    return {
        **record,
        "action": "resumed",
        "head": git(repo, "rev-parse", f"{branch}^{{commit}}"),
        "dirty": bool(git(expected, "status", "--porcelain")),
        "record": str(path),
    }


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
    topology = validate_target_topology(
        repo,
        target=args.target,
        target_head=target_head,
        target_role=args.target_role,
        parent_unit=args.parent_unit,
    )
    git(repo, "worktree", "add", str(worktree), "-b", branch, target_head)
    payload = {
        "schema_version": 2,
        "unit": args.unit,
        "state": "in_progress",
        "branch": branch,
        "worktree": str(worktree),
        "target": args.target,
        "target_role": args.target_role,
        **topology,
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


def close(args: argparse.Namespace) -> dict[str, Any]:
    validate_identity(args.unit)
    if not args.owner_ref.strip():
        raise SystemExit("[BLOCKED] --owner-ref must identify the project task owner decision")
    repo = git_root(args.repo)
    path, record = record_for_unit(repo, args.unit)
    if record.get("state") != "sealed":
        raise SystemExit("[BLOCKED] only a sealed Change Unit can receive a final disposition")
    disposition = args.disposition
    if disposition == "integrated":
        if not args.integration_commit:
            raise SystemExit("[BLOCKED] integrated disposition requires --integration-commit")
        integration_commit = git(repo, "rev-parse", "--verify", f"{args.integration_commit}^{{commit}}")
        target_head = git(repo, "rev-parse", "--verify", f"{record['target']}^{{commit}}")
        if not is_ancestor(repo, integration_commit, target_head):
            raise SystemExit("[BLOCKED] integration commit is not reachable from the registered target line")
    elif args.integration_commit:
        raise SystemExit("[BLOCKED] --integration-commit is valid only for integrated disposition")
    else:
        integration_commit = None
    closed = {
        **record,
        "state": disposition,
        "owner_ref": args.owner_ref.strip(),
        "integration_commit": integration_commit,
        "closed_at": now(),
    }
    write_record(repo, str(record["branch"]), closed)
    return {**closed, "record": str(path)}


def list_units(args: argparse.Namespace) -> dict[str, Any]:
    repo = git_root(args.repo)
    items: list[dict[str, Any]] = []
    directory = records_dir(repo)
    for path in sorted(directory.glob("*.json")) if directory.is_dir() else []:
        try:
            record = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise SystemExit(f"[BLOCKED] Change Unit record is invalid: {path}: {exc}") from exc
        if not isinstance(record, dict):
            raise SystemExit(f"[BLOCKED] Change Unit record is not an object: {path}")
        state = str(record.get("state", "unknown"))
        disposition = state
        target = str(record.get("target", ""))
        head = record.get("head")
        target_probe = subprocess.run(
            ["git", "-C", str(repo), "rev-parse", "--verify", f"{target}^{{commit}}"],
            check=False,
            capture_output=True,
            text=True,
        )
        target_head = target_probe.stdout.strip() if target_probe.returncode == 0 else None
        if state == "sealed":
            disposition = (
                "integrated"
                if head and target_head and is_ancestor(repo, str(head), target_head)
                else "pending_integration"
            )
        items.append(
            {
                "unit": record.get("unit"),
                "branch": record.get("branch"),
                "target": target or None,
                "target_head": target_head,
                "head": head,
                "state": state,
                "derived_disposition": disposition,
                "owner_ref": record.get("owner_ref"),
                "integration_commit": record.get("integration_commit"),
                "worktree": record.get("worktree"),
            }
        )
    return {
        "schema_version": 1,
        "repository_root": str(repo),
        "units": sorted(items, key=lambda item: (str(item["derived_disposition"]), str(item["unit"]))),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    prepare_parser = subparsers.add_parser("prepare")
    prepare_parser.add_argument("--repo", type=Path, required=True)
    prepare_parser.add_argument("--target", default="main")
    prepare_parser.add_argument(
        "--target-role",
        choices=("integration-line", "stacked-unit", "frozen-commit"),
        default="integration-line",
    )
    prepare_parser.add_argument("--parent-unit")
    prepare_parser.add_argument("--unit", required=True)
    prepare_parser.add_argument("--slug", required=True)
    prepare_parser.add_argument("--branch")
    prepare_parser.add_argument("--worktree", type=Path, required=True)

    for name in ("resume", "verify", "seal"):
        subparser = subparsers.add_parser(name)
        subparser.add_argument("--repo", type=Path, required=True)
        subparser.add_argument("--unit", required=True)

    list_parser = subparsers.add_parser("list")
    list_parser.add_argument("--repo", type=Path, required=True)

    close_parser = subparsers.add_parser("close")
    close_parser.add_argument("--repo", type=Path, required=True)
    close_parser.add_argument("--unit", required=True)
    close_parser.add_argument("--disposition", choices=("integrated", "excluded", "superseded"), required=True)
    close_parser.add_argument("--owner-ref", required=True)
    close_parser.add_argument("--integration-commit")

    args = parser.parse_args()
    if args.command == "prepare":
        report = prepare(args)
    elif args.command == "resume":
        report = resume(args)
    elif args.command == "verify":
        report = verify(args)
    elif args.command == "seal":
        report = seal(args)
    elif args.command == "list":
        report = list_units(args)
    else:
        report = close(args)
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
