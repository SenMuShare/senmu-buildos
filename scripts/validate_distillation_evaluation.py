#!/usr/bin/env python3
"""Validate a differential behavior-evaluation receipt for distilled rules."""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any


REQUIRED_ROLES = {"target", "non_trigger", "exception", "adversarial"}
VALID_VERDICTS = {"improved", "unchanged", "regressed", "invalidated"}
VALID_CONCLUSIONS = {"accept", "revise", "reject", "invalidated"}
VALID_REVIEW_IDENTITIES = {"evidence_based_self_review", "independent_review"}


def fail(message: str) -> None:
    raise ValueError(message)


def require_text(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        fail(f"{field} must be a non-empty string")
    return value.strip()


def require_text_list(value: Any, field: str) -> list[str]:
    if not isinstance(value, list) or not value:
        fail(f"{field} must be a non-empty list")
    result = [require_text(item, f"{field}[]") for item in value]
    if len(result) != len(set(result)):
        fail(f"{field} must not contain duplicates")
    return result


def load_receipt(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        fail(f"cannot read evaluation receipt: {exc}")
    if not isinstance(data, dict):
        fail("evaluation receipt root must be an object")
    return data


def validate_surface(data: dict[str, Any], field: str) -> dict[str, str]:
    value = data.get(field)
    if not isinstance(value, dict):
        fail(f"{field} must be an object")
    return {
        key: require_text(value.get(key), f"{field}.{key}")
        for key in ("identity", "skill_surface", "isolation_probe")
    }


def validate_environment(data: dict[str, Any]) -> None:
    value = data.get("environment")
    if not isinstance(value, dict):
        fail("environment must be an object")
    for key in ("model", "reasoning", "harness", "tools", "budget"):
        require_text(value.get(key), f"environment.{key}")
    repeat_count = value.get("repeat_count")
    if not isinstance(repeat_count, int) or isinstance(repeat_count, bool) or repeat_count < 1:
        fail("environment.repeat_count must be an integer of at least 1")


def validate_receipt(data: dict[str, Any]) -> list[str]:
    warnings: list[str] = []
    if data.get("schema_version") != 1:
        fail("schema_version must be 1")
    require_text(data.get("evaluation_id"), "evaluation_id")
    require_text(data.get("scope"), "scope")
    candidate_ids = require_text_list(data.get("candidate_ids"), "candidate_ids")
    for candidate_id in candidate_ids:
        if not re.fullmatch(r"C-\d{3,}", candidate_id):
            fail(f"candidate_ids contains invalid ID: {candidate_id}")

    baseline = validate_surface(data, "baseline")
    candidate = validate_surface(data, "candidate")
    if baseline["identity"] == candidate["identity"]:
        fail("baseline.identity and candidate.identity must differ")
    if baseline["skill_surface"] == candidate["skill_surface"]:
        fail("baseline.skill_surface and candidate.skill_surface must differ")
    validate_environment(data)

    cases = data.get("cases")
    if not isinstance(cases, list) or not cases:
        fail("cases must be a non-empty list")
    seen_ids: set[str] = set()
    covered_roles: set[str] = set()
    verdict_counts: Counter[str] = Counter()
    for index, case in enumerate(cases, start=1):
        if not isinstance(case, dict):
            fail(f"cases[{index}] must be an object")
        case_id = require_text(case.get("case_id"), f"cases[{index}].case_id")
        if not re.fullmatch(r"E-\d{3,}", case_id):
            fail(f"{case_id}: case_id must match E-NNN")
        if case_id in seen_ids:
            fail(f"duplicate case_id: {case_id}")
        seen_ids.add(case_id)

        roles = set(require_text_list(case.get("roles"), f"{case_id}.roles"))
        unsupported = sorted(roles - REQUIRED_ROLES)
        if unsupported:
            fail(f"{case_id}: unsupported roles: {', '.join(unsupported)}")
        covered_roles.update(roles)
        for field in (
            "prompt",
            "success_criteria",
            "baseline_observation",
            "candidate_observation",
            "evidence",
        ):
            require_text(case.get(field), f"{case_id}.{field}")
        verdict = require_text(case.get("verdict"), f"{case_id}.verdict")
        if verdict not in VALID_VERDICTS:
            fail(f"{case_id}: unsupported verdict {verdict}")
        verdict_counts[verdict] += 1

    missing_roles = sorted(REQUIRED_ROLES - covered_roles)
    if missing_roles:
        fail("evaluation cases do not cover required roles: " + ", ".join(missing_roles))

    conclusion = data.get("conclusion")
    if not isinstance(conclusion, dict):
        fail("conclusion must be an object")
    status = require_text(conclusion.get("status"), "conclusion.status")
    if status not in VALID_CONCLUSIONS:
        fail(f"unsupported conclusion.status: {status}")
    review_identity = require_text(
        conclusion.get("review_identity"), "conclusion.review_identity"
    )
    if review_identity not in VALID_REVIEW_IDENTITIES:
        fail(f"unsupported conclusion.review_identity: {review_identity}")
    require_text(conclusion.get("rationale"), "conclusion.rationale")

    if verdict_counts["invalidated"] and status != "invalidated":
        fail("invalidated cases require conclusion.status=invalidated")
    if status == "accept":
        if verdict_counts["regressed"] or verdict_counts["invalidated"]:
            fail("accept cannot contain regressed or invalidated cases")
        if not verdict_counts["improved"]:
            fail("accept requires at least one improved case")
    if data["environment"]["repeat_count"] == 1:
        warnings.append("repeat_count=1; do not claim stability across repeated runs")
    return warnings


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate a BuildOS distillation differential-evaluation receipt."
    )
    parser.add_argument("receipt", type=Path)
    args = parser.parse_args()
    try:
        data = load_receipt(args.receipt)
        warnings = validate_receipt(data)
    except ValueError as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        return 1

    counts = Counter(case["verdict"] for case in data["cases"])
    print(
        f"[OK] evaluation {data['evaluation_id']}: "
        f"{len(data['cases'])} cases, conclusion={data['conclusion']['status']}"
    )
    print("[OK] verdicts: " + ", ".join(f"{key}={counts[key]}" for key in sorted(counts)))
    for warning in warnings:
        print(f"[WARN] {warning}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
