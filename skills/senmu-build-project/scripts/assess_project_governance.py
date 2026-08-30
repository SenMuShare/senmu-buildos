#!/usr/bin/env python3
"""Read-only, authority-first inventory for an existing project."""

from __future__ import annotations

import argparse
import json
import os
import re
from collections import defaultdict
from pathlib import Path
from typing import Any


ENTRYPOINT_NAMES = {"AGENTS.md", "README.md"}
MAP_NAMES = {"PROJECT_MAP.md", "repositories.json", "REPOSITORY_CUTOVER_REPORT.md"}
AUTHORITY_REGISTRY_NAMES = {
    "项目总架构与AI修改导航.md": "project_navigation",
    "项目治理规则.md": "governance_rules",
    "发布单元登记表.md": "release_unit_registry",
    "工作树与例外登记.md": "worktree_registry",
    "当前基线.env": "current_baseline",
    "生产发布标准清单.md": "production_release_policy",
}
DURABLE_TASK_NAMES = {"TASK_REGISTER.md", "tasks.json"}
TASK_INSTANCE_NAMES = {"production-job.json", "task.json"}
QUALITY_NAMES = {"Makefile", "package.json", "pyproject.toml", "tox.ini"}
WORKFLOW_MARKERS = {"WORKFLOW.md", "WORKFLOW_AND_ARTIFACTS.md", "run-manifest.json", "workflow-manifest.json"}
PRODUCT_NAMES = {
    "PRD.md", "USER_REQUIREMENTS.md", "PRODUCT_SPECIFICATION.md",
    "REQUIREMENT_BACKLOG.md", "ROADMAP.md", "ITERATION_PLAN.md",
}
ENGINEERING_NAMES = {
    "TECHNICAL_DESIGN.md", "SYSTEM_TECHNICAL_SPECIFICATION.md", "TEST_CASES.md",
    "ARCHITECTURE.md", "TECH_DEBT.md", "TESTING_STRATEGY.md",
}
WORKLOG_NAMES = {"WORKLOG.md", "CHANGELOG.md"}
PRODUCTION_NAMES = {"RELEASE_RECORD.md", "ARTIFACT_MANIFEST.json", "DEPLOYMENT.md", "VERSION"}

# These markers are evidence for reassessment, not automatic conclusions. A
# Dockerfile may be local tooling, and an Xcode project may never ship a DMG.
CAPABILITY_MARKERS = {
    "public_source_repository": {
        "LICENSE", "LICENSE.md", "CODE_OF_CONDUCT.md", "CONTRIBUTING.md",
        "plugin.json", "marketplace.json",
    },
    "container_candidate": {
        "Dockerfile", "docker-compose.yml", "docker-compose.yaml", "compose.yml", "compose.yaml",
        "Chart.yaml",
    },
    "desktop_bundle_candidate": {
        "Package.swift", "Info.plist", "entitlements.plist", "electron-builder.yml", "electron-builder.yaml",
    },
    "package_registry_candidate": {
        "pyproject.toml", "setup.py", "setup.cfg", "package.json", "Cargo.toml", "pom.xml",
    },
    "managed_service_candidate": {
        "Procfile", "app.yaml", "vercel.json", "netlify.toml", "serverless.yml", "serverless.yaml",
    },
}
CAPABILITY_SUFFIXES = {
    "desktop_bundle_candidate": (".xcodeproj/project.pbxproj", ".xcworkspace/contents.xcworkspacedata"),
}

