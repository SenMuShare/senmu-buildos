#!/usr/bin/env python3
"""Collect resumable review receipts; never infer quality or approval from coverage."""

from __future__ import annotations

import argparse
from collections import OrderedDict
from contextvars import ContextVar
from functools import wraps
import importlib.util
from contextlib import contextmanager
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import subprocess
import tempfile
from typing import Any
import uuid

_SHARED = Path(__file__).resolve().parents[2] / "senmu-build-delivery/scripts/git_review_inventory.py"
_SPEC = importlib.util.spec_from_file_location("buildos_git_review_inventory", _SHARED)
assert _SPEC and _SPEC.loader
_shared = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_shared)

SCHEMA = 3
STATES = ("pending", "completed", "failed", "reused")
COMMIT = re.compile(r"(?:[0-9a-f]{40}|[0-9a-f]{64})\Z")
MAX_BYTES = 4 * 1024 * 1024
CACHE_BYTES = 16 * 1024 * 1024
_GIT_CACHE: ContextVar[Any] = ContextVar("review_git_cache", default=None)
_SOURCE_VIEWS: ContextVar[Any] = ContextVar("review_source_views", default=None)
MAX_JSON_DEPTH = 64
MAX_SOURCE_VIEWS = 4


def evidence_operation(function):
    """Reuse immutable reads only inside one operation, never across CLI invocations."""
    @wraps(function)
    def wrapped(*args, **kwargs):
        if _GIT_CACHE.get() is not None:
            return function(*args, **kwargs)
        token = _GIT_CACHE.set(OrderedDict())
        sources = _SOURCE_VIEWS.set({})
        try:
            return function(*args, **kwargs)
        finally:
            _SOURCE_VIEWS.reset(sources)
            _GIT_CACHE.reset(token)
    return wrapped


def cache_put(key: tuple[Any, ...], data: bytes) -> None:
    cache = _GIT_CACHE.get()
    if cache is None or len(data) > CACHE_BYTES:
        return
    cache.pop(key, None)
    while cache and sum(map(len, cache.values())) + len(data) > CACHE_BYTES:
        cache.popitem(last=False)
    cache[key] = data


class ReviewError(ValueError):
    """An input, receipt or execution invariant could not be established."""


