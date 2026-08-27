#!/usr/bin/env python3
"""Validate a file-backed mature-project governance control record."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


TASK_STATUSES = {"planned", "active", "blocked", "verifying", "completed", "cancelled", "archived"}
STAGE_STATUSES = {"planned", "active", "blocked", "completed", "not_applicable"}
SEVERITIES = {"P0", "P1", "P2", "P3"}
FINDING_STATUSES = {
    "suspected",
    "confirmed",
    "accepted_risk",
    "resolved_unverified",
    "verified_resolved",
    "false_positive",
    "superseded",
}
DECISIONS = {"pending", "remediate", "accept_risk", "defer", "false_positive"}
AUTHORIZATION_STATUSES = {"pending", "approved", "declined", "not_required"}
REVIEW_STATUSES = {"pending", "passed", "failed"}
REVIEW_IDENTITIES = {"independent", "peer", "evidence_based_self_review"}
RECOVERY_STATUSES = {"pending", "verified", "not_applicable"}
CLEANUP_STATUSES = {"pending_user_decision", "retain", "archive", "delete_authorized"}
FINAL_FINDING_STATUSES = {"accepted_risk", "verified_resolved", "false_positive", "superseded"}
ID_PATTERN = re.compile(r"^[A-Z][A-Z0-9]*(?:-[A-Z0-9]+)+$")


def nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def string_list(value: Any) -> bool:
    return isinstance(value, list) and all(nonempty(item) for item in value)


def approval_complete(value: Any) -> bool:
    return isinstance(value, dict) and nonempty(value.get("approved_by")) and nonempty(value.get("approved_at"))


def require_object(record: dict[str, Any], key: str, errors: list[str]) -> dict[str, Any]:
    value = record.get(key)
    if not isinstance(value, dict):
        errors.append(f"{key} must be an object")
        return {}
    return value


def require_list(record: dict[str, Any], key: str, errors: list[str]) -> list[Any]:
    value = record.get(key)
    if not isinstance(value, list):
        errors.append(f"{key} must be a list")
        return []
    return value


def validate_finding(finding: Any, completed: bool, errors: list[str]) -> None:
    if not isinstance(finding, dict):
        errors.append("findings entries must be objects")
        return
    finding_id = finding.get("id")
    label = str(finding_id or "<unknown>")
    if not nonempty(finding_id) or not ID_PATTERN.fullmatch(str(finding_id)):
        errors.append(f"finding has invalid id: {label}")
    severity = finding.get("severity")
    status = finding.get("status")
    if severity not in SEVERITIES:
        errors.append(f"{label} has invalid severity")
    if status not in FINDING_STATUSES:
        errors.append(f"{label} has invalid status")
    if not nonempty(finding.get("owner")):
        errors.append(f"{label} has no owner")
    if not string_list(finding.get("evidence_refs")) or not finding.get("evidence_refs"):
        errors.append(f"{label} must have evidence_refs")

    decision = finding.get("decision")
    if not isinstance(decision, dict) or decision.get("status") not in DECISIONS:
        errors.append(f"{label} has invalid decision")
        return
    decision_status = decision.get("status")
    if decision_status != "pending" and not approval_complete(decision):
        errors.append(f"{label} decision must record approved_by and approved_at")
    if severity in {"P0", "P1"} and decision_status == "defer":
        errors.append(f"{label} blocking finding cannot be deferred")

    remediation = finding.get("remediation")
    verification = finding.get("verification")
    if decision_status == "remediate":
        if not isinstance(remediation, dict):
            errors.append(f"{label} remediation must be an object")
        else:
            if not nonempty(remediation.get("task_id")):
                errors.append(f"{label} remediation has no task_id")
            if not string_list(remediation.get("change_refs")) or not remediation.get("change_refs"):
                errors.append(f"{label} remediation has no change_refs")
        if not isinstance(verification, dict) or verification.get("status") != "passed":
            errors.append(f"{label} remediation has not passed verification")
        elif not string_list(verification.get("evidence_refs")) or not verification.get("evidence_refs"):
            errors.append(f"{label} verification has no evidence_refs")
        if completed and status != "verified_resolved":
            errors.append(f"{label} remediated finding is not verified_resolved")
    elif decision_status in {"accept_risk", "defer"}:
        if completed and status != "accepted_risk":
            errors.append(f"{label} accepted or deferred finding is not accepted_risk")
    elif decision_status == "false_positive":
        if not isinstance(verification, dict) or verification.get("status") != "passed":
            errors.append(f"{label} false-positive decision lacks passed verification")
        elif not string_list(verification.get("evidence_refs")) or not verification.get("evidence_refs"):
            errors.append(f"{label} false-positive verification has no evidence_refs")
        if completed and status != "false_positive":
            errors.append(f"{label} false-positive decision has inconsistent status")

    if completed:
        if decision_status == "pending":
            errors.append(f"{label} has no user or owner decision")
        if status not in FINAL_FINDING_STATUSES:
            errors.append(f"{label} is not closed or accepted")
        if status == "resolved_unverified":
            errors.append(f"{label} is resolved but not re-reviewed")


def validate_record(record: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = {
        "schema_version",
        "governance_id",
        "status",
        "authoritative_task_owner",
        "baseline",
        "implementation_authorization",
        "coverage",
        "stages",
        "findings",
        "remediation_waves",
        "final_review",
        "recovery",
        "cleanup",
    }
    missing = sorted(required - record.keys())
    if missing:
        errors.append(f"missing fields: {', '.join(missing)}")
    if record.get("schema_version") != 1:
        errors.append("unsupported schema_version")
    governance_id = record.get("governance_id")
    if not nonempty(governance_id) or not ID_PATTERN.fullmatch(str(governance_id)):
        errors.append("invalid governance_id")
    status = record.get("status")
    if status not in TASK_STATUSES:
        errors.append("invalid status")
    completed = status == "completed"

    task_owner = require_object(record, "authoritative_task_owner", errors)
    for key in ("kind", "locator", "task_id"):
        if not nonempty(task_owner.get(key)):
            errors.append(f"authoritative_task_owner.{key} is required")

    baseline = require_object(record, "baseline", errors)
    if baseline.get("status") not in {"pending", "frozen"}:
        errors.append("baseline.status must be pending or frozen")
    if not isinstance(baseline.get("release_units"), list):
        errors.append("baseline.release_units must be a list")
    if not isinstance(baseline.get("evidence_refs"), list):
        errors.append("baseline.evidence_refs must be a list")
    if completed:
        if baseline.get("status") != "frozen":
            errors.append("completed governance requires a frozen baseline")
        for key in ("captured_at", "target_identity"):
            if not nonempty(baseline.get(key)):
                errors.append(f"completed governance requires baseline.{key}")
        if not string_list(baseline.get("evidence_refs")) or not baseline.get("evidence_refs"):
            errors.append("completed governance requires baseline evidence_refs")

    authorization = require_object(record, "implementation_authorization", errors)
    if authorization.get("status") not in AUTHORIZATION_STATUSES:
        errors.append("implementation_authorization.status is invalid")
    if not isinstance(authorization.get("scope"), list):
        errors.append("implementation_authorization.scope must be a list")
    if authorization.get("status") == "approved" and not approval_complete(authorization):
        errors.append("approved implementation_authorization lacks approver or time")
    if completed and authorization.get("status") == "pending":
        errors.append("completed governance cannot leave implementation authorization pending")

    coverage = require_object(record, "coverage", errors)
    if coverage.get("status") not in {"pending", "assessed"}:
        errors.append("coverage.status must be pending or assessed")
    if not isinstance(coverage.get("evidence_refs"), list):
        errors.append("coverage.evidence_refs must be a list")
    if not isinstance(coverage.get("unassessed"), list):
        errors.append("coverage.unassessed must be a list")
    if completed:
        if coverage.get("status") != "assessed":
            errors.append("completed governance requires assessed coverage")
        if not string_list(coverage.get("evidence_refs")) or not coverage.get("evidence_refs"):
            errors.append("completed governance requires coverage evidence_refs")

    stages = require_list(record, "stages", errors)
    stage_ids: set[str] = set()
    for stage in stages:
        if not isinstance(stage, dict) or not nonempty(stage.get("id")):
            errors.append("stage has no id")
            continue
        if stage["id"] in stage_ids:
            errors.append(f"duplicate stage id: {stage['id']}")
        stage_ids.add(stage["id"])
        if stage.get("status") not in STAGE_STATUSES:
            errors.append(f"stage {stage['id']} has invalid status")
        if not isinstance(stage.get("evidence_refs"), list):
            errors.append(f"stage {stage['id']} evidence_refs must be a list")
        if completed and stage.get("status") not in {"completed", "not_applicable"}:
            errors.append(f"completed governance has unfinished stage: {stage['id']}")

    findings = require_list(record, "findings", errors)
    finding_ids: set[str] = set()
    for finding in findings:
        validate_finding(finding, completed, errors)
        if isinstance(finding, dict) and nonempty(finding.get("id")):
            if finding["id"] in finding_ids:
                errors.append(f"duplicate finding id: {finding['id']}")
            finding_ids.add(finding["id"])

    waves = require_list(record, "remediation_waves", errors)
    for wave in waves:
        if not isinstance(wave, dict) or not nonempty(wave.get("id")):
            errors.append("remediation wave has no id")
            continue
        if wave.get("status") not in STAGE_STATUSES:
            errors.append(f"remediation wave {wave['id']} has invalid status")
        linked = wave.get("finding_ids")
        if not isinstance(linked, list) or not linked:
            errors.append(f"remediation wave {wave['id']} has no finding_ids")
        elif any(item not in finding_ids for item in linked):
            errors.append(f"remediation wave {wave['id']} references unknown finding")
        if completed and wave.get("status") not in {"completed", "not_applicable"}:
            errors.append(f"completed governance has unfinished remediation wave: {wave['id']}")

    if any(
        isinstance(finding, dict)
        and isinstance(finding.get("decision"), dict)
        and finding["decision"].get("status") == "remediate"
        for finding in findings
    ) and authorization.get("status") != "approved":
        errors.append("remediation exists without approved implementation authorization")

    final_review = require_object(record, "final_review", errors)
    if final_review.get("status") not in REVIEW_STATUSES:
        errors.append("final_review.status is invalid")
    if final_review.get("review_identity") not in REVIEW_IDENTITIES | {None}:
        errors.append("final_review.review_identity is invalid")
    if completed:
        if final_review.get("status") != "passed":
            errors.append("completed governance requires a passed final_review")
        if not nonempty(final_review.get("frozen_target")):
            errors.append("completed governance requires final_review.frozen_target")
        if final_review.get("review_identity") not in REVIEW_IDENTITIES:
            errors.append("completed governance requires final_review.review_identity")
        if not nonempty(final_review.get("reviewed_at")):
            errors.append("completed governance requires final_review.reviewed_at")
        if not string_list(final_review.get("evidence_refs")) or not final_review.get("evidence_refs"):
            errors.append("completed governance requires final_review evidence_refs")

    recovery = require_object(record, "recovery", errors)
    if recovery.get("status") not in RECOVERY_STATUSES:
        errors.append("recovery.status is invalid")
    if not isinstance(recovery.get("evidence_refs"), list):
        errors.append("recovery.evidence_refs must be a list")
    if completed and recovery.get("status") == "pending":
        errors.append("completed governance cannot leave recovery pending")
    if recovery.get("status") == "verified" and (
        not string_list(recovery.get("evidence_refs")) or not recovery.get("evidence_refs")
    ):
        errors.append("verified recovery requires evidence_refs")

    cleanup = require_object(record, "cleanup", errors)
    if cleanup.get("status") not in CLEANUP_STATUSES:
        errors.append("cleanup.status is invalid")
    if completed and cleanup.get("status") == "pending_user_decision":
        errors.append("completed governance cannot leave cleanup pending user decision")
    if cleanup.get("status") in {"retain", "archive", "delete_authorized"} and not approval_complete(cleanup):
        errors.append("terminal cleanup decision lacks approver or time")
    return errors


def load_record(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(f"[ERROR] governance control record is unreadable: {exc}") from exc
    if not isinstance(value, dict):
        raise SystemExit("[ERROR] governance control record must be a JSON object")
    return value


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--record", required=True, type=Path)
    args = parser.parse_args()
    errors = validate_record(load_record(args.record))
    if errors:
        for error in errors:
            print(f"[ERROR] {error}")
        raise SystemExit(1)
    print(f"[OK] mature-project governance record is valid: {args.record}")


if __name__ == "__main__":
    main()
