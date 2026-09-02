#!/usr/bin/env python3
"""Validate a project-local governance scaffold without third-party dependencies."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any
from urllib.parse import unquote

POLICY_REL = Path(".senmu-buildos/config.json")
REQUIRED_POLICY_KEYS = {
    "schema_version",
    "project_name",
    "project_type",
    "layout",
    "profile",
    "selected_modules",
    "initialization_status",
    "required_paths",
    "worklog_path",
    "lessons_path",
    "lessons_validation",
    "validator",
}
VALID_PROJECT_TYPES = {"software", "script", "workflow", "media", "poc", "mixed"}
VALID_MODULES = {"product", "code", "architecture", "git", "workflow", "delivery", "poc", "agents"}
VALID_TASK_STATUSES = {"planned", "active", "blocked", "verifying", "completed", "cancelled", "archived"}
VALID_AGENT_STATUSES = {"draft", "active", "deprecated", "retired"}
VALID_LIFECYCLE_INTENTS = {"exploration", "pilot", "production", "migration", "one_off"}
VALID_DELIVERY_MODELS = {"continuous_product", "source_distribution", "versioned_artifact", "managed_service", "project_delivery", "internal_process"}
VALID_COMPOSITIONS = {"single_domain", "composite"}
VALID_PUBLICATION_MODELS = {"private_only", "public_native", "private_authority_public_projection"}
VALID_RELEASE_CHANNELS = {
    "public_source_repository", "marketplace_install", "source_archive", "package_registry",
    "container_image", "desktop_bundle", "mobile_bundle", "managed_service", "project_delivery",
}
VALID_ARTIFACT_KINDS = {
    "signed_source_archive", "package", "container_image", "dmg", "pkg", "msi",
    "mobile_bundle", "binary", "wheel", "jar",
}
VALID_ROOT_LOCATOR_KINDS = {"git_toplevel", "governance_policy_root"}
VALID_LAYOUTS = {"software-repository", "project-system", "publication-workspace"}
VALID_MAIN_MODES = {"integration", "release_ready"}
CHANGE_UNIT_STATES = {"in_progress", "sealed", "integrated", "excluded", "superseded"}
TASK_FILE = re.compile(r"^TASK-\d{4}-[a-z0-9]+(?:-[a-z0-9]+)*\.md$")
# Angle-bracket format tokens such as TASK-<NNNN>, v<version>, or
# agents/{agent-key} are executable documentation, not uncalibrated instance
# fields. Strict validation only rejects human-facing Chinese placeholders.
PLACEHOLDER = re.compile(r"<待确认(?:或不适用)?>|<[^>\n]*[\u4e00-\u9fff][^>\n]*>")
PROJECT_MAP_REQUIRED_HEADINGS = ("## 责任与入口地图", "## 项目规范索引")
ABSOLUTE_PRIVATE_PATH = re.compile(
    r"(?:/Users/[A-Za-z0-9._-]+/|/home/[A-Za-z0-9._-]+/|[A-Za-z]:\\Users\\[A-Za-z0-9._-]+\\)"
)


def issue(code: str, message: str, path: str, severity: str) -> dict[str, str]:
    return {"code": code, "path": path, "message": message, "severity": severity}


def strip_fenced_code_blocks(text: str) -> str:
    visible: list[str] = []
    fence_character: str | None = None
    fence_length = 0
    for line in text.splitlines():
        match = re.match(r"^\s*(`{3,}|~{3,})", line)
        if match:
            marker = match.group(1)
            if fence_character is None:
                fence_character = marker[0]
                fence_length = len(marker)
                visible.append("")
                continue
            if marker[0] == fence_character and len(marker) >= fence_length:
                fence_character = None
                fence_length = 0
                visible.append("")
                continue
        visible.append(line if fence_character is None else "")
    return "\n".join(visible)


def find_matching_delimiter(
    text: str, start: int, opening: str, closing: str
) -> int | None:
    depth = 0
    index = start
    while index < len(text):
        character = text[index]
        if character == "\\":
            index += 2
            continue
        if character == opening:
            depth += 1
        elif character == closing:
            depth -= 1
            if depth == 0:
                return index
        index += 1
    return None


def parse_link_destination(content: str) -> str | None:
    content = content.strip()
    if not content:
        return None
    if content.startswith("<"):
        closing = content.find(">", 1)
        return content[1:closing].strip() if closing >= 0 else None
    escaped = False
    characters: list[str] = []
    for character in content:
        if escaped:
            characters.append(character)
            escaped = False
        elif character == "\\":
            escaped = True
        elif character.isspace():
            break
        else:
            characters.append(character)
    return "".join(characters).strip() or None


def extract_markdown_link_targets(text: str) -> list[str]:
    visible = strip_fenced_code_blocks(text)
    targets: list[str] = []
    index = 0
    while index < len(visible):
        opening = visible.find("[", index)
        if opening < 0:
            break
        closing = find_matching_delimiter(visible, opening, "[", "]")
        if closing is None:
            break
        cursor = closing + 1
        while cursor < len(visible) and visible[cursor] in " \t":
            cursor += 1
        if cursor >= len(visible) or visible[cursor] != "(":
            index = closing + 1
            continue
        destination_end = find_matching_delimiter(visible, cursor, "(", ")")
        if destination_end is None:
            index = cursor + 1
            continue
        target = parse_link_destination(visible[cursor + 1 : destination_end])
        if target is not None:
            targets.append(target)
        index = destination_end + 1
    return targets


def markdown_section(text: str, heading: str) -> str:
    lines = text.splitlines()
    start: int | None = None
    level = len(heading) - len(heading.lstrip("#"))
    for index, line in enumerate(lines):
        if line.strip() == heading:
            start = index + 1
            break
    if start is None:
        return ""
    end = len(lines)
    for index in range(start, len(lines)):
        match = re.match(r"^(#{1,6})\s+", lines[index])
        if match and len(match.group(1)) <= level:
            end = index
            break
    return "\n".join(lines[start:end])


def table_rows(section: str) -> list[list[str]]:
    rows: list[list[str]] = []
    for line in section.splitlines():
        if not line.strip().startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if cells and all(re.fullmatch(r":?-{3,}:?", cell) for cell in cells):
            continue
        rows.append(cells)
    return rows[1:] if rows else []


def is_external_or_anchor(target: str) -> bool:
    return bool(
        not target
        or target.startswith(("#", "//"))
        or re.match(r"^[A-Za-z][A-Za-z0-9+.-]*:", target)
    )


def resolve_governed_target(
    root: Path, base: Path, raw_target: str
) -> tuple[Path | None, str | None]:
    target = raw_target.strip()
    if is_external_or_anchor(target):
        return None, None
    path_part = unquote(target.split("#", 1)[0].split("?", 1)[0]).strip()
    if not path_part or "{" in path_part or "<" in path_part:
        return None, None
    resolved = (base / path_part).resolve()
    try:
        resolved.relative_to(root)
    except ValueError:
        return resolved, "outside"
    if not resolved.exists():
        return resolved, "missing"
    return resolved, None


def validate_project_map_index(
    root: Path,
    project_map_path: Path,
    text: str,
    errors: list[str],
    warnings: list[dict[str, str]],
    stats: dict[str, int],
) -> None:
    relative_map = project_map_path.relative_to(root).as_posix()
    section = markdown_section(text, "## 项目规范索引")
    rows = table_rows(section)
    stats["standards_rows"] = len(rows)
    seen_rows: set[tuple[str, ...]] = set()
    index_problems: set[tuple[str, str]] = set()
    for row_number, cells in enumerate(rows, start=1):
        if len(cells) < 5 or PLACEHOLDER.search(" | ".join(cells)):
            continue
        normalized = tuple(re.sub(r"\s+", " ", cell).strip() for cell in cells)
        if normalized in seen_rows:
            warnings.append(
                issue(
                    "project_map.duplicate_index_row",
                    f"项目规范索引第 {row_number} 个数据行与前文完全重复；保留一个即可",
                    relative_map,
                    "warning",
                )
            )
        seen_rows.add(normalized)
        status = cells[4]
        if (
            re.search(
                r"(?:^|[\s/；;,])active(?:$|[\s/；;,])",
                status,
                re.IGNORECASE,
            )
            is None
        ):
            continue
        stats["active_standards_rows"] += 1
        target_cell = cells[3]
        link_targets = extract_markdown_link_targets(target_cell)
        code_targets = re.findall(r"`([^`]+)`", target_cell)
        governed_targets: list[tuple[Path, str]] = []
        for target in link_targets:
            governed_targets.append((project_map_path.parent, target))
        for target in code_targets:
            governed_targets.append((root, target))
        checked = 0
        for base, target in governed_targets:
            resolved, problem = resolve_governed_target(root, base, target)
            if resolved is None:
                continue
            checked += 1
            stats["active_index_targets_checked"] += 1
            if problem == "outside":
                errors.append(f"Project Map 项目规范索引路径越出项目根：{target}")
                index_problems.add((str(resolved), problem))
            elif problem == "missing":
                errors.append(f"Project Map 项目规范索引路径不存在：{target}")
                index_problems.add((str(resolved), problem))
        if checked == 0:
            warnings.append(
                issue(
                    "project_map.active_index_unverifiable",
                    f"项目规范索引第 {row_number} 个 active 数据行没有可校验的项目内路径",
                    relative_map,
                    "warning",
                )
            )

    for target in extract_markdown_link_targets(text):
        resolved, problem = resolve_governed_target(
            root, project_map_path.parent, target
        )
        if resolved is not None:
            stats["project_map_links_checked"] += 1
        if problem is None or (str(resolved), problem) in index_problems:
            continue
        if problem == "outside":
            errors.append(f"Project Map 本地链接越出项目根：{target}")
        elif problem == "missing":
            errors.append(f"Project Map 本地链接不存在：{target}")


def canonical_git_root(root: Path) -> Path:
    """Return the main worktree root when root belongs to Git, otherwise root."""

    probe = subprocess.run(
        ["git", "-C", str(root), "rev-parse", "--show-toplevel"],
        check=False,
        capture_output=True,
        text=True,
    )
    if probe.returncode != 0:
        return root.resolve()
    checkout = Path(probe.stdout.strip()).resolve()
    common = subprocess.run(
        ["git", "-C", str(root), "rev-parse", "--path-format=absolute", "--git-common-dir"],
        check=False,
        capture_output=True,
        text=True,
    )
    if common.returncode != 0:
        return checkout
    common_dir = Path(common.stdout.strip()).resolve()
    return common_dir.parent if common_dir.name == ".git" else checkout


def validate(
    root: Path,
    strict: bool,
    warnings: list[dict[str, str]] | None = None,
    stats: dict[str, int] | None = None,
) -> list[str]:
    errors: list[str] = []
    warnings = warnings if warnings is not None else []
    stats = stats if stats is not None else {
        "standards_rows": 0,
        "active_standards_rows": 0,
        "active_index_targets_checked": 0,
        "project_map_links_checked": 0,
    }
    root = root.resolve()
    policy_path = root / POLICY_REL
    if not policy_path.is_file():
        return [f"缺少治理 policy：{policy_path}"]

    try:
        policy = json.loads(policy_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"治理 policy 无法解析：{exc}"]

    missing_keys = sorted(REQUIRED_POLICY_KEYS - set(policy))
    if missing_keys:
        errors.append(f"治理 policy 缺少字段：{', '.join(missing_keys)}")

    schema_version = str(policy.get("schema_version", "0"))
    if schema_version != "3.0.0":
        errors.append("BuildOS v2 只接受 schema_version 3.0.0；请重新评估并生成当前治理实例")

    classification = policy.get("classification")
    if not isinstance(classification, dict):
        errors.append("schema 3.0.0 必须包含 classification 对象")
    else:
        for key, allowed in (
            ("lifecycle_intent", VALID_LIFECYCLE_INTENTS),
            ("delivery_model", VALID_DELIVERY_MODELS),
            ("composition", VALID_COMPOSITIONS),
        ):
            if classification.get(key) not in allowed:
                errors.append(f"classification.{key} 无效：{classification.get(key)}")

    project_type = policy.get("project_type")
    if project_type not in VALID_PROJECT_TYPES:
        errors.append(f"project_type 无效：{project_type}")

    layout = policy.get("layout")
    if layout not in VALID_LAYOUTS:
        errors.append(f"layout 无效：{layout}")

    publication = policy.get("publication")
    if not isinstance(publication, dict):
        errors.append("schema 3.0.0 必须包含 publication 对象")
    else:
        publication_model = publication.get("model")
        if publication_model not in VALID_PUBLICATION_MODELS:
            errors.append(f"publication.model 无效：{publication_model}")
        if publication_model == "private_authority_public_projection":
            if layout != "publication-workspace":
                errors.append("私有权威到公开投影模型必须使用 publication-workspace")
            for key in ("public_projection_root", "release_staging_root"):
                if not publication.get(key):
                    errors.append(f"publication.{key} 不能为空")
            if publication.get("projection_mode") != "generated_only":
                errors.append("公开投影必须声明 projection_mode=generated_only")
        elif any(publication.get(key) is not None for key in ("public_projection_root", "release_staging_root", "projection_mode")):
            errors.append("非投影公开模型不得声明公开投影路径或生成模式")

    release_channels = policy.get("release_channels")
    if not isinstance(release_channels, list):
        errors.append("release_channels 必须是数组")
        release_channels = []
    unknown_channels = sorted(set(release_channels) - VALID_RELEASE_CHANNELS)
    if unknown_channels:
        errors.append(f"release_channels 包含未知值：{', '.join(unknown_channels)}")

    artifact_kinds = policy.get("artifact_kinds")
    if not isinstance(artifact_kinds, list):
        errors.append("artifact_kinds 必须是数组")
        artifact_kinds = []
    unknown_artifacts = sorted(set(artifact_kinds) - VALID_ARTIFACT_KINDS)
    if unknown_artifacts:
        errors.append(f"artifact_kinds 包含未知值：{', '.join(unknown_artifacts)}")

    path_roles = policy.get("path_roles")
    if not isinstance(path_roles, dict):
        errors.append("schema 3.0.0 必须包含 path_roles 对象")
    else:
        for role, raw in path_roles.items():
            if raw is None:
                continue
            role_path = Path(str(raw))
            if role_path.is_absolute() or ".." in role_path.parts:
                errors.append(f"path_roles.{role} 必须是工作区内相对路径：{raw}")

    if policy.get("workspace_root") not in {".", ".."}:
        errors.append("workspace_root 只能保存相对定位 . 或 ..")

    selected_modules = policy.get("selected_modules", [])
    if not isinstance(selected_modules, list) or not selected_modules:
        errors.append("selected_modules 必须是非空数组")
        selected_modules = []
    unknown_modules = sorted(set(selected_modules) - VALID_MODULES)
    if unknown_modules:
        errors.append(f"selected_modules 包含未知模块：{', '.join(unknown_modules)}")

    git_management = policy.get("git_management")
    if "git" in selected_modules:
        if not isinstance(git_management, dict):
            errors.append("启用 git 模块时 git_management 必须是对象")
        else:
            if git_management.get("main_mode") not in VALID_MAIN_MODES:
                errors.append("git_management.main_mode 必须为 integration 或 release_ready")
            if git_management.get("direct_main_writes") is not False:
                errors.append("git_management.direct_main_writes 必须为 false")
            worktree_root = Path(str(git_management.get("worktree_root", "")))
            if worktree_root.is_absolute() or ".." in worktree_root.parts or not worktree_root.parts:
                errors.append("git_management.worktree_root 必须是项目受管相对路径")
            if set(git_management.get("change_unit_states") or []) != CHANGE_UNIT_STATES:
                errors.append("git_management.change_unit_states 必须使用统一 Change Unit 状态集合")
    elif git_management is not None:
        errors.append("未启用 git 模块时 git_management 必须为 null")

    release_policy = policy.get("release_policy")
    if "delivery" in selected_modules:
        if not isinstance(release_policy, dict):
            errors.append("启用 delivery 模块时 release_policy 必须是对象")
        else:
            if release_policy.get("official_tag_semantics") != "verified_release":
                errors.append("release_policy.official_tag_semantics 必须为 verified_release")
            if release_policy.get("candidate_identity") != "commit_and_artifact":
                errors.append("release_policy.candidate_identity 必须为 commit_and_artifact")
            if release_policy.get("authorization_mode") != "bounded_release_session":
                errors.append("release_policy.authorization_mode 必须为 bounded_release_session")
    elif release_policy is not None:
        errors.append("未启用 delivery 模块时 release_policy 必须为 null")

    root_locator = policy.get("root_locator")
    if not isinstance(root_locator, dict):
        errors.append("schema 3.0.0 必须包含 root_locator 对象")
    else:
        if root_locator.get("kind") not in VALID_ROOT_LOCATOR_KINDS:
            errors.append(f"root_locator.kind 无效：{root_locator.get('kind')}")
        if root_locator.get("relative_path") != ".":
            errors.append("root_locator.relative_path 必须为项目内相对路径 .")
        if root_locator.get("kind") == "git_toplevel" and canonical_git_root(root) != root:
            errors.append("root_locator.kind=git_toplevel 但当前根不是权威 Git 根")

    canonical = canonical_git_root(root)
    if canonical != root:
        errors.append(f"当前路径是外部 worktree；必须从权威项目根校验：{canonical}")

    required_paths = policy.get("required_paths", [])
    if not isinstance(required_paths, list) or not required_paths:
        errors.append("required_paths 必须是非空数组")
        required_paths = []
    for raw in required_paths:
        target = (root / str(raw)).resolve()
        try:
            target.relative_to(root)
        except ValueError:
            errors.append(f"required_paths 越出项目根：{raw}")
            continue
        if not target.is_file():
            errors.append(f"缺少治理文件：{raw}")

    placeholder_scan_paths = policy.get("placeholder_scan_paths", required_paths)
    if not isinstance(placeholder_scan_paths, list):
        errors.append("placeholder_scan_paths 必须是数组")
        placeholder_scan_paths = []
    for raw in placeholder_scan_paths:
        target = (root / str(raw)).resolve()
        try:
            target.relative_to(root)
        except ValueError:
            errors.append(f"placeholder_scan_paths 越出项目根：{raw}")
            continue
        if not target.is_file():
            errors.append(f"placeholder_scan_paths 文件不存在：{raw}")

    for key in ("worklog_path", "lessons_path"):
        raw = policy.get(key)
        if raw and not (root / str(raw)).is_file():
            errors.append(f"{key} 不存在：{raw}")

    lessons_validation = policy.get("lessons_validation")
    if lessons_validation is not None:
        if not isinstance(lessons_validation, dict):
            errors.append("lessons_validation 必须是对象")
        else:
            script_raw = lessons_validation.get("script_path")
            lessons_raw = policy.get("lessons_path")
            expected_command = f"python3 {script_raw} {lessons_raw}"
            if lessons_validation.get("command") != expected_command:
                errors.append("lessons_validation.command 与声明路径不一致")
            script_path = (root / str(script_raw or "")).resolve()
            lessons_path = (root / str(lessons_raw or "")).resolve()
            try:
                script_path.relative_to(root)
                lessons_path.relative_to(root)
            except ValueError:
                errors.append("lessons_validation 路径越出项目根")
            else:
                if not script_path.is_file():
                    errors.append(f"经验校验器不存在：{script_raw}")
                elif lessons_path.is_file():
                    result = subprocess.run(
                        [sys.executable, str(script_path), str(lessons_path)],
                        check=False,
                        capture_output=True,
                        text=True,
                    )
                    if result.returncode != 0:
                        detail = (result.stdout or result.stderr).strip().replace("\n", "; ")
                        errors.append(f"经验台账校验失败：{detail}")
                    elif "[WARNING]" in result.stdout:
                        for line in result.stdout.splitlines():
                            if line.startswith("[WARNING]"):
                                print(f"[LESSONS] {line}")

    task_management = policy.get("task_management")
    requires_task_management = policy.get("profile") in {"standard", "release"}
    if requires_task_management and not isinstance(task_management, dict):
        errors.append("task_management 必须是对象")
    elif isinstance(task_management, dict):
        if task_management.get("owner_kind") != "senmu_markdown":
            errors.append("默认生成实例的 task_management.owner_kind 必须为 senmu_markdown")
        task_paths: dict[str, Path | None] = {}
        for key in ("task_directory", "register_path", "template_path"):
            target = (root / str(task_management.get(key, ""))).resolve()
            try:
                target.relative_to(root)
            except ValueError:
                errors.append(f"task_management.{key} 越出项目根")
                task_paths[key] = None
            else:
                task_paths[key] = target
        task_directory = task_paths["task_directory"]
        register_path = task_paths["register_path"]
        template_path = task_paths["template_path"]
        statuses = task_management.get("statuses")
        if task_directory is not None and not task_directory.is_dir():
            errors.append("task_management.task_directory 不存在")
        if register_path is not None and not register_path.is_file():
            errors.append("task_management.register_path 不存在")
        if template_path is not None and not template_path.is_file():
            errors.append("task_management.template_path 不存在")
        if set(statuses or []) != VALID_TASK_STATUSES:
            errors.append("task_management.statuses 必须使用统一任务状态集合")
        if task_management.get("task_file_format") != "TASK-NNNN-slug.md":
            errors.append("task_management.task_file_format 必须为 TASK-NNNN-slug.md")
        if task_directory is not None and task_directory.is_dir():
            for candidate in task_directory.iterdir():
                if candidate.name == "TASK_REGISTER.md":
                    continue
                if candidate.name.startswith("."):
                    continue
                if candidate.is_dir():
                    errors.append(f"任务计划不得使用独立目录：{candidate.relative_to(root)}")
                elif not TASK_FILE.fullmatch(candidate.name):
                    errors.append(f"任务目录包含非标准文件：{candidate.relative_to(root)}")

    if layout == "project-system":
        external_directories = policy.get("external_directories")
        if not isinstance(external_directories, dict):
            errors.append("project-system 布局必须声明 external_directories")
        else:
            for role in ("sources", "workspace", "deliveries", "archive"):
                raw = external_directories.get(role)
                if not raw or not (root / str(raw)).resolve().is_dir():
                    errors.append(f"external_directories.{role} 不存在：{raw}")

    project_map_path = policy.get("project_map_path")
    if policy.get("profile") in {"standard", "release"}:
        if not project_map_path or not (root / str(project_map_path)).is_file():
            errors.append("standard/release 档位必须提供有效 project_map_path")
        else:
            resolved_project_map_path = root / str(project_map_path)
            project_map_text = resolved_project_map_path.read_text(encoding="utf-8")
            for heading in PROJECT_MAP_REQUIRED_HEADINGS:
                if heading not in project_map_text:
                    errors.append(f"Project Map 缺少必要索引区：{heading}")
            if all(heading in project_map_text for heading in PROJECT_MAP_REQUIRED_HEADINGS):
                validate_project_map_index(
                    root,
                    resolved_project_map_path,
                    project_map_text,
                    errors,
                    warnings,
                    stats,
                )
    elif project_map_path is not None:
        errors.append("core 档位的 project_map_path 必须为 null")

    product_management = policy.get("product_management")
    if "product" in selected_modules and policy.get("profile") in {"standard", "release"}:
        if not isinstance(product_management, dict):
            errors.append("启用 product 模块时 product_management 必须是对象")
        else:
            for key in ("user_requirements_path", "product_specification_path"):
                raw = product_management.get(key)
                if not raw or not (root / str(raw)).is_file():
                    errors.append(f"product_management.{key} 不存在")
            expected_patterns = {
                "version_directory_pattern": "versions/{version}",
                "prd_path_pattern": "versions/{version}/PRD.md",
                "technical_design_path_pattern": "versions/{version}/TECHNICAL_DESIGN.md",
                "test_cases_path_pattern": "versions/{version}/TEST_CASES.md",
            }
            for key, expected in expected_patterns.items():
                if product_management.get(key) != expected:
                    errors.append(f"product_management.{key} 必须为 {expected}")
            if product_management.get("adaptive_outline") is not True:
                errors.append("product_management.adaptive_outline 必须为 true")
    elif product_management is not None:
        errors.append("未启用 product 模块时 product_management 必须为 null")

    workflow_management = policy.get("workflow_management")
    if "workflow" in selected_modules and policy.get("profile") in {"standard", "release"}:
        if not isinstance(workflow_management, dict):
            errors.append("启用 workflow 模块时 workflow_management 必须是对象")
        elif not (root / str(workflow_management.get("contract_path", ""))).is_file():
            errors.append("workflow_management.contract_path 不存在")
    elif workflow_management is not None:
        errors.append("未启用 workflow 模块时 workflow_management 必须为 null")

    agent_management = policy.get("agent_management")
    if "agent_management" not in policy:
        errors.append("schema 3.0.0 必须声明 agent_management；未启用时设为 null")
    if "agents" in selected_modules:
        if not isinstance(agent_management, dict):
            errors.append("启用 agents 模块时 agent_management 必须是对象")
        else:
            if agent_management.get("owner_kind") != "senmu_markdown":
                errors.append("默认生成实例的 agent_management.owner_kind 必须为 senmu_markdown")
            agent_paths: dict[str, Path | None] = {}
            for key in ("directory", "register_path", "template_path", "validator_path"):
                target = (root / str(agent_management.get(key, ""))).resolve()
                try:
                    target.relative_to(root)
                except ValueError:
                    errors.append(f"agent_management.{key} 越出项目根")
                    agent_paths[key] = None
                else:
                    agent_paths[key] = target
            if agent_paths["directory"] is not None and not agent_paths["directory"].is_dir():
                errors.append("agent_management.directory 不存在")
            for key in ("register_path", "template_path", "validator_path"):
                target = agent_paths[key]
                if target is not None and not target.is_file():
                    errors.append(f"agent_management.{key} 不存在")
            if agent_management.get("definition_path_format") != "agents/{agent-key}/AGENT.md":
                errors.append("agent_management.definition_path_format 必须为 agents/{agent-key}/AGENT.md")
            if set(agent_management.get("statuses") or []) != VALID_AGENT_STATUSES:
                errors.append("agent_management.statuses 必须使用统一 Agent 状态集合")
            expected_agent_command = "python3 .senmu-buildos/validate_agents.py --root ."
            if agent_management.get("validation_command") != expected_agent_command:
                errors.append("agent_management.validation_command 与默认校验入口不一致")
            agent_validator = agent_paths.get("validator_path")
            if agent_validator is not None and agent_validator.is_file():
                command = [sys.executable, str(agent_validator), "--root", str(root)]
                if strict:
                    command.append("--strict")
                result = subprocess.run(command, check=False, capture_output=True, text=True)
                if result.returncode != 0:
                    detail = (result.stdout or result.stderr).strip().replace("\n", "; ")
                    errors.append(f"Agent 定义校验失败：{detail}")
    elif agent_management is not None:
        errors.append("未启用 agents 模块时 agent_management 必须为 null")

    release_retention = policy.get("release_retention")
    artifact_kinds = policy.get("artifact_kinds", [])
    requires_release_retention = bool(artifact_kinds)
    if requires_release_retention:
        if not isinstance(release_retention, dict):
            errors.append("已确认独立制品时必须声明 release_retention")
        else:
            for key in ("config_path", "cleanup_script", "contract_test"):
                raw = release_retention.get(key)
                if not raw or not (root / str(raw)).is_file():
                    errors.append(f"release_retention.{key} 不存在：{raw}")
            if release_retention.get("default_keep") != ["current", "previous"]:
                errors.append("release_retention.default_keep 必须为 current、previous")
    elif release_retention is not None:
        errors.append("没有独立制品时 release_retention 必须为 null")

    if strict:
        if policy.get("initialization_status") != "active":
            errors.append("严格校验要求 initialization_status=active")
        lessons_path = str(policy.get("lessons_path", ""))
        for raw in placeholder_scan_paths:
            target = root / str(raw)
            if (
                str(raw) == lessons_path
                or target.suffix.lower() != ".md"
                or ".template." in target.name
                or str(raw).startswith(".senmu-buildos/templates/")
                or not target.is_file()
            ):
                continue
            match = PLACEHOLDER.search(target.read_text(encoding="utf-8"))
            if match:
                errors.append(f"严格校验发现未校准占位符：{raw}: {match.group(0)}")
            text = target.read_text(encoding="utf-8")
            if ABSOLUTE_PRIVATE_PATH.search(text):
                errors.append(f"严格校验发现持久化的本机绝对路径：{raw}")
    return list(dict.fromkeys(errors))


def error_issue(message: str, policy: dict[str, Any] | None) -> dict[str, str]:
    code = "governance.structural_violation"
    path = "."
    if message.startswith("缺少治理 policy"):
        code, path = "policy.missing", POLICY_REL.as_posix()
    elif message.startswith("治理 policy") or message.startswith("schema 3.0.0"):
        code, path = "policy.invalid", POLICY_REL.as_posix()
    elif message.startswith("Project Map 缺少必要索引区"):
        code = "project_map.missing_section"
    elif message.startswith("Project Map 本地链接越出项目根"):
        code = "project_map.link_outside_root"
    elif message.startswith("Project Map 本地链接不存在"):
        code = "project_map.link_missing"
    elif message.startswith("Project Map 项目规范索引路径越出项目根"):
        code = "project_map.index_path_outside_root"
    elif message.startswith("Project Map 项目规范索引路径不存在"):
        code = "project_map.index_path_missing"
    elif "越出项目根" in message or "越出工作区" in message:
        code = "path.outside_root"
    elif "不存在" in message or message.startswith("缺少治理文件"):
        code = "path.missing"
    elif message.startswith("严格校验"):
        code = "strict.violation"
    if code.startswith("project_map.") and isinstance(policy, dict):
        path = str(policy.get("project_map_path") or ".")
    elif code.startswith(("policy.", "path.")):
        path = POLICY_REL.as_posix()
    return issue(code, message, path, "error")


def audit(root: Path, strict: bool) -> dict[str, Any]:
    resolved_root = root.resolve()
    warnings: list[dict[str, str]] = []
    stats = {
        "standards_rows": 0,
        "active_standards_rows": 0,
        "active_index_targets_checked": 0,
        "project_map_links_checked": 0,
    }
    errors = validate(resolved_root, strict, warnings, stats)
    policy: dict[str, Any] | None = None
    try:
        loaded = json.loads((resolved_root / POLICY_REL).read_text(encoding="utf-8"))
        if isinstance(loaded, dict):
            policy = loaded
    except (OSError, json.JSONDecodeError):
        pass
    unique_warnings = {
        (item["code"], item["path"], item["message"]): item for item in warnings
    }
    return {
        "schema_version": 1,
        "root": str(resolved_root),
        "mode": "strict" if strict else "structural",
        "errors": [error_issue(message, policy) for message in errors],
        "warnings": list(unique_warnings.values()),
        "stats": stats,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--strict", action="store_true", help="要求 policy 激活且治理文档无占位符")
    parser.add_argument("--json", action="store_true", help="输出稳定 JSON 回执")
    args = parser.parse_args()
    try:
        report = audit(args.root, args.strict)
    except Exception as exc:  # pragma: no cover - defensive CLI boundary
        if args.json:
            print(
                json.dumps(
                    {
                        "schema_version": 1,
                        "root": str(args.root.resolve()),
                        "mode": "strict" if args.strict else "structural",
                        "errors": [
                            issue(
                                "validator.internal_failure",
                                str(exc),
                                ".",
                                "error",
                            )
                        ],
                        "warnings": [],
                        "stats": {},
                    },
                    ensure_ascii=False,
                    indent=2,
                )
            )
        else:
            print(f"[ERROR] 校验器内部失败：{exc}")
        return 2
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        for item in report["errors"]:
            print(f"[ERROR] {item['message']}")
        for item in report["warnings"]:
            print(f"[WARNING] {item['message']}")
    if report["errors"]:
        return 1
    mode = "严格" if args.strict else "结构"
    if not args.json:
        print(
            f"[OK] 项目治理{mode}校验通过：{args.root.resolve()}"
            f"（{len(report['warnings'])} 条警告）"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