class ReuseUnavailable(ReviewError):
    """Only an external reuse dependency is invalid; local evidence stays checked."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ReviewError(message)


def nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def sha(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def digest(value: Any) -> str:
    return sha(json.dumps(value, ensure_ascii=False, sort_keys=True,
                          separators=(",", ":"), allow_nan=False).encode("utf-8"))


def git(repo: Path, *args: str, _input: bytes | None = None,
        _cache: bool = True) -> bytes:
    key = (str(repo), args, _input)
    cache = _GIT_CACHE.get()
    if _cache and cache is not None and key in cache:
        cache.move_to_end(key)
        return cache[key]
    result = subprocess.run(["git", "-C", str(repo), *args], input=_input,
                            capture_output=True, check=False, timeout=30, env=_shared.git_environment())
    require(result.returncode == 0, "Git could not establish the requested frozen object")
    if _cache:
        cache_put(key, result.stdout)
    return result.stdout


def preload_evidence(repo: Path, items: list[dict[str, Any]]) -> None:
    """Batch small frozen blobs after inventory validation; keep memory bounded.

    Large sets retain checked per-blob reads. External sources use a separate bounded
    operation-local view; no source view or verdict survives the operation.
    A separate final `check` reopens and revalidates all relevant evidence.
    """
    cache = _GIT_CACHE.get()
    if cache is None:
        return
    blobs: set[str] = set()
    for item in items:
        require(not sensitive(item), "sensitive path: retain as unverified; use a separate authorized review")
        for prefix in ("old", "new"):
            mode = item[prefix + "_mode"]
            if mode == "000000":
                continue
            require(mode in {"100644", "100755"},
                    "symlink or submodule requires a separate scoped review, not a retry")
            blob = item[prefix + "_blob"]
            if (str(repo), ("cat-file", "blob", blob), None) not in cache:
                blobs.add(blob)
    if not blobs:
        return
    ordered = sorted(blobs)
    payload = ("\n".join(ordered) + "\n").encode("ascii")
    headers = git(repo, "cat-file", "--batch-check", _input=payload, _cache=False).split(b"\n")
    require(len(headers) == len(ordered) + 1 and headers[-1] == b"", "invalid Git size batch")
    sizes = []
    for blob, header in zip(ordered, headers):
        parts = header.split()
        require(len(parts) == 3 and parts[0] == blob.encode() and parts[1] == b"blob",
                "frozen evidence is not an available blob")
        size = int(parts[2])
        require(0 <= size <= MAX_BYTES,
                "file exceeds bounded evidence support; use a separate scoped review, not a retry")
        sizes.append(size)
        cache_put((str(repo), ("cat-file", "-s", blob), None), str(size).encode() + b"\n")
    # Leave room for headers and already cached inventory. Never buffer an unlimited set.
    if sum(sizes) > CACHE_BYTES // 2:
        return
    raw = git(repo, "cat-file", "--batch", _input=payload, _cache=False)
    position = 0
    for blob, size in zip(ordered, sizes):
        stop = raw.find(b"\n", position)
        require(stop >= position and raw[position:stop] == f"{blob} blob {size}".encode(),
                "invalid Git evidence batch header")
        position = stop + 1
        data = raw[position:position + size]
        position += size
        require(len(data) == size and raw[position:position + 1] == b"\n",
                "truncated Git evidence batch")
        position += 1
        _shared.verify_blob(blob, data)
        cache_put((str(repo), ("cat-file", "blob", blob), None), data)
    require(position == len(raw), "unexpected Git evidence batch suffix")


def text(repo: Path, *args: str) -> str:
    return git(repo, *args).decode("utf-8").removesuffix("\n")


def repository(repo: Path) -> str:
    require(Path(text(repo, "rev-parse", "--show-toplevel")).resolve() == repo,
            "--repo must be the actual worktree root")
    common = Path(text(repo, "rev-parse", "--path-format=absolute", "--git-common-dir")).resolve()
    info = common.stat()
    # This is a local execution record, not a portable claim about another clone.
    return digest([str(common), info.st_dev, info.st_ino])


def exact_commit(repo: Path, value: Any) -> str:
    require(isinstance(value, str) and COMMIT.fullmatch(value) is not None,
            "frozen endpoints require full commit IDs, not moving refs")
    require(text(repo, "rev-parse", "--verify", value + "^{commit}") == value,
            "commit identity mismatch")
    return value


def inventory(repo: Path, base: str, head: str) -> list[dict[str, Any]]:
    return _shared.inventory(repo, base, head, run=git)


def frozen_inventory(repo: Path, base: str, head: str, items: Any) -> list[dict[str, Any]]:
    """Translate shared input errors into the runtime's existing public contract."""
    try:
        return _shared.frozen_inventory(repo, base, head, items, run=git)
    except ReviewError:
        raise
    except ValueError as exc:
        raise ReviewError("frozen inventory is missing, duplicated or inconsistent with Git") from exc


def init_record(scope: dict[str, Any], repo: Path, rules_identity: str) -> dict[str, Any]:
    require(isinstance(scope, dict) and scope.get("kind") == "git_review_scope",
            "input must be a Delivery git_review_scope")
    require(nonempty(rules_identity), "supply the effective rules/context identity")
    require(Path(str(scope.get("repository_root", ""))).resolve() == repo,
            "scope belongs to another worktree")
    base = exact_commit(repo, scope.get("review_base"))
    head = exact_commit(repo, scope.get("head"))
    git(repo, "merge-base", "--is-ancestor", base, head)
    tree = text(repo, "rev-parse", head + "^{tree}")
    require(scope.get("tree") == tree, "scope tree mismatch")
    require(scope.get("inventory_policy", _shared.POLICY) == _shared.POLICY,
            "scope inventory policy differs; recapture through the current Delivery entrypoint")
    files = (frozen_inventory(repo, base, head, scope["inventory_items"])
             if "inventory_items" in scope else inventory(repo, base, head))
    require(scope.get("changed_paths") == [item["path"] for item in files],
            "scope paths do not match the frozen Git inventory")
    snapshot = {"repository_root": str(repo), "repository_identity": repository(repo),
                "review_base": base, "head": head, "tree": tree,
                "rules_identity": rules_identity, "unit": scope.get("unit"),
                "inventory_policy": _shared.POLICY, "inventory_identity": digest(files)}
    return {"schema_version": SCHEMA, "run_id": uuid.uuid4().hex,
            "snapshot": snapshot, "snapshot_identity": digest(snapshot),
            "items": [{**item, "state": "pending", "attempt": 1,
                       "receipt": None, "history": []} for item in files]}


