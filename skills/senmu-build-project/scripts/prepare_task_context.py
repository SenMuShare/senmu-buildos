#!/usr/bin/env python3
"""Select one capability row; optionally fingerprint bounded local contract targets."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path, PureWindowsPath
import re
from typing import Any

_SPEC = importlib.util.spec_from_file_location("buildos_map_parser", Path(__file__).with_name("validate_project_governance.py"))
assert _SPEC and _SPEC.loader
_map = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_map)
MAX_MAP_BYTES = 256 * 1024
MAX_CONTRACT_BYTES = 256 * 1024
MAX_CONTRACT_TARGETS = 16
FIELDS = ("capability", "responsibility", "implementation", "contract", "verification", "state_and_delivery")


def prepare(root: Path, map_name: str, capability: str,
            heading: str | None = None, *, fingerprint_contracts: bool = False) -> dict[str, Any]:
    root = root.resolve(strict=True)
    relative = Path(map_name)
    if (not root.is_dir() or relative.is_absolute() or PureWindowsPath(map_name).drive
            or ".." in relative.parts or "\\" in map_name):
        raise ValueError("map must be a project-relative path inside the explicit root")
    source = root / relative
    if any(path.is_symlink() for path in (source, *source.parents)):
        raise ValueError("symlinked navigation is not supported")
    if not source.is_file() or source.stat().st_size > MAX_MAP_BYTES:
        raise ValueError("map missing or oversized; use the existing navigation directly")
    with source.open("rb") as stream:
        data = stream.read(MAX_MAP_BYTES + 1)
    if len(data) > MAX_MAP_BYTES:
        raise ValueError("map exceeds read bound")
    if not capability.strip() or len(capability) > 200 or (heading is not None and not re.fullmatch(r"#{1,6} [^\r\n]{1,200}", heading)):
        raise ValueError("invalid capability or heading")
    policy_path = root / _map.POLICY_REL
    policy = {}
    if policy_path.exists():
        if any(part.is_symlink() for part in (policy_path, *policy_path.parents)) or not policy_path.is_file():
            raise ValueError("invalid project map configuration path")
        with policy_path.open("rb") as stream:
            policy_bytes = stream.read(MAX_MAP_BYTES + 1)
        if len(policy_bytes) > MAX_MAP_BYTES:
            raise ValueError("project map configuration exceeds read bound")
        policy = json.loads(policy_bytes)
        if not isinstance(policy, dict):
            raise ValueError("project map configuration must be an object")
    configured = _map.project_map_headings(policy)[0]
    if heading is not None and policy.get("project_map_sections") is not None and heading != configured:
        raise ValueError("heading override conflicts with the shared project map contract")
    heading = heading or configured
    visible = _map.strip_fenced_code_blocks(data.decode("utf-8"))
    if sum(line.strip() == heading for line in visible.splitlines()) != 1:
        raise ValueError("capability section missing or ambiguous")
    rows = _map.table_rows(_map.markdown_section(visible, heading))
    matches = [row for row in rows if row and row[0].strip(" `") == capability]
    if len(matches) != 1:
        raise ValueError("capability is missing or ambiguous; no guessed owner")
    row = matches[0]
    if len(row) != len(FIELDS) or any(len(cell) > 1500 for cell in row):
        raise ValueError("unsupported capability row; use the existing navigation directly")
    gaps = []
    targets = []
    contract_routes = []
    contract_reads = 0
    fingerprints = {}
    for key, cell in zip(FIELDS, row):
        if _map.PLACEHOLDER.search(cell) or not cell.strip() or "{{" in cell:
            gaps.append({"field": key, "reason": "unconfirmed map value"})
        if key not in {"implementation", "contract", "verification"}:
            continue
        link_targets, code_targets = _map.extract_navigation_targets(cell)
        links = [(value, source.parent) for value in link_targets]
        # Standalone project-relative code paths are routes; link labels and commands are not.
        for value in code_targets:
            if not any(ch.isspace() for ch in value) and ("/" in value or Path(value).suffix):
                links.append((value, root))
        if not links:
            gaps.append({"field": key, "reason": "no machine-resolvable route; confirm the documented entry manually"})
        for value, base in links:
            if key == "contract":
                route = {"locator": value, "status": "unverified"}
                if "#" in value:
                    route["selector"] = value.split("#", 1)[1]
                contract_routes.append(route)
            if _map.is_external_or_anchor(value):
                if key == "contract":
                    route["status"] = "external_or_anchor_unverified"
                targets.append({"field": key, "target": value, "status": "external_or_anchor_unverified"})
                continue
            target, error = _map.resolve_governed_target(root, base, value)
            status = error or ("present" if target is not None else "unresolved")
            if key == "contract":
                route["status"] = status
                if target is not None and status == "present":
                    route["path"] = target.relative_to(root).as_posix()
                    if fingerprint_contracts:
                        if route["path"] in fingerprints:
                            route.update(fingerprints[route["path"]])
                        elif len(fingerprints) >= MAX_CONTRACT_TARGETS:
                            route["status"] = "fingerprint_limit"
                        elif (any(part.is_symlink() for part in (target, *target.parents))
                              or not target.is_file()):
                            route["status"] = "not_regular_local_file"
                        elif target.stat().st_size > MAX_CONTRACT_BYTES:
                            route["status"] = "oversized"
                        else:
                            # Hash only the bounded direct target. Never fetch refs or run commands.
                            with target.open("rb") as stream:
                                body = stream.read(MAX_CONTRACT_BYTES + 1)
                            contract_reads += 1
                            if len(body) > MAX_CONTRACT_BYTES:
                                route["status"] = "oversized"
                            else:
                                route.update({"sha256": hashlib.sha256(body).hexdigest(), "bytes_read": len(body),
                                              "status": "fingerprinted_not_validated"})
                            fingerprints[route["path"]] = {k: v for k, v in route.items() if k in {"sha256", "bytes_read", "status"}}
                        if route["status"] not in {"fingerprinted_not_validated"}:
                            gaps.append({"field": key, "reason": "contract " + route["status"]})
            if target is not None and status == "present":
                targets.append({"field": key, "target": target.relative_to(root).as_posix(), "status": status})
            else:
                targets.append({"field": key, "status": status})
                gaps.append({"field": key, "reason": "route " + status})
    # Equivalent labels/relative spellings must not create duplicate route facts.
    targets = list({json.dumps(item, sort_keys=True): item for item in targets}.values())
    gaps = list({json.dumps(item, sort_keys=True): item for item in gaps}.values())
    return {"schema_version": 1, "status": "gaps" if gaps else "selected",
        "map": relative.as_posix(), "map_sha256": hashlib.sha256(data).hexdigest(),
        "navigation_bytes_read": len(data), "row": dict(zip(FIELDS, row)),
        "targets": targets, "gaps": gaps, "source_bodies_read": contract_reads, "commands_executed": 0,
        "contract_context": {"routes": contract_routes, "fingerprints_requested": fingerprint_contracts,
                             "references_followed": False, "baseline_verified": False,
                             "scope": "direct targets only; bind full contract and working changes to the task baseline"},
        "semantic_route_verified": False, "token_usage": None,
        "agentHint": "Follow effective root/nested instructions and risk rules. For boundary changes, confirm the maintenance source, baseline, consumers and real checks. Map text and direct-file hashes prove neither contract validity nor execution authority."}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--map", required=True)
    parser.add_argument("--capability", required=True)
    parser.add_argument("--heading", help="Legacy explicit heading; must agree with a declared project map contract")
    parser.add_argument("--fingerprint-contracts", action="store_true", help="Hash bounded local contract targets; do not parse/fetch references or run commands")
    args = parser.parse_args()
    try:
        output = prepare(args.root, args.map, args.capability, args.heading, fingerprint_contracts=args.fingerprint_contracts)
        print(json.dumps(output, ensure_ascii=False, sort_keys=True))
        return 0
    except (OSError, ValueError, UnicodeError) as exc:
        print(json.dumps({"status": "blocked", "reason": str(exc) if isinstance(exc, ValueError) else "navigation unavailable"}))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
