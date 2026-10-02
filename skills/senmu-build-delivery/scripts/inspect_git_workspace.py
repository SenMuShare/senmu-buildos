#!/usr/bin/env python3
"""Read-only Git branch/worktree inventory and execution-surface coaching."""

from __future__ import annotations

import argparse
import importlib.util
import os
import json
import subprocess
from pathlib import Path
from typing import Any


INTENTS = ("inventory", "read", "write", "parallel-write", "release-closeout")


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


def recommend_execution_surface(
    *,
    intent: str,
    current_dirty: bool,
    active_other_worktree_count: int,
    exclusive_writer: bool,
) -> dict[str, Any]:
    """Translate ordinary task intent into a safe Git execution-surface choice."""
    if intent == "read":
        return {
            "mode": "read_only_existing_worktree",
            "requires_isolation": False,
            "reason": "Read-only work does not need a branch or extra worktree.",
        }
    if intent == "parallel-write":
        return {
            "mode": "isolated_short_branch_worktree",
            "requires_isolation": True,
            "reason": "Concurrent writers must not share one physical checkout.",
        }
    if intent == "release-closeout":
        return {
            "mode": "release_intake_then_clean_release_source",
            "requires_isolation": current_dirty or active_other_worktree_count > 0,
            "reason": (
                "Classify completed in-scope changes before integrating into one clean "
                "release source; never merge every branch mechanically."
            ),
        }
    if intent == "write":
        if current_dirty:
            return {
                "mode": "preserve_dirty_owner_then_isolate_or_handoff",
                "requires_isolation": True,
                "reason": (
                    "Existing uncommitted changes may belong to another task or user; "
                    "do not mix, stash, reset, or overwrite them."
                ),
            }
        if active_other_worktree_count > 0:
            return {
                "mode": "isolated_short_branch_worktree",
                "requires_isolation": True,
                "reason": "Other execution surfaces exist, so concurrent writing is plausible.",
            }
        if not exclusive_writer:
            return {
                "mode": "isolated_short_branch_worktree",
                "requires_isolation": True,
                "reason": (
                    "Codex writing is parallel-capable by default: another session may begin "
                    "before this edit finishes, so current absence of another writer is not "
                    "an exclusive-write guarantee."
                ),
            }
        return {
            "mode": "short_branch_current_worktree",
            "requires_isolation": False,
            "reason": (
                "An explicit exclusive-write guarantee covers the whole edit window, so a "
                "clean checkout can use one short branch without another directory."
            ),
        }
    return {
        "mode": "inventory_only",
        "requires_isolation": False,
        "reason": "No execution intent was supplied; report facts without choosing a write strategy.",
    }


def unit_facts(repo: Path, unit: str) -> dict[str, Any]:
    """Read one registered unit and its physical surface; never restore or delete it."""
    spec = importlib.util.spec_from_file_location(
        "buildos_workspace_change_unit", Path(__file__).with_name("manage_change_unit.py"))
    assert spec and spec.loader
    manager = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(manager)
    manager.validate_identity(unit)
    repo = manager.git_root(repo)
    _, record, observed = manager.observe_unit(repo, unit)
    expected = Path(record["worktree"]).expanduser()
    raw = manager.git(repo, "worktree", "list", "--porcelain", "-z")
    registrations = []
    for block in raw.split("\0\0"):
        fields = dict(field.partition(" ")[::2] for field in block.split("\0") if field)
        if "worktree" in fields:
            registrations.append(fields)
    expected_path = expected.resolve()
    expected_branch = "refs/heads/" + record["branch"]
    related_registrations = [
        {"path": item["worktree"], "branch": item.get("branch")}
        for item in registrations
        if Path(item["worktree"]).resolve() == expected_path
        or item.get("branch") == expected_branch]
    registered = bool(related_registrations)
    target = record.get("integration_target", record.get("target"))
    receipt = record.get("integration_commit")
    target_head, reachable = None, None
    issues = list(observed["identity_issues"])
    if any(Path(item["path"]).resolve() != expected_path or item["branch"] != expected_branch
           for item in related_registrations):
        if "worktree_registration_mismatch" not in issues:
            issues.append("worktree_registration_mismatch")
    if record["state"] == "integrated":
        try:
            if (not isinstance(target, str) or not target.strip()
                    or not isinstance(receipt, str) or manager.COMMIT_PATTERN.fullmatch(receipt) is None):
                raise SystemExit("invalid receiving identity")
            target_head = manager.resolve_commit(repo, target)
            reachable = bool(receipt and manager.is_ancestor(repo, receipt, target_head))
        except SystemExit:
            issues.append("receiving_line_or_receipt_unresolved")
    _, final_record, final_observed = manager.observe_unit(repo, unit)
    if final_record != record or final_observed != observed:
        issues.append("unit_changed_during_observation")
    if raw != manager.git(repo, "worktree", "list", "--porcelain", "-z"):
        issues.append("worktree_registration_changed_during_observation")
    if target_head is not None:
        try:
            if manager.resolve_commit(repo, target) != target_head:
                issues.append("receiving_line_changed_during_observation")
        except SystemExit:
            issues.append("receiving_line_changed_during_observation")
    return {
        **observed, "identity_issues": issues,
        "source_commit": record.get("head"), "integration_target": target,
        "integration_commit": receipt, "integration_proof": record.get("integration_proof"),
        "target_head": target_head, "receipt_reachable": reachable,
        "worktree_registrations": related_registrations,
        "physical": {"branch_exists": observed["head"] is not None,
                     "worktree_registered": registered,
                     "worktree_path_present": os.path.lexists(expected)},
        "authority": "not_assessed", "writer_exit": "not_assessed",
        "observation_scope": "registered_unit_snapshot_not_deletion_permission",
    }