def safe_path(path: Path) -> Path:
    path = Path(os.path.abspath(path.expanduser()))
    require(not any(part.is_symlink() for part in (path, *path.parents)),
            "symlinked record or evidence paths are not supported")
    return path


def load(path: Path) -> dict[str, Any]:
    path = safe_path(path)
    require(path.is_file() and path.stat().st_size <= MAX_BYTES, "invalid or oversized JSON file")
    def unique(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        obj: dict[str, Any] = {}
        for key, value in pairs:
            require(key not in obj, "duplicate JSON key")
            obj[key] = value
        return obj
    with path.open("rb") as stream:
        raw = stream.read(MAX_BYTES + 1)
    require(len(raw) <= MAX_BYTES, "JSON input grew past its read bound")
    source = raw.decode("utf-8")
    depth = 0
    quoted = False
    escaped = False
    for char in source:
        if quoted:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                quoted = False
        elif char == '"':
            quoted = True
        elif char in "[{":
            depth += 1
            require(depth <= MAX_JSON_DEPTH, "JSON nesting exceeds supported depth")
        elif char in "]}":
            depth -= 1
    try:
        value = json.loads(source, object_pairs_hook=unique)
    except RecursionError as exc:
        raise ReviewError("JSON nesting exceeds parser capacity") from exc
    require(isinstance(value, dict), "JSON input must be an object")
    return value


def sensitive(item: dict[str, Any]) -> bool:
    for name in (item["path"], item["old_path"]):
        parts = name.lower().split("/")
        leaf = parts[-1]
        if ".ssh" in parts or leaf in {"id_rsa", "id_dsa", "id_ecdsa", "id_ed25519",
                                        ".netrc", "_netrc", ".npmrc", ".pypirc", ".dockercfg"}:
            return True
        if (leaf == ".env" or leaf.startswith(".env.")) and leaf not in {
                ".env.example", ".env.sample", ".env.template"}:
            return True
    return False


@evidence_operation
def evidence(repo: Path, item: dict[str, Any], side: str,
             start: int | None = None, end: int | None = None) -> dict[str, Any]:
    require(side in {"base", "head"}, "evidence side must be base or head")
    require(not sensitive(item), "sensitive path: retain as unverified; do not emit its contents")
    prefix = "old" if side == "base" else "new"
    require(item[prefix + "_mode"] in {"100644", "100755"},
            "absent, symlink or submodule content requires a separate scoped review")
    blob = item[prefix + "_blob"]
    require(int(text(repo, "cat-file", "-s", blob)) <= MAX_BYTES,
            "file exceeds bounded evidence support; keep coverage incomplete")
    data = git(repo, "cat-file", "blob", blob)
    require(b"\0" not in data, "binary content requires a separate scoped review")
    try:
        data.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ReviewError("non-UTF-8 content requires a separate scoped review, not a retry") from exc
    _shared.verify_blob(blob, data)
    lines = _shared.lf_lines(data)
    start = (1 if lines else 0) if start is None else start
    end = len(lines) if end is None else end
    require(type(start) is int and type(end) is int and
            ((not lines and start == end == 0) or (1 <= start <= end <= len(lines))),
            "evidence line range is outside frozen content")
    selected = b"".join(lines[start - 1:end]) if lines else b""
    return {"side": side, "blob": blob, "line_start": start, "line_end": end,
            "file_sha256": sha(data), "range_sha256": sha(selected)}


def changed_ranges(repo: Path, item: dict[str, Any]) -> dict[str, list[tuple[int, int]]]:
    """Required content ranges in Git LF coordinates, plus zero-width change anchors.

    Adds/deletes cover all available content. Metadata-only changes bind full existing
    sides. These ranges attest declared input coverage, not the reviewer's reasoning.
    """
    whole = {side: evidence(repo, item, side)
             for side, prefix in (("base", "old"), ("head", "new"))
             if item[prefix + "_mode"] != "000000"}
    if len(whole) < 2 or item["old_blob"] == item["new_blob"]:
        return {side: [(proof["line_start"], proof["line_end"])]
                for side, proof in whole.items()}
    patch = git(repo, "diff", "--text", "--no-color", "--no-ext-diff", "--no-textconv",
                "--no-renames", "--unified=0", "--inter-hunk-context=0",
                "--no-indent-heuristic", "--diff-algorithm=myers",
                item["old_blob"], item["new_blob"], "--")
    ranges: dict[str, list[tuple[int, int]]] = {"base": [], "head": []}
    for line in patch.split(b"\n"):
        match = re.match(rb"^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@", line)
        if not match:
            continue
        for side, a, n in (("base", 1, 2), ("head", 3, 4)):
            start, count = int(match[a]), int(match[n] or b"1")
            if count:
                span = (start, start + count - 1)
            else:
                # Insertions/deletions have no changed line on one side: bind the
                # nearest surviving boundary line, or the explicit empty-side 0..0.
                anchor = min(max(1, start), whole[side]["line_end"])
                span = (anchor, anchor)
            ranges[side].append(span)
    require(all(ranges.values()), "Git did not establish changed-line coverage")
    return ranges


def covers(spans: list[tuple[int, int]], required: tuple[int, int]) -> bool:
    cursor, end = required
    for start, stop in sorted(spans):
        if stop < cursor:
            continue
        if start > cursor:
            return False
        cursor = max(cursor, stop + 1)
        if cursor > end:
            return True
    return False


def receipt_identity(record: dict[str, Any], item: dict[str, Any],
                     receipt: dict[str, Any]) -> None:
    require(isinstance(receipt, dict), "missing receipt")
    require(receipt.get("state") in STATES[1:], "invalid receipt state")
    for key, expected in (("run_id", record["run_id"]),
                          ("snapshot_identity", record["snapshot_identity"]),
                          ("item_id", item["item_id"]), ("attempt", item["attempt"])):
        require(receipt.get(key) == expected and type(receipt.get(key)) is type(expected),
                "stale or foreign receipt identity")
    require(nonempty(receipt.get("executor")), "receipt requires executor attribution")
    if receipt["state"] == "failed":
        require(nonempty(receipt.get("reason")), "failed receipt requires a reason")
    else:
        require(nonempty(receipt.get("summary")), "completion requires an actual review summary")
        require(isinstance(receipt.get("evidence"), list) and bool(receipt["evidence"]),
                "completion requires frozen evidence")

    if receipt["state"] == "reused":
        source_metadata(receipt.get("source"))


def validate_receipt(record: dict[str, Any], repo: Path, item: dict[str, Any],
                     receipt: dict[str, Any], *, allow_reuse: bool = True) -> None:
    receipt_identity(record, item, receipt)
    if receipt["state"] == "failed":
        return
    proofs = receipt["evidence"]
    submitted: dict[str, list[tuple[int, int]]] = {}
    for proof in proofs:
        require(isinstance(proof, dict), "invalid evidence object")
        expected = evidence(repo, item, proof.get("side"),
                            proof.get("line_start"), proof.get("line_end"))
        require(proof == expected, "evidence does not match frozen file and range")
        span = (proof["line_start"], proof["line_end"])
        spans = submitted.setdefault(proof["side"], [])
        require(span not in spans, "duplicate evidence range")
        spans.append(span)
    required = changed_ranges(repo, item)
    require(set(submitted) == set(required), "receipt must cover both existing sides of the change")
    require(all(covers(submitted[side], span) for side, spans in required.items() for span in spans),
            "evidence anchors do not cover every changed range or required boundary")
    if receipt["state"] == "reused":
        require(allow_reuse, "reuse chains are not supported; reference a completed source receipt")
        validate_reuse_source(record, repo, item, receipt)


def source_metadata(source: Any) -> dict[str, Any]:
    require(isinstance(source, dict) and nonempty(source.get("record")), "reuse requires source record")
    require(isinstance(source.get("receipt_identity"), str) and
            re.fullmatch(r"sha256:[0-9a-f]{64}", source["receipt_identity"]) is not None,
            "invalid source receipt identity")
    return source


def source_path(source: Any) -> Path:
    source = source_metadata(source)
    path = Path(source["record"])
    require(path.is_absolute(), "reuse source must use an absolute canonical path; no working-directory lookup")
    canonical = safe_path(path)
    require(str(canonical) == source["record"], "reuse source must use an absolute canonical path")
    return canonical


def validate_reuse_source(record: dict[str, Any], repo: Path, item: dict[str, Any],
                          receipt: dict[str, Any]) -> None:
    try:
        source = receipt.get("source")
        path = source_path(source)
        views = _SOURCE_VIEWS.get()
        key = str(path)
        if views is not None and key in views:
            parent, failure = views[key]
            if failure is not None:
                raise ReviewError(failure)
        else:
            try:
                parent = load(path)
            except (OSError, ValueError) as exc:
                if views is not None and len(views) < MAX_SOURCE_VIEWS:
                    views[key] = (None, str(exc) if isinstance(exc, ReviewError) else type(exc).__name__)
                raise
            if views is not None and len(views) < MAX_SOURCE_VIEWS:
                views[key] = (parent, None)
        validate_envelope(parent, repo, record["snapshot"]["rules_identity"])
        require(parent["run_id"] != record["run_id"] and
                parent["snapshot_identity"] == record["snapshot_identity"],
                "reuse is limited to the identical frozen input and rules")
        original = find_item(parent, item["item_id"])
        require(original["state"] == "completed", "reuse source must be directly completed; no chains")
        validate_receipt(parent, repo, original, original["receipt"], allow_reuse=False)
        require(digest(original["receipt"]) == source.get("receipt_identity") and
                original["receipt"]["evidence"] == receipt["evidence"],
                "reuse source is not a valid completed receipt")
    except (ReviewError, OSError, ValueError, KeyError, TypeError, IndexError,
            StopIteration, subprocess.TimeoutExpired) as exc:
        # The record itself and its local proofs are checked before this boundary.
        # Do not print payloads/paths or call missing external evidence 'completed'.
        detail = str(exc) if isinstance(exc, ReviewError) else type(exc).__name__
        raise ReuseUnavailable("reuse source invalid: " + detail + "; restore it or explicitly reopen this item") from exc


def validate_envelope(record: dict[str, Any], repo: Path, rules_identity: str) -> None:
    require(record.get("schema_version") == SCHEMA and type(record.get("schema_version")) is int,
            "unsupported execution schema; retain the old record and init a separate schema-3 record; no automatic promotion")
    require(isinstance(record.get("run_id"), str) and
            re.fullmatch(r"[0-9a-f]{32}", record["run_id"]) is not None, "invalid run identity")
    snapshot = record.get("snapshot")
    require(isinstance(snapshot, dict), "missing snapshot")
    require(snapshot.get("inventory_policy") == _shared.POLICY, "review inventory policy changed")
    require(nonempty(rules_identity) and snapshot.get("rules_identity") == rules_identity,
            "effective rules/context identity is missing or changed")
    require(snapshot.get("repository_root") == str(repo) and
            snapshot.get("repository_identity") == repository(repo), "repository identity changed")
    base = exact_commit(repo, snapshot.get("review_base"))
    head = exact_commit(repo, snapshot.get("head"))
    git(repo, "merge-base", "--is-ancestor", base, head)
    require(snapshot.get("tree") == text(repo, "rev-parse", head + "^{tree}") and
            record.get("snapshot_identity") == digest(snapshot), "frozen snapshot mismatch")
    items = record.get("items")
    expected = frozen_inventory(repo, base, head, items)
    if "inventory_identity" in snapshot:
        require(snapshot["inventory_identity"] == digest(expected), "captured inventory identity changed")
    require(isinstance(items, list) and len(items) == len(expected), "inventory coverage changed")
    for item, original in zip(items, expected):
        require(isinstance(item, dict) and all(item.get(k) == v for k, v in original.items()),
                "inventory paths, order or content identity changed")
        require(item.get("state") in STATES and type(item.get("attempt")) is int and item["attempt"] > 0,
                "invalid item state or attempt")
        history = item.get("history")
        require(isinstance(history, list) and len(history) == item["attempt"] - 1, "missing retry history")
        operation_ids: set[str] = set()
        for number, prior in enumerate(history, 1):
            require(isinstance(prior, dict) and type(prior.get("attempt")) is int and prior.get("attempt") == number and
                    prior.get("state") in {"pending", "failed", "reused"} and nonempty(prior.get("reason")),
                    "invalid retry history")
            operation = prior.get("operation")
            if operation is not None:
                require(isinstance(operation, dict) and operation.get("version") == 1 and
                        type(operation.get("version")) is int, "invalid recovery operation")
                require(isinstance(operation.get("id"), str) and
                        re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,127}", operation["id"]) is not None,
                        "invalid recovery operation ID")
                require(operation["id"] not in operation_ids, "duplicate recovery operation ID")
                operation_ids.add(operation["id"])
                require(operation.get("kind") == ("reopen" if prior["state"] == "reused" else "retry") and
                        operation.get("run_id") == record["run_id"] and
                        type(operation.get("expected_attempt")) is int and
                        operation["expected_attempt"] == number, "recovery operation identity mismatch")
            if prior["state"] in {"failed", "reused"}:
                receipt_identity(record, {**item, "attempt": number}, prior.get("receipt"))
                require(prior["receipt"]["state"] == prior["state"], "history receipt state mismatch")
                if prior["state"] == "reused":
                    require(operation is not None and nonempty(prior.get("invalidation_reason")) and
                            prior.get("receipt_identity") == digest(prior["receipt"]),
                            "reopened reuse requires its operation and preserved receipt identity")
            else:
                require(prior.get("receipt") is None, "pending history cannot claim a receipt")
        if item["state"] == "pending":
            require(item.get("receipt") is None, "pending item cannot carry a result")
        else:
            receipt_identity(record, item, item.get("receipt"))
            require(item["receipt"]["state"] == item["state"], "receipt and item state differ")


