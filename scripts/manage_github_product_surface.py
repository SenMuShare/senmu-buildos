#!/usr/bin/env python3
"""Validate and synchronize the GitHub discovery surface for Senmu BuildOS."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SURFACE_FILE = "GITHUB_PRODUCT_SURFACE.json"
LANGUAGES = {"zh", "en", "ja"}
TOPIC_PATTERN = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")


class ProductSurfaceError(ValueError):
    """Raised when the local or remote GitHub product surface is invalid."""


def load_surface(root: Path = ROOT) -> dict[str, object]:
    path = root / SURFACE_FILE
    try:
        surface = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ProductSurfaceError(f"{SURFACE_FILE} is unreadable: {exc}") from exc
    if not isinstance(surface, dict):
        raise ProductSurfaceError(f"{SURFACE_FILE} must contain one JSON object")
    return surface


def validate_local_surface(root: Path = ROOT) -> dict[str, object]:
    surface = load_surface(root)
    if surface.get("schema_version") != 1:
        raise ProductSurfaceError("unsupported GitHub product surface schema")

    version = (root / "VERSION").read_text(encoding="utf-8").strip()
    if surface.get("reviewed_for_version") != version:
        raise ProductSurfaceError("GitHub product surface review must match VERSION")

    repository = surface.get("repository")
    if not isinstance(repository, str) or not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repository):
        raise ProductSurfaceError("repository must use owner/name")
    description = surface.get("description")
    if not isinstance(description, str) or not 40 <= len(description) <= 350 or "BuildOS" not in description:
        raise ProductSurfaceError("description must be a concise 40-350 character BuildOS statement")

    topics = surface.get("topics")
    if not isinstance(topics, list) or not 8 <= len(topics) <= 20:
        raise ProductSurfaceError("topics must contain 8-20 discovery terms")
    if len(set(topics)) != len(topics) or topics != sorted(topics):
        raise ProductSurfaceError("topics must be unique and sorted")
    if any(not isinstance(topic, str) or TOPIC_PATTERN.fullmatch(topic) is None for topic in topics):
        raise ProductSurfaceError("topics must be lowercase GitHub topic slugs")

    readmes = surface.get("readmes")
    if not isinstance(readmes, dict) or set(readmes) != LANGUAGES:
        raise ProductSurfaceError("readmes must declare zh, en, and ja files")
    marker = f"<!-- product-surface-review: {version} -->"
    for language, relative in readmes.items():
        if not isinstance(relative, str):
            raise ProductSurfaceError(f"README path for {language} must be a string")
        path = root / relative
        if not path.is_file() or marker not in path.read_text(encoding="utf-8"):
            raise ProductSurfaceError(f"{relative} must carry the current product-surface review marker")

    review = surface.get("readme_review")
    if not isinstance(review, dict):
        raise ProductSurfaceError("readme_review is required")
    sections = review.get("updated_sections")
    if not isinstance(sections, list) or not sections or any(not isinstance(item, str) or not item.strip() for item in sections):
        raise ProductSurfaceError("readme_review.updated_sections must name the reviewed product sections")
    summary = review.get("summary")
    if not isinstance(summary, dict) or set(summary) != LANGUAGES:
        raise ProductSurfaceError("readme_review.summary must contain zh, en, and ja")
    if any(not isinstance(value, str) or len(value.strip()) < 20 for value in summary.values()):
        raise ProductSurfaceError("each README review summary must describe the product narrative change")
    return surface


def run_gh(command: list[str], *, root: Path, input_text: str | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["gh", *command],
        cwd=root,
        check=False,
        capture_output=True,
        text=True,
        input=input_text,
    )


def read_remote_surface(surface: dict[str, object], root: Path = ROOT) -> dict[str, object]:
    repository = str(surface["repository"])
    result = run_gh(["api", f"repos/{repository}"], root=root)
    if result.returncode != 0:
        raise ProductSurfaceError(f"cannot read GitHub repository metadata: {(result.stdout + result.stderr).strip()}")
    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise ProductSurfaceError(f"GitHub repository metadata is invalid JSON: {exc}") from exc
    return {
        "description": payload.get("description") or "",
        "topics": sorted(payload.get("topics") or []),
    }


def sync_remote_surface(surface: dict[str, object], *, root: Path = ROOT, apply: bool) -> dict[str, object]:
    expected = {
        "description": surface["description"],
        "topics": surface["topics"],
    }
    before = read_remote_surface(surface, root)
    if before == expected:
        return {"repository": surface["repository"], "changed": False, "verified": True}
    if not apply:
        raise ProductSurfaceError("GitHub repository description or topics differ from the reviewed product surface")

    repository = str(surface["repository"])
    description = run_gh(
        ["api", "-X", "PATCH", f"repos/{repository}", "-f", f"description={surface['description']}"],
        root=root,
    )
    if description.returncode != 0:
        raise ProductSurfaceError(f"cannot update GitHub description: {(description.stdout + description.stderr).strip()}")
    topics = run_gh(
        ["api", "-X", "PUT", f"repos/{repository}/topics", "--input", "-"],
        root=root,
        input_text=json.dumps({"names": surface["topics"]}),
    )
    if topics.returncode != 0:
        raise ProductSurfaceError(f"cannot update GitHub topics: {(topics.stdout + topics.stderr).strip()}")
    after = read_remote_surface(surface, root)
    if after != expected:
        raise ProductSurfaceError("GitHub product surface still differs after synchronization")
    return {"repository": surface["repository"], "changed": True, "verified": True}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--check-remote", action="store_true")
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    root = args.root.resolve()
    try:
        surface = validate_local_surface(root)
        report: dict[str, object] = {
            "version": surface["reviewed_for_version"],
            "repository": surface["repository"],
            "local_valid": True,
        }
        if args.check_remote or args.apply:
            report["remote"] = sync_remote_surface(surface, root=root, apply=args.apply)
    except (OSError, ProductSurfaceError) as exc:
        raise SystemExit(f"[ERROR] {exc}") from exc
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
