#!/usr/bin/env python3
"""Prepare and validate a Senmu BuildOS release version."""

from __future__ import annotations

import argparse
import difflib
import json
import os
import re
import stat
import tempfile
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SEMVER_RE = re.compile(
    r"^(?P<major>0|[1-9]\d*)\."
    r"(?P<minor>0|[1-9]\d*)\."
    r"(?P<patch>0|[1-9]\d*)"
    r"(?:-(?P<prerelease>[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?"
    r"(?:\+(?P<build>[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?$"
)
README_VERSION_PATTERNS = {
    "README.md": r"(Senmu BuildOS 当前正式版本为 `v)([^`]+)(`)",
    "README.en.md": r"(The current formal release is Senmu BuildOS `v)([^`]+)(`)",
    "README.ja.md": r"(Senmu BuildOS の現行正式リリースは `v)([^`]+)(`)",
}


class ReleaseError(ValueError):
    """Raised when release metadata is incomplete or inconsistent."""


def parse_semver(value: str) -> re.Match[str]:
    match = SEMVER_RE.fullmatch(value)
    if not match:
        raise ReleaseError(f"invalid semantic version: {value}")
    return match


def prerelease_key(value: str | None) -> tuple[int, tuple[tuple[int, int | str], ...]]:
    if value is None:
        return (1, ())
    parts: list[tuple[int, int | str]] = []
    for part in value.split("."):
        if part.isdigit():
            parts.append((0, int(part)))
        else:
            parts.append((1, part))
    return (0, tuple(parts))


def version_key(value: str) -> tuple[int, int, int, tuple[int, tuple[tuple[int, int | str], ...]]]:
    match = parse_semver(value)
    return (
        int(match.group("major")),
        int(match.group("minor")),
        int(match.group("patch")),
        prerelease_key(match.group("prerelease")),
    )