CACHE_PARTS = {
    ".cache", ".mypy_cache", ".next", ".pytest_cache", ".remotion", ".ruff_cache", ".tox", ".venv",
    "__pycache__", "dist", "node_modules", "vendor", "venv",
}
HISTORY_PARTS = {
    "archive", "archives", "deprecated", "history", "historical", "legacy", "old", "retired",
    "历史", "归档", "旧版", "退役",
}
BACKUP_PARTS = {
    "backup", "backups", "bak", "recovery", "restore", "snapshot", "snapshots", "备份", "快照", "恢复",
}
WORKTREE_CONTAINER_PARTS = {".worktrees", "worktrees"}
TEMPORARY_PARTS = {"scratch", "staging", "temp", "temporary", "tmp", "临时", "数据临时区", "迁移核验凭证"}
SUMMARY_EXAMPLE_LIMIT = 3
TOKEN_SPLIT_PATTERN = re.compile(r"[\s=:`\"'<>()[\]{},;，；]+")
DURABLE_TASK_PATTERN = re.compile(r"^task-\d{4}-[a-z0-9]+(?:-[a-z0-9]+)*\.md$", re.IGNORECASE)
DECLARED_ACTIVE_PATH_KEYS = {"ledger"}
DECLARED_RETIRED_PATH_KEYS = {"database", "freeze_marker", "freeze_manifest"}


def exclusion_reason(name: str) -> str | None:
    lowered = name.lower()
    normalized = re.sub(r"^\d+[._ -]+", "", lowered)
    if lowered in WORKTREE_CONTAINER_PARTS:
        return "linked_worktree"
    if lowered in CACHE_PARTS or lowered.startswith(".playwright") or "chrome-profile" in lowered:
        return "cache_or_generated"
    if (
        lowered in TEMPORARY_PARTS
        or normalized in TEMPORARY_PARTS
        or normalized.startswith(("临时", "数据临时", "迁移核验", "dev-data", "test-data"))
    ):
        return "temporary_or_staging"
    if (
        lowered in HISTORY_PARTS
        or normalized in HISTORY_PARTS
        or name in HISTORY_PARTS
        or normalized.startswith(("历史", "归档", "退役", "旧版"))
        or normalized.startswith(("history-", "archive-", "retired-"))
    ):
        return "archive_or_retired"
    if (
        lowered in BACKUP_PARTS
        or normalized in BACKUP_PARTS
        or name in BACKUP_PARTS
        or normalized.startswith(("备份", "快照", "恢复", "backup-", "recovery-", "restore-", "snapshot-"))
        or normalized.endswith(("-backup", "-backups", "_backup", "_backups", "备份"))
    ):
        return "backup_or_recovery"
    if lowered.endswith((".bak", ".backup", ".old", ".orig")):
        return "backup_or_recovery"
    return None


def git_marker_kind(root: Path) -> str | None:
    marker = root / ".git"
    if marker.is_dir():
        return "repository"
    if not marker.is_file():
        return None
    try:
        first_line = marker.read_text(encoding="utf-8", errors="replace").splitlines()[0]
    except (OSError, IndexError):
        return "git_file_repository_candidate"
    if first_line.lower().startswith("gitdir:"):
        target_text = first_line.split(":", 1)[1].strip()
        target = Path(target_text)
        if not target.is_absolute():
            target = (root / target).resolve()
        if "worktrees" in {part.lower() for part in target.parts}:
            return "linked_worktree"
    return "git_file_repository_candidate"


def release_unit_for(path: Path, root: Path, release_roots: list[Path]) -> str:
    owners = [candidate for candidate in release_roots if path == candidate or candidate in path.parents]
    owner = max(owners, key=lambda candidate: len(candidate.parts), default=root)
    return "." if owner == root else owner.relative_to(root).as_posix()


