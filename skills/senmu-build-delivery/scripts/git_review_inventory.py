"""Canonical read-only Git inventory and LF coordinates shared by review entrypoints."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
from typing import Any, Callable

POLICY = "git-review-inventory/v1:rename50-limit1000-lf"
OBJECT_ID = re.compile(r"(?:[0-9a-f]{40}|[0-9a-f]{64})\Z")


# Explicit --repo wins over inherited hook/shell repository routing. Keep normal
# project/global Git configuration, credentials and PATH; never echo env values.
_REPOSITORY_ENV = {
    "GIT_DIR", "GIT_WORK_TREE", "GIT_COMMON_DIR", "GIT_INDEX_FILE", "GIT_PREFIX",
    "GIT_OBJECT_DIRECTORY", "GIT_ALTERNATE_OBJECT_DIRECTORIES", "GIT_NAMESPACE",
    "GIT_REPLACE_REF_BASE", "GIT_SHALLOW_FILE", "GIT_GRAFT_FILE", "GIT_CONFIG",
    "GIT_CONFIG_PARAMETERS", "GIT_CONFIG_COUNT", "GIT_IMPLICIT_WORK_TREE",
    "GIT_DIFF_OPTS", "GIT_EXTERNAL_DIFF", "GIT_EXTERNAL_DIFF_TRUST_EXIT_CODE",
}


def git_environment() -> dict[str, str]:
    """Read original objects in the explicitly selected repository, not replacements."""
    env = {key: value for key, value in os.environ.items()
           if key not in _REPOSITORY_ENV and not key.startswith(("GIT_CONFIG_KEY_", "GIT_CONFIG_VALUE_"))}
    env["GIT_NO_REPLACE_OBJECTS"] = "1"
    env["GIT_NO_LAZY_FETCH"] = "1"
    env["GIT_TERMINAL_PROMPT"] = "0"
    return env


def verify_blob(object_id: str, data: bytes) -> None:
    """A source proof must name the actual raw Git blob, including its object header."""
    if not isinstance(object_id, str) or not OBJECT_ID.fullmatch(object_id):
        raise ValueError("invalid frozen blob identity")
    algorithm = hashlib.sha1 if len(object_id) == 40 else hashlib.sha256
    actual = algorithm(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()
    if actual != object_id:
        raise ValueError("raw Git blob identity mismatch")


def _git(repo: Path, *args: str) -> bytes:
    result = subprocess.run(["git", "-C", str(repo), *args], capture_output=True,
                            check=False, timeout=30, env=git_environment())
    if result.returncode:
        raise ValueError("Git could not establish the frozen review inventory")
    return result.stdout


def inventory(repo: Path, base: str, head: str, *,
              run: Callable[..., bytes] = _git, detect_renames: bool = True) -> list[dict[str, Any]]:
    """Return the same objects regardless of quotePath, rename, order or relative config.

    Rename detection has a fixed threshold/work limit; paths are NUL-delimited.
    Unsupported filename encoding fails explicitly rather than dropping an entry.
    The callback lets an owning tool retain its diagnostics and per-command cache.
    """
    if not all(isinstance(value, str) and OBJECT_ID.fullmatch(value) for value in (base, head)):
        raise ValueError("review inventory endpoints must be full object IDs")
    raw = run(repo, "diff", "--raw", "--no-abbrev", "--no-color", "--no-ext-diff",
              "--no-textconv", "--no-relative", "--ignore-submodules=none",
              *( ["--find-renames=50%", "-l1000"] if detect_renames else ["--no-renames"] ),
              "-z", base, head, "--").split(b"\0")
    items: list[dict[str, Any]] = []
    index = 0
    while index < len(raw) - 1:
        fields = raw[index].decode("ascii").split()
        if len(fields) != 5 or not re.fullmatch(r":[0-7]{6}", fields[0]):
            raise ValueError("invalid Git review inventory header")
        old_mode, new_mode, old_blob, new_blob, status = fields
        if (not re.fullmatch(r"[0-7]{6}", new_mode)
                or not all(OBJECT_ID.fullmatch(blob) for blob in (old_blob, new_blob))
                or not re.fullmatch(r"[AMDRCT][0-9]*", status)):
            raise ValueError("invalid Git review inventory object")
        index += 1
        if index >= len(raw) - 1:
            raise ValueError("missing Git review inventory path")
        old_path = raw[index].decode("utf-8")
        index += 1
        path = old_path
        if status[0] in {"R", "C"}:
            if index >= len(raw) - 1:
                raise ValueError("missing renamed review inventory path")
            path = raw[index].decode("utf-8")
            index += 1
        if not path or not old_path:
            raise ValueError("empty Git review inventory path")
        item = {"path": path, "old_path": old_path, "change_type": status[0],
                "old_mode": old_mode[1:], "new_mode": new_mode,
                "old_blob": old_blob, "new_blob": new_blob}
        canonical = json.dumps(item, ensure_ascii=False, sort_keys=True,
                               separators=(",", ":"), allow_nan=False).encode("utf-8")
        item["item_id"] = "sha256:" + hashlib.sha256(canonical).hexdigest()
        items.append(item)
    if index != len(raw) - 1 or raw[-1] != b"":
        raise ValueError("incomplete Git review inventory")
    # Git's diff.orderFile must not alter the sealed review list's ordering.
    return sorted(items, key=lambda item: (item["path"].encode("utf-8"),
                                          item["old_path"].encode("utf-8")))


INVENTORY_FIELDS = ("path", "old_path", "change_type", "old_mode", "new_mode", "old_blob", "new_blob")


def frozen_inventory(repo: Path, base: str, head: str, declared: Any, *,
                     run: Callable[..., bytes] = _git) -> list[dict[str, Any]]:
    """Validate a captured pairing against *all* raw changes, without rerunning similarity.

    A rename is a review grouping, not a proof of historical intent. Expand it to
    delete/add and compare raw identities. Local attributes cannot change this
    denominator, and duplicate, missing or invented paths cannot be accepted.
    Extra runtime receipt fields never participate in the captured inventory.
    """
    if not isinstance(declared, list):
        raise ValueError("frozen inventory must be an array")
    actual = inventory(repo, base, head, run=run, detect_renames=False)
    expected = [tuple(item[k] for k in INVENTORY_FIELDS) for item in actual]
    expanded = []
    captured = []
    for raw in declared:
        if not isinstance(raw, dict) or any(not isinstance(raw.get(k), str) for k in INVENTORY_FIELDS):
            raise ValueError("invalid frozen inventory entry")
        item = {k: raw[k] for k in INVENTORY_FIELDS}
        if item["change_type"] not in {"A", "M", "D", "R", "T"}:
            raise ValueError("unsupported frozen pairing")
        canonical = json.dumps(item, ensure_ascii=False, sort_keys=True,
                               separators=(",", ":"), allow_nan=False).encode("utf-8")
        identity = "sha256:" + hashlib.sha256(canonical).hexdigest()
        if raw.get("item_id") != identity:
            raise ValueError("frozen inventory identity mismatch")
        if item["change_type"] == "R":
            if item["path"] == item["old_path"]:
                raise ValueError("rename requires distinct paths")
            zero = "0" * len(base)
            removed = {**item, "path": item["old_path"], "change_type": "D",
                       "new_mode": "000000", "new_blob": zero}
            added = {**item, "old_path": item["path"], "change_type": "A",
                     "old_mode": "000000", "old_blob": zero}
            expanded.extend(tuple(x[k] for k in INVENTORY_FIELDS) for x in (removed, added))
        else:
            if item["path"] != item["old_path"]:
                raise ValueError("unpaired inventory paths differ")
            expanded.append(tuple(item[k] for k in INVENTORY_FIELDS))
        captured.append({**item, "item_id": identity})
    if sorted(expanded) != sorted(expected):
        raise ValueError("frozen inventory omits, duplicates or changes raw Git input")
    ordered = sorted(captured, key=lambda x: (x["path"].encode("utf-8"), x["old_path"].encode("utf-8")))
    if captured != ordered or len({x["item_id"] for x in captured}) != len(captured):
        raise ValueError("frozen inventory order or uniqueness changed")
    return captured


def lf_lines(data: bytes) -> list[bytes]:
    """Git counts LF bytes, not Unicode line separators; preserve CR and final bytes."""
    if not data:
        return []
    parts = data.split(b"\n")
    return [part + b"\n" for part in parts[:-1]] + ([parts[-1]] if parts[-1] else [])