@evidence_operation
def inspect_record(record: dict[str, Any], repo: Path, rules_identity: str,
                   *, allow_reuse: bool = True) -> dict[str, str]:
    """Fail closed for local corruption; diagnose unavailable external sources per item."""
    validate_envelope(record, repo, rules_identity)
    completed = [item for item in record["items"] if item["state"] in {"completed", "reused"}]
    preload_evidence(repo, completed)
    invalid: dict[str, str] = {}
    for item in completed:
        try:
            validate_receipt(record, repo, item, item["receipt"], allow_reuse=allow_reuse)
        except ReuseUnavailable as exc:
            invalid[item["item_id"]] = str(exc)
    return invalid


@evidence_operation
def validate_record(record: dict[str, Any], repo: Path, rules_identity: str,
                    *, allow_reuse: bool = True) -> None:
    invalid = inspect_record(record, repo, rules_identity, allow_reuse=allow_reuse)
    require(not invalid, "external reuse evidence is invalid; inspect status and restore or reopen affected items")


def find_item(record: dict[str, Any], item_id: str) -> dict[str, Any]:
    matches = [item for item in record["items"] if item["item_id"] == item_id]
    require(len(matches) == 1, "unknown or ambiguous item")
    return matches[0]


@evidence_operation
def apply_receipt(record: dict[str, Any], repo: Path, item_id: str, state: str,
                  payload: dict[str, Any]) -> dict[str, str]:
    invalid = inspect_record(record, repo, record["snapshot"]["rules_identity"])
    if state == "reused":
        # Reject ambiguous inputs before admission instead of guessing a base directory.
        source_path(payload.get("source"))
    item = find_item(record, item_id)
    require(payload.get("state", state) == state, "payload cannot override requested state")
    receipt = {**payload, "state": state}
    validate_receipt(record, repo, item, receipt)
    if item["state"] != "pending":
        require(item["state"] == state and item["receipt"] == receipt, "conflicting terminal receipt")
        return invalid
    item["state"], item["receipt"] = state, receipt
    return invalid


