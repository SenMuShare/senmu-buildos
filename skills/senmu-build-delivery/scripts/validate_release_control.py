#!/usr/bin/env python3
"""Validate one durable, resumable release-control sheet."""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
from typing import Any


GATE_ORDER = [
    "scope_accounted",
    "integration_complete",
    "candidate_verified",
    "release_authorized",
    "release_verified",
    "git_execution_closed",
]
GATE_STATES = {"pending", "passed", "blocked", "not_applicable"}
ITEM_STATES = {"pending", "include", "exclude", "blocked"}
CLEANUP_STATES = {"pending", "removed", "retained", "blocked"}
RELEASE_STATES = {"planning", "candidate", "authorized", "released", "closed", "failed", "cancelled"}


def nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def refs(value: Any) -> bool:
    return isinstance(value, list) and all(nonempty(item) for item in value)


def validate_record(data: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(data, dict):
        return ["root must be an object"]
    if data.get("schema_version") != 1:
        errors.append("schema_version must be 1")

    release = data.get("release")
    if not isinstance(release, dict):
        return errors + ["release must be an object"]
    for key in ("id", "release_unit", "target_line", "release_source_root"):
        if not nonempty(release.get(key)):
            errors.append(f"release.{key} must be a non-empty string")
    if release.get("status") not in RELEASE_STATES:
        errors.append(f"release.status must be one of {sorted(RELEASE_STATES)}")

    requirements = data.get("requirements")
    if not isinstance(requirements, list):
        errors.append("requirements must be a list")
        requirements = []
    for index, item in enumerate(requirements):
        prefix = f"requirements[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{prefix} must be an object")
            continue
        if not nonempty(item.get("id")):
            errors.append(f"{prefix}.id must be a non-empty string")
        if item.get("disposition") not in ITEM_STATES:
            errors.append(f"{prefix}.disposition must be one of {sorted(ITEM_STATES)}")
        if not refs(item.get("evidence_refs")):
            errors.append(f"{prefix}.evidence_refs must be a list of non-empty strings")
        if item.get("disposition") in {"exclude", "blocked"} and not nonempty(item.get("reason")):
            errors.append(f"{prefix}.reason is required for exclude or blocked")

    units = data.get("change_units")
    if not isinstance(units, list):
        errors.append("change_units must be a list")
        units = []
    included_units: set[str] = set()
    for index, item in enumerate(units):
        prefix = f"change_units[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{prefix} must be an object")
            continue
        unit = item.get("unit")
        disposition = item.get("disposition")
        if not nonempty(unit):
            errors.append(f"{prefix}.unit must be a non-empty string")
        if disposition not in ITEM_STATES:
            errors.append(f"{prefix}.disposition must be one of {sorted(ITEM_STATES)}")
        if not refs(item.get("evidence_refs")) or not refs(item.get("test_refs")):
            errors.append(f"{prefix}.evidence_refs and test_refs must be lists of non-empty strings")
        if disposition == "include":
            if nonempty(unit):
                included_units.add(unit)
            for key in ("branch", "source_commit", "integration_commit"):
                if not nonempty(item.get(key)):
                    errors.append(f"{prefix}.{key} is required for include")
            if not item.get("test_refs"):
                errors.append(f"{prefix}.test_refs must contain verification evidence for include")
        elif disposition in {"exclude", "blocked"}:
            if not nonempty(item.get("reason")):
                errors.append(f"{prefix}.reason is required for exclude or blocked")
            if not item.get("evidence_refs"):
                errors.append(f"{prefix}.evidence_refs must explain exclude or blocked")

    gates = data.get("gates")
    if not isinstance(gates, list):
        errors.append("gates must be a list")
        gates = []
    gate_ids = [item.get("id") for item in gates if isinstance(item, dict)]
    if gate_ids != GATE_ORDER or len(gates) != len(GATE_ORDER):
        errors.append(f"gates must appear exactly once in this order: {GATE_ORDER}")
    gate_states: dict[str, str] = {}
    unfinished_seen = False
    for index, item in enumerate(gates):
        prefix = f"gates[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{prefix} must be an object")
            continue
        gate_id, status = item.get("id"), item.get("status")
        if status not in GATE_STATES:
            errors.append(f"{prefix}.status must be one of {sorted(GATE_STATES)}")
        if not refs(item.get("evidence_refs")):
            errors.append(f"{prefix}.evidence_refs must be a list of non-empty strings")
        if status in {"passed", "not_applicable"} and not item.get("evidence_refs"):
            errors.append(f"{prefix}.evidence_refs is required when status is {status}")
        if status in {"blocked", "not_applicable"} and not nonempty(item.get("reason")):
            errors.append(f"{prefix}.reason is required when status is {status}")
        if unfinished_seen and status in {"passed", "not_applicable"}:
            errors.append(f"{prefix} cannot close before an earlier unfinished gate")
        if status in {"pending", "blocked"}:
            unfinished_seen = True
        if nonempty(gate_id) and isinstance(status, str):
            gate_states[gate_id] = status

    if gate_states.get("scope_accounted") == "passed" and any(
        item.get("disposition") in {"pending", "blocked"} for item in requirements if isinstance(item, dict)
    ):
        errors.append("scope_accounted cannot pass while requirements are pending or blocked")
    if gate_states.get("integration_complete") == "passed" and any(
        item.get("disposition") in {"pending", "blocked"} for item in units if isinstance(item, dict)
    ):
        errors.append("integration_complete cannot pass while change units are pending or blocked")
    if gate_states.get("candidate_verified") == "passed" and not nonempty(release.get("candidate_commit")):
        errors.append("candidate_verified requires release.candidate_commit")
    if gate_states.get("release_authorized") == "passed" and not nonempty(release.get("authorization_ref")):
        errors.append("release_authorized requires release.authorization_ref")
    if gate_states.get("release_verified") == "passed" and not nonempty(release.get("release_record_ref")):
        errors.append("release_verified requires release.release_record_ref")

    cleanup = data.get("cleanup")
    if not isinstance(cleanup, list):
        errors.append("cleanup must be a list")
        cleanup = []
    cleanup_by_unit: dict[str, dict[str, Any]] = {}
    for index, item in enumerate(cleanup):
        prefix = f"cleanup[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{prefix} must be an object")
            continue
        unit, disposition = item.get("unit"), item.get("disposition")
        if not nonempty(unit):
            errors.append(f"{prefix}.unit must be a non-empty string")
        elif unit in cleanup_by_unit:
            errors.append(f"{prefix}.unit duplicates {unit}")
        else:
            cleanup_by_unit[unit] = item
        if disposition not in CLEANUP_STATES:
            errors.append(f"{prefix}.disposition must be one of {sorted(CLEANUP_STATES)}")
        if not refs(item.get("evidence_refs")):
            errors.append(f"{prefix}.evidence_refs must be a list of non-empty strings")
        if disposition in {"removed", "retained"} and not item.get("evidence_refs"):
            errors.append(f"{prefix}.evidence_refs is required for {disposition}")
        if disposition == "retained" and not (
            nonempty(item.get("owner")) and nonempty(item.get("exit_condition"))
        ):
            errors.append(f"{prefix} retained cleanup requires owner and exit_condition")

    if gate_states.get("git_execution_closed") == "not_applicable" and included_units:
        errors.append("git_execution_closed cannot be not_applicable while change units are included")
    if gate_states.get("git_execution_closed") == "passed":
        missing = sorted(included_units - cleanup_by_unit.keys())
        if missing:
            errors.append(f"git_execution_closed is missing cleanup rows for included units: {missing}")
        unfinished_cleanup = sorted(
            unit for unit, item in cleanup_by_unit.items()
            if item.get("disposition") in {"pending", "blocked"}
        )
        if unfinished_cleanup:
            errors.append(f"git_execution_closed has unfinished cleanup rows: {unfinished_cleanup}")
        for unit in included_units:
            if cleanup_by_unit.get(unit, {}).get("disposition") not in {"removed", "retained"}:
                errors.append(f"git_execution_closed requires removed or retained cleanup for {unit}")

    if release.get("status") == "closed" and any(
        gate_states.get(gate_id) not in {"passed", "not_applicable"} for gate_id in GATE_ORDER
    ):
        errors.append("release.status closed requires every gate to be passed or not_applicable")
    recovery = data.get("recovery")
    if release.get("status") != "closed" and not (
        isinstance(recovery, dict)
        and recovery.get("checkpoint") in GATE_ORDER
        and nonempty(recovery.get("next_action"))
    ):
        errors.append("an open release requires recovery.checkpoint and next_action")
    return errors


