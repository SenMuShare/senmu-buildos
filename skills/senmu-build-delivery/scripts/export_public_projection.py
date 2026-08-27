#!/usr/bin/env python3
"""Plan or generate a public source projection from an explicit allowlist."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import tempfile
from pathlib import Path


MARKER = ".senmu-public-projection.json"
ABSOLUTE_PRIVATE_PATH = re.compile(
    r"(?:/Users/[A-Za-z0-9._-]+/|/home/[A-Za-z0-9._-]+/|[A-Za-z]:\\Users\\[A-Za-z0-9._-]+\\)"
)


def relative_path(raw: str, label: str) -> Path:
    path = Path(raw)
    if path.is_absolute() or ".." in path.parts or path == Path("."):
        raise ValueError(f"{label} 必须是项目内非空相对路径：{raw}")
    return path


def load_manifest(path: Path) -> dict[str, object]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("schema_version") != "1.0":
        raise ValueError("manifest.schema_version 必须为 1.0")
    includes = data.get("include")
    if not isinstance(includes, list) or not includes:
        raise ValueError("manifest.include 必须是非空数组")
    data["include"] = [relative_path(str(item), "include") for item in includes]
    excludes = data.get("exclude", [])
    if not isinstance(excludes, list):
        raise ValueError("manifest.exclude 必须是数组")
    data["exclude"] = [relative_path(str(item), "exclude") for item in excludes]
    deny_terms = data.get("deny_terms", [])
    if not isinstance(deny_terms, list) or any(not isinstance(item, str) or not item for item in deny_terms):
        raise ValueError("manifest.deny_terms 必须是非空字符串数组")
    return data


def is_excluded(path: Path, excludes: list[Path]) -> bool:
    return any(path == excluded or excluded in path.parents for excluded in excludes)


def collect_files(source: Path, includes: list[Path], excludes: list[Path]) -> list[Path]:
    files: set[Path] = set()
    for included in includes:
        candidate = source / included
        if not candidate.exists():
            raise ValueError(f"公开白名单路径不存在：{included.as_posix()}")
        candidates = [candidate] if candidate.is_file() else candidate.rglob("*")
        for path in candidates:
            if path.is_symlink():
                raise ValueError(f"公开投影拒绝符号链接：{path.relative_to(source)}")
            if not path.is_file():
                continue
            relative = path.relative_to(source)
            if ".git" in relative.parts or "__pycache__" in relative.parts or is_excluded(relative, excludes):
                continue
            files.add(relative)
    return sorted(files)


def scan_file(path: Path, relative: Path, deny_terms: list[str]) -> list[str]:
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return []
    errors = []
    if ABSOLUTE_PRIVATE_PATH.search(text):
        errors.append(f"{relative.as_posix()}: 包含本机绝对路径")
    for term in deny_terms:
        if term in text:
            errors.append(f"{relative.as_posix()}: 包含私有实例标识 {term!r}")
    return errors


def manifest_digest(manifest_path: Path) -> str:
    return hashlib.sha256(manifest_path.read_bytes()).hexdigest()


def apply_projection(source: Path, target: Path, files: list[Path], digest: str) -> None:
    target.mkdir(parents=True, exist_ok=True)
    existing = {path.name for path in target.iterdir()}
    if existing - {".git", MARKER} and not (target / MARKER).is_file():
        raise ValueError("目标目录非空且没有公开投影标记，拒绝覆盖")

    with tempfile.TemporaryDirectory(prefix="senmu-public-projection-") as temporary:
        staging = Path(temporary)
        for relative in files:
            destination = staging / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source / relative, destination)
        marker = {
            "schema_version": "1.0",
            "projection_mode": "generated_only",
            "manifest_sha256": digest,
        }
        (staging / MARKER).write_text(json.dumps(marker, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

        for path in target.iterdir():
            if path.name == ".git":
                continue
            if path.is_dir():
                shutil.rmtree(path)
            else:
                path.unlink()
        for path in staging.iterdir():
            destination = target / path.name
            if path.is_dir():
                shutil.copytree(path, destination)
            else:
                shutil.copy2(path, destination)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--target", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--apply", action="store_true", help="通过检查后同步目标；默认只输出计划")
    args = parser.parse_args()

    source = args.source.expanduser().resolve()
    target = args.target.expanduser().resolve()
    manifest_path = args.manifest.expanduser().resolve()
    if not source.is_dir() or not manifest_path.is_file():
        raise SystemExit("[ERROR] source 必须是目录且 manifest 必须存在")
    if target == source or source in target.parents or target in source.parents:
        raise SystemExit("[ERROR] 公开投影目标与私有权威根不得重叠")

    try:
        manifest = load_manifest(manifest_path)
        files = collect_files(source, manifest["include"], manifest["exclude"])
        errors = []
        for relative in files:
            errors.extend(scan_file(source / relative, relative, manifest["deny_terms"]))
        if errors:
            raise ValueError("公开投影隐私门禁失败：\n" + "\n".join(errors))
        digest = manifest_digest(manifest_path)
        if args.apply:
            apply_projection(source, target, files, digest)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        raise SystemExit(f"[ERROR] {exc}") from exc

    print(json.dumps({
        "mode": "apply" if args.apply else "plan",
        "file_count": len(files),
        "manifest_sha256": digest,
        "files": [path.as_posix() for path in files],
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