def recovery_request(record: dict[str, Any], item: dict[str, Any], reason: str,
                     run_id: str, expected_attempt: int, operation_id: str,
                     kind: str) -> tuple[dict[str, Any], bool]:
    require(run_id == record["run_id"] and type(run_id) is str, "recovery belongs to another run")
    require(type(expected_attempt) is int and expected_attempt > 0 and nonempty(reason),
            "recovery requires an explicit expected attempt and reason")
    require(isinstance(operation_id, str) and
            re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,127}", operation_id) is not None,
            "recovery requires a stable operation ID")
    operation = {"version": 1, "id": operation_id, "kind": kind,
                 "run_id": run_id, "expected_attempt": expected_attempt}
    for prior in item["history"]:
        saved = prior.get("operation")
        if isinstance(saved, dict) and saved.get("id") == operation_id:
            require(saved == operation and prior["reason"] == reason, "conflicting recovery request replay")
            return operation, True
    require(expected_attempt == item["attempt"], "stale recovery request; current attempt is unchanged")
    return operation, False


def transition_result(item: dict[str, Any], operation: dict[str, Any], replayed: bool) -> dict[str, Any]:
    return {"operation_id": operation["id"], "kind": operation["kind"],
            "item_id": item["item_id"], "from_attempt": operation["expected_attempt"],
            "to_attempt": operation["expected_attempt"] + 1, "replayed": replayed}


