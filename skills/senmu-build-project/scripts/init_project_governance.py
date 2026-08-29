#!/usr/bin/env python3
"""Create a non-destructive project-local governance scaffold."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
from datetime import date
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parent.parent
SKILLS_ROOT = SKILL_ROOT.parent
STARTER = SKILL_ROOT / "assets" / "project-governance-starter"
LESSONS_VALIDATOR_SOURCE = SKILLS_ROOT / "senmu-build-learning" / "scripts" / "validate_lessons.py"
AGENT_VALIDATOR_SOURCE = SKILLS_ROOT / "senmu-build-workflow" / "scripts" / "validate_agents.py"

BASE = {
    ".gitignore.template": ".gitignore",
    "README.template.md": "README.md",
    "AGENTS.template.md": "AGENTS.md",
    "GOVERNANCE.template.md": "governance/GOVERNANCE.md",
}
BASE_STANDARD = {
    "TASK_REGISTER.template.md": "governance/tasks/TASK_REGISTER.md",
    "TASK.template.md": ".senmu-buildos/templates/TASK.md",
    "WORKLOG.template.md": "governance/logs/WORKLOG.md",
    "../learning-governance/LESSONS_LEARNED.template.md": "governance/lessons/LESSONS_LEARNED.md",
    "PROJECT_MAP.template.md": "governance/PROJECT_MAP.md",
}
PRODUCT_CORE = {
    "../product-governance/REQUIREMENT_BACKLOG.template.md": "product/requirements/REQUIREMENT_BACKLOG.md",
    "../product-governance/REQUIREMENT.template.md": ".senmu-buildos/templates/REQUIREMENT.md",
    "../product-governance/REQUIREMENT_REVIEW.template.md": ".senmu-buildos/templates/REQUIREMENT_REVIEW.md",
}
PRODUCT_STANDARD = {
    "../product-governance/PRD.template.md": "product/requirements/PRD.md",
    "../product-governance/ROADMAP.template.md": "product/requirements/ROADMAP.md",
    "../product-governance/ITERATION_PLAN.template.md": "product/ITERATION_PLAN.md",
}
CODE_CORE = {
    "../code-quality/CODE_QUALITY.template.md": "engineering/CODE_QUALITY.md",
    "../engineering-governance/TESTING_STRATEGY.template.md": "engineering/TESTING_STRATEGY.md",
    "../engineering-governance/TECHNICAL_REVIEW.template.md": ".senmu-buildos/templates/TECHNICAL_REVIEW.md",
}
ARCHITECTURE_STANDARD = {
    "../engineering-governance/TECHNICAL_DESIGN.template.md": ".senmu-buildos/templates/TECHNICAL_DESIGN.md",
    "../architecture-governance/ADR.template.md": ".senmu-buildos/templates/ADR.md",
    "../architecture-governance/ARCHITECTURE_CONTRACT.template.md": "engineering/ARCHITECTURE.md",
}
GIT_STANDARD = {
    "../delivery-governance/BRANCHING.template.md": "delivery/BRANCHING.md",
}
DELIVERY_STANDARD = {
    "../delivery-governance/VERSION_AND_RELEASE.template.md": "delivery/RELEASE_PLAN.md",
    "../delivery-governance/CHANGELOG_RULES.template.md": "delivery/CHANGELOG_POLICY.md",
}
WORKFLOW_CORE = {
    "../workflow-governance/WORKFLOW.template.md": "workflows/WORKFLOW.md",
}
AGENT_CORE = {
    "../agent-governance/AGENT_REGISTER.template.md": "agents/AGENT_REGISTER.md",
    "../agent-governance/AGENT.template.md": ".senmu-buildos/templates/agent/AGENT.md",
}
POC_CORE = {
    "../poc-experiment-governance/EXPERIMENT_REGISTER.template.md": "experiments/EXPERIMENT_REGISTER.md",
    "../poc-experiment-governance/experiment-package/EXPERIMENT.template.md": ".senmu-buildos/templates/experiment-package/EXPERIMENT.md",
    "../poc-experiment-governance/experiment-package/PLAN.template.md": ".senmu-buildos/templates/experiment-package/PLAN.md",
    "../poc-experiment-governance/experiment-package/RESULTS.template.md": ".senmu-buildos/templates/experiment-package/RESULTS.md",
    "../poc-experiment-governance/experiment-package/DECISION.template.md": ".senmu-buildos/templates/experiment-package/DECISION.md",
    "../poc-experiment-governance/experiment-package/experiment-manifest.template.json": ".senmu-buildos/templates/experiment-package/experiment-manifest.json",
}
VERSIONED_RELEASE = {
    "../delivery-governance/VERSION.template": "VERSION",
    "../delivery-governance/CHANGELOG.template.md": "CHANGELOG.md",
}
DEPLOYMENT = {
    "../delivery-governance/DEPLOYMENT.template.md": "operations/DEPLOYMENT.md",
}
ARTIFACT_LIFECYCLE = {
    "../delivery-governance/RELEASE_RETENTION.template.env": "operations/release-retention.env",
    "../delivery-governance/CLEANUP_RELEASE_ASSETS.template.sh": "operations/scripts/cleanup-release-assets.sh",
    "../delivery-governance/TEST_RELEASE_RETENTION.template.sh": "operations/scripts/test-release-retention.sh",
}
PUBLICATION_STANDARD = {
    "../delivery-governance/PUBLICATION.template.md": "delivery/PUBLICATION.md",
}

DEFAULT_PROJECT_SYSTEM_DIR = "00-project-system"
DEFAULT_PROJECT_SYSTEM_EXTERNAL_DIRS = {
    "sources": "01-sources",
    "workspace": "02-workspace",
    "deliveries": "03-deliveries",
    "archive": "04-archive",
}
DEFAULT_PUBLICATION_PATHS = {
    "authority_root": "internal",
    "public_projection_root": "public",
    "release_staging_root": ".release-staging",
}

TYPE_MODULES = {
    "software": ("product", "code", "architecture", "git", "delivery"),
    "script": ("code", "git"),
    "workflow": ("workflow", "code", "git", "delivery"),
    "media": ("workflow", "delivery"),
    "poc": ("poc", "code", "git"),
    "mixed": ("product", "workflow", "code", "architecture", "git", "delivery"),
}
MODULE_CHOICES = ("product", "workflow", "code", "architecture", "git", "poc", "delivery", "agents")

CLASSIFICATION_DEFAULTS = {
    "software": {"lifecycle_intent": "production", "delivery_model": "continuous_product", "composition": "single_domain"},
    "script": {"lifecycle_intent": "one_off", "delivery_model": "internal_process", "composition": "single_domain"},
    "workflow": {"lifecycle_intent": "production", "delivery_model": "managed_service", "composition": "single_domain"},
    "media": {"lifecycle_intent": "production", "delivery_model": "project_delivery", "composition": "single_domain"},
    "poc": {"lifecycle_intent": "exploration", "delivery_model": "internal_process", "composition": "single_domain"},
    "mixed": {"lifecycle_intent": "production", "delivery_model": "project_delivery", "composition": "composite"},
}

PUBLICATION_MODELS = ("private_only", "public_native", "private_authority_public_projection")
RELEASE_CHANNELS = (
    "public_source_repository",
    "marketplace_install",
    "source_archive",
    "package_registry",
    "container_image",
    "desktop_bundle",
    "mobile_bundle",
    "managed_service",
    "project_delivery",
)
ARTIFACT_KINDS = (
    "signed_source_archive",
    "package",
    "container_image",
    "dmg",
    "pkg",
    "msi",
    "mobile_bundle",
    "binary",
    "wheel",
    "jar",
)

BASELINE_COMMIT_MESSAGE = "chore: initialize project governance"


def canonical_git_root(root: Path) -> Path:
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


def render(
    template: Path,
    project_name: str,
    root: Path,
    workspace_root: Path,
    layout: str,
    profile: str,
    project_type: str,
    classification: dict[str, str],
    selected_modules: set[str],
    publication_model: str,
    release_channels: list[str],
    artifact_kinds: list[str],
) -> str:
    text = template.read_text(encoding="utf-8")
    values = {
        "{{PROJECT_NAME}}": project_name,
        "{{PROJECT_ROOT}}": "Git toplevel（运行时解析）" if (root / ".git").exists() else "包含 .senmu-buildos/config.json 的项目根（运行时解析）",
        "{{WORKSPACE_ROOT}}": ".." if root != workspace_root else ".",
        "{{LAYOUT}}": layout,
        "{{PROFILE}}": profile,
        "{{PROJECT_TYPE}}": project_type,
        "{{LIFECYCLE_INTENT}}": classification["lifecycle_intent"],
        "{{DELIVERY_MODEL}}": classification["delivery_model"],
        "{{COMPOSITION}}": classification["composition"],
        "{{PUBLICATION_MODEL}}": publication_model,
        "{{RELEASE_CHANNELS}}": ", ".join(release_channels) if release_channels else "none",
        "{{ARTIFACT_KINDS}}": ", ".join(artifact_kinds) if artifact_kinds else "none",
        "{{DATE}}": date.today().isoformat(),
        "{{MODULE_PRODUCT}}": "active" if "product" in selected_modules else "inactive",
        "{{MODULE_WORKFLOW}}": "active" if "workflow" in selected_modules else "inactive",
        "{{MODULE_CODE}}": "active" if "code" in selected_modules else "inactive",
        "{{MODULE_ARCHITECTURE}}": "active" if "architecture" in selected_modules else "inactive",
        "{{MODULE_GIT}}": "active" if "git" in selected_modules else "inactive",
        "{{MODULE_POC}}": "active" if "poc" in selected_modules else "inactive",
        "{{MODULE_DELIVERY}}": "active" if "delivery" in selected_modules else "inactive",
        "{{MODULE_AGENTS}}": "active" if "agents" in selected_modules else "inactive",
    }
    for old, new in values.items():
        text = text.replace(old, new)
    return text


def resolve_template(source_rel: str) -> Path:
    """Resolve a starter or specialist-owned template without duplicating assets."""

    specialist_routes = {
        "../code-quality/": SKILLS_ROOT / "senmu-build-engineering" / "assets" / "code-quality",
        "../architecture-governance/": SKILLS_ROOT / "senmu-build-engineering" / "assets" / "architecture-governance",
        "../engineering-governance/": SKILLS_ROOT / "senmu-build-engineering" / "assets" / "engineering-governance",
        "../product-governance/": SKILLS_ROOT / "senmu-build-product" / "assets" / "product-governance",
        "../workflow-governance/": SKILLS_ROOT / "senmu-build-workflow" / "assets" / "workflow-governance",
        "../agent-governance/": SKILLS_ROOT / "senmu-build-workflow" / "assets" / "agent-governance",
        "../delivery-governance/": SKILLS_ROOT / "senmu-build-delivery" / "assets" / "delivery-governance",
        "../poc-experiment-governance/": SKILLS_ROOT / "senmu-build-assurance" / "assets" / "poc-experiment-governance",
        "../learning-governance/": SKILLS_ROOT / "senmu-build-learning" / "assets" / "learning-governance",
    }
    for prefix, owner_root in specialist_routes.items():
        if source_rel.startswith(prefix):
            return owner_root / source_rel.removeprefix(prefix)
    return STARTER / source_rel


def validate_relative_role_path(workspace_root: Path, label: str, raw: str) -> str:
    """Validate a persisted path role without storing the machine's absolute path."""

    candidate = Path(raw)
    if candidate.is_absolute():
        raise SystemExit(f"[ERROR] {label} 必须是相对工作区的路径：{raw}")
    resolved = (workspace_root / candidate).resolve()
    try:
        resolved.relative_to(workspace_root)
    except ValueError as exc:
        raise SystemExit(f"[ERROR] {label} 不得越出工作区：{raw}") from exc
    return candidate.as_posix()


