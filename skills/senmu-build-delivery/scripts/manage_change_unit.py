#!/usr/bin/env python3
"""Inspect, prepare, resume, review, seal, and close a task-specific Git Change Unit."""

from __future__ import annotations

import argparse
import importlib.util
import hashlib
import json
import os
import re
import subprocess
from contextlib import contextmanager
from datetime import datetime, timezone
from collections.abc import Iterator
from pathlib import Path
from typing import Any


_REVIEW_SPEC = importlib.util.spec_from_file_location(
    "buildos_shared_review_inventory", Path(__file__).with_name("git_review_inventory.py"))
assert _REVIEW_SPEC and _REVIEW_SPEC.loader
_review_git = importlib.util.module_from_spec(_REVIEW_SPEC)
_REVIEW_SPEC.loader.exec_module(_review_git)


UNIT_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{2,127}$")
SLUG_PATTERN = re.compile(r"^[a-z0-9][a-z0-9-]{1,63}$")
COMMIT_PATTERN = re.compile(r"[0-9a-f]{40}|[0-9a-f]{64}")
REPAIR_ROUTES = {
    "in_progress": "existing_unit", "sealed": "linked_repair",
    "integrated": "current_target", "excluded": "new_authorized_scope",
    "superseded": "current_task_owner",
}
RETIRED_STATES = {"integrated", "excluded", "superseded"}



def git(repo: Path, *args: str, check: bool = True) -> str:
    result = subprocess.run(
        ["git", "-C", str(repo), *args],
        check=False,
        capture_output=True,
        text=True,
     env=_review_git.git_environment())
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


def records_for_unit(repo: Path, unit: str) -> list[tuple[Path, dict[str, Any]]]:
    matches: list[tuple[Path, dict[str, Any]]] = []
    directory = records_dir(repo)
    for path in sorted(directory.glob("*.json")) if directory.is_dir() else []:
        try:
            value = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise SystemExit(f"[BLOCKED] Change Unit record is invalid: {path}: {exc}") from exc
        if not isinstance(value, dict):
            raise SystemExit(f"[BLOCKED] Change Unit record is not an object: {path}")
        if value.get("unit") == unit:
            matches.append((path, value))
    return matches


def record_for_unit(repo: Path, unit: str) -> tuple[Path, dict[str, Any]]:
    matches = records_for_unit(repo, unit)
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
     env=_review_git.git_environment())
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
     env=_review_git.git_environment())
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
            raise SystemExit(
                "[BLOCKED] stacked-unit target must be sealed before a dependent unit starts. "
                "For repairs within the same acceptance batch, use the existing open unit "
                "and review an exact commit; do not seal merely to request review. "
                "A genuinely separate dependency needs its own approved boundary."
            )
        if target_record.get("head") != target_head:
            raise SystemExit("[BLOCKED] stacked-unit target has moved after its recorded sealed head")
        _, _, observed = observe_unit(repo, parent_unit)
        require_identity(observed, absent_surface_issues(repo, observed))
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
    """Restore only the registered open surface after checking its actual identity."""
    validate_identity(args.unit)
    repo = git_root(args.repo)
    with preparation_lock(repo):
        return resume_registered(repo, args.unit)


def resume_registered(repo: Path, unit: str) -> dict[str, Any]:
    path, record, observed = observe_unit(repo, unit)
    ensure_record_matches(record, branch=observed["branch"], unit=unit)
    expected = Path(observed["worktree"])
    # A genuinely absent, unattached worktree can be restored; a replacement cannot.
    allowed = set()
    if not expected.exists() and worktree_for_branch(repo, observed["branch"]) is None:
        allowed = {"worktree_unavailable", "worktree_registration_mismatch"}
    require_identity(observed, allowed)
    if not observed["worktree_exists"]:
        git(repo, "worktree", "add", str(expected), observed["branch"])
    final_path, final_record, current = observe_unit(repo, unit)
    require_identity(current)
    if final_path != path or final_record != record or current["head"] != observed["head"]:
        raise SystemExit("[BLOCKED] Change Unit changed during recovery; reconcile current facts")
    return {**record, "action": "resumed", "head": current["head"],
            "dirty": current["dirty"], "record": str(path)}