def retry(record: dict[str, Any], item_id: str, reason: str, *,
          run_id: str, expected_attempt: int, operation_id: str) -> dict[str, Any]:
    """Advance only the requested attempt; duplicate/late transport cannot cancel new work."""
    item = find_item(record, item_id)
    operation, replayed = recovery_request(record, item, reason, run_id, expected_attempt, operation_id, "retry")
    if not replayed:
        require(item["state"] in {"pending", "failed"}, "retry requires pending/failed work")
        item["history"].append({"attempt": item["attempt"], "state": item["state"],
                                "receipt": item["receipt"], "reason": reason, "operation": operation})
        item.update(state="pending", attempt=item["attempt"] + 1, receipt=None)
    return transition_result(item, operation, replayed)


@evidence_operation
def reopen(record: dict[str, Any], repo: Path, item_id: str, reason: str, *,
           run_id: str, expected_attempt: int, operation_id: str) -> dict[str, Any]:
    invalid = inspect_record(record, repo, record["snapshot"]["rules_identity"])
    item = find_item(record, item_id)
    operation, replayed = recovery_request(record, item, reason, run_id, expected_attempt, operation_id, "reopen")
    if not replayed:
        require(item["state"] == "reused" and item_id in invalid,
                "reopen requires invalid external reuse evidence; valid or completed work cannot be erased")
        item["history"].append({"attempt": item["attempt"], "state": "reused", "receipt": item["receipt"],
                                "reason": reason, "operation": operation,
                                "invalidation_reason": invalid[item_id],
                                "receipt_identity": digest(item["receipt"])})
        item.update(state="pending", attempt=item["attempt"] + 1, receipt=None)
    return transition_result(item, operation, replayed)


