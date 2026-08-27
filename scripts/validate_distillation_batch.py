#!/usr/bin/env python3
"""Validate a temporary Senmu BuildOS knowledge-distillation batch.

The batch is an intermediate review artifact. This tool validates structure and
surfaces likely duplicates; it never decides whether a rule is correct or edits
the active Skills.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent.parent
SOURCE_TYPES = {"web", "pdf", "book", "repository", "skill", "document", "other"}
DISPOSITIONS = {
    "merge",
    "replace",
    "add",
    "project_only",
    "needs_evidence",
    "discard",
}
DOMAINS = {
    "core",
    "architecture",
    "implementation",
    "review",
    "testing",
    "language",
    "framework",
    "delivery",
    "other",
}
REQUIRED_CANDIDATE_FIELDS = (
    "candidate_id",
    "domain",
    "statement",
    "decision",
    "trigger",
    "action",
    "exceptions",
    "verification",
    "scope",
    "suggested_owner",
    "disposition",
)
FINAL_DISPOSITIONS = {"merge", "replace", "add"}


def fail(message: str) -> None:
    raise ValueError(message)


def normalized(text: str) -> str:
    return re.sub(r"[\W_]+", "", text, flags=re.UNICODE).casefold()


def require_text(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        fail(f"{field} must be a non-empty string")
    return value.strip()


def load_batch(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        fail(f"cannot read batch: {exc}")
    if not isinstance(data, dict):
        fail("batch root must be an object")
    return data


def validate_batch(data: dict[str, Any]) -> list[str]:
    warnings: list[str] = []
    if data.get("schema_version") != 1:
        fail("schema_version must be 1")
    require_text(data.get("batch_id"), "batch_id")
    require_text(data.get("scope"), "scope")
    require_text(data.get("read_boundary"), "read_boundary")

    sources = data.get("sources")
    if not isinstance(sources, list) or not sources:
        fail("sources must contain at least one source")
    for index, source in enumerate(sources, start=1):
        if not isinstance(source, dict):
            fail(f"sources[{index}] must be an object")
        source_type = require_text(source.get("type"), f"sources[{index}].type")
        if source_type not in SOURCE_TYPES:
            fail(f"sources[{index}].type is unsupported: {source_type}")
        require_text(source.get("locator"), f"sources[{index}].locator")
        require_text(source.get("scope_read"), f"sources[{index}].scope_read")

    candidates = data.get("candidates")
    if not isinstance(candidates, list) or not candidates:
        fail("candidates must contain at least one candidate")

    seen_ids: set[str] = set()
    seen_statements: dict[str, str] = {}
    for index, candidate in enumerate(candidates, start=1):
        if not isinstance(candidate, dict):
            fail(f"candidates[{index}] must be an object")
        values = {
            field: require_text(candidate.get(field), f"candidates[{index}].{field}")
            for field in REQUIRED_CANDIDATE_FIELDS
        }
        candidate_id = values["candidate_id"]
        if not re.fullmatch(r"C-\d{3,}", candidate_id):
            fail(f"{candidate_id}: candidate_id must match C-NNN")
        if candidate_id in seen_ids:
            fail(f"duplicate candidate_id: {candidate_id}")
        seen_ids.add(candidate_id)

        domain = values["domain"]
        if domain not in DOMAINS:
            fail(f"{candidate_id}: unsupported domain {domain}")
        disposition = values["disposition"]
        if disposition not in DISPOSITIONS:
            fail(f"{candidate_id}: unsupported disposition {disposition}")

        statement_key = normalized(values["statement"])
        previous = seen_statements.get(statement_key)
        if previous:
            fail(f"duplicate candidate statements: {previous} and {candidate_id}")
        seen_statements[statement_key] = candidate_id

        if disposition in {"merge", "replace"}:
            require_text(candidate.get("existing_rule"), f"{candidate_id}.existing_rule")
        if disposition == "add":
            require_text(candidate.get("gap"), f"{candidate_id}.gap")
        if disposition == "needs_evidence":
            require_text(candidate.get("evidence_needed"), f"{candidate_id}.evidence_needed")

        if disposition in FINAL_DISPOSITIONS and len(values["verification"]) < 8:
            warnings.append(f"{candidate_id}: verification may be too vague")
        if len(values["statement"]) < 12:
            warnings.append(f"{candidate_id}: statement may be too generic")

    for left_index, left in enumerate(candidates):
        for right in candidates[left_index + 1 :]:
            score = SequenceMatcher(
                None,
                normalized(left["statement"]),
                normalized(right["statement"]),
            ).ratio()
            if score >= 0.82:
                warnings.append(
                    f"{left['candidate_id']} and {right['candidate_id']} "
                    f"are likely semantic duplicates ({score:.2f})"
                )
    return warnings


def active_rule_units(root: Path) -> list[tuple[Path, str]]:
    units: list[tuple[Path, str]] = []
    for path in sorted(root.rglob("*.md")):
        text = path.read_text(encoding="utf-8")
        for raw_line in text.splitlines():
            line = re.sub(r"^\s*(?:[-*+] |\d+[.)] )", "", raw_line).strip()
            if len(line) >= 24 and not line.startswith(("#", "|", "```")):
                units.append((path, line))
        for raw in re.split(r"\n\s*\n|\n(?=#+\s)", text):
            unit = re.sub(r"\s+", " ", raw).strip(" -\t")
            if len(unit) >= 24 and not unit.startswith("|") and not unit.startswith("```"):
                units.append((path, unit))
    return units


def find_likely_matches(
    data: dict[str, Any], root: Path, threshold: float, limit: int
) -> list[str]:
    units = active_rule_units(root)
    matches: list[str] = []
    for candidate in data["candidates"]:
        probes = (
            normalized(candidate["statement"]),
            normalized(candidate["action"]),
            normalized(candidate["statement"] + candidate["action"]),
        )
        ranked: list[tuple[float, Path, str]] = []
        for path, unit in units:
            target = normalized(unit)
            score = max(SequenceMatcher(None, probe, target).ratio() for probe in probes)
            if score >= threshold:
                ranked.append((score, path, unit))
        for score, path, unit in sorted(ranked, reverse=True)[:limit]:
            excerpt = unit[:100] + ("..." if len(unit) > 100 else "")
            try:
                display_path = path.relative_to(ROOT)
            except ValueError:
                display_path = path
            matches.append(
                f"{candidate['candidate_id']} {score:.2f} "
                f"{display_path} :: {excerpt}"
            )
    return matches


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Validate a temporary BuildOS knowledge-distillation batch."
    )
    parser.add_argument("batch", type=Path, help="temporary batch JSON file")
    parser.add_argument(
        "--active-root",
        type=Path,
        default=ROOT / "skills",
        help="active Markdown root used for likely-duplicate hints",
    )
    parser.add_argument("--similarity", type=float, default=0.64)
    parser.add_argument("--limit", type=int, default=3)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        data = load_batch(args.batch)
        warnings = validate_batch(data)
        if not 0.0 <= args.similarity <= 1.0:
            fail("--similarity must be between 0 and 1")
        if args.limit < 1:
            fail("--limit must be at least 1")
        active_root = args.active_root.resolve()
        if not active_root.is_dir():
            fail(f"active rule root does not exist: {active_root}")
        matches = find_likely_matches(data, active_root, args.similarity, args.limit)
    except ValueError as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        return 1

    counts = Counter(candidate["disposition"] for candidate in data["candidates"])
    print(f"[OK] batch {data['batch_id']}: {len(data['candidates'])} candidates")
    print("[OK] dispositions: " + ", ".join(f"{key}={counts[key]}" for key in sorted(counts)))
    for warning in warnings:
        print(f"[WARN] {warning}")
    if matches:
        print("[INFO] likely active-rule matches; semantic review required:")
        for match in matches:
            print(f"  - {match}")
    else:
        print("[INFO] no likely active-rule matches at the selected threshold")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
