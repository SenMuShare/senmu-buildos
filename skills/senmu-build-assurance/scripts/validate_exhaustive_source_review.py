#!/usr/bin/env python3
"""Validate exhaustive source-governance coverage and closeout records."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


RECORD_STATUSES = {
    "inventory", "review_in_progress", "review_complete",
    "remediation_in_progress", "verified_complete",
}
CONCLUSIONS = {
    "not_assessed", "inconclusive", "not_supported",
    "supported_with_conditions", "supported",
}
REVIEW_IDENTITIES = {"independent", "peer", "evidence_based_self_review"}
INVENTORY_METHODS = {
    "pending", "language_aware", "project_native", "mixed_verified", "manual_verified",
}
FILE_CLASSIFICATIONS = {"first_party_source", "test_source", "generated", "vendor", "other"}
INVENTORY_STATUSES = {"pending", "complete", "blocked"}
REVIEW_STATUSES = {
    "pending", "reviewed_pass", "reviewed_with_findings", "blocked", "not_applicable",
}
UNIT_KINDS = {
    "function", "method", "constructor", "property_accessor",
    "lambda", "top_level_executable", "other",
}
COMMENT_KINDS = {"docstring", "line", "block", "todo_fixme", "other"}
CHECK_RESULTS = {"pass", "finding", "not_applicable"}
UNIT_CHECKS = {
    "responsibility", "abstraction", "inputs_outputs", "side_effects",
    "errors_resources", "dependencies_architecture", "duplication_economy",
    "tests", "comments_docs",
}
COMMENT_CHECKS = {"accuracy", "necessity", "currency", "safety"}
SEVERITIES = {"P0", "P1", "P2", "P3"}
FINDING_STATUSES = {
    "suspected", "confirmed", "disputed", "accepted_risk", "resolved_unverified",
    "verified_resolved", "false_positive", "superseded",
}
CLOSED_FINDING_STATUSES = {"accepted_risk", "verified_resolved", "false_positive", "superseded"}
FULLY_CONFORMING_FINDING_STATUSES = {"verified_resolved", "false_positive", "superseded"}
ID_PATTERN = re.compile(r"^[A-Z][A-Z0-9]*(?:-[A-Z0-9]+)+$")
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


def validate_checks(
    checks: Any, required: set[str], label: str, errors: list[str],
) -> bool:
    if not isinstance(checks, dict):
        errors.append(f"{label}.checks must be an object")
        return False
    if set(checks) != required:
        errors.append(
            f"{label}.checks mismatch: missing={sorted(required - set(checks))}, "
            f"extra={sorted(set(checks) - required)}"
        )
        return False
    invalid = sorted(key for key, result in checks.items() if result not in CHECK_RESULTS)
    if invalid:
        errors.append(f"{label}.checks has invalid results: {', '.join(invalid)}")
        return False
    return any(result == "finding" for result in checks.values())


def validate_review_item(
    item: Any,
    *,
    kind_field: str,
    valid_kinds: set[str],
    required_checks: set[str],
    label: str,
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
    if item.get(kind_field) not in valid_kinds:
        errors.append(f"{item_label} has invalid {kind_field}")
    if not isinstance(item.get("line_start"), int) or not isinstance(item.get("line_end"), int):
        errors.append(f"{item_label} requires integer line_start and line_end")
    elif item["line_start"] < 1 or item["line_end"] < item["line_start"]:
        errors.append(f"{item_label} has invalid line range")
    if not nonempty(item.get("qualified_name")):
        errors.append(f"{item_label} requires qualified_name")
    if not nonempty(item.get("fingerprint")) or not FINGERPRINT_PATTERN.fullmatch(str(item.get("fingerprint"))):
        errors.append(f"{item_label} requires sha256 fingerprint")
    status = item.get("status")
    if status not in {"reviewed_pass", "reviewed_with_findings"}:
        errors.append(f"{item_label} has invalid status")
    if not string_list(item.get("evidence_refs")) or not item.get("evidence_refs"):
        errors.append(f"{item_label} requires evidence_refs")
    finding_ids = item.get("finding_ids")
    if not isinstance(finding_ids, list) or any(not nonempty(entry) for entry in finding_ids):
        errors.append(f"{item_label}.finding_ids must be a string list")
        finding_ids = []
    has_finding_check = validate_checks(item.get("checks"), required_checks, item_label, errors)
    if status == "reviewed_pass" and (finding_ids or has_finding_check):
        errors.append(f"{item_label} reviewed_pass cannot carry findings")
    if status == "reviewed_with_findings" and (not finding_ids or not has_finding_check):
        errors.append(f"{item_label} reviewed_with_findings requires finding checks and IDs")
    return str(item_id), set(str(entry) for entry in finding_ids)


def validate_scan(
    scan: Any,
    *,
    scan_label: str,
    collection_key: str,
    valid_kinds: set[str],
    kind_field: str,
    required_checks: set[str],
    require_complete: bool,
    errors: list[str],
) -> tuple[set[str], dict[str, set[str]]]:
    value = require_object(scan, scan_label, errors)
    status = value.get("status")
    if status not in INVENTORY_STATUSES:
        errors.append(f"{scan_label}.status is invalid")
    if require_complete and status != "complete":
        errors.append(f"{scan_label} must be complete")
    entries = require_list(value.get(collection_key), f"{scan_label}.{collection_key}", errors)
    if not entries and not nonempty(value.get("empty_reason")):
        errors.append(f"{scan_label} with no entries requires empty_reason")
    ids: set[str] = set()
    finding_refs: dict[str, set[str]] = {}
    for index, item in enumerate(entries, start=1):
        item_id, item_findings = validate_review_item(
            item,
            kind_field=kind_field,
            valid_kinds=valid_kinds,
            required_checks=required_checks,
            label=f"{scan_label}.{collection_key}[{index}]",
            errors=errors,
        )
        if item_id:
            if item_id in ids:
                errors.append(f"duplicate review item id: {item_id}")
            ids.add(item_id)
            finding_refs[item_id] = item_findings
    return ids, finding_refs


def validate_finding(
    finding: Any, errors: list[str],
) -> tuple[str | None, set[str], str | None, str | None]:
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
    return str(finding_id), set(str(item) for item in locations), str(severity), str(status)


def validate_record(record: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = {
        "schema_version", "review_id", "status", "conclusion", "review_identity",
        "target", "scope", "inventory", "findings", "verification",
    }
    missing = sorted(required - set(record))
    if missing:
        errors.append(f"missing fields: {', '.join(missing)}")
    if record.get("schema_version") != 1:
        errors.append("unsupported schema_version")
    if not nonempty(record.get("review_id")) or not ID_PATTERN.fullmatch(str(record.get("review_id"))):
        errors.append("invalid review_id")
    status = record.get("status")
    conclusion = record.get("conclusion")
    if status not in RECORD_STATUSES:
        errors.append("invalid status")
    if conclusion not in CONCLUSIONS:
        errors.append("invalid conclusion")
    if record.get("review_identity") not in REVIEW_IDENTITIES:
        errors.append("invalid review_identity")
    coverage_complete = status in {"review_complete", "remediation_in_progress", "verified_complete"}
    verified_complete = status == "verified_complete"

    target = require_object(record.get("target"), "target", errors)
    scope = require_object(record.get("scope"), "scope", errors)
    inventory = require_object(record.get("inventory"), "inventory", errors)
    method = require_object(inventory.get("method"), "inventory.method", errors)
    files = require_list(inventory.get("files"), "inventory.files", errors)
    findings = require_list(record.get("findings"), "findings", errors)
    verification = require_object(record.get("verification"), "verification", errors)

    if method.get("kind") not in INVENTORY_METHODS:
        errors.append("inventory.method.kind is invalid")
    if not string_list(method.get("tools")):
        errors.append("inventory.method.tools must be a string list")
    if not string_list(method.get("limitations")):
        errors.append("inventory.method.limitations must be a string list")
    if not isinstance(scope.get("exclusions"), list):
        errors.append("scope.exclusions must be a list")
    if coverage_complete:
        for key in ("baseline_identity", "current_identity", "captured_at"):
            if not nonempty(target.get(key)):
                errors.append(f"complete coverage requires target.{key}")
        for key in ("release_units", "systems", "included_roots"):
            if not string_list(scope.get(key)) or not scope.get(key):
                errors.append(f"complete coverage requires scope.{key}")
        if method.get("kind") == "pending":
            errors.append("complete coverage requires a completed inventory method")
        if not method.get("tools"):
            errors.append("complete coverage requires inventory.method.tools")
        if not files:
            errors.append("complete coverage requires inventory files")

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
    review_item_ids: set[str] = set()
    item_finding_refs: dict[str, set[str]] = {}
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
        for key in ("path", "release_unit", "system", "module"):
            if not nonempty(file_entry.get(key)):
                errors.append(f"{file_label}.{key} is required")
        if file_entry.get("classification") not in FILE_CLASSIFICATIONS:
            errors.append(f"{file_label} has invalid classification")
        scope_status = file_entry.get("scope_status")
        if scope_status not in {"included", "excluded_with_reason"}:
            errors.append(f"{file_label} has invalid scope_status")
        if scope_status == "excluded_with_reason":
            if not nonempty(file_entry.get("exclusion_reason")):
                errors.append(f"{file_label} exclusion requires a reason")
            if file_entry.get("review_status") != "not_applicable":
                errors.append(f"{file_label} excluded file must be not_applicable")
            continue
        if file_entry.get("inventory_status") not in INVENTORY_STATUSES:
            errors.append(f"{file_label} has invalid inventory_status")
        if file_entry.get("review_status") not in REVIEW_STATUSES:
            errors.append(f"{file_label} has invalid review_status")
        if coverage_complete:
            if file_entry.get("inventory_status") != "complete":
                errors.append(f"{file_label} inventory is not complete")
            if file_entry.get("review_status") not in {"reviewed_pass", "reviewed_with_findings"}:
                errors.append(f"{file_label} review is not complete")
        if not string_list(file_entry.get("evidence_refs")) or not file_entry.get("evidence_refs"):
            errors.append(f"{file_label} requires evidence_refs")
        unit_ids, unit_refs = validate_scan(
            file_entry.get("symbol_scan"),
            scan_label=f"{file_label}.symbol_scan",
            collection_key="units",
            valid_kinds=UNIT_KINDS,
            kind_field="kind",
            required_checks=UNIT_CHECKS,
            require_complete=coverage_complete,
            errors=errors,
        )
        comment_ids, comment_refs = validate_scan(
            file_entry.get("comment_scan"),
            scan_label=f"{file_label}.comment_scan",
            collection_key="comments",
            valid_kinds=COMMENT_KINDS,
            kind_field="kind",
            required_checks=COMMENT_CHECKS,
            require_complete=coverage_complete,
            errors=errors,
        )
        for item_id in unit_ids | comment_ids:
            if item_id in review_item_ids:
                errors.append(f"duplicate review item id across files: {item_id}")
            review_item_ids.add(item_id)
        item_finding_refs.update(unit_refs)
        item_finding_refs.update(comment_refs)
        direct_file_findings = {
            finding_id for finding_id, locations in finding_locations.items()
            if file_id in locations
        }
        referenced_findings = set().union(*unit_refs.values(), *comment_refs.values())
        referenced_findings |= direct_file_findings
        if file_entry.get("review_status") == "reviewed_pass" and referenced_findings:
            errors.append(f"{file_label} reviewed_pass cannot reference findings")
        if file_entry.get("review_status") == "reviewed_with_findings" and not referenced_findings:
            errors.append(f"{file_label} reviewed_with_findings requires a finding")

    valid_locations = file_ids | review_item_ids
    for finding_id, locations in finding_locations.items():
        unknown = sorted(locations - valid_locations)
        if unknown:
            errors.append(f"{finding_id} references unknown locations: {', '.join(unknown)}")
    for item_id, references in item_finding_refs.items():
        unknown = sorted(references - finding_ids)
        if unknown:
            errors.append(f"{item_id} references unknown findings: {', '.join(unknown)}")
        for finding_id in references & finding_ids:
            if item_id not in finding_locations.get(finding_id, set()):
                errors.append(f"{item_id} and {finding_id} do not reference each other")
    for finding_id, locations in finding_locations.items():
        for item_id in locations & review_item_ids:
            if finding_id not in item_finding_refs.get(item_id, set()):
                errors.append(f"{finding_id} and {item_id} do not reference each other")

    if verified_complete:
        if verification.get("status") != "passed":
            errors.append("verified_complete requires passed verification")
        if not nonempty(verification.get("frozen_target")):
            errors.append("verified_complete requires verification.frozen_target")
        if not string_list(verification.get("evidence_refs")) or not verification.get("evidence_refs"):
            errors.append("verified_complete requires verification.evidence_refs")
        if target.get("current_identity") != verification.get("frozen_target"):
            errors.append("verification frozen_target must match target.current_identity")
        open_findings = sorted(
            finding_id for finding_id, (_, finding_status) in finding_meta.items()
            if finding_status not in CLOSED_FINDING_STATUSES
        )
        if open_findings:
            errors.append(f"verified_complete has open findings: {', '.join(open_findings)}")
        accepted_blockers = sorted(
            finding_id for finding_id, (severity, finding_status) in finding_meta.items()
            if severity in {"P0", "P1"} and finding_status == "accepted_risk"
        )
        if accepted_blockers:
            errors.append(f"verified_complete cannot accept P0/P1 risk: {', '.join(accepted_blockers)}")
        if conclusion not in {"supported", "supported_with_conditions"}:
            errors.append("verified_complete requires a supported conclusion")
        accepted_risks = {
            finding_id for finding_id, (_, finding_status) in finding_meta.items()
            if finding_status == "accepted_risk"
        }
        if conclusion == "supported" and accepted_risks:
            errors.append("supported conclusion cannot contain accepted_risk findings")
        if conclusion == "supported_with_conditions" and not accepted_risks:
            errors.append("supported_with_conditions requires an accepted_risk finding")
        if conclusion == "supported":
            nonconforming = sorted(
                finding_id for finding_id, (_, finding_status) in finding_meta.items()
                if finding_status not in FULLY_CONFORMING_FINDING_STATUSES
            )
            if nonconforming:
                errors.append(f"supported conclusion has nonconforming findings: {', '.join(nonconforming)}")
    elif conclusion in {"supported", "supported_with_conditions"}:
        errors.append("supported conclusions require verified_complete status")

    return errors


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate exhaustive source review control records.")
    parser.add_argument("--record", required=True)
    args = parser.parse_args()
    record_path = Path(args.record).expanduser().resolve()
    try:
        value = json.loads(record_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(f"[ERROR] review record is unreadable: {exc}")
    if not isinstance(value, dict):
        raise SystemExit("[ERROR] review record must be a JSON object")
    errors = validate_record(value)
    if errors:
        print("[ERROR] exhaustive source review record is invalid:")
        for error in errors:
            print(f"- {error}")
        raise SystemExit(1)
    files = value.get("inventory", {}).get("files", [])
    included = [item for item in files if isinstance(item, dict) and item.get("scope_status") == "included"]
    unit_count = sum(len(item.get("symbol_scan", {}).get("units", [])) for item in included)
    comment_count = sum(len(item.get("comment_scan", {}).get("comments", [])) for item in included)
    print(
        "[OK] exhaustive source review record is valid: "
        f"status={value.get('status')}, files={len(included)}, units={unit_count}, comments={comment_count}"
    )


if __name__ == "__main__":
    main()