def candidate_roles(name: str, relative: str) -> list[tuple[str, str]]:
    lowered = name.lower()
    relative_lower = relative.lower()
    roles: list[tuple[str, str]] = []
    if name in DURABLE_TASK_NAMES or DURABLE_TASK_PATTERN.fullmatch(lowered):
        roles.append(("durable_task_state", "task filename marker"))
    if name in TASK_INSTANCE_NAMES:
        roles.append(("task_instance_state", "single task or production-run filename marker"))
    if lowered.endswith((".sqlite", ".sqlite3", ".db")) or name in {"run-manifest.json", "workflow-manifest.json"}:
        roles.append(("run_state", "runtime state filename or database extension"))
    if name in QUALITY_NAMES:
        roles.append(("quality_entrypoint", "recognized quality or build entrypoint"))
    if name in WORKFLOW_MARKERS or ("workflow" in lowered and lowered.endswith((".md", ".json", ".yaml", ".yml"))):
        roles.append(("workflow_contract", "workflow filename marker"))
    if name in PRODUCT_NAMES or "/product/" in f"/{relative_lower}/":
        roles.append(("product_governance", "product path or filename marker"))
    if name in ENGINEERING_NAMES or "/engineering/" in f"/{relative_lower}/":
        roles.append(("engineering_governance", "engineering path or filename marker"))
    if name in WORKLOG_NAMES:
        roles.append(("work_log", "work or version log filename marker"))
    if name in PRODUCTION_NAMES or "/receipts/" in f"/{relative_lower}/" or "/releases/" in f"/{relative_lower}/":
        roles.append(("production_truth", "release, deployment, artifact, or receipt marker"))
    path_parts = [re.sub(r"^\d+[._ -]+", "", part) for part in relative_lower.split("/")[:-1]]
    if roles and any(part == "poc" or part.startswith("poc-") or "实验" in part or part.startswith("experiment") for part in path_parts):
        return [("experiment_evidence", "candidate belongs to a POC or experiment subtree")]
    return roles


