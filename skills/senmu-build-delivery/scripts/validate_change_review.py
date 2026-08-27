#!/usr/bin/env python3
"""Validate merge-gate change review records and optional Git identity."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path
from typing import Any


STATUSES = {"draft", "review_in_progress", "changes_requested", "approved", "superseded"}
CHANGE_KINDS = {"pending", "code", "docs_config_only", "generated_only"}
GOVERNANCE_LEVELS = {"G0", "G1", "G2", "G3", "G4"}
INVENTORY_METHODS = {"pending", "language_aware", "project_native", "mixed_verified", "manual_verified"}
FILE_CLASSIFICATIONS = {
    "first_party_source", "test_source", "docs_config", "generated", "vendor", "other",
}
CHANGE_TYPES = {"added", "modified", "deleted", "renamed"}
REVIEW_STATUSES = {"pending", "reviewed_pass", "reviewed_with_findings", "blocked", "not_applicable"}
UNIT_KINDS = {
    "function", "method", "constructor", "property_accessor", "lambda",
    "top_level_executable", "other",
}
COMMENT_KINDS = {"docstring", "line", "block", "todo_fixme", "other"}
CHECK_RESULTS = {"pass", "finding", "not_applicable"}
UNIT_CHECKS = {
    "responsibility", "abstraction", "inputs_outputs", "side_effects",
    "errors_resources", "dependencies_architecture", "duplication_economy",
    "tests", "comments_docs",
}
COMMENT_CHECKS = {"accuracy", "necessity", "currency", "safety"}
FINDING_STATUSES = {
    "suspected", "confirmed", "disputed", "accepted_risk", "resolved_unverified",
    "verified_resolved", "false_positive", "superseded",
}
CLOSED_FINDING_STATUSES = {"accepted_risk", "verified_resolved", "false_positive", "superseded"}
SEVERITIES = {"P0", "P1", "P2", "P3"}
CHECK_STATUSES = {"pending", "passed", "failed", "not_applicable"}
REVIEW_IDENTITIES = {"not_assessed", "peer", "independent", "evidence_based_self_review"}
OUTCOMES = {"not_assessed", "changes_requested", "approved", "approved_with_conditions"}
ID_PATTERN = re.compile(r"^[A-Z][A-Z0-9]*(?:-[A-Z0-9]+)+$")
COMMIT_PATTERN = re.compile(r"^[0-9a-f]{7,64}$")
FINGERPRINT_PATTERN = re.compile(r"^sha256:[0-9a-f]{64}$")


def nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def string_list(value: Any) -> bool:
    return isinstance(value, list) and all(nonempty(item) for item in value)


def require_object(value: Any, label: str, errors: list[str]) -> dict[str, Any]:
    if not isinstance(value, dict):
        errors.append(f"{label} must be an object")
        return {}
    return value


def require_list(value: Any, label: str, errors: list[str]) -> list[Any]:
    if not isinstance(value, list):
        errors.append(f"{label} must be a list")
        return []
    return value


def validate_checks(checks: Any, required: set[str], label: str, errors: list[str]) -> bool:
    if not isinstance(checks, dict):
        errors.append(f"{label}.checks must be an object")
        return False
    if set(checks) != required:
        errors.append(
            f"{label}.checks mismatch: missing={sorted(required - set(checks))}, "
            f"extra={sorted(set(checks) - required)}"
        )
        return False
    invalid = sorted(key for key, value in checks.items() if value not in CHECK_RESULTS)
    if invalid:
        errors.append(f"{label}.checks has invalid results: {', '.join(invalid)}")
        return False
    return any(value == "finding" for value in checks.values())


def validate_review_item(
    item: Any,
    *,
    label: str,
    valid_kinds: set[str],
    required_checks: set[str],
    errors: list[str],
) -> tuple[str | None, set[str]]:
    if not isinstance(item, dict):
        errors.append(f"{label} must be an object")
        return None, set()
    item_id = item.get("id")
    if not nonempty(item_id) or not ID_PATTERN.fullmatch(str(item_id)):
        errors.append(f"{label} has invalid id")
        return None, set()
    item_label = f"{label} {item_id}"
    if item.get("kind") not in valid_kinds:
        errors.append(f"{item_label} has invalid kind")
    if not nonempty(item.get("qualified_name")):
        errors.append(f"{item_label} requires qualified_name")
    if not isinstance(item.get("line_start"), int) or not isinstance(item.get("line_end"), int):
        errors.append(f"{item_label} requires integer line range")
    elif item["line_start"] < 1 or item["line_end"] < item["line_start"]:
        errors.append(f"{item_label} has invalid line range")
    if not nonempty(item.get("fingerprint")) or not FINGERPRINT_PATTERN.fullmatch(str(item.get("fingerprint"))):
        errors.append(f"{item_label} requires sha256 fingerprint")
    status = item.get("review_status")
    if status not in REVIEW_STATUSES - {"pending", "blocked", "not_applicable"}:
        errors.append(f"{item_label} has invalid review_status")
    if not string_list(item.get("evidence_refs")) or not item.get("evidence_refs"):
        errors.append(f"{item_label} requires evidence_refs")
    finding_ids = item.get("finding_ids")
    if not string_list(finding_ids):
        errors.append(f"{item_label}.finding_ids must be a string list")
        finding_ids = []
    has_finding_check = validate_checks(item.get("checks"), required_checks, item_label, errors)
    if status == "reviewed_pass" and (finding_ids or has_finding_check):
        errors.append(f"{item_label} reviewed_pass cannot carry findings")
    if status == "reviewed_with_findings" and (not finding_ids or not has_finding_check):
        errors.append(f"{item_label} reviewed_with_findings requires finding checks and IDs")
    return str(item_id), {str(value) for value in finding_ids}


def validate_collection(
    value: Any,
    *,
    label: str,
    valid_kinds: set[str],
    required_checks: set[str],
    errors: list[str],
) -> tuple[set[str], dict[str, set[str]]]:
    section = require_object(value, label, errors)
    if section.get("status") not in {"pending", "complete", "blocked"}:
        errors.append(f"{label}.status is invalid")
    entries = require_list(section.get("items"), f"{label}.items", errors)
    if not entries and not nonempty(section.get("empty_reason")):
        errors.append(f"{label} with no items requires empty_reason")
    ids: set[str] = set()
    references: dict[str, set[str]] = {}
    for index, item in enumerate(entries, start=1):
        item_id, finding_ids = validate_review_item(
            item,
            label=f"{label}.items[{index}]",
            valid_kinds=valid_kinds,
            required_checks=required_checks,
            errors=errors,
        )
        if item_id:
            if item_id in ids:
                errors.append(f"duplicate review item id: {item_id}")
            ids.add(item_id)
            references[item_id] = finding_ids
    return ids, references


def validate_finding(finding: Any, errors: list[str]) -> tuple[str | None, set[str], str | None, str | None]:
    if not isinstance(finding, dict):
        errors.append("finding must be an object")
        return None, set(), None, None
    finding_id = finding.get("id")
    if not nonempty(finding_id) or not ID_PATTERN.fullmatch(str(finding_id)):
        errors.append("finding has invalid id")
        return None, set(), None, None
    label = str(finding_id)
    severity = finding.get("severity")
    status = finding.get("status")
    if severity not in SEVERITIES:
        errors.append(f"{label} has invalid severity")
    if status not in FINDING_STATUSES:
        errors.append(f"{label} has invalid status")
    locations = finding.get("location_ids")
    if not isinstance(locations, list) or not locations or any(not nonempty(item) for item in locations):
        errors.append(f"{label} requires location_ids")
        locations = []
    if not string_list(finding.get("evidence_refs")) or not finding.get("evidence_refs"):
        errors.append(f"{label} requires evidence_refs")
    if status == "verified_resolved":
        if not string_list(finding.get("verification_refs")) or not finding.get("verification_refs"):
            errors.append(f"{label} verified_resolved requires verification_refs")
    if status == "accepted_risk":
        acceptance = require_object(finding.get("acceptance"), f"{label}.acceptance", errors)
        for key in ("owner", "accepted_at", "condition"):
            if not nonempty(acceptance.get(key)):
                errors.append(f"{label}.acceptance.{key} is required")
    return label, {str(item) for item in locations}, str(severity), str(status)


def validate_record(record: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = {
        "schema_version", "review_id", "status", "change", "inventory", "findings",
        "quality_checks", "approval",
    }
    missing = sorted(required - set(record))
    if missing:
        errors.append(f"missing fields: {', '.join(missing)}")
    if record.get("schema_version") != 1:
        errors.append("unsupported schema_version")
    if not nonempty(record.get("review_id")) or not ID_PATTERN.fullmatch(str(record.get("review_id"))):
        errors.append("invalid review_id")
    status = record.get("status")
    if status not in STATUSES:
        errors.append("invalid status")
    approved = status == "approved"

    change = require_object(record.get("change"), "change", errors)
    inventory = require_object(record.get("inventory"), "inventory", errors)
    method = require_object(inventory.get("method"), "inventory.method", errors)
    files = require_list(inventory.get("files"), "inventory.files", errors)
    findings = require_list(record.get("findings"), "findings", errors)
    quality_checks = require_list(record.get("quality_checks"), "quality_checks", errors)
    approval = require_object(record.get("approval"), "approval", errors)

    change_kind = change.get("change_kind")
    governance_level = change.get("governance_level")
    if change_kind not in CHANGE_KINDS:
        errors.append("change.change_kind is invalid")
    if governance_level not in GOVERNANCE_LEVELS:
        errors.append("change.governance_level is invalid")
    if method.get("kind") not in INVENTORY_METHODS:
        errors.append("inventory.method.kind is invalid")
    if not string_list(method.get("tools")):
        errors.append("inventory.method.tools must be a string list")
    if not string_list(method.get("limitations")):
        errors.append("inventory.method.limitations must be a string list")

    if approved:
        for key in ("repository", "integration_target", "source_branch"):
            if not nonempty(change.get(key)):
                errors.append(f"approved review requires change.{key}")
        for key in ("base_commit", "head_commit"):
            if not nonempty(change.get(key)) or not COMMIT_PATTERN.fullmatch(str(change.get(key))):
                errors.append(f"approved review requires valid change.{key}")
        if change.get("base_commit") == change.get("head_commit"):
            errors.append("approved review requires different base and head commits")
        if change_kind == "pending" or (
            change_kind == "code" and governance_level in {"G0", "G1"}
        ):
            errors.append("approved code review requires explicit code kind and G2-G4 level")
        if method.get("kind") == "pending" or not method.get("tools"):
            errors.append("approved review requires completed inventory method and tools")
        if not files:
            errors.append("approved review requires inventory files")

    finding_ids: set[str] = set()
    finding_locations: dict[str, set[str]] = {}
    finding_meta: dict[str, tuple[str | None, str | None]] = {}
    for finding in findings:
        finding_id, locations, severity, finding_status = validate_finding(finding, errors)
        if finding_id:
            if finding_id in finding_ids:
                errors.append(f"duplicate finding id: {finding_id}")
            finding_ids.add(finding_id)
            finding_locations[finding_id] = locations
            finding_meta[finding_id] = (severity, finding_status)

    file_ids: set[str] = set()
    paths: set[str] = set()
    item_ids: set[str] = set()
    item_findings: dict[str, set[str]] = {}
    for index, file_entry in enumerate(files, start=1):
        label = f"inventory.files[{index}]"
        if not isinstance(file_entry, dict):
            errors.append(f"{label} must be an object")
            continue
        file_id = file_entry.get("id")
        if not nonempty(file_id) or not ID_PATTERN.fullmatch(str(file_id)):
            errors.append(f"{label} has invalid id")
            continue
        file_id = str(file_id)
        if file_id in file_ids:
            errors.append(f"duplicate file id: {file_id}")
        file_ids.add(file_id)
        file_label = f"{label} {file_id}"
        path = file_entry.get("path")
        if not nonempty(path):
            errors.append(f"{file_label}.path is required")
        elif str(path) in paths:
            errors.append(f"duplicate changed file path: {path}")
        else:
            paths.add(str(path))
        classification = file_entry.get("classification")
        if classification not in FILE_CLASSIFICATIONS:
            errors.append(f"{file_label} has invalid classification")
        if file_entry.get("change_type") not in CHANGE_TYPES:
            errors.append(f"{file_label} has invalid change_type")
        scope_status = file_entry.get("scope_status")
        if scope_status not in {"included", "excluded_with_reason"}:
            errors.append(f"{file_label} has invalid scope_status")
        if scope_status == "excluded_with_reason":
            if classification in {"first_party_source", "test_source"}:
                errors.append(f"{file_label} first-party code cannot be excluded from merge review")
            if not nonempty(file_entry.get("exclusion_reason")):
                errors.append(f"{file_label} exclusion requires a reason")
            if file_entry.get("review_status") != "not_applicable":
                errors.append(f"{file_label} excluded file must be not_applicable")
            continue
        if file_entry.get("review_status") not in REVIEW_STATUSES:
            errors.append(f"{file_label} has invalid review_status")
        if approved and file_entry.get("review_status") not in {"reviewed_pass", "reviewed_with_findings"}:
            errors.append(f"{file_label} review is not complete")
        if not string_list(file_entry.get("evidence_refs")) or not file_entry.get("evidence_refs"):
            errors.append(f"{file_label} requires evidence_refs")
        line_ranges = file_entry.get("changed_line_ranges")
        if file_entry.get("change_type") != "deleted":
            if not isinstance(line_ranges, list) or not line_ranges:
                errors.append(f"{file_label} requires changed_line_ranges")
            else:
                for range_index, line_range in enumerate(line_ranges, start=1):
                    range_label = f"{file_label}.changed_line_ranges[{range_index}]"
                    if not isinstance(line_range, dict):
                        errors.append(f"{range_label} must be an object")
                    elif (
                        not isinstance(line_range.get("start"), int)
                        or not isinstance(line_range.get("end"), int)
                        or line_range["start"] < 1
                        or line_range["end"] < line_range["start"]
                    ):
                        errors.append(f"{range_label} has invalid range")
        unit_ids, unit_refs = validate_collection(
            file_entry.get("changed_units"),
            label=f"{file_label}.changed_units",
            valid_kinds=UNIT_KINDS,
            required_checks=UNIT_CHECKS,
            errors=errors,
        )
        comment_ids, comment_refs = validate_collection(
            file_entry.get("changed_comments"),
            label=f"{file_label}.changed_comments",
            valid_kinds=COMMENT_KINDS,
            required_checks=COMMENT_CHECKS,
            errors=errors,
        )
        if approved:
            if file_entry.get("changed_units", {}).get("status") != "complete":
                errors.append(f"{file_label}.changed_units must be complete")
            if file_entry.get("changed_comments", {}).get("status") != "complete":
                errors.append(f"{file_label}.changed_comments must be complete")
        for item_id in unit_ids | comment_ids:
            if item_id in item_ids:
                errors.append(f"duplicate review item id across files: {item_id}")
            item_ids.add(item_id)
        item_findings.update(unit_refs)
        item_findings.update(comment_refs)
        direct_findings = {
            finding_id for finding_id, locations in finding_locations.items() if file_id in locations
        }
        referenced_findings = set().union(*unit_refs.values(), *comment_refs.values()) | direct_findings
        if file_entry.get("review_status") == "reviewed_pass" and referenced_findings:
            errors.append(f"{file_label} reviewed_pass cannot reference findings")
        if file_entry.get("review_status") == "reviewed_with_findings" and not referenced_findings:
            errors.append(f"{file_label} reviewed_with_findings requires a finding")

    valid_locations = file_ids | item_ids
    for finding_id, locations in finding_locations.items():
        unknown = sorted(locations - valid_locations)
        if unknown:
            errors.append(f"{finding_id} references unknown locations: {', '.join(unknown)}")
        for item_id in locations & item_ids:
            if finding_id not in item_findings.get(item_id, set()):
                errors.append(f"{finding_id} and {item_id} do not reference each other")
    for item_id, references in item_findings.items():
        unknown = sorted(references - finding_ids)
        if unknown:
            errors.append(f"{item_id} references unknown findings: {', '.join(unknown)}")
        for finding_id in references & finding_ids:
            if item_id not in finding_locations.get(finding_id, set()):
                errors.append(f"{item_id} and {finding_id} do not reference each other")

    for index, check in enumerate(quality_checks, start=1):
        label = f"quality_checks[{index}]"
        if not isinstance(check, dict):
            errors.append(f"{label} must be an object")
            continue
        if not nonempty(check.get("id")) or not ID_PATTERN.fullmatch(str(check.get("id"))):
            errors.append(f"{label} has invalid id")
        check_status = check.get("status")
        if check_status not in CHECK_STATUSES:
            errors.append(f"{label} has invalid status")
        if check_status == "not_applicable":
            if not nonempty(check.get("not_applicable_reason")):
                errors.append(f"{label} not_applicable requires a reason")
        elif check_status in {"passed", "failed"}:
            if not string_list(check.get("evidence_refs")) or not check.get("evidence_refs"):
                errors.append(f"{label} requires evidence_refs")
    if approved:
        if not quality_checks:
            errors.append("approved review requires quality_checks")
        unfinished_checks = [
            str(check.get("id", index)) for index, check in enumerate(quality_checks, start=1)
            if not isinstance(check, dict) or check.get("status") not in {"passed", "not_applicable"}
        ]
        if unfinished_checks:
            errors.append(f"approved review has unfinished quality checks: {', '.join(unfinished_checks)}")

    review_identity = approval.get("review_identity")
    outcome = approval.get("outcome")
    if review_identity not in REVIEW_IDENTITIES:
        errors.append("approval.review_identity is invalid")
    if outcome not in OUTCOMES:
        errors.append("approval.outcome is invalid")
    if approved:
        for key in ("author", "reviewer", "reviewed_head", "reviewed_at"):
            if not nonempty(approval.get(key)):
                errors.append(f"approved review requires approval.{key}")
        if approval.get("reviewed_head") != change.get("head_commit"):
            errors.append("approval.reviewed_head must match change.head_commit")
        if outcome not in {"approved", "approved_with_conditions"}:
            errors.append("approved status requires approved outcome")
        exception = approval.get("exception")
        if change_kind == "code":
            if review_identity not in {"peer", "independent"}:
                if not isinstance(exception, dict):
                    errors.append("code merge review requires peer or independent reviewer")
                else:
                    for key in ("owner", "reason", "approved_at", "expires_at"):
                        if not nonempty(exception.get(key)):
                            errors.append(f"approval.exception.{key} is required")
            elif approval.get("author") == approval.get("reviewer"):
                errors.append("code merge review author and reviewer must differ")
            if governance_level == "G4" and review_identity != "independent":
                errors.append("G4 code merge review requires independent identity")
        open_findings = sorted(
            finding_id for finding_id, (_, finding_status) in finding_meta.items()
            if finding_status not in CLOSED_FINDING_STATUSES
        )
        if open_findings:
            errors.append(f"approved review has open findings: {', '.join(open_findings)}")
        accepted_blockers = sorted(
            finding_id for finding_id, (severity, finding_status) in finding_meta.items()
            if severity in {"P0", "P1"} and finding_status == "accepted_risk"
        )
        if accepted_blockers:
            errors.append(f"approved review cannot accept P0/P1 risk: {', '.join(accepted_blockers)}")
        accepted_risks = {
            finding_id for finding_id, (_, finding_status) in finding_meta.items()
            if finding_status == "accepted_risk"
        }
        if accepted_risks and outcome != "approved_with_conditions":
            errors.append("accepted risk requires approved_with_conditions outcome")
        if not accepted_risks and outcome == "approved_with_conditions":
            errors.append("approved_with_conditions requires accepted risk")
    return errors


def git_output(repo: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(repo), *args],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip() or "git command failed")
    return result.stdout.strip()


def validate_git(record: dict[str, Any], repo: Path, require_current_head: bool) -> list[str]:
    errors: list[str] = []
    change = record.get("change", {})
    base = str(change.get("base_commit") or "")
    head = str(change.get("head_commit") or "")
    try:
        resolved_base = git_output(repo, "rev-parse", base)
        resolved_head = git_output(repo, "rev-parse", head)
        git_output(repo, "merge-base", "--is-ancestor", resolved_base, resolved_head)
    except RuntimeError as exc:
        errors.append(f"git identity validation failed: {exc}")
        return errors
    try:
        changed_paths = set(filter(None, git_output(repo, "diff", "--name-only", resolved_base, resolved_head).splitlines()))
    except RuntimeError as exc:
        errors.append(f"git diff validation failed: {exc}")
        return errors
    recorded_paths = {
        str(item.get("path")) for item in record.get("inventory", {}).get("files", [])
        if isinstance(item, dict) and nonempty(item.get("path"))
    }
    if recorded_paths != changed_paths:
        missing = sorted(changed_paths - recorded_paths)
        extra = sorted(recorded_paths - changed_paths)
        errors.append(f"inventory paths do not match git diff: missing={missing}, extra={extra}")
    if require_current_head:
        try:
            current_head = git_output(repo, "rev-parse", "HEAD")
        except RuntimeError as exc:
            errors.append(f"current HEAD validation failed: {exc}")
        else:
            if current_head != resolved_head:
                errors.append("current HEAD does not match reviewed head")
    return errors


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate merge-gate change review records.")
    parser.add_argument("--record", required=True)
    parser.add_argument("--repo")
    parser.add_argument("--require-current-head", action="store_true")
    args = parser.parse_args()
    record_path = Path(args.record).expanduser().resolve()
    try:
        record = json.loads(record_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(f"[ERROR] change review record is unreadable: {exc}")
    if not isinstance(record, dict):
        raise SystemExit("[ERROR] change review record must be a JSON object")
    errors = validate_record(record)
    if args.require_current_head and not args.repo:
        errors.append("--require-current-head requires --repo")
    if args.repo:
        errors.extend(validate_git(record, Path(args.repo).expanduser().resolve(), args.require_current_head))
    if errors:
        print("[ERROR] change review record is invalid:")
        for error in errors:
            print(f"- {error}")
        raise SystemExit(1)
    files = record.get("inventory", {}).get("files", [])
    units = sum(len(item.get("changed_units", {}).get("items", [])) for item in files if isinstance(item, dict))
    comments = sum(len(item.get("changed_comments", {}).get("items", [])) for item in files if isinstance(item, dict))
    print(
        "[OK] change review record is valid: "
        f"status={record.get('status')}, files={len(files)}, units={units}, comments={comments}"
    )


if __name__ == "__main__":
    main()
