#!/usr/bin/env python3
"""Verify that review, tests, tag, and artifact resolve to one release commit."""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path


def git(repo: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(repo), *args],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        detail = (result.stderr or result.stdout).strip()
        raise SystemExit(f"[BLOCKED] git {' '.join(args)} failed: {detail}")
    return result.stdout.rstrip("\n")


def resolve(repo: Path, ref: str) -> str:
    return git(repo, "rev-parse", "--verify", f"{ref}^{{commit}}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--source-ref", required=True)
    parser.add_argument("--tested-commit", required=True)
    parser.add_argument("--reviewed-commit")
    parser.add_argument("--tag")
    parser.add_argument("--artifact-source")
    parser.add_argument("--require-clean", action="store_true")
    args = parser.parse_args()

    repo = Path(git(args.repo, "rev-parse", "--show-toplevel")).resolve()
    identities = {
        "release_worktree_head": resolve(repo, "HEAD"),
        "release_source": resolve(repo, args.source_ref),
        "tested_commit": resolve(repo, args.tested_commit),
    }
    optional = {
        "reviewed_commit": args.reviewed_commit,
        "tag_commit": args.tag,
        "artifact_source": args.artifact_source,
    }
    for name, ref in optional.items():
        if ref:
            identities[name] = resolve(repo, ref)

    candidate = identities["release_source"]
    mismatches = {name: commit for name, commit in identities.items() if commit != candidate}
    if mismatches:
        detail = ", ".join(f"{name}={commit}" for name, commit in sorted(mismatches.items()))
        raise SystemExit(f"[BLOCKED] release identity drift from {candidate}: {detail}")
    if args.require_clean and git(repo, "status", "--porcelain"):
        raise SystemExit("[BLOCKED] release source worktree is not clean")

    print(
        json.dumps(
            {
                "schema_version": 1,
                "status": "release_identity_verified",
                "repo": str(repo),
                "source_ref": args.source_ref,
                "candidate_commit": candidate,
                "identities": identities,
            },
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