def validate_live_closeout(data: dict[str, Any], repo: Path) -> tuple[list[str], list[dict[str, Any]]]:
    """Observe included units only; verify ledger/Git identity, not consent or acceptance."""
    spec = importlib.util.spec_from_file_location(
        "buildos_release_workspace", Path(__file__).with_name("inspect_git_workspace.py"))
    assert spec and spec.loader
    inspector = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(inspector)
    errors, observations = [], []
    cleanup = {item["unit"]: item for item in data["cleanup"]}
    closed_claim = any(gate["id"] == "git_execution_closed" and gate["status"] == "passed"
                       for gate in data["gates"])
    target = data["release"]["target_line"]
    target = target if target.startswith("refs/heads/") else "refs/heads/" + target
    seen = set()
    for item in data["change_units"]:
        if item["disposition"] != "include":
            continue
        unit = item["unit"]
        if unit in seen:
            errors.append(f"{unit}: duplicate included unit")
            continue
        seen.add(unit)
        try:
            facts = inspector.unit_facts(repo, unit)
        except (SystemExit, OSError, ValueError) as exc:
            errors.append(f"{unit}: live unit observation failed: {exc}")
            continue
        observations.append(facts)
        if facts["identity_issues"]:
            errors.append(f"{unit}: {', '.join(facts['identity_issues'])}")
        if not closed_claim:
            continue
        if facts["state"] != "integrated":
            errors.append(f"{unit}: included unit is not registered integrated")
        for field in ("branch", "source_commit", "integration_commit"):
            if item[field] != facts[field]:
                errors.append(f"{unit}: {field} differs from the registered receipt")
        observed_target = facts["integration_target"]
        if not isinstance(observed_target, str):
            observed_target = ""
        observed_target = (observed_target if observed_target.startswith("refs/heads/")
                           else "refs/heads/" + observed_target)
        if observed_target != target or facts["receipt_reachable"] is not True:
            errors.append(f"{unit}: receiving line or receipt reachability does not match release")
        proof = facts["integration_proof"]
        if not isinstance(proof, dict) or any(
            proof.get(field) != facts[fact_field]
            for field, fact_field in (("source_head", "source_commit"), ("integration_commit", "integration_commit"))
        ):
            errors.append(f"{unit}: stored content proof does not identify this receipt")
        if isinstance(proof, dict) and "receiving_target" in proof:
            proof_target = proof["receiving_target"]
            if not nonempty(proof_target):
                errors.append(f"{unit}: stored proof receiving target is invalid")
            else:
                proof_target = (proof_target if proof_target.startswith("refs/heads/")
                                else "refs/heads/" + proof_target)
                if proof_target != observed_target:
                    errors.append(f"{unit}: stored proof receiving target differs from the registered receipt")
        if facts["head"] is not None and facts["head"] != facts["source_commit"]:
            errors.append(f"{unit}: retained source branch moved after seal")
        disposition = cleanup[unit]
        if disposition.get("branch") is not None and disposition["branch"] != facts["branch"]:
            errors.append(f"{unit}: cleanup branch differs from registered surface")
        cleanup_path = disposition.get("worktree")
        if cleanup_path is not None and (
            not nonempty(cleanup_path) or Path(cleanup_path).expanduser().absolute()
            != Path(facts["worktree"]).absolute()
        ):
            errors.append(f"{unit}: cleanup path differs from registered surface")
        if disposition["disposition"] == "removed" and any(facts["physical"].values()):
            errors.append(f"{unit}: cleanup says removed but branch/worktree still exists or is registered")
    return errors, observations


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("record", type=Path)
    parser.add_argument("--repo", type=Path, help="Opt-in readback of included units in this repository; never deletes resources.")
    parser.add_argument("--json", action="store_true", help="Report structural and observed facts separately.")
    args = parser.parse_args()
    try:
        data = json.loads(args.record.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        data = None
        errors = [str(exc)]
    else:
        errors = validate_record(data)
    structure_valid = not errors
    observations = []
    live_checked = args.repo is not None and structure_valid
    if live_checked:
        live_errors, observations = validate_live_closeout(data, args.repo)
        errors.extend(live_errors)
    if args.json:
        print(json.dumps({"schema_version": 1, "kind": "release_control_check",
                          "structure_valid": structure_valid, "git_state_checked": live_checked,
                          "units": observations, "errors": errors,
                          "scope": "included_registered_units_only",
                          "limits": "Snapshot and stored proof identity only; no fresh content replay, approval, acceptance, writer-exit or deletion proof beyond observed presence."},
                         ensure_ascii=False, indent=2))
        return 1 if errors else 0
    if errors:
        for error in errors:
            print(f"[ERROR] {error}")
        return 1
    scope = "included-unit Git readback" if live_checked else "structure only; Git not observed"
    print(f"[OK] release control valid: {args.record} ({scope})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
