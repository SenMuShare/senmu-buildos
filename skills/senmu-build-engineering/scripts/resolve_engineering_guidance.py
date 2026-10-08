#!/usr/bin/env python3
"""Select bounded BuildOS reference routes from declared paths and risks, without scanning source."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path, PurePosixPath, PureWindowsPath
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
ENGINEERING = "skills/senmu-build-engineering/references/"
DEPLOYMENT = "skills/senmu-build-delivery/references/security/public-service-security-baseline.md"
PROFILES = {
    "python": "python-engineering-profile.md", "typescript": "typescript-engineering-profile.md",
    "go": "go-engineering-profile.md", "java": "java-engineering-profile.md",
    "rust": "stack-profiles/rust-engineering-profile.md", "javascript": "stack-profiles/javascript-node-engineering-profile.md",
    "c": "stack-profiles/c-cpp-engineering-profile.md", "cpp": "stack-profiles/c-cpp-engineering-profile.md",
    "kotlin": "stack-profiles/kotlin-engineering-profile.md", "swift": "stack-profiles/swift-engineering-profile.md",
    "php": "stack-profiles/php-engineering-profile.md",
}
EXTENSIONS = {
    ".py": "python", ".pyi": "python",
    ".ts": "typescript", ".tsx": "typescript", ".mts": "typescript", ".cts": "typescript",
    ".go": "go", ".java": "java", ".rs": "rust", ".c": "c",
    ".cpp": "cpp", ".cc": "cpp", ".cxx": "cpp", ".hpp": "cpp", ".hxx": "cpp",
    ".js": "javascript", ".jsx": "javascript", ".mjs": "javascript", ".cjs": "javascript",
    ".kt": "kotlin", ".kts": "kotlin", ".swift": "swift", ".php": "php", ".phtml": "php",
}
RISKS = ("public-service", "untrusted-input", "paid-api", "dependency", "public-contract")
# Optional declared concerns select methods; they do not diagnose a project.
GENERAL_EXECUTION = "skills/senmu-build-project/references/task-execution-and-state-management.md"
CONCERN_ROUTES = {
    "verification": ENGINEERING + "software-testing-and-quality-verification.md",
    "complexity": ENGINEERING + "implementation-economy-and-overengineering.md",
    "coordination": GENERAL_EXECUTION,
    "integration": "skills/senmu-build-delivery/references/multi-agent-change-units-and-version-line-closeout.md",
}
MAX_REFERENCE_BYTES = 64 * 1024
FILE_ROLES = ("compose", "kubernetes", "terraform")
SUMMARY_EXAMPLES = 3


def fingerprint(value: Any) -> str:
    return "sha256:" + hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False,
        separators=(",", ":"), allow_nan=False).encode()).hexdigest()


def path_name(value: str) -> PurePosixPath:
    if (not isinstance(value, str) or not value or len(value) > 2048 or "\\" in value
            or any(ord(ch) < 32 for ch in value) or PureWindowsPath(value).drive):
        raise ValueError("paths must be bounded project-relative POSIX names")
    path = PurePosixPath(value)
    if path.is_absolute() or ".." in path.parts or str(path) != value or value == ".":
        raise ValueError("paths must be canonical project-relative names")
    return path


def select(paths: list[str], risks: list[str], runtime: str | None = None,
           header_language: str | None = None, *, root: Path = ROOT,
           notebook_languages: dict[str, str] | None = None,
           file_roles: dict[str, str] | None = None,
           concerns: list[str] | None = None) -> dict[str, Any]:
    if len(paths) > 200 or any(risk not in RISKS for risk in risks):
        raise ValueError("unsupported risk or oversized path list")
    if runtime not in {None, "node", "browser"} or header_language not in {None, "c", "cpp"}:
        raise ValueError("invalid runtime or header language")
    concerns = [] if concerns is None else concerns
    if (not isinstance(concerns, list) or len(concerns) > 8
            or any(not isinstance(item, str) or not re.fullmatch(r"[a-z][a-z0-9-]{0,63}", item)
                   for item in concerns)):
        raise ValueError("concerns must be at most eight bounded lowercase names")
    concerns = sorted(set(concerns))
    if not paths and not risks and not concerns:
        raise ValueError("declare at least one path, risk or concern")
    notebook_languages = notebook_languages or {}
    file_roles = file_roles or {}
    for declarations in (notebook_languages, file_roles):
        if not isinstance(declarations, dict) or len(declarations) > 200:
            raise ValueError("invalid path-scoped declarations")
        for path, value in declarations.items():
            path_name(path)
            if path not in paths or not isinstance(value, str) or not re.fullmatch(r"[a-z][a-z0-9+-]{0,31}", value):
                raise ValueError("declarations must name an input path and a bounded value")
    if any(PurePosixPath(path).suffix.lower() != ".ipynb" for path in notebook_languages):
        raise ValueError("notebook language only applies to notebook paths")
    if any(role not in FILE_ROLES for role in file_roles.values()):
        raise ValueError("unsupported declared file role")
    selections: dict[str, dict[str, set[str]]] = {}
    unresolved: list[dict[str, str]] = []

    def add(reference: str, subject: str, reason: str) -> None:
        entry = selections.setdefault(reference, {"subjects": set(), "reasons": set()})
        entry["subjects"].add(subject)
        entry["reasons"].add(reason)

    for concern in concerns:
        add(CONCERN_ROUTES.get(concern, GENERAL_EXECUTION), concern,
            "declared execution concern; investigate before changing the method")
        if concern not in CONCERN_ROUTES:
            unresolved.append({"concern": concern,
                "reason": "unlisted concern: compare the goal, evidence and next action; investigate its actual cause"})

    for raw in sorted(set(paths)):
        path = path_name(raw)
        suffix, leaf = path.suffix.lower(), path.name.lower()
        language = EXTENSIONS.get(suffix)
        if suffix == ".ipynb":
            declared = notebook_languages.get(raw)
            language = declared if declared in PROFILES else None
            if not language:
                unresolved.append({"path": raw, "reason": "declare this notebook's confirmed language; unlisted kernels use project and official guidance"})
        if suffix == ".h":
            language = header_language
            if not language:
                unresolved.append({"path": raw, "reason": "header consumer language is ambiguous; declare c or cpp"})
        if language:
            add(ENGINEERING + PROFILES[language], raw, "language-specific implementation and review")
        if runtime == "node" and language in {"typescript", "javascript"}:
            add(ENGINEERING + PROFILES["javascript"], raw, "declared Node runtime")
        dependency = (leaf in {"cargo.toml", "cargo.lock", "package.json", "package-lock.json", "yarn.lock",
            "pnpm-lock.yaml", "pyproject.toml", "uv.lock", "poetry.lock", "pom.xml", "build.gradle",
            "build.gradle.kts", "composer.json", "composer.lock", "go.mod", "go.sum", "makefile",
            "cmakelists.txt"} or leaf.startswith("requirements") and suffix == ".txt"
            or suffix in {".sh", ".bash", ".ps1"}
            or ".github/workflows/" in raw and suffix in {".yml", ".yaml"})
        if dependency:
            add(ENGINEERING + "stack-profiles/dependency-and-ci-review.md", raw, "executable build or supply-chain input")
        if leaf == "cargo.toml":
            add(ENGINEERING + PROFILES["rust"], raw, "Cargo crate/toolchain contract")
        if suffix in {".sql", ".proto", ".graphql", ".gql", ".prisma"}:
            add(ENGINEERING + "stack-profiles/schema-and-migration-review.md", raw, "stored-data or consumer contract")
        infrastructure = (leaf.startswith("dockerfile") or leaf in {".dockerignore", "compose.yaml",
            "compose.yml", "docker-compose.yaml", "docker-compose.yml", "nginx.conf", "caddyfile"}
            or suffix in {".tf", ".tfvars", ".hcl", ".bicep"})
        infrastructure = infrastructure or bool(re.fullmatch(
            r"(?:docker-compose|compose)(?:\.[a-z0-9_-]+)+\.ya?ml", leaf))
        infrastructure = infrastructure or leaf.endswith((".tfvars.json", ".tf.json"))
        if raw in file_roles:
            infrastructure = True
            add(DEPLOYMENT, raw, "declared " + file_roles[raw] + " configuration")
        if infrastructure:
            add(DEPLOYMENT, raw, "deployment configuration; confirm actual exposure and platform")
        if not language and not dependency and not infrastructure and suffix not in {
                ".h", ".ipynb", ".sql", ".proto", ".graphql", ".gql", ".prisma"}:
            unresolved.append({"path": raw, "reason": "use project role and official guidance; no file-role guess"})
    for risk in sorted(set(risks)):
        if risk in {"public-service", "untrusted-input", "paid-api"}:
            add(ENGINEERING + "application-security-and-abuse.md", risk, "declared trust or cost boundary")
        if risk == "public-service":
            add(DEPLOYMENT, risk, "declared public deployment")
        if risk == "dependency":
            add(ENGINEERING + "stack-profiles/dependency-and-ci-review.md", risk, "declared dependency decision")
        if risk == "public-contract":
            add(ENGINEERING + "backend-services-and-data-contracts.md", risk, "declared producer/consumer change")
    output = []
    for relative, selection in sorted(selections.items()):
        path = root / relative
        if path.is_symlink() or not path.is_file() or path.stat().st_size > MAX_REFERENCE_BYTES:
            raise ValueError("selected installed reference is missing or invalid")
        with path.open("rb") as stream:
            data = stream.read(MAX_REFERENCE_BYTES + 1)
        if len(data) > MAX_REFERENCE_BYTES:
            raise ValueError("selected reference exceeds read bound")
        output.append({"reference": relative, "sha256": hashlib.sha256(data).hexdigest(),
            "bytes": len(data), "subjects": sorted(selection["subjects"]), "reasons": sorted(selection["reasons"])})
    identity = {"schema_version": 1, "paths": sorted(set(paths)), "risks": sorted(set(risks)),
                "runtime": runtime, "header_language": header_language, "references": output,
                "notebook_languages": dict(sorted(notebook_languages.items())),
                "file_roles": dict(sorted(file_roles.items())),
                "unresolved": unresolved}
    if concerns:
        identity["concerns"] = concerns
    return {**identity, "reference_selection_identity": fingerprint(identity),
        "status": "partial" if unresolved else "selected", "source_scanned": False,
        "project_rules_included": False, "token_usage": None,
        "agentHint": ("Investigate the declared concern against the goal, evidence and next action. "
                      "Consider unlisted causes; routes are not diagnosis, authority or a mandatory process. "
                      "Preserve valid work and safety; healthy progress needs no new ceremony."
                      if concerns else
                      "Read matching project rules first. These routes are not the complete effective review policy.")}


def summarize(result: dict[str, Any]) -> dict[str, Any]:
    """Bound model-visible paths; the identity still covers the complete selection."""
    output = {key: value for key, value in result.items()
              if key not in {"paths", "references", "unresolved", "notebook_languages", "file_roles"}}
    output.update(format="summary", path_count=len(result["paths"]),
                  unresolved_count=len(result["unresolved"]),
                  unresolved_examples=result["unresolved"][:SUMMARY_EXAMPLES],
                  declaration_count=len(result["notebook_languages"]) + len(result["file_roles"]),
                  details="Repeat the same arguments with --format full for every input and mapping.")
    output["references"] = [{**{key: value for key, value in reference.items() if key != "subjects"},
                             "subject_count": len(reference["subjects"]),
                             "subject_examples": reference["subjects"][:SUMMARY_EXAMPLES]}
                            for reference in result["references"]]
    return output


def declarations(values: list[str]) -> dict[str, str]:
    parsed = {}
    for value in values:
        name, separator, role = value.rpartition("=")
        if not separator or name in parsed:
            raise ValueError("use one PATH=value declaration per input path")
        parsed[name] = role
    return parsed


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--path", action="append", default=[])
    parser.add_argument("--risk", action="append", choices=RISKS, default=[])
    parser.add_argument("--runtime", choices=("node", "browser"))
    parser.add_argument("--header-language", choices=("c", "cpp"))
    parser.add_argument("--notebook-language", action="append", default=[], metavar="PATH=LANGUAGE")
    parser.add_argument("--file-role", action="append", default=[], metavar="PATH=ROLE")
    parser.add_argument("--concern", action="append", default=[], metavar="NAME",
                        help="Optional method concern: verification, complexity, coordination, integration; other names retain an explicit investigation gap")

    parser.add_argument("--format", choices=("summary", "full"), default="summary")
    args = parser.parse_args()
    try:
        result = select(args.path, args.risk, args.runtime, args.header_language,
                        notebook_languages=declarations(args.notebook_language),
                        file_roles=declarations(args.file_role), concerns=args.concern)
        print(json.dumps(summarize(result) if args.format == "summary" else result,
                         ensure_ascii=False, sort_keys=True))
        return 0
    except (OSError, ValueError) as exc:
        print(json.dumps({"status": "blocked", "reason": str(exc) if isinstance(exc, ValueError) else "reference unavailable"}))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