def is_resumable_draft(root: Path) -> bool:
    policy_path = root / ".senmu-buildos/config.json"
    if not policy_path.is_file():
        return False
    try:
        policy = json.loads(policy_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return False
    return policy.get("initialization_status") == "draft" and policy.get("schema_version") == "3.0.0"


def create_baseline_commit(root: Path, managed_paths: list[str]) -> dict[str, str | None]:
    """Validate and commit only initializer-managed files in a new draft project."""

    validator = root / ".senmu-buildos/validate.py"
    validation = subprocess.run(
        ["python3", str(validator), "--root", str(root)],
        check=False,
        capture_output=True,
        text=True,
    )
    if validation.returncode != 0:
        raise SystemExit(
            "[ERROR] 项目治理结构校验失败，未创建基线提交：\n"
            + (validation.stdout or validation.stderr)
        )

    identity = {}
    for key in ("user.name", "user.email"):
        probe = subprocess.run(
            ["git", "-C", str(root), "config", "--get", key],
            check=False,
            capture_output=True,
            text=True,
        )
        identity[key] = probe.stdout.strip() if probe.returncode == 0 else ""
    if not all(identity.values()):
        return {
            "status": "skipped",
            "commit": None,
            "reason": "Git user.name/user.email 未配置；治理骨架保持未提交状态",
        }

    staged = subprocess.run(
        ["git", "-C", str(root), "diff", "--cached", "--name-only"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    if staged:
        return {
            "status": "skipped",
            "commit": None,
            "reason": "索引中已有暂存内容；拒绝把既有改动并入初始化基线",
        }

    paths = sorted({path for path in managed_paths if (root / path).exists()})
    subprocess.run(["git", "-C", str(root), "add", "--", *paths], check=True)
    has_changes = subprocess.run(
        ["git", "-C", str(root), "diff", "--cached", "--quiet"],
        check=False,
    ).returncode != 0
    if not has_changes:
        return {"status": "unchanged", "commit": None, "reason": "没有新的初始化文件需要提交"}

    subprocess.run(
        ["git", "-C", str(root), "commit", "-m", BASELINE_COMMIT_MESSAGE],
        check=True,
        capture_output=True,
        text=True,
    )
    commit = subprocess.run(
        ["git", "-C", str(root), "rev-parse", "HEAD"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    return {"status": "committed", "commit": commit, "reason": None}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--mode",
        choices=("plan-new", "initialize-new"),
        required=True,
        help="plan-new 只输出候选文件且零写入；initialize-new 按已审阅参数创建实例",
    )
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--project-name", required=True)
    parser.add_argument("--project-type", choices=tuple(TYPE_MODULES), required=True)
    parser.add_argument(
        "--layout",
        choices=("auto", "software-repository", "project-system", "publication-workspace"),
        default="auto",
        help="software-repository: 项目根即 Git 仓库；project-system: 项目系统与外部物料分离；publication-workspace: 私有权威仓与公开投影仓分离",
    )
    parser.add_argument("--lifecycle-intent", choices=("exploration", "pilot", "production", "migration", "one_off"))
    parser.add_argument("--delivery-model", choices=("continuous_product", "source_distribution", "versioned_artifact", "managed_service", "project_delivery", "internal_process"))
    parser.add_argument("--composition", choices=("single_domain", "composite"))
    parser.add_argument("--publication-model", choices=PUBLICATION_MODELS, default="private_only")
    parser.add_argument("--release-channel", action="append", choices=RELEASE_CHANNELS, default=[])
    parser.add_argument("--artifact-kind", action="append", choices=ARTIFACT_KINDS, default=[])
    parser.add_argument("--authority-path", default=DEFAULT_PUBLICATION_PATHS["authority_root"])
    parser.add_argument("--public-projection-path", default=DEFAULT_PUBLICATION_PATHS["public_projection_root"])
    parser.add_argument("--release-staging-path", default=DEFAULT_PUBLICATION_PATHS["release_staging_root"])
    parser.add_argument("--project-system-path", default=DEFAULT_PROJECT_SYSTEM_DIR)
    parser.add_argument("--sources-path", default=DEFAULT_PROJECT_SYSTEM_EXTERNAL_DIRS["sources"])
    parser.add_argument("--work-area-path", default=DEFAULT_PROJECT_SYSTEM_EXTERNAL_DIRS["workspace"])
    parser.add_argument("--deliveries-path", default=DEFAULT_PROJECT_SYSTEM_EXTERNAL_DIRS["deliveries"])
    parser.add_argument("--archive-path", default=DEFAULT_PROJECT_SYSTEM_EXTERNAL_DIRS["archive"])
    parser.add_argument("--profile", choices=("core", "standard", "release"), required=True)
    parser.add_argument(
        "--modules",
        nargs="*",
        choices=MODULE_CHOICES,
        default=None,
        help="显式覆盖项目类型的推荐模块；只写 --modules 表示不启用专业模块",
    )
    parser.add_argument(
        "--with-agents",
        action="store_true",
        help="为确实维护项目自有 Agent／系统提示词的项目启用 Agent Register、定义模板和校验器",
    )
    parser.add_argument(
        "--commit-baseline",
        action="store_true",
        help="结构校验通过后，只提交本初始化器管理的文件；不创建 Tag，不适用于成熟项目",
    )
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    if args.mode == "plan-new":
        args.dry_run = True

    workspace_root = args.root.expanduser().resolve()
    if workspace_root.is_dir():
        meaningful_entries = {
            path.name for path in workspace_root.iterdir() if path.name not in {".git", ".gitignore", ".DS_Store"}
        }
        candidate_roots = (
            workspace_root / args.project_system_path,
            workspace_root / args.authority_path,
            workspace_root,
        )
        resumable_root = next((candidate for candidate in candidate_roots if candidate.is_dir()), workspace_root)
        if meaningful_entries and not is_resumable_draft(resumable_root):
            assessor = Path(__file__).with_name("assess_project_governance.py")
            raise SystemExit(
                "[ERROR] initialize-new 只用于空白项目；已有项目请先只读审视："
                f"python3 {assessor} --root {workspace_root}"
            )
    if not workspace_root.exists():
        if not args.dry_run:
            workspace_root.mkdir(parents=True)
    if workspace_root.exists() and not workspace_root.is_dir():
        raise SystemExit(f"[ERROR] 目标不是目录：{workspace_root}")

    layout = args.layout
    if layout == "auto":
        if args.publication_model == "private_authority_public_projection":
            layout = "publication-workspace"
        else:
            layout = "software-repository" if args.project_type in {"software", "script"} else "project-system"

    project_system_path = validate_relative_role_path(workspace_root, "project-system-path", args.project_system_path)
    authority_path = validate_relative_role_path(workspace_root, "authority-path", args.authority_path)
    public_projection_path = validate_relative_role_path(workspace_root, "public-projection-path", args.public_projection_path)
    release_staging_path = validate_relative_role_path(workspace_root, "release-staging-path", args.release_staging_path)
    external_role_paths = {
        "sources": validate_relative_role_path(workspace_root, "sources-path", args.sources_path),
        "workspace": validate_relative_role_path(workspace_root, "work-area-path", args.work_area_path),
        "deliveries": validate_relative_role_path(workspace_root, "deliveries-path", args.deliveries_path),
        "archive": validate_relative_role_path(workspace_root, "archive-path", args.archive_path),
    }
    if layout == "publication-workspace" and args.publication_model != "private_authority_public_projection":
        raise SystemExit("[ERROR] publication-workspace 仅用于 private_authority_public_projection")
    root = (
        workspace_root
        if layout == "software-repository"
        else workspace_root / (authority_path if layout == "publication-workspace" else project_system_path)
    )

    if layout == "project-system":
        if not args.dry_run:
            root.mkdir(parents=True, exist_ok=True)
            for dirname in external_role_paths.values():
                (workspace_root / dirname).mkdir(parents=True, exist_ok=True)
    elif layout == "publication-workspace" and not args.dry_run:
        root.mkdir(parents=True, exist_ok=True)
        public_root = workspace_root / public_projection_path
        public_root.mkdir(parents=True, exist_ok=True)
        if not (public_root / ".git").exists():
            subprocess.run(["git", "init", str(public_root)], check=True, capture_output=True, text=True)
        (workspace_root / release_staging_path).mkdir(parents=True, exist_ok=True)

    if root.exists():
        canonical = canonical_git_root(root)
        if (root / ".git").exists() and canonical != root:
            raise SystemExit(f"[ERROR] 拒绝在外部 worktree 初始化；请使用权威项目根：{canonical}")

    if not args.dry_run and not (root / ".git").exists():
        subprocess.run(["git", "init", str(root)], check=True, capture_output=True, text=True)

    selected_modules = list(dict.fromkeys(TYPE_MODULES[args.project_type] if args.modules is None else args.modules))
    if args.with_agents and "agents" not in selected_modules:
        selected_modules.append("agents")
    selected_module_set = set(selected_modules)
    has_standard_owners = args.profile in {"standard", "release"}
    classification = dict(CLASSIFICATION_DEFAULTS[args.project_type])
    release_channels = list(dict.fromkeys(args.release_channel))
    artifact_kinds = list(dict.fromkeys(args.artifact_kind))
    if args.lifecycle_intent:
        classification["lifecycle_intent"] = args.lifecycle_intent
    if args.delivery_model:
        classification["delivery_model"] = args.delivery_model
    if args.composition:
        classification["composition"] = args.composition
    templates = dict(BASE)
    if "agents" in selected_module_set:
        templates.update(AGENT_CORE)
    if has_standard_owners:
        templates.update(BASE_STANDARD)
        if "product" in selected_module_set:
            templates.update(PRODUCT_CORE)
        if "code" in selected_module_set:
            templates.update(CODE_CORE)
        if "workflow" in selected_module_set:
            templates.update(WORKFLOW_CORE)
        if "poc" in selected_module_set:
            templates.update(POC_CORE)
        if "product" in selected_module_set:
            templates.update(PRODUCT_STANDARD)
        if "architecture" in selected_module_set:
            templates.update(ARCHITECTURE_STANDARD)
        if "git" in selected_module_set:
            templates.update(GIT_STANDARD)
        if "delivery" in selected_module_set:
            templates.update(DELIVERY_STANDARD)
    if has_standard_owners and args.publication_model == "private_authority_public_projection":
        templates.update(PUBLICATION_STANDARD)
    if args.profile == "release":
        templates.update(VERSIONED_RELEASE)
    if set(release_channels) & {"managed_service", "container_image"}:
        templates.update(DEPLOYMENT)
    if artifact_kinds:
        templates.update(ARTIFACT_LIFECYCLE)

    required_paths = list(templates.values())
    generated: list[str] = []
    planned: list[str] = []
    skipped: list[str] = []
    for source_rel, target_rel in templates.items():
        source = resolve_template(source_rel).resolve()
        target = root / target_rel
        if target.exists():
            skipped.append(target_rel)
            continue
        if args.dry_run:
            planned.append(target_rel)
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(
            render(
                source,
                args.project_name,
                root,
                workspace_root,
                layout,
                args.profile,
                args.project_type,
                classification,
                selected_module_set,
                args.publication_model,
                release_channels,
                artifact_kinds,
            ),
            encoding="utf-8",
        )
        if target_rel.startswith("operations/scripts/") and target.suffix == ".sh":
            target.chmod(0o755)
        generated.append(target_rel)

    validator_rel = ".senmu-buildos/validate.py"
    validator_target = root / validator_rel
    if validator_target.exists():
        skipped.append(validator_rel)
    elif args.dry_run:
        planned.append(validator_rel)
    else:
        validator_target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(Path(__file__).with_name("validate_project_governance.py"), validator_target)
        validator_target.chmod(0o755)
        generated.append(validator_rel)
    required_paths.append(validator_rel)

    lessons_validator_rel = ".senmu-buildos/validate_lessons.py"
    if has_standard_owners:
        lessons_validator_target = root / lessons_validator_rel
        if lessons_validator_target.exists():
            skipped.append(lessons_validator_rel)
        elif args.dry_run:
            planned.append(lessons_validator_rel)
        else:
            lessons_validator_target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(LESSONS_VALIDATOR_SOURCE, lessons_validator_target)
            lessons_validator_target.chmod(0o755)
            generated.append(lessons_validator_rel)
        required_paths.append(lessons_validator_rel)

    if "agents" in selected_module_set:
        agent_validator_rel = ".senmu-buildos/validate_agents.py"
        agent_validator_target = root / agent_validator_rel
        if agent_validator_target.exists():
            skipped.append(agent_validator_rel)
        elif args.dry_run:
            planned.append(agent_validator_rel)
        else:
            agent_validator_target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(AGENT_VALIDATOR_SOURCE, agent_validator_target)
            agent_validator_target.chmod(0o755)
            generated.append(agent_validator_rel)
        required_paths.append(agent_validator_rel)

    policy_rel = ".senmu-buildos/config.json"
    policy_target = root / policy_rel
    if policy_target.exists():
        skipped.append(policy_rel)
    elif args.dry_run:
        planned.append(policy_rel)
    else:
        policy_target.parent.mkdir(parents=True, exist_ok=True)
        policy = {
            "schema_version": "3.0.0",
            "project_name": args.project_name,
            "project_type": args.project_type,
            "layout": layout,
            "classification": classification,
            "publication": {
                "model": args.publication_model,
                "public_projection_root": public_projection_path if args.publication_model == "private_authority_public_projection" else None,
                "release_staging_root": release_staging_path if args.publication_model == "private_authority_public_projection" else None,
                "projection_mode": "generated_only" if args.publication_model == "private_authority_public_projection" else None,
            },
            "release_channels": release_channels,
            "artifact_kinds": artifact_kinds,
            "profile": args.profile,
            "selected_modules": selected_modules,
            "git_management": {
                "main_mode": "release_ready",
                "direct_main_writes": False,
                "worktree_root": ".worktrees",
                "change_unit_states": [
                    "in_progress", "sealed", "integrated", "excluded", "superseded",
                ],
            } if "git" in selected_module_set else None,
            "release_policy": {
                "official_tag_semantics": "verified_release",
                "candidate_identity": "commit_and_artifact",
                "authorization_mode": "bounded_release_session",
            } if "delivery" in selected_module_set else None,
            "initialization_status": "draft",
            "root_locator": {
                "kind": "git_toplevel" if (root / ".git").exists() else "governance_policy_root",
                "relative_path": ".",
            },
            "required_paths": sorted(required_paths),
            "placeholder_scan_paths": sorted(required_paths),
            "workspace_root": ".." if layout in {"project-system", "publication-workspace"} else ".",
            "path_roles": {
                "authority_root": authority_path if layout == "publication-workspace" else (project_system_path if layout == "project-system" else "."),
                "public_projection_root": public_projection_path if args.publication_model == "private_authority_public_projection" else None,
                "release_staging_root": release_staging_path if args.publication_model == "private_authority_public_projection" else None,
            },
            "external_directories": {
                key: f"../{value}" for key, value in external_role_paths.items()
            } if layout == "project-system" else {},
            "worklog_path": "governance/logs/WORKLOG.md" if has_standard_owners else None,
            "lessons_path": "governance/lessons/LESSONS_LEARNED.md" if has_standard_owners else None,
            "lessons_validation": {
                "script_path": ".senmu-buildos/validate_lessons.py",
                "command": "python3 .senmu-buildos/validate_lessons.py governance/lessons/LESSONS_LEARNED.md",
            } if has_standard_owners else None,
            "task_management": {
                "owner_kind": "senmu_markdown",
                "task_directory": "governance/tasks",
                "register_path": "governance/tasks/TASK_REGISTER.md",
                "template_path": ".senmu-buildos/templates/TASK.md",
                "task_file_format": "TASK-NNNN-slug.md",
                "statuses": ["planned", "active", "blocked", "verifying", "completed", "cancelled", "archived"],
            } if has_standard_owners else None,
            "project_map_path": "governance/PROJECT_MAP.md" if args.profile in {"standard", "release"} else None,
            "validator": "python3 .senmu-buildos/validate.py --root .",
            "strict_validator": "python3 .senmu-buildos/validate.py --root . --strict",
            "release_units": [],
            "quality_commands": {},
            "product_management": {
                "backlog_path": "product/requirements/REQUIREMENT_BACKLOG.md",
                "roadmap_path": "product/requirements/ROADMAP.md" if args.profile in {"standard", "release"} else None,
                "iteration_plan_path": "product/ITERATION_PLAN.md" if args.profile in {"standard", "release"} else None,
                "requirement_id_format": "REQ-xxxx",
            } if "product" in selected_modules and has_standard_owners else None,
            "workflow_management": {
                "contract_path": "workflows/WORKFLOW.md",
            } if "workflow" in selected_module_set and has_standard_owners else None,
            "agent_management": {
                "owner_kind": "senmu_markdown",
                "directory": "agents",
                "register_path": "agents/AGENT_REGISTER.md",
                "template_path": ".senmu-buildos/templates/agent/AGENT.md",
                "definition_path_format": "agents/{agent-key}/AGENT.md",
                "statuses": ["draft", "active", "deprecated", "retired"],
                "validator_path": ".senmu-buildos/validate_agents.py",
                "validation_command": "python3 .senmu-buildos/validate_agents.py --root .",
            } if "agents" in selected_module_set else None,
            "release_retention": {
                "config_path": "operations/release-retention.env",
                "cleanup_script": "operations/scripts/cleanup-release-assets.sh",
                "contract_test": "operations/scripts/test-release-retention.sh",
                "default_keep": ["current", "previous"],
            } if artifact_kinds else None,
        }
        policy_target.write_text(json.dumps(policy, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        generated.append(policy_rel)

    managed_paths = [*required_paths, policy_rel]
    baseline_commit = None
    if args.commit_baseline and not args.dry_run:
        baseline_commit = create_baseline_commit(root, managed_paths)

    print(json.dumps({"mode": args.mode, "workspace_root": str(workspace_root), "root": str(root), "layout": layout, "project_type": args.project_type, "classification": classification, "publication_model": args.publication_model, "release_channels": release_channels, "artifact_kinds": artifact_kinds, "profile": args.profile, "selected_modules": selected_modules, "planned": planned, "generated": generated, "skipped": skipped, "baseline_commit": baseline_commit}, ensure_ascii=False, indent=2))
    if not args.dry_run:
        print("[NEXT] 先校准占位字段，再将 .senmu-buildos/config.json 的 initialization_status 改为 active 并运行 --strict。")


if __name__ == "__main__":
    main()