@contextmanager
def preparation_lock(repo: Path) -> Iterator[None]:
    """Serialize worktree preparation/recovery, not ordinary development."""
    path = records_dir(repo).parent / "change-units.prepare.lock"
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        guard = path.open("a+b")
    except OSError as exc:
        raise SystemExit(f"[BLOCKED] cannot open Change Unit preparation lock: {exc}") from exc
    with guard:
        try:
            if os.name == "nt":
                import msvcrt
                # Windows permits locking one byte beyond EOF; no marker writes needed.
                guard.seek(0)
                msvcrt.locking(guard.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                import fcntl
                fcntl.flock(guard.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError as exc:
            raise SystemExit(
                "[BLOCKED] Change Unit preparation lock unavailable; "
                f"another prepare/resume may be active. Retry after it exits: {exc}"
            ) from exc
        try:
            yield
        finally:
            if os.name == "nt":
                guard.seek(0)
                msvcrt.locking(guard.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                fcntl.flock(guard.fileno(), fcntl.LOCK_UN)
    # Keep the same lock inode. Unlinking it would allow competing lock files.


def prepare(args: argparse.Namespace) -> dict[str, Any]:
    validate_identity(args.unit, args.slug)
    repo = git_root(args.repo)
    with preparation_lock(repo):
        return prepare_locked(args, repo)


def prepare_locked(args: argparse.Namespace, repo: Path) -> dict[str, Any]:
    branch = args.branch or f"codex/{args.slug}"
    worktree = args.worktree.expanduser().resolve()
    if worktree == repo:
        raise SystemExit("[BLOCKED] Change Unit worktree cannot be the current repository checkout")

    # Unit IDs, not branch names, define recovery identity. Check before Git writes.
    matches = records_for_unit(repo, args.unit)
    if len(matches) > 1:
        raise SystemExit(
            f"[BLOCKED] expected one Change Unit record for {args.unit}, found {len(matches)}; "
            "reconcile existing records without creating or deleting a unit"
        )
    if matches:
        registered_path, registered = matches[0]
        registered_branch = registered.get("branch")
        registered_worktree = registered.get("worktree")
        if any(not isinstance(value, str) or not value.strip()
               for value in (registered_branch, registered_worktree)):
            raise SystemExit("[BLOCKED] registered Change Unit lacks branch or worktree identity")
        ensure_record_matches(registered, branch=registered_branch, unit=args.unit)
        if (branch != registered_branch
                or worktree != Path(registered_worktree).expanduser().resolve()):
            raise SystemExit(
                f"[BLOCKED] Change Unit {args.unit} is already registered at "
                f"{registered_branch} ({registered_worktree}); use inspect/resume for this ID"
            )
        if registered_path != record_path(repo, registered_branch):
            raise SystemExit("[BLOCKED] Change Unit record location does not match its branch")
        if (args.target != registered.get("target")
                or args.target_role != registered.get("target_role", "integration-line")
                or args.parent_unit != registered.get("parent_unit")):
            raise SystemExit("[BLOCKED] existing Change Unit target binding differs; use inspect/resume")
        return resume_registered(repo, args.unit)

    target_head = git(repo, "rev-parse", "--verify", f"{args.target}^{{commit}}")
    existing_record = load_record(repo, branch)
    if branch_exists(repo, branch):
        if existing_record is None:
            raise SystemExit(
                f"[BLOCKED] branch {branch} already exists without a matching Change Unit record; use a new branch"
            )
        # A different unit owns this existing branch. Never adopt it by its name.
        ensure_record_matches(existing_record, branch=branch, unit=args.unit)
        raise SystemExit("[BLOCKED] branch record is not uniquely registered for this unit")

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
    _, stored, observed = observe_unit(repo, args.unit)
    require_identity(observed)
    if stored != payload or observed["head"] != target_head:
        raise SystemExit("[BLOCKED] Change Unit changed during creation; preserve and reconcile its record")
    return {**payload, "action": "created", "record": str(path)}


def verify(args: argparse.Namespace) -> dict[str, Any]:
    validate_identity(args.unit)
    repo = git_root(args.repo)
    branch = git(repo, "branch", "--show-current")
    if not branch:
        raise SystemExit("[BLOCKED] detached HEAD is not a writable Change Unit")
    if load_record(repo, branch) is None:
        raise SystemExit(f"[BLOCKED] branch {branch} has no prepared Change Unit record")
    path, record, observed = observe_unit(repo, args.unit)
    require_identity(observed)
    ensure_record_matches(record, branch=branch, unit=args.unit)
    if observed["worktree"] != str(repo):
        raise SystemExit(f"[BLOCKED] edit is running in {repo}, not the registered worktree {observed['worktree']}")
    return {**record, "verified": True, "record": str(path)}


def seal(args: argparse.Namespace) -> dict[str, Any]:
    payload = verify(args)
    repo = git_root(args.repo)
    branch = str(payload["branch"])
    before = Path(payload["record"]).read_bytes()
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
    if (verify(args) != payload or Path(payload["record"]).read_bytes() != before
            or git(repo, "rev-parse", "HEAD") != head or git(repo, "status", "--porcelain")):
        raise SystemExit("[BLOCKED] Change Unit changed during sealing; inspect current facts")
    path = write_record(repo, branch, sealed)
    return {**sealed, "record": str(path)}


def resolve_commit(repo: Path, ref: str) -> str:
    return git(repo, "rev-parse", "--verify", "--end-of-options", f"{ref}^{{commit}}")


def integration_proof(
    repo: Path, record: dict[str, Any], receipt: str, receiving_base: str | None,
    *, receiving_target: str | None = None,
) -> dict[str, str | None]:
    """Prove frozen source reception, not product acceptance or current behavior."""
    for key in ("head", "baseline", "branch", "target"):
        if not isinstance(record.get(key), str) or not record[key].strip():
            raise SystemExit(f"[BLOCKED] sealed Change Unit requires {key}")
    source = resolve_commit(repo, record["head"])
    baseline = resolve_commit(repo, record["baseline"])
    if not is_ancestor(repo, baseline, source) or baseline == source:
        raise SystemExit("[BLOCKED] sealed source must descend from its recorded baseline")
    branch = record["branch"]
    if branch_exists(repo, branch) and resolve_commit(repo, f"refs/heads/{branch}") != source:
        raise SystemExit("[BLOCKED] Change Unit branch moved after seal; reconcile the frozen candidate")
    target_ref = receiving_target or record["target"]
    target = resolve_commit(repo, target_ref)
    if not is_ancestor(repo, receipt, target):
        raise SystemExit("[BLOCKED] integration commit is not reachable from the registered target line")

    actual_tree = git(repo, "rev-parse", f"{receipt}^{{tree}}")
    if receiving_base is not None:
        before = resolve_commit(repo, receiving_base)
    elif receipt == source:
        # Object identity proves reception but says nothing about where the target
        # pointed before it advanced. The source may already contain target merges.
        before = None
    else:
        parents = git(repo, "rev-list", "--parents", "-n", "1", receipt).split()
        if len(parents) < 2:
            raise SystemExit("[BLOCKED] integration receipt has no receiving parent")
        before = parents[1]
    if before is not None:
        if before == receipt or not is_ancestor(repo, before, receipt):
            raise SystemExit("[BLOCKED] integration base must be a strict ancestor of the receipt")
        if not is_ancestor(repo, baseline, before):
            raise SystemExit("[BLOCKED] receiving base does not descend from the source baseline")

    if receipt == source:
        kind = "exact_commit"
    else:
        assert before is not None
        # Replay the full frozen delta. A squash/cherry-pick may have new commit IDs.
        # merge-tree writes Git objects, never the index, worktree or branch refs.
        merged = subprocess.run(
            ["git", "-C", str(repo), "merge-tree", "--write-tree", "--no-messages",
             f"--merge-base={baseline}", before, source],
            check=False, capture_output=True, text=True,
         env=_review_git.git_environment())
        if merged.returncode != 0:
            detail = (merged.stderr or merged.stdout).strip()
            raise SystemExit(
                "[BLOCKED] cannot prove clean integration replay; retain sealed state. "
                "Use the actual receiving range or review a target-specific candidate. "
                f"Git reported: {detail}"
            )
        expected_tree = merged.stdout.strip().splitlines()[0] if merged.stdout.strip() else ""
        if not re.fullmatch(r"[0-9a-f]{40}|[0-9a-f]{64}", expected_tree):
            raise SystemExit("[BLOCKED] merge-tree did not return a valid tree identity")
        if expected_tree != actual_tree:
            raise SystemExit("[BLOCKED] integration receipt content does not match the sealed Change Unit replay")
        if expected_tree == git(repo, "rev-parse", f"{before}^{{tree}}"):
            raise SystemExit("[BLOCKED] receiving range adds no source change; use the actual receipt or supersession")
        kind = "tree_replay"
    # Fail before changing a record when either observed ref moved during verification.
    if resolve_commit(repo, target_ref) != target:
        raise SystemExit("[BLOCKED] target moved during integration verification; retry against current facts")
    if branch_exists(repo, branch) and resolve_commit(repo, f"refs/heads/{branch}") != source:
        raise SystemExit("[BLOCKED] Change Unit branch moved during integration verification")
    return {
        "kind": kind, "source_baseline": baseline, "source_head": source,
        "receiving_base": before, "integration_commit": receipt,
        "receiving_tree": actual_tree, "observed_target_head": target,
        "receiving_target": target_ref,
    }


def approved_receiving_target(repo: Path, args: argparse.Namespace) -> str | None:
    """Bind a caller-approved final line; a reference is not authentication of consent."""
    requested = getattr(args, "integration_target", None)
    authority = getattr(args, "target_authorization_ref", None)
    if requested is None:
        if authority is not None:
            raise SystemExit("[BLOCKED] --target-authorization-ref requires --integration-target")
        return None
    if not requested.strip() or not authority or not authority.strip():
        raise SystemExit("[BLOCKED] --integration-target requires --target-authorization-ref for its approved scope")
    target = requested if requested.startswith("refs/heads/") else "refs/heads/" + requested
    git(repo, "check-ref-format", target)
    branch = target.removeprefix("refs/heads/")
    if not branch_exists(repo, branch):
        raise SystemExit("[BLOCKED] integration target must be an existing named local line")
    if load_record(repo, branch) is not None:
        raise SystemExit("[BLOCKED] final integration target cannot be a Change Unit branch")
    return target


def close(args: argparse.Namespace) -> dict[str, Any]:
    validate_identity(args.unit)
    if not args.owner_ref.strip():
        raise SystemExit("[BLOCKED] --owner-ref must identify the project task owner decision")
    repo = git_root(args.repo)
    path, record, observed = observe_unit(repo, args.unit)
    require_identity(observed, absent_surface_issues(repo, observed))
    if record.get("state") != "sealed":
        raise SystemExit("[BLOCKED] only a sealed Change Unit can receive a final disposition")
    disposition = args.disposition
    proof = None
    if disposition == "integrated":
        if not args.integration_commit:
            raise SystemExit("[BLOCKED] integrated disposition requires --integration-commit")
        integration_commit = resolve_commit(repo, args.integration_commit)
        receiving_target = approved_receiving_target(repo, args)
        proof = integration_proof(repo, record, integration_commit, args.integration_base,
                                  receiving_target=receiving_target)
    elif (args.integration_commit or args.integration_base
          or getattr(args, "integration_target", None) is not None
          or getattr(args, "target_authorization_ref", None) is not None):
        raise SystemExit("[BLOCKED] integration arguments are valid only for integrated disposition")
    else:
        integration_commit = None
    closed = {
        **record,
        "state": disposition,
        "owner_ref": args.owner_ref.strip(),
        "integration_commit": integration_commit,
        "closed_at": now(),
    }
    if proof is not None:
        closed["integration_proof"] = proof
        closed["integration_target"] = proof["receiving_target"]
        if receiving_target is not None:
            closed["target_authorization_ref"] = args.target_authorization_ref.strip()
    final_path, final_record, current = observe_unit(repo, args.unit)
    require_identity(current, absent_surface_issues(repo, current))
    if final_path != path or final_record != record or current != observed:
        raise SystemExit("[BLOCKED] Change Unit record or source changed during closeout")
    write_record(repo, str(record["branch"]), closed)
    return {**closed, "record": str(path)}


def list_units_full(args: argparse.Namespace) -> dict[str, Any]:
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
         env=_review_git.git_environment())
        target_head = target_probe.stdout.strip() if target_probe.returncode == 0 else None
        candidate_reachable = (
            bool(head and target_head and is_ancestor(repo, str(head), target_head))
            if state == "sealed" else None
        )
        if state == "sealed":
            # An ancestry hint does not prove that a merge retained the source content.
            disposition = "pending_integration"
        items.append(
            {
                "unit": record.get("unit"),
                "branch": record.get("branch"),
                "target": target or None,
                "target_head": target_head,
                "head": head,
                "state": state,
                "derived_disposition": disposition,
                "candidate_reachable": candidate_reachable,
                "integration_proof": record.get("integration_proof"),
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



def list_units(args: argparse.Namespace) -> dict[str, Any]:
    """Bounded metadata summary. Use inspect for live identity, full for schema v1."""
    if args.format == "full":
        if (args.state is not None or args.unit is not None or args.issues_only
                or args.limit is not None or args.offset != 0):
            raise SystemExit("[BLOCKED] --format full is the unfiltered legacy schema; use summary for filters/pages")
        return list_units_full(args)
    limit = 10 if args.limit is None else args.limit
    if not 1 <= limit <= 100 or args.offset < 0:
        raise SystemExit("[BLOCKED] --limit must be 1..100 and --offset must be nonnegative")
    if args.unit is not None:
        validate_identity(args.unit)
    repo = git_root(args.repo)
    entries: list[dict[str, Any]] = []
    counts = {state: 0 for state in REPAIR_ROUTES}
    counts["unknown"] = 0
    by_unit: dict[str, list[dict[str, Any]]] = {}
    directory = records_dir(repo)
    for path in sorted(directory.glob("*.json")) if directory.is_dir() else []:
        try:
            record = json.loads(path.read_text(encoding="utf-8"))
            if not isinstance(record, dict):
                raise ValueError("not an object")
            issues = registration_issues(path, record)
        except (OSError, ValueError):
            record, issues = {}, ["record_unreadable"]
        raw_state = record.get("state")
        state = raw_state if isinstance(raw_state, str) and raw_state in REPAIR_ROUTES else "unknown"
        raw_unit = record.get("unit")
        unit = raw_unit if isinstance(raw_unit, str) and UNIT_PATTERN.fullmatch(raw_unit) else None
        counts[state] += 1
        item = {"unit": unit, "state": state, "record_name": path.name,
                "branch": str(record.get("branch", ""))[:128], "identity_issues": issues}
        entries.append(item)
        if unit is not None:
            by_unit.setdefault(unit, []).append(item)
    for group in by_unit.values():
        if len(group) > 1:
            for item in group:
                item["identity_issues"].append("duplicate_unit")
    entries.sort(key=lambda item: (str(item["unit"] or ""), item["record_name"]))
    issues = [item for item in entries if item["identity_issues"]]
    selected = entries
    if args.unit is not None:
        selected = [item for item in selected if item["unit"] == args.unit]
    if args.state is not None and args.state != "all":
        selected = [item for item in selected if item["state"] == args.state]
    elif args.state is None and args.unit is None and not args.issues_only:
        selected = [item for item in selected if item["state"] in {"in_progress", "sealed"}]
    if args.issues_only:
        selected = [item for item in selected if item["identity_issues"]]
    end = args.offset + limit
    return {
        "schema_version": 2, "kind": "change_unit_summary", "repository_root": str(repo),
        "total_records": len(entries), "counts_by_state": counts,
        "matching_records": len(selected), "offset": args.offset, "limit": limit,
        "next_offset": end if end < len(selected) else None,
        "units": selected[args.offset:end], "issue_records": len(issues),
        "issues": [] if args.issues_only else issues[:limit],
        "issues_truncated": not args.issues_only and len(issues) > limit,
        "identity_checks": "registration_only",
        "scope": {"state": args.state or ("all" if args.unit or args.issues_only else "active"),
                  "unit": args.unit, "issues_only": args.issues_only},
        "details": "inspect --repo <repo> --unit <id> checks live Git identity; list --format full preserves schema v1",
        "expand": "list --state all for history; list --issues-only for anomalies; continue with --offset <next_offset>",
    }


def registration_issues(path: Path, record: dict[str, Any]) -> list[str]:
    """Check portable record structure without Git probes or claimed acceptance."""
    issues: list[str] = []
    unit, branch = record.get("unit"), record.get("branch")
    if not isinstance(unit, str) or UNIT_PATTERN.fullmatch(unit) is None:
        issues.append("unit_identity_invalid")
    for field in ("branch", "worktree", "baseline", "target"):
        if not isinstance(record.get(field), str) or not record[field].strip():
            issues.append(field + "_identity_missing")
    if isinstance(branch, str) and branch:
        expected = hashlib.sha256(branch.encode("utf-8")).hexdigest()[:20] + ".json"
        if path.name != expected:
            issues.append("record_location_mismatch")
    if str(record.get("state")) not in REPAIR_ROUTES:
        issues.append("state_unresolved")
    baseline = record.get("baseline")
    if isinstance(baseline, str) and COMMIT_PATTERN.fullmatch(baseline) is None:
        issues.append("baseline_identity_invalid")
    if record.get("state") == "sealed":
        head = record.get("head")
        if not isinstance(head, str) or COMMIT_PATTERN.fullmatch(head) is None:
            issues.append("sealed_head_invalid")
    return issues


def observe_unit(repo: Path, unit: str) -> tuple[Path, dict[str, Any], dict[str, Any]]:
    """One fact checker for all lifecycle entrypoints; policies stay with each action."""
    path, record = record_for_unit(repo, unit)
    issues = registration_issues(path, record)
    required = ("branch", "worktree", "baseline")
    if any(not isinstance(record.get(key), str) or not record[key].strip() for key in required):
        raise SystemExit("[BLOCKED] " + ", ".join(issues))
    branch, baseline = record["branch"], record["baseline"]
    expected = Path(record["worktree"]).expanduser().resolve()
    attached = worktree_for_branch(repo, branch)
    exists = expected.is_dir()
    state = record.get("state")
    retired = state in RETIRED_STATES if isinstance(state, str) else False
    head = resolve_commit(repo, f"refs/heads/{branch}") if branch_exists(repo, branch) else None
    if head is None and not retired:
        issues.append("branch_unavailable")
    if not exists and not retired:
        issues.append("worktree_unavailable")
    if attached != expected and not retired:
        issues.append("worktree_registration_mismatch")
    dirty = None
    # Closed, retired paths can legitimately be reused. Open/sealed surfaces cannot.
    if exists and (not retired or attached == expected):
        try:
            if (git_root(expected) != expected or common_git_dir(expected) != common_git_dir(repo)
                    or git(expected, "branch", "--show-current") != branch):
                issues.append("worktree_identity_mismatch")
            else:
                dirty = bool(git(expected, "--no-optional-locks", "status", "--porcelain"))
        except SystemExit:
            issues.append("worktree_identity_unresolved")
    try:
        resolved_baseline = resolve_commit(repo, baseline)
        if head is not None and not is_ancestor(repo, resolved_baseline, head):
            issues.append("baseline_not_ancestor")
        if state == "sealed" and "sealed_head_invalid" not in issues:
            sealed_head = resolve_commit(repo, record["head"])
            if not is_ancestor(repo, resolved_baseline, sealed_head) or sealed_head == resolved_baseline:
                issues.append("sealed_baseline_mismatch")
    except SystemExit:
        issues.append("baseline_or_sealed_head_unresolved")
    if state == "sealed" and head is not None and head != record.get("head"):
        issues.append("sealed_head_changed")
    observed = {
        "unit": unit, "state": state, "record": str(path),
        "repository_root": str(repo), "branch": branch, "worktree": str(expected),
        "worktree_exists": exists, "head": head, "baseline": baseline,
        "target": record.get("target"), "dirty": dirty,
        "identity_issues": issues,
        "repair_route": "reconcile_identity" if issues else REPAIR_ROUTES[state],
        "acceptance": "not_assessed",
    }
    return path, record, observed


def require_identity(observed: dict[str, Any], allowed: set[str] | None = None) -> None:
    issues = [issue for issue in observed["identity_issues"] if issue not in (allowed or set())]
    if issues:
        raise SystemExit("[BLOCKED] " + ", ".join(issues))


def absent_surface_issues(repo: Path, observed: dict[str, Any]) -> set[str]:
    """Reception/stacking can use frozen objects after a surface was retired."""
    allowed: set[str] = set()
    if not Path(observed["worktree"]).exists() and worktree_for_branch(repo, observed["branch"]) is None:
        allowed.update({"worktree_unavailable", "worktree_registration_mismatch"})
    if observed["head"] is None:
        allowed.add("branch_unavailable")
    return allowed


def inspect_unit(args: argparse.Namespace) -> dict[str, Any]:
    """Observe one registered unit; do not restore paths or infer authorization."""
    validate_identity(args.unit)
    return observe_unit(git_root(args.repo), args.unit)[2]


def review(args: argparse.Namespace) -> dict[str, Any]:
    """Return a fixed Git review scope without sealing, approvals or test claims."""
    observed = inspect_unit(args)
    if observed["identity_issues"]:
        raise SystemExit("[BLOCKED] " + ", ".join(observed["identity_issues"]))
    repo = git_root(args.repo)
    if str(repo) != observed["worktree"]:
        raise SystemExit("[BLOCKED] review must run in the registered worktree")
    if observed["state"] not in {"in_progress", "sealed"}:
        raise SystemExit("[BLOCKED] review requires an open or sealed unit, not closed work")
    if observed["dirty"]:
        raise SystemExit("[BLOCKED] review cannot capture uncommitted files; preserve and attribute them")
    before = Path(observed["record"]).read_bytes()
    head = observed["head"]
    baseline = resolve_commit(repo, observed["baseline"])
    since = args.since
    if since is not None:
        if re.fullmatch(r"[0-9a-f]{40}|[0-9a-f]{64}", since) is None:
            raise SystemExit("[BLOCKED] --since requires an exact previous review commit SHA")
        since = resolve_commit(repo, since)
        if not is_ancestor(repo, baseline, since) or not is_ancestor(repo, since, head):
            raise SystemExit("[BLOCKED] previous review must be within this unit's baseline..head ancestry")
    review_base = since or baseline
    try:
        captured_inventory = _review_git.inventory(repo, review_base, head)
        paths = [item["path"] for item in captured_inventory]
    except (ValueError, OSError, subprocess.TimeoutExpired) as exc:
        raise SystemExit("[BLOCKED] frozen review inventory unavailable: " + type(exc).__name__) from exc
    tree = git(repo, "rev-parse", f"{head}^{{tree}}")
    # Do not hand off a scope observed across a moving branch or registration.
    if (inspect_unit(args) != observed or Path(observed["record"]).read_bytes() != before):
        raise SystemExit("[BLOCKED] Change Unit changed during review capture; inspect current facts")
    return {
        **observed, "kind": "git_review_scope", "tree": tree,
        "review_base": review_base, "scope": "delta" if since else "unit",
        "changed_paths": paths, "inventory_policy": _review_git.POLICY,
        "inventory_items": captured_inventory,
        "diff_range": f"{review_base}..{head}", "tests": "not_run",
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
    prepare_parser.add_argument("--unit", required=True, help="Unique Change Unit ID within this repository, not a reusable parent-task ID.")
    prepare_parser.add_argument("--slug", required=True)
    prepare_parser.add_argument("--branch")
    prepare_parser.add_argument("--worktree", type=Path, required=True)

    for name in ("resume", "verify", "seal", "inspect", "review"):
        subparser = subparsers.add_parser(name)
        subparser.add_argument("--repo", type=Path, required=True)
        subparser.add_argument("--unit", required=True)
        if name == "review":
            subparser.add_argument("--since", help="Exact previous review commit; report its delta without reusing approval.")

    list_parser = subparsers.add_parser("list")
    list_parser.add_argument("--repo", type=Path, required=True)
    list_parser.add_argument("--format", choices=("summary", "full"), default="summary",
                             help="Default: bounded schema v2 summary. full: unfiltered legacy schema v1.")
    list_parser.add_argument("--unit", help="Filter by exact unit ID, including retired records.")
    list_parser.add_argument("--state", choices=(*REPAIR_ROUTES, "unknown", "all"),
                             help="Default: active units. all includes retired history.")
    list_parser.add_argument("--issues-only", action="store_true", help="Page registration anomalies; not a live Git audit.")
    list_parser.add_argument("--limit", type=int, help="Summary page size, 1..100 (default 10).")
    list_parser.add_argument("--offset", type=int, default=0, help="Summary offset (use next_offset from the previous result).")

    close_parser = subparsers.add_parser("close")
    close_parser.add_argument("--repo", type=Path, required=True)
    close_parser.add_argument("--unit", required=True)
    close_parser.add_argument("--disposition", choices=("integrated", "excluded", "superseded"), required=True)
    close_parser.add_argument("--owner-ref", required=True)
    close_parser.add_argument("--integration-commit")
    close_parser.add_argument("--integration-target", help="Approved final local line; original target and sealed parent stay unchanged.")
    close_parser.add_argument("--target-authorization-ref", help="Existing decision authorizing the explicit receiving line; checked by the caller.")
    close_parser.add_argument(
        "--integration-base",
        help="Target commit before reception; defaults to the receipt's first parent for rewritten history.",
    )

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
    elif args.command == "inspect":
        report = inspect_unit(args)
    elif args.command == "review":
        report = review(args)
    else:
        report = close(args)
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