def summary(record: dict[str, Any], limit: int = 10, offset: int = 0, *,
            invalid_sources: dict[str, str] | None = None) -> dict[str, Any]:
    invalid_sources = invalid_sources or {}
    counts = {state: 0 for state in (*STATES, "invalid_source")}
    remaining = []
    for item in record["items"]:
        observed = "invalid_source" if item["item_id"] in invalid_sources else item["state"]
        counts[observed] += 1
        if observed in {"pending", "failed", "invalid_source"}:
            entry = {key: item[key] for key in ("item_id", "path", "state", "attempt")}
            if observed == "invalid_source":
                entry.update(state=observed, recorded_state=item["state"],
                             reason=invalid_sources[item["item_id"]], recovery="restore_source_or_reopen")
            remaining.append(entry)
    total = len(record["items"])
    complete = total > 0 and not remaining
    return {"run_id": record["run_id"], "snapshot_identity": record["snapshot_identity"],
            "total": total, **counts, "execution_complete": complete,
            "execution_state": "skipped" if not total else ("complete" if complete else "incomplete"),
            "quality_outcome": "not_assessed", "approval_outcome": "not_assessed",
            "coverage_basis": "declared_changed_ranges_and_file_metadata",
            "remaining": remaining[offset:offset + limit],
            "next_offset": offset + limit if offset + limit < len(remaining) else None,
            "agentHint": ("Restore invalid reuse sources or explicitly reopen their current attempt; other work may continue."
                          if invalid_sources else ("Evaluate findings and the existing approval gate separately." if complete else
                          "Continue pending work or retry with run ID, expected attempt and operation ID; do not claim full coverage."))}


def record_destination(path: Path, repo: Path) -> Path:
    path = safe_path(path)
    metadata = [Path(text(repo, "rev-parse", "--path-format=absolute", flag)).resolve()
                for flag in ("--git-dir", "--git-common-dir")]
    require(not path.is_relative_to(repo) and ".git" not in path.parts and
            not any(path.is_relative_to(directory) for directory in metadata),
            "execution records must be outside the reviewed worktree and actual Git metadata")
    return path