def load_json(path: Path) -> dict[str, object]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ReleaseError(f"cannot read valid JSON from {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise ReleaseError(f"expected a JSON object in {path}")
    return payload


def current_version(root: Path) -> str:
    try:
        version = (root / "VERSION").read_text(encoding="utf-8").strip()
    except OSError as exc:
        raise ReleaseError(f"cannot read VERSION: {exc}") from exc
    parse_semver(version)

    plugin = load_json(root / ".codex-plugin/plugin.json")
    claude_plugin = load_json(root / ".claude-plugin/plugin.json")
    marketplace = load_json(root / ".agents/plugins/marketplace.json")
    claude_marketplace = load_json(root / ".claude-plugin/marketplace.json")
    plugins = marketplace.get("plugins")
    if not isinstance(plugins, list) or len(plugins) != 1 or not isinstance(plugins[0], dict):
        raise ReleaseError("marketplace must contain exactly one plugin entry")
    source = plugins[0].get("source")
    if not isinstance(source, dict):
        raise ReleaseError("marketplace plugin source is missing")

    if plugin.get("version") != version:
        raise ReleaseError("VERSION and plugin manifest version do not agree")
    if claude_plugin.get("version") != version:
        raise ReleaseError("VERSION and Claude Code plugin manifest version do not agree")
    if source.get("ref") != f"v{version}":
        raise ReleaseError("VERSION and marketplace release ref do not agree")
    claude_plugins = claude_marketplace.get("plugins")
    if not isinstance(claude_plugins, list) or len(claude_plugins) != 1 or not isinstance(claude_plugins[0], dict):
        raise ReleaseError("Claude Code marketplace must contain exactly one plugin entry")
    if claude_plugins[0].get("version") != version:
        raise ReleaseError("VERSION and Claude Code marketplace version do not agree")

    for relative, pattern in README_VERSION_PATTERNS.items():
        text = (root / relative).read_text(encoding="utf-8")
        match = re.search(pattern, text)
        if match is None or match.group(2) != version:
            raise ReleaseError(f"VERSION and {relative} current release do not agree")

    changelog = (root / "CHANGELOG.md").read_text(encoding="utf-8")
    if f"## [{version}]" not in changelog:
        raise ReleaseError(f"CHANGELOG.md has no release heading for {version}")
    return version


def validate_current(root: Path, tag: str | None = None) -> str:
    version = current_version(root)
    if tag is not None and tag != f"v{version}":
        raise ReleaseError(f"tag {tag} does not match v{version}")
    return version


def replace_once(text: str, pattern: str, replacement: str, label: str) -> str:
    updated, count = re.subn(pattern, replacement, text, count=1)
    if count != 1:
        raise ReleaseError(f"could not update exactly one {label}")
    return updated


def prepare_changes(root: Path, target: str, release_date: str) -> dict[Path, str]:
    current = validate_current(root)
    parse_semver(target)
    if version_key(target) <= version_key(current):
        raise ReleaseError(f"target version {target} must be newer than {current}")
    try:
        date.fromisoformat(release_date)
    except ValueError as exc:
        raise ReleaseError(f"invalid release date: {release_date}") from exc

    version_path = root / "VERSION"
    plugin_path = root / ".codex-plugin/plugin.json"
    claude_plugin_path = root / ".claude-plugin/plugin.json"
    marketplace_path = root / ".agents/plugins/marketplace.json"
    claude_marketplace_path = root / ".claude-plugin/marketplace.json"
    changelog_path = root / "CHANGELOG.md"
    readme_paths = {relative: root / relative for relative in README_VERSION_PATTERNS}

    plugin_text = plugin_path.read_text(encoding="utf-8")
    claude_plugin_text = claude_plugin_path.read_text(encoding="utf-8")
    marketplace_text = marketplace_path.read_text(encoding="utf-8")
    claude_marketplace_text = claude_marketplace_path.read_text(encoding="utf-8")
    changelog_text = changelog_path.read_text(encoding="utf-8")
    readme_texts = {relative: path.read_text(encoding="utf-8") for relative, path in readme_paths.items()}

    unreleased_marker = "## Unreleased\n"
    if changelog_text.count(unreleased_marker) != 1:
        raise ReleaseError("CHANGELOG.md must contain exactly one Unreleased heading")
    _, unreleased_body = changelog_text.split(unreleased_marker, 1)
    next_release = re.search(r"^## \[", unreleased_body, re.MULTILINE)
    pending = unreleased_body[: next_release.start()] if next_release else unreleased_body
    if not re.search(r"^### ", pending, re.MULTILINE):
        raise ReleaseError("CHANGELOG.md Unreleased section has no releasable entries")

    changes = {
        version_path: f"{target}\n",
        plugin_path: replace_once(
            plugin_text,
            r'("version"\s*:\s*")[^"]+("(?=\s*[,}]))',
            rf"\g<1>{target}\g<2>",
            "plugin version",
        ),
        claude_plugin_path: replace_once(
            claude_plugin_text,
            r'("version"\s*:\s*")[^"]+("(?=\s*[,}]))',
            rf"\g<1>{target}\g<2>",
            "Claude Code plugin version",
        ),
        marketplace_path: replace_once(
            marketplace_text,
            r'("ref"\s*:\s*")v[^"]+("\s*)',
            rf"\g<1>v{target}\g<2>",
            "marketplace release ref",
        ),
        claude_marketplace_path: replace_once(
            claude_marketplace_text,
            r'("version"\s*:\s*")[^"]+("(?=\s*[,}]))',
            rf"\g<1>{target}\g<2>",
            "Claude Code marketplace version",
        ),
        changelog_path: changelog_text.replace(
            unreleased_marker,
            f"{unreleased_marker}\n## [{target}] - {release_date}\n",
            1,
        ),
    }
    for relative, pattern in README_VERSION_PATTERNS.items():
        changes[readme_paths[relative]] = replace_once(
            readme_texts[relative],
            pattern,
            rf"\g<1>{target}\g<3>",
            f"{relative} current release",
        )

    json.loads(changes[plugin_path])
    json.loads(changes[claude_plugin_path])
    json.loads(changes[marketplace_path])
    json.loads(changes[claude_marketplace_path])
    return changes


def apply_changes(changes: dict[Path, str]) -> None:
    originals = {path: path.read_bytes() for path in changes}
    original_modes = {path: stat.S_IMODE(path.stat().st_mode) for path in changes}
    temporary: dict[Path, Path] = {}
    replaced: list[Path] = []
    try:
        for path, content in changes.items():
            descriptor, raw_path = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
            temp_path = Path(raw_path)
            temporary[path] = temp_path
            with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
                handle.write(content)
                handle.flush()
                os.fsync(handle.fileno())
            os.chmod(temp_path, original_modes[path])
        for path, temp_path in temporary.items():
            os.replace(temp_path, path)
            replaced.append(path)
    except Exception:
        for path in replaced:
            path.write_bytes(originals[path])
            os.chmod(path, original_modes[path])
        raise
    finally:
        for temp_path in temporary.values():
            temp_path.unlink(missing_ok=True)


def print_diff(changes: dict[Path, str], root: Path) -> None:
    for path, updated in changes.items():
        original = path.read_text(encoding="utf-8")
        relative = path.relative_to(root)
        for line in difflib.unified_diff(
            original.splitlines(keepends=True),
            updated.splitlines(keepends=True),
            fromfile=str(relative),
            tofile=str(relative),
        ):
            print(line, end="")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("version", nargs="?", help="new semantic version without the v prefix")
    parser.add_argument("--date", default=date.today().isoformat(), help="release date in YYYY-MM-DD")
    parser.add_argument("--dry-run", action="store_true", help="show the release diff without writing")
    parser.add_argument("--check", action="store_true", help="validate current release metadata only")
    parser.add_argument("--tag", help="also require this Git tag to equal vVERSION")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    try:
        if args.check:
            if args.version:
                raise ReleaseError("--check does not accept a target version")
            version = validate_current(ROOT, args.tag)
            print(f"[OK] release metadata agrees on v{version}")
            return
        if not args.version:
            raise ReleaseError("provide a target version or use --check")
        if args.tag:
            raise ReleaseError("--tag is only valid with --check")
        changes = prepare_changes(ROOT, args.version, args.date)
        print_diff(changes, ROOT)
        if args.dry_run:
            print(f"[DRY RUN] no files changed; target is v{args.version}")
            return
        apply_changes(changes)
        validate_current(ROOT)
        print(f"[OK] prepared release metadata for v{args.version}")
        print("Next: run all tests, review the diff, commit, then create and push tag v" + args.version)
    except (OSError, ReleaseError) as exc:
        raise SystemExit(f"[ERROR] {exc}") from exc


if __name__ == "__main__":
    main()
