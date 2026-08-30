#!/usr/bin/env python3
"""Validate a project-local governance scaffold without third-party dependencies."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path


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


def validate(root: Path, strict: bool) -> list[str]:
    errors: list[str] = []
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
            project_map_text = (root / str(project_map_path)).read_text(encoding="utf-8")
            for heading in PROJECT_MAP_REQUIRED_HEADINGS:
                if heading not in project_map_text:
                    errors.append(f"Project Map 缺少必要索引区：{heading}")
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
    return errors


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--strict", action="store_true", help="要求 policy 激活且治理文档无占位符")
    args = parser.parse_args()
    errors = validate(args.root, args.strict)
    if errors:
        for error in errors:
            print(f"[ERROR] {error}")
        raise SystemExit(1)
    mode = "严格" if args.strict else "结构"
    print(f"[OK] 项目治理{mode}校验通过：{args.root.resolve()}")


if __name__ == "__main__":
    main()