def declared_authority_from_maps(root: Path, map_paths: list[Path]) -> dict[str, list[dict[str, str]]]:
    """Extract only explicit, portable authority facts from supported project maps."""

    release_units: dict[str, dict[str, str]] = {}
    active_paths: dict[str, dict[str, str]] = {}
    retired_paths: dict[str, dict[str, str]] = {}

    def add_path(
        collection: dict[str, dict[str, str]],
        raw: Any,
        source: Path,
        role: str,
    ) -> None:
        if not isinstance(raw, str) or not raw.strip():
            return
        candidate = (root / raw).resolve()
        try:
            relative = candidate.relative_to(root).as_posix()
        except ValueError:
            return
        collection[relative] = {
            "path": relative,
            "role": role,
            "source": source.relative_to(root).as_posix(),
            "status": "declared" if collection is active_paths else "declared_retired",
        }

    for source in map_paths:
        if source.name != "repositories.json":
            continue
        try:
            payload = json.loads(source.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        repositories = payload.get("repositories")
        if isinstance(repositories, list):
            for repository in repositories:
                if not isinstance(repository, dict):
                    continue
                raw_path = repository.get("path")
                if isinstance(raw_path, str) and raw_path.strip():
                    candidate = (root / raw_path).resolve()
                    try:
                        relative = candidate.relative_to(root).as_posix()
                    except ValueError:
                        relative = ""
                    if relative:
                        release_units[relative] = {
                            "path": relative,
                            "repository_id": str(repository.get("repository_id", "")),
                            "source": source.relative_to(root).as_posix(),
                            "status": "declared",
                        }
                for key in DECLARED_ACTIVE_PATH_KEYS:
                    add_path(active_paths, repository.get(key), source, key)
        legacy = payload.get("legacy_authority")
        if isinstance(legacy, dict):
            for key in DECLARED_RETIRED_PATH_KEYS:
                add_path(retired_paths, legacy.get(key), source, key)

    return {
        "release_units": sorted(release_units.values(), key=lambda item: item["path"]),
        "active_paths": sorted(active_paths.values(), key=lambda item: item["path"]),
        "retired_paths": sorted(retired_paths.values(), key=lambda item: item["path"]),
    }


def compact(items: list[Any]) -> dict[str, Any]:
    if items and isinstance(items[0], dict):
        by_release_unit: dict[str, int] = defaultdict(int)
        for item in items:
            by_release_unit[item["release_unit"]] += 1
        return {
            "count": len(items),
            "by_release_unit": dict(sorted(by_release_unit.items())),
            "examples": [item["path"] for item in items[:SUMMARY_EXAMPLE_LIMIT]],
        }
    return {"count": len(items), "examples": items[:SUMMARY_EXAMPLE_LIMIT]}


def extract_registered_worktrees(root: Path, registry_paths: list[tuple[Path, str]]) -> list[dict[str, Any]]:
    references: dict[tuple[str, str], dict[str, Any]] = {}
    for source, registry_role in registry_paths:
        try:
            text = source.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for token in TOKEN_SPLIT_PATTERN.split(text):
            normalized = token.rstrip(".。!！?？)】]}>")
            if ".worktrees/" not in normalized.replace("\\", "/"):
                continue
            candidate = Path(normalized).expanduser()
            resolved = candidate.resolve() if candidate.is_absolute() else (root / candidate).resolve()
            try:
                relative = resolved.relative_to(root).as_posix()
            except ValueError:
                continue
            source_relative = source.relative_to(root).as_posix()
            references[(source_relative, relative)] = {
                "path": relative,
                "source": source_relative,
                "registry_role": registry_role,
                "status": "authority_reference_not_scanned",
                "exists": resolved.exists(),
                "git_marker": git_marker_kind(resolved),
            }
    priority = {"current_baseline": 0, "release_unit_registry": 1, "worktree_registry": 2}
    return sorted(
        references.values(),
        key=lambda item: (priority.get(item["registry_role"], 9), item["source"], item["path"]),
    )


def compact_registered_worktrees(items: list[dict[str, Any]]) -> dict[str, Any]:
    by_registry_role: dict[str, int] = defaultdict(int)
    for item in items:
        by_registry_role[item["registry_role"]] += 1
    return {
        "count": len(items),
        "by_registry_role": dict(sorted(by_registry_role.items())),
        "examples": items[:SUMMARY_EXAMPLE_LIMIT],
    }


def assess_capability_signals(paths: list[Path], root: Path) -> dict[str, Any]:
    """Return bounded architecture/release signals without promoting them to facts."""

    signals: dict[str, list[str]] = defaultdict(list)
    for path in paths:
        relative = path.relative_to(root).as_posix()
        for capability, names in CAPABILITY_MARKERS.items():
            if path.name in names:
                signals[capability].append(relative)
        for capability, suffixes in CAPABILITY_SUFFIXES.items():
            if any(relative.endswith(suffix) for suffix in suffixes):
                signals[capability].append(relative)

    return {
        "status": "candidate_signals_require_contract_confirmation",
        "signals": {
            key: {"count": len(set(values)), "examples": sorted(set(values))[:SUMMARY_EXAMPLE_LIMIT]}
            for key, values in sorted(signals.items())
        },
        "decision_rule": (
            "依需求、技术架构、真实安装/部署/交付消费者确认发布渠道和制品；"
            "文件标记只触发复核，不自动创建制品目录。"
        ),
    }


def assess(root: Path, max_depth: int, verbose: bool) -> dict[str, Any]:
    excluded: dict[str, list[str]] = defaultdict(list)
    scanned_files: list[Path] = []
    release_roots: set[Path] = {root}

    for current, dirnames, filenames in os.walk(root):
        current_path = Path(current)
        depth = len(current_path.relative_to(root).parts)
        marker_kind = git_marker_kind(current_path)
        if current_path != root and marker_kind == "linked_worktree":
            excluded["linked_worktree"].append(current_path.relative_to(root).as_posix() + "/")
            dirnames[:] = []
            continue
        if marker_kind in {"repository", "git_file_repository_candidate"}:
            release_roots.add(current_path)

        kept_dirs = []
        for dirname in dirnames:
            if dirname == ".git":
                continue
            relative = (current_path / dirname).relative_to(root).as_posix() + "/"
            reason = exclusion_reason(dirname)
            if reason:
                excluded[reason].append(relative)
            elif depth < max_depth:
                kept_dirs.append(dirname)
        dirnames[:] = kept_dirs

        for filename in filenames:
            path = current_path / filename
            relative = path.relative_to(root).as_posix()
            reason = exclusion_reason(filename)
            if reason:
                excluded[reason].append(relative)
            else:
                scanned_files.append(path)

    ordered_release_roots = sorted(release_roots, key=lambda item: (len(item.parts), item.as_posix()))
    release_units = []
    authority_entrypoints = []
    declared_maps = []
    policy_files = []
    authority_registries: dict[str, list[str]] = defaultdict(list)

    for unit_root in ordered_release_roots:
        unit_name = "." if unit_root == root else unit_root.relative_to(root).as_posix()
        marker_kind = git_marker_kind(unit_root)
        entrypoints = [
            path.relative_to(root).as_posix()
            for path in (unit_root / "AGENTS.md", unit_root / "README.md")
            if path.is_file()
        ]
        quality = [
            (unit_root / name).relative_to(root).as_posix()
            for name in sorted(QUALITY_NAMES)
            if (unit_root / name).is_file()
        ]
        release_units.append({
            "path": unit_name,
            "status": "candidate",
            "detection": (
                "assessment_root_linked_worktree"
                if unit_root == root and marker_kind == "linked_worktree"
                else "assessment_root"
                if unit_root == root and marker_kind is None
                else "git_repository_root_candidate"
                if marker_kind == "repository"
                else "git_file_repository_candidate"
            ),
            "entrypoints": entrypoints,
            "quality_entrypoints": quality,
        })
        authority_entrypoints.extend(entrypoints)
    for path in scanned_files:
        relative = path.relative_to(root).as_posix()
        if path.name in MAP_NAMES:
            declared_maps.append(relative)
        if path.name in AUTHORITY_REGISTRY_NAMES:
            authority_registries[AUTHORITY_REGISTRY_NAMES[path.name]].append(relative)
        if relative.endswith(".senmu-buildos/config.json"):
            policy_files.append(relative)

    registry_source_paths = [
        (root / relative, role)
        for role, paths in authority_registries.items()
        for relative in paths
    ]
    registered_worktrees = extract_registered_worktrees(root, registry_source_paths)

    candidates: dict[str, list[dict[str, str]]] = defaultdict(list)
    map_paths = [path for path in scanned_files if path.name in MAP_NAMES]
    declared_authority = declared_authority_from_maps(root, map_paths)
    declared_release_unit_paths = {item["path"] for item in declared_authority["release_units"]}
    declared_active_paths = {item["path"] for item in declared_authority["active_paths"]}
    declared_retired_paths = {item["path"] for item in declared_authority["retired_paths"]}
    for release_unit in release_units:
        if release_unit["path"] in declared_release_unit_paths:
            release_unit["status"] = "declared"
            release_unit["detection"] = "declared_map_and_git_repository"

    for path in scanned_files:
        relative = path.relative_to(root).as_posix()
        unit = release_unit_for(path, root, ordered_release_roots)
        if relative in declared_retired_paths:
            excluded["archive_or_retired"].append(relative)
            continue
        if relative in declared_active_paths:
            continue
        for role, reason in candidate_roles(path.name, relative):
            candidates[role].append({
                "path": relative,
                "release_unit": unit,
                "status": "candidate",
                "reason": reason,
            })

    for role in candidates:
        candidates[role] = sorted(candidates[role], key=lambda item: (item["release_unit"], item["path"]))
    for reason in excluded:
        excluded[reason] = sorted(set(excluded[reason]))

    gaps = ["候选文件名不能单独证明语义 owner；必须读取权威入口并确认当前、历史和运行事实边界。"]
    if not authority_entrypoints:
        gaps.append("评估根及已识别发布单元没有根级 README.md 或 AGENTS.md。")
    if not declared_maps and not policy_files and not authority_registries:
        gaps.append("未发现项目地图、治理 policy 或可识别的权威登记入口；发布单元和 owner 关系需要语义确认。")
    if not candidates.get("durable_task_state"):
        gaps.append("未发现 Durable Task State Owner 候选。")
    if not candidates.get("production_truth"):
        gaps.append("未发现发布授权、回执或生产事实 owner 候选；若项目不发布，应明确标为不适用。")

    conflicts = []
    if len(declared_maps) > 1:
        gaps.append("发现多个地图类证据；它们可能互补而非冲突，需读取正文确认导航、登记和迁移报告的权威关系。")

    migration_risks = []
    if len(release_units) > 1:
        migration_risks.append("存在多个 Git 仓库候选；必须对照发布单元登记确认真实交付边界，不能按目录数量推断或在顶层铺设统一副本。")
    if any(excluded.values()):
        migration_risks.append("发现缓存、备份、归档或退役位置；不得把其中证据提升为当前 owner。")
    if registered_worktrees:
        migration_risks.append("权威登记引用了 linked worktree；它们不是新发布单元，只能在语义确认当前基线后作为实施入口读取。")
    if len(candidates.get("durable_task_state", [])) > 1:
        migration_risks.append("存在多个任务状态候选；需区分任务集合、单个任务实例、运行状态和历史记录。")
    if len(candidates.get("run_state", [])) > 1:
        migration_risks.append("存在多个数据库或运行清单候选；需确认当前库、投影、备份库和各发布单元 owner。")

    agent_entrypoints = sorted({path for path in authority_entrypoints if path.endswith("AGENTS.md")})
    if agent_entrypoints:
        migration_risks.append(
            "现有 AGENTS.md 必须先做语义去重：保留项目事实、真实命令、权威路径和明确覆盖；"
            "把已有专业正文压缩为路由；删除与 BuildOS 相同的通用方法；冲突或时效不明项交用户裁决。"
        )

    result: dict[str, Any] = {
        "mode": "assess-existing",
        "assessment_status": "inventory_complete_semantic_confirmation_required",
        "project_root_runtime": str(root),
        "write_operations": [],
        "authority_evidence": {
            "project_entrypoints": sorted(set(authority_entrypoints)),
            "declared_maps": sorted(set(declared_maps)),
            "governance_policies": sorted(set(policy_files)),
            "authority_registries": {
                role: sorted(set(paths)) for role, paths in sorted(authority_registries.items())
            },
            "registered_worktree_references": compact_registered_worktrees(registered_worktrees),
            "release_units": release_units,
            "declared_state_owners": declared_authority["active_paths"],
            "declared_retired_evidence": declared_authority["retired_paths"],
        },
        "candidate_mappings": {role: compact(items) for role, items in sorted(candidates.items())},
        "capability_assessment": assess_capability_signals(scanned_files, root),
        "instruction_layering_review": {
            "status": "semantic_review_required" if agent_entrypoints else "no_agents_entrypoint_found",
            "entrypoints": agent_entrypoints,
            "baseline": "senmu-buildos_if_adopted",
            "required_actions": [
                "retain_project_fact_command_path_or_explicit_override",
                "compress_project_specific_body_to_canonical_owner_route",
                "remove_buildos_duplicate",
                "replace_unconditional_cross_domain_preload_with_signal_routing",
                "remove_generic_skill_catalog_from_project_delta",
                "escalate_conflict_or_staleness_for_user_decision",
            ],
            "write_default_agents_template": False,
            "runtime_validation": {
                "status": "required_before_routing_claim",
                "maximum_unverified_claim": "structural_routing_prepared",
                "scenarios": [
                    "low_risk_single_unit_task_avoids_global_governance_preload",
                    "domain_boundary_task_loads_only_matching_contracts",
                    "release_or_rollback_task_loads_baseline_authorization_and_recovery",
                ],
            },
        },
        "excluded_evidence": {reason: compact(items) for reason, items in sorted(excluded.items())},
        "conflicts": conflicts,
        "gaps": gaps,
        "migration_risks": migration_risks,
        "next_step": "按权威入口逐发布单元确认语义 owner；未经授权不得生成默认目录或改写现有项目。",
    }
    if verbose:
        result["full_candidate_inventory"] = dict(sorted(candidates.items()))
        result["full_excluded_inventory"] = dict(sorted(excluded.items()))
        result["full_registered_worktree_references"] = registered_worktrees
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--max-depth", type=int, default=6)
    parser.add_argument("--verbose", action="store_true", help="输出完整候选和排除清单；默认只输出有界摘要")
    args = parser.parse_args()

    root = args.root.expanduser().resolve()
    if not root.is_dir():
        raise SystemExit(f"[ERROR] 项目目录不存在：{root}")
    print(json.dumps(assess(root, args.max_depth, args.verbose), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
