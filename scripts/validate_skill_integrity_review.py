#!/usr/bin/env python3
"""Validate the review record for the current Skill behavior surface."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
RECORD = ROOT / "evidence/reviews/CURRENT_SKILL_INTEGRITY_REVIEW.json"
VALID_IDENTITIES = {"independent", "peer", "evidence_based_self_review"}
VALID_VERDICTS = {
    "supported",
    "supported_with_conditions",
    "not_supported",
    "inconclusive",
}
BLOCKING_SEVERITIES = {"P0", "P1"}
CLOSED_FINDING_STATES = {"verified_resolved", "accepted_risk", "false_positive", "superseded"}


def fail(message: str) -> None:
    raise SystemExit(f"[ERROR] {message}")


def surface_files(root: Path = ROOT) -> list[Path]:
    files: set[Path] = set()
    for relative in ("skills", "hooks", "adapters/claude-code/hooks", "tests/behavior"):
        base = root / relative
        if base.is_dir():
            files.update(path for path in base.rglob("*") if path.is_file() and "__pycache__" not in path.parts)
    for relative in (
        ".github/workflows/release.yml",
        ".github/workflows/validate.yml",
        "docs/architecture/skill-boundaries.md",
        "docs/architecture/hook-lifecycle.md",
        "scripts/validate_package.py",
        "scripts/validate_distillation_batch.py",
        "scripts/validate_skill_integrity_review.py",
    ):
        path = root / relative
        if path.is_file():
            files.add(path)
    return sorted(files, key=lambda path: path.relative_to(root).as_posix())


def surface_sha256(root: Path = ROOT) -> str:
    digest = hashlib.sha256()
    for path in surface_files(root):
        relative = path.relative_to(root).as_posix().encode("utf-8")
        data = path.read_bytes()
        digest.update(len(relative).to_bytes(8, "big"))
        digest.update(relative)
        digest.update(len(data).to_bytes(8, "big"))
        digest.update(data)
    return digest.hexdigest()


def load_record(path: Path = RECORD) -> dict[str, object]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        fail(f"Skill integrity review record is unreadable: {exc}")
    if not isinstance(value, dict):
        fail("Skill integrity review record must be a JSON object")
    return value


def validate_record(
    record: dict[str, object],
    *,
    require_current: bool,
    release: bool,
    root: Path = ROOT,
) -> None:
    required = {
        "schema_version",
        "review_id",
        "reviewed_at",
        "review_identity",
        "verdict",
        "surface_sha256",
        "report",
        "findings",
        "conditions",
        "unassessed",
    }
    missing = sorted(required - record.keys())
    if missing:
        fail(f"Skill integrity review record missing fields: {', '.join(missing)}")
    if record["schema_version"] != 1:
        fail("unsupported Skill integrity review schema version")
    if not isinstance(record["review_id"], str) or not re.fullmatch(r"REV-[A-Za-z0-9-]+", record["review_id"]):
        fail("invalid Skill integrity review ID")
    if record["review_identity"] not in VALID_IDENTITIES:
        fail("invalid Skill integrity review identity")
    if record["verdict"] not in VALID_VERDICTS:
        fail("invalid Skill integrity review verdict")
    if not isinstance(record["surface_sha256"], str) or not re.fullmatch(r"[0-9a-f]{64}", record["surface_sha256"]):
        fail("invalid Skill integrity surface digest")
    for field in ("findings", "conditions", "unassessed"):
        if not isinstance(record[field], list):
            fail(f"Skill integrity review {field} must be a list")
    report = root / str(record["report"])
    if not report.is_file():
        fail(f"Skill integrity review report does not exist: {record['report']}")
    report_text = report.read_text(encoding="utf-8")
    if str(record["review_id"]) not in report_text:
        fail("Skill integrity review report does not identify the current review")
    if require_current:
        actual = surface_sha256(root)
        if record["surface_sha256"] != actual:
            fail(f"Skill integrity review is stale: expected {actual}, recorded {record['surface_sha256']}")
    for finding in record["findings"]:
        if not isinstance(finding, dict):
            fail("Skill integrity review findings must be objects")
        if not isinstance(finding.get("id"), str) or not finding["id"].startswith("FND-"):
            fail("Skill integrity review finding has an invalid ID")
        if finding.get("severity") not in {"P0", "P1", "P2", "P3"}:
            fail(f"Skill integrity review finding has invalid severity: {finding.get('id')}")
        if not isinstance(finding.get("status"), str):
            fail(f"Skill integrity review finding has invalid status: {finding.get('id')}")
    if release:
        if record["verdict"] not in {"supported", "supported_with_conditions"}:
            fail(f"Skill integrity review verdict blocks release: {record['verdict']}")
        if record["conditions"]:
            fail("Skill integrity review has unresolved release conditions")
        for finding in record["findings"]:
            if finding.get("severity") in BLOCKING_SEVERITIES and finding.get("status") not in CLOSED_FINDING_STATES:
                fail(f"blocking Skill integrity finding is not closed: {finding.get('id', '<unknown>')}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--schema-only", action="store_true")
    parser.add_argument("--release", action="store_true")
    parser.add_argument("--print-digest", action="store_true")
    args = parser.parse_args()
    if args.print_digest:
        print(surface_sha256())
        return
    record = load_record()
    validate_record(record, require_current=not args.schema_only, release=args.release)
    mode = "release" if args.release else "schema" if args.schema_only else "current"
    print(f"[OK] Skill integrity review is valid ({mode}): {record['review_id']}")


if __name__ == "__main__":
    main()