def inspect_registered_unit(repo: Path, unit: str, intent: str) -> dict[str, Any]:
    facts = unit_facts(repo, unit)
    issues = set(facts["identity_issues"])
    recoverable_absence = (
        issues <= {"worktree_unavailable", "worktree_registration_mismatch"}
        and not facts["physical"]["worktree_path_present"]
        and not facts["physical"]["worktree_registered"])
    if intent in {"read", "inventory", "release-closeout"}:
        mode = "read_only_registered_unit"
    elif issues and not recoverable_absence:
        mode = "reconcile_registered_unit"
    elif facts["state"] == "in_progress":
        mode = "resume_existing_unit" if intent == "write" else "establish_existing_writer_handoff"
    else:
        mode = facts["repair_route"]
    return {
        "schema_version": 2, "kind": "registered_unit_workspace",
        "repository_root": facts["repository_root"], "change_unit": facts,
        "execution_recommendation": {
            "mode": mode, "unit": unit, "worktree": facts["worktree"],
            "reason": "Use the task owner's exact unit ID. Inspection neither grants writing nor proves the prior writer exited; do not create a sibling for a known unit.",
        },
    }


def inspect(
    repo_arg: Path,
    target: str,
    protected: set[str],
    intent: str = "inventory",
    exclusive_writer: bool = False,
    unit: str | None = None,
) -> dict[str, Any]:
    if unit is not None:
        return inspect_registered_unit(repo_arg, unit, intent)
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
    current_path = repo
    current_worktree = next(
        (item for item in inspected_worktrees if Path(str(item["path"])) == current_path),
        None,
    )
    if current_worktree is None and current_path == repo:
        current_worktree = next(
            (item for item in inspected_worktrees if item["is_primary"]),
            None,
        )
    current_dirty = bool(current_worktree and current_worktree["dirty"])
    active_other_worktree_count = sum(
        1
        for item in inspected_worktrees
        if Path(str(item["path"])) != current_path
        and item["classification"]
        in {"dirty_review_required", "unmerged_review_required", "detached_review_required"}
    )

    return {
        "schema_version": 1,
        "repository_root": str(repo),
        "primary_worktree": str(primary_path),
        "target": target,
        "target_head": target_head,
        "remotes": remotes,
        "worktrees": inspected_worktrees,
        "branches": branches,
        "execution_recommendation": recommend_execution_surface(
            intent=intent,
            current_dirty=current_dirty,
            active_other_worktree_count=active_other_worktree_count,
            exclusive_writer=exclusive_writer,
        ),
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
    parser.add_argument(
        "--intent",
        choices=INTENTS,
        default="inventory",
        help="Translate task intent into a read-only execution-surface recommendation.",
    )
    parser.add_argument(
        "--exclusive-writer",
        action="store_true",
        help=(
            "Use only when project authority or the harness guarantees that no other writer "
            "can appear for the entire edit window."
        ),
    )
    parser.add_argument("--unit", help="Exact Change Unit ID recovered from the authoritative task; never inferred from a title.")
    parser.add_argument("--compact", action="store_true")
    args = parser.parse_args()
    report = inspect(
        args.repo,
        args.target,
        set(args.protected),
        args.intent,
        args.exclusive_writer,
        args.unit,
    )
    print(json.dumps(report, ensure_ascii=False, indent=None if args.compact else 2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