@contextmanager
def locked(path: Path):
    try:
        import fcntl
    except ImportError as exc:
        raise ReviewError("record mutation requires POSIX file locking") from exc
    path.parent.mkdir(parents=True, exist_ok=True)
    lock = safe_path(path.with_name(path.name + ".lock"))
    descriptor = os.open(lock, os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW, 0o600)
    try:
        require(stat.S_ISREG(os.fstat(descriptor).st_mode), "invalid execution lock")
        try:
            fcntl.flock(descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise ReviewError("execution record is busy; retry this operation") from exc
        yield
    finally:
        os.close(descriptor)


def write(path: Path, record: dict[str, Any]) -> None:
    data = json.dumps(record, ensure_ascii=False, indent=2, sort_keys=True, allow_nan=False) + "\n"
    require(len(data.encode("utf-8")) <= MAX_BYTES, "execution record exceeds bounded storage")
    descriptor, name = tempfile.mkstemp(prefix=".review-", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(name, path)
    finally:
        Path(name).unlink(missing_ok=True)


@evidence_operation
def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    for command in ("init", "status", "evidence", "receipt", "retry", "reopen", "check"):
        sub = commands.add_parser(command)
        sub.add_argument("--repo", type=Path, required=True)
        sub.add_argument("--record", type=Path, required=True)
        sub.add_argument("--rules-identity", required=True)
        if command == "init":
            sub.add_argument("--scope", type=Path, required=True)
        if command in {"evidence", "receipt", "retry", "reopen"}:
            sub.add_argument("--item", required=True)
        if command == "evidence":
            sub.add_argument("--side", choices=("base", "head"), required=True)
            sub.add_argument("--start", type=int)
            sub.add_argument("--end", type=int)
        if command == "receipt":
            sub.add_argument("--state", choices=STATES[1:], required=True)
            sub.add_argument("--receipt", type=Path, required=True)
        if command in {"retry", "reopen"}:
            sub.add_argument("--reason", required=True)
            sub.add_argument("--run-id", required=True)
            sub.add_argument("--expected-attempt", type=int, required=True)
            sub.add_argument("--operation-id", required=True)
        if command in {"status", "check"}:
            sub.add_argument("--limit", type=int, default=10)
            sub.add_argument("--offset", type=int, default=0)
        if command == "check":
            sub.add_argument("--base", required=True)
            sub.add_argument("--head", required=True)
    args = parser.parse_args()
    try:
        repo = args.repo.expanduser().resolve()
        path = record_destination(args.record, repo)
        invalid: dict[str, str] = {}
        transition = None
        if args.command in {"init", "receipt", "retry", "reopen"}:
            with locked(path):
                if args.command == "init":
                    candidate = init_record(load(args.scope), repo, args.rules_identity)
                    if path.exists():
                        record = load(path)
                        invalid = inspect_record(record, repo, args.rules_identity)
                        require(record["snapshot_identity"] == candidate["snapshot_identity"],
                                "existing record has another snapshot; choose a new record path")
                    else:
                        record = candidate
                        write(path, record)
                else:
                    record = load(path)
                    snapshot = record.get("snapshot")
                    require(isinstance(snapshot, dict) and
                            snapshot.get("rules_identity") == args.rules_identity,
                            "effective rules/context identity is missing or changed")
                    before = digest(record)
                    if args.command == "receipt":
                        invalid = apply_receipt(record, repo, args.item, args.state, load(args.receipt))
                    elif args.command == "retry":
                        invalid = inspect_record(record, repo, args.rules_identity)
                        transition = retry(record, args.item, args.reason, run_id=args.run_id,
                                           expected_attempt=args.expected_attempt, operation_id=args.operation_id)
                    else:
                        transition = reopen(record, repo, args.item, args.reason, run_id=args.run_id,
                                            expected_attempt=args.expected_attempt, operation_id=args.operation_id)
                        invalid = inspect_record(record, repo, args.rules_identity)
                    # The old record and incoming result were validated once;
                    # these two deterministic transitions cannot change inventory.
                    if digest(record) != before:
                        write(path, record)
        else:
            record = load(path)
            invalid = inspect_record(record, repo, args.rules_identity)
        limit, offset = getattr(args, "limit", 10), getattr(args, "offset", 0)
        require(1 <= limit <= 100 and offset >= 0, "invalid pagination")
        if args.command == "evidence":
            output = evidence(repo, find_item(record, args.item), args.side, args.start, args.end)
        else:
            output = summary(record, limit, offset, invalid_sources=invalid)
            if transition is not None:
                output["transition"] = transition
        if args.command == "check":
            require(args.base == record["snapshot"]["review_base"] and
                    args.head == record["snapshot"]["head"], "approval target differs from execution snapshot")
        print(json.dumps(output, ensure_ascii=False, sort_keys=True))
        return 1 if args.command == "check" and not output["execution_complete"] else 0
    except (ReviewError, OSError, ValueError, KeyError, TypeError, IndexError,
            StopIteration, subprocess.TimeoutExpired) as exc:
        # Do not echo JSON payloads, Git stderr or secret-bearing source content.
        message = str(exc) if isinstance(exc, ReviewError) else type(exc).__name__
        print(json.dumps({"status": "blocked", "reason": message,
                          "quality_outcome": "not_assessed", "approval_outcome": "not_assessed"}))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
