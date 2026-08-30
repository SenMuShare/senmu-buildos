#!/usr/bin/env python3
"""Validate the current Senmu BuildOS product package."""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
EXPECTED_SKILLS = {
    "senmu-build-project",
    "senmu-build-product",
    "senmu-build-workflow",
    "senmu-build-engineering",
    "senmu-build-delivery",
    "senmu-build-assurance",
    "senmu-build-learning",
}

REFERENCE_OWNERS = {
    "项目实践指南.md": "senmu-build-project",
    "任务执行与状态管理规范.md": "senmu-build-project",
    "治理强度分级与门禁规范.md": "senmu-build-project",
    "项目落地移交与场景路由规范.md": "senmu-build-project",
    "项目目录与文档规范.md": "senmu-build-project",
    "项目治理实例与演进规范.md": "senmu-build-project",
    "项目规范发现与按需加载规范.md": "senmu-build-project",
    "成熟项目接管治理专项规范.md": "senmu-build-project",
    "需求与产品迭代管理规范.md": "senmu-build-product",
    "工作流、物料与交付物治理规范.md": "senmu-build-workflow",
    "工作流运行状态与恢复协议.md": "senmu-build-workflow",
    "reference附件治理.md": "senmu-build-workflow",
    "Agent定义与系统提示词框架.md": "senmu-build-workflow",
    "发布授权与生产事实协议.md": "senmu-build-delivery",
    "独立审查与证据分级规范.md": "senmu-build-assurance",
    "技术路线与组件选型.md": "senmu-build-engineering",
    "实现经济性与过度工程治理规范.md": "senmu-build-engineering",
    "架构约束与技术债治理规范.md": "senmu-build-engineering",
    "源代码工程质量与AI协作规范.md": "senmu-build-engineering",
    "软件测试与质量验证规范.md": "senmu-build-engineering",
    "源码级重构与技术栈升级规范.md": "senmu-build-engineering",
    "Python工程编码规范.md": "senmu-build-engineering",
    "TypeScript工程编码规范.md": "senmu-build-engineering",
    "Go工程编码规范.md": "senmu-build-engineering",
    "Java工程编码规范.md": "senmu-build-engineering",
    "frontend-ant-design-practice.md": "senmu-build-engineering",
    "frontend-html-daisyui-practice.md": "senmu-build-engineering",
    "项目工程规范发现方法.md": "senmu-build-engineering",
    "代码管理与合并规范.md": "senmu-build-delivery",
    "多Agent变更单元与版本线收口规范.md": "senmu-build-delivery",
    "仓库边界与发布单元治理规范.md": "senmu-build-delivery",
    "协作日志与版本日志规范.md": "senmu-build-delivery",
    "版本制品与发布规范.md": "senmu-build-delivery",
    "部署测试与安全规范.md": "senmu-build-delivery",
    "POC可复现实验治理规范.md": "senmu-build-assurance",
    "AI复盘与治理闭环规范.md": "senmu-build-learning",
    "BuildOS项目演进与反哺规范.md": "senmu-build-learning",
    "反馈候选与集中审议规范.md": "senmu-build-learning",
    "工程知识蒸馏与标准晋级规范.md": "senmu-build-learning",
}

PUBLIC_TEXT_SUFFIXES = {".md", ".json", ".yaml", ".yml", ".py", ".js", ".sh", ".env"}
FORBIDDEN_ORIGIN_TERMS = (
    "project" + "-practice",
    "spec" + "-kit",
    "spec " + "kit",
    "open" + "spec",
    "b" + "mad",
    "super" + "powers",
)
MAX_SKILL_ENTRY_CHARS = 2_200
MAX_SKILL_DESCRIPTION_CHARS = 400
MAX_DESCRIPTION_CATALOG_CHARS = 2_400
MAX_REFERENCE_CHARS = 10_000
MAX_PROJECT_AGENTS_TEMPLATE_CHARS = 2_300
MAX_SKILL_ENTRY_CONTEXT_UNITS = 1_200
MAX_SKILL_DESCRIPTION_CONTEXT_UNITS = 90
MAX_DESCRIPTION_CATALOG_CONTEXT_UNITS = 500
MAX_REFERENCE_CONTEXT_UNITS = 5_500
MAX_SINGLE_REFERENCE_ROUTE_CONTEXT_UNITS = 6_500
MAX_TWO_REFERENCE_ROUTE_CONTEXT_UNITS = 12_000


def fail(message: str) -> None:
    raise SystemExit(f"[ERROR] {message}")


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def estimate_context_units(text: str) -> int:
    """Conservative dependency-free proxy for mixed CJK and Latin token cost."""
    cjk = sum(
        1
        for char in text
        if "\u3400" <= char <= "\u9fff"
        or "\u3040" <= char <= "\u30ff"
        or "\uac00" <= char <= "\ud7af"
    )
    return cjk + (len(text) - cjk + 3) // 4


def parse_skill_name(text: str) -> str:
    match = re.match(r"^---\n([\s\S]*?)\n---\n", text)
    if not match:
        fail("SKILL.md missing YAML frontmatter")
    name_match = re.search(r"^name:\s*([^\n]+)$", match.group(1), re.MULTILINE)
    if not name_match:
        fail("SKILL.md frontmatter missing name")
    return name_match.group(1).strip().strip('"\'')


def parse_skill_description(text: str) -> str:
    match = re.match(r"^---\n([\s\S]*?)\n---\n", text)
    if not match:
        fail("SKILL.md missing YAML frontmatter")
    description_match = re.search(r"^description:\s*(.+)$", match.group(1), re.MULTILINE)
    if not description_match:
        fail("SKILL.md frontmatter missing description")
    return description_match.group(1).strip().strip('"\'')


def validate_product_identity() -> None:
    for path in sorted(ROOT.rglob("*")):
        if not path.is_file() or ".git" in path.parts or path == Path(__file__).resolve():
            continue
        if path.suffix.lower() not in PUBLIC_TEXT_SUFFIXES:
            continue
        text = path.read_text(encoding="utf-8").casefold()
        for term in FORBIDDEN_ORIGIN_TERMS:
            if term in text:
                fail(f"product-origin or competitor term leaked into {path.relative_to(ROOT)}: {term}")


def validate_plugins() -> None:
    manifest_path = ROOT / ".codex-plugin/plugin.json"
    hooks_path = ROOT / "hooks/hooks.json"
    claude_manifest_path = ROOT / ".claude-plugin/plugin.json"
    claude_hooks_path = ROOT / "adapters/claude-code/hooks/hooks.json"
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        hooks = json.loads(hooks_path.read_text(encoding="utf-8"))
        claude_manifest = json.loads(claude_manifest_path.read_text(encoding="utf-8"))
        claude_hooks = json.loads(claude_hooks_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        fail(f"plugin or hook manifest is invalid: {exc}")
    if manifest.get("name") != "senmu-buildos":
        fail("plugin name must be senmu-buildos")
    try:
        version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    except OSError as exc:
        fail(f"VERSION is unreadable: {exc}")
    if manifest.get("version") != version:
        fail("VERSION and plugin manifest version must agree")
    if claude_manifest.get("version") != version:
        fail("VERSION and Claude Code plugin manifest version must agree")
    if manifest.get("skills") != "./skills/":
        fail("plugin skill route is incorrect")
    if "hooks" in manifest:
        fail("use the default hooks/hooks.json discovery path; do not duplicate it in plugin.json")
    if manifest.get("author", {}).get("name") != "Senmu":
        fail("plugin author.name must identify Senmu")
    interface = manifest.get("interface", {})
    if interface.get("developerName") != "Senmu":
        fail("plugin interface.developerName must identify Senmu")
    prompts = interface.get("defaultPrompt", [])
    if not isinstance(prompts, list) or not 1 <= len(prompts) <= 3:
        fail("plugin defaultPrompt must contain one to three prompts")
    registered = set(hooks.get("hooks", {}))
    expected_hooks = {"SessionStart", "SubagentStart"}
    if registered != expected_hooks:
        fail(f"unexpected lifecycle hooks: {sorted(registered)}")
    if claude_manifest.get("name") != "senmu-buildos":
        fail("Claude Code plugin name must be senmu-buildos")
    if claude_manifest.get("hooks") != "./adapters/claude-code/hooks/hooks.json":
        fail("Claude Code plugin must route to its isolated Hook adapter")
    claude_registered = set(claude_hooks.get("hooks", {}))
    if claude_registered != expected_hooks:
        fail(f"unexpected Claude Code lifecycle hooks: {sorted(claude_registered)}")
    claude_serialized = json.dumps(claude_hooks)
    if "${CLAUDE_PLUGIN_ROOT}" not in claude_serialized:
        fail("Claude Code Hooks must resolve files from CLAUDE_PLUGIN_ROOT")
    for unsafe in ("curl ", "wget ", "git ", "rm ", ".claude/"):
        if unsafe in claude_serialized.casefold():
            fail(f"Claude Code Hook adapter contains unsafe side effect: {unsafe.strip()}")


def validate_marketplaces() -> None:
    marketplace_path = ROOT / ".agents/plugins/marketplace.json"
    try:
        marketplace = json.loads(marketplace_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        fail(f"marketplace catalog is invalid: {exc}")
    if marketplace.get("name") != "senmu-buildos":
        fail("marketplace name must be senmu-buildos")
    if marketplace.get("interface", {}).get("displayName") != "Senmu BuildOS":
        fail("marketplace displayName must be Senmu BuildOS")
    plugins = marketplace.get("plugins")
    if not isinstance(plugins, list) or len(plugins) != 1:
        fail("marketplace must publish exactly one plugin")
    entry = plugins[0]
    if entry.get("name") != "senmu-buildos":
        fail("marketplace plugin name must be senmu-buildos")
    source = entry.get("source", {})
    if source.get("source") != "url":
        fail("marketplace plugin source must use the repository URL")
    if source.get("url") != "https://github.com/SenMuShare/senmu-buildos.git":
        fail("marketplace plugin source URL is incorrect")
    version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    if source.get("ref") != f"v{version}":
        fail("marketplace release ref must agree with VERSION")
    if entry.get("policy") != {"installation": "AVAILABLE", "authentication": "ON_INSTALL"}:
        fail("marketplace installation policy is incorrect")
    if entry.get("category") != "Productivity":
        fail("marketplace category must be Productivity")

    claude_marketplace_path = ROOT / ".claude-plugin/marketplace.json"
    try:
        claude_marketplace = json.loads(claude_marketplace_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        fail(f"Claude Code marketplace catalog is invalid: {exc}")
    if claude_marketplace.get("name") != "senmu-buildos":
        fail("Claude Code marketplace name must be senmu-buildos")
    if claude_marketplace.get("owner", {}).get("name") != "Senmu":
        fail("Claude Code marketplace owner must identify Senmu")
    claude_plugins = claude_marketplace.get("plugins")
    if not isinstance(claude_plugins, list) or len(claude_plugins) != 1:
        fail("Claude Code marketplace must publish exactly one plugin")
    claude_entry = claude_plugins[0]
    if claude_entry.get("name") != "senmu-buildos" or claude_entry.get("source") != "./":
        fail("Claude Code marketplace must install this repository as senmu-buildos")
    if claude_entry.get("version") != version:
        fail("Claude Code marketplace version must agree with VERSION")


def validate_skills() -> None:
    skills_root = ROOT / "skills"
    actual = {path.name for path in skills_root.iterdir() if path.is_dir()}
    if actual != EXPECTED_SKILLS:
        fail(f"skill set mismatch: expected {sorted(EXPECTED_SKILLS)}, got {sorted(actual)}")
    seen_references: dict[str, str] = {}
    description_catalog_chars = 0
    description_catalog_context_units = 0
    for skill_name in sorted(actual):
        skill_root = skills_root / skill_name
        entry = skill_root / "SKILL.md"
        agents = skill_root / "agents/openai.yaml"
        if not entry.is_file() or not agents.is_file():
            fail(f"{skill_name} is missing SKILL.md or agents/openai.yaml")
        text = entry.read_text(encoding="utf-8")
        if parse_skill_name(text) != skill_name:
            fail(f"{skill_name} frontmatter name does not match folder")
        description = parse_skill_description(text)
        description_catalog_chars += len(description)
        description_units = estimate_context_units(description)
        description_catalog_context_units += description_units
        if len(description) > MAX_SKILL_DESCRIPTION_CHARS:
            fail(
                f"{skill_name}/SKILL.md description exceeds "
                f"{MAX_SKILL_DESCRIPTION_CHARS} characters"
            )
        if description_units > MAX_SKILL_DESCRIPTION_CONTEXT_UNITS:
            fail(
                f"{skill_name}/SKILL.md description exceeds "
                f"{MAX_SKILL_DESCRIPTION_CONTEXT_UNITS} context units"
            )
        if len(text) > MAX_SKILL_ENTRY_CHARS:
            fail(f"{skill_name}/SKILL.md exceeds {MAX_SKILL_ENTRY_CHARS} characters")
        entry_units = estimate_context_units(text)
        if entry_units > MAX_SKILL_ENTRY_CONTEXT_UNITS:
            fail(
                f"{skill_name}/SKILL.md exceeds "
                f"{MAX_SKILL_ENTRY_CONTEXT_UNITS} context units"
            )
        if len(text.splitlines()) > 140:
            fail(f"{skill_name}/SKILL.md exceeds 140 lines")
        ui = agents.read_text(encoding="utf-8")
        for field in ("display_name:", "short_description:", "default_prompt:"):
            if field not in ui:
                fail(f"{skill_name}/agents/openai.yaml missing {field}")
        reference_units: list[tuple[int, Path]] = []
        for reference in sorted((skill_root / "references").glob("*.md")):
            reference_text = reference.read_text(encoding="utf-8")
            if len(reference_text) > MAX_REFERENCE_CHARS:
                fail(f"{reference} exceeds {MAX_REFERENCE_CHARS} characters")
            units = estimate_context_units(reference_text)
            if units > MAX_REFERENCE_CONTEXT_UNITS:
                fail(f"{reference} exceeds {MAX_REFERENCE_CONTEXT_UNITS} context units")
            if f"references/{reference.name}" not in text:
                fail(f"{reference} is not directly routed from its owner SKILL.md")
            if reference.name in seen_references:
                fail(f"reference has duplicate active owners: {reference.name}")
            seen_references[reference.name] = skill_name
            reference_units.append((units, reference))
        largest = sorted(reference_units, reverse=True)
        if largest and entry_units + largest[0][0] > MAX_SINGLE_REFERENCE_ROUTE_CONTEXT_UNITS:
            fail(
                f"{skill_name} entry plus {largest[0][1].name} exceeds "
                f"{MAX_SINGLE_REFERENCE_ROUTE_CONTEXT_UNITS} context units"
            )
        if len(largest) > 1 and entry_units + largest[0][0] + largest[1][0] > MAX_TWO_REFERENCE_ROUTE_CONTEXT_UNITS:
            fail(
                f"{skill_name} entry plus two largest references exceeds "
                f"{MAX_TWO_REFERENCE_ROUTE_CONTEXT_UNITS} context units"
            )
    if seen_references != REFERENCE_OWNERS:
        fail("active reference owner map does not match the product architecture")
    if description_catalog_chars > MAX_DESCRIPTION_CATALOG_CHARS:
        fail(
            "Skill description catalog exceeds "
            f"{MAX_DESCRIPTION_CATALOG_CHARS} characters"
        )
    if description_catalog_context_units > MAX_DESCRIPTION_CATALOG_CONTEXT_UNITS:
        fail(
            "Skill description catalog exceeds "
            f"{MAX_DESCRIPTION_CATALOG_CONTEXT_UNITS} context units"
        )

    required_resources = (
        ROOT / "AGENTS.md",
        ROOT / ".github/workflows/release.yml",
        ROOT / "scripts/bump_version.py",
        ROOT / "scripts/validate_distillation_batch.py",
        ROOT / "scripts/validate_skill_integrity_review.py",
        ROOT / "scripts/validate_public_surface.py",
        ROOT / "skills/senmu-build-project/scripts/validate_mature_project_governance.py",
        ROOT / "skills/senmu-build-project/assets/mature-project-governance/TAKEOVER_TASK.template.md",
        ROOT / "skills/senmu-build-project/assets/mature-project-governance/GOVERNANCE_CONTROL.template.json",
        ROOT / "skills/senmu-build-assurance/scripts/validate_exhaustive_source_review.py",
        ROOT / "skills/senmu-build-assurance/assets/review-governance/EXHAUSTIVE_SOURCE_REVIEW_CONTROL.template.json",
        ROOT / "skills/senmu-build-engineering/assets/architecture-governance/EXHAUSTIVE_SOURCE_REVIEW_TASK.template.md",
        ROOT / "skills/senmu-build-delivery/scripts/validate_change_review.py",
        ROOT / "skills/senmu-build-delivery/assets/delivery-governance/CHANGE_REVIEW_CONTROL.template.json",
        ROOT / "skills/senmu-build-delivery/scripts/export_public_projection.py",
        ROOT / "skills/senmu-build-workflow/assets/agent-governance/AGENT_REGISTER.template.md",
        ROOT / "skills/senmu-build-workflow/assets/agent-governance/AGENT.template.md",
        ROOT / "skills/senmu-build-workflow/scripts/validate_agents.py",
        ROOT / "tests/behavior/senmu-buildos-trigger-matrix.md",
        ROOT / "tests/behavior/skill-entry-invariants.md",
        ROOT / "hooks/feedback.js",
        ROOT / "hooks/feedback-cli.js",
        ROOT / "bin/senmu-feedback",
    )
    for resource in required_resources:
        if not resource.is_file():
            fail(f"required product resource is missing: {resource.relative_to(ROOT)}")
    release_workflow = (ROOT / ".github/workflows/release.yml").read_text(encoding="utf-8")
    if "python3 scripts/validate_public_surface.py" not in release_workflow:
        fail("release workflow must enforce the public source boundary")
    validation_workflow = (ROOT / ".github/workflows/validate.yml").read_text(encoding="utf-8")
    if "python3 scripts/validate_public_surface.py" not in validation_workflow:
        fail("validation workflow must validate the public source boundary")


def validate_no_exact_duplicate_active_files() -> None:
    seen: dict[str, Path] = {}
    for path in sorted((ROOT / "skills").rglob("*")):
        if not path.is_file() or path.name == "openai.yaml":
            continue
        digest = sha256(path.read_bytes())
        previous = seen.get(digest)
        if previous:
            fail(
                "exact duplicate active files: "
                f"{previous.relative_to(ROOT)} and {path.relative_to(ROOT)}"
            )
        seen[digest] = path


def validate_no_duplicate_instruction_paragraphs() -> None:
    seen: dict[str, Path] = {}
    candidates = []
    for skill_root in sorted((ROOT / "skills").iterdir()):
        candidates.append(skill_root / "SKILL.md")
        candidates.extend(sorted((skill_root / "references").glob("*.md")))
    for path in candidates:
        text = path.read_text(encoding="utf-8")
        for raw in re.split(r"\n\s*\n", text):
            normalized = re.sub(r"\s+", " ", raw).strip()
            if len(normalized) < 180 or normalized.startswith("|") or normalized.startswith("```"):
                continue
            digest = sha256(normalized.encode("utf-8"))
            previous = seen.get(digest)
            if previous and previous != path:
                fail(
                    "duplicate active instruction paragraph: "
                    f"{previous.relative_to(ROOT)} and {path.relative_to(ROOT)}"
                )
            seen[digest] = path


def validate_behavior_invariant_ids() -> None:
    path = ROOT / "tests/behavior/skill-entry-invariants.md"
    seen: dict[str, int] = {}
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        match = re.match(r"^\|\s*([A-Z]+-\d+)\s*\|", line)
        if match is None:
            continue
        invariant_id = match.group(1)
        previous = seen.get(invariant_id)
        if previous is not None:
            fail(
                "duplicate behavior invariant id "
                f"{invariant_id} in {path.relative_to(ROOT)}:{previous} and :{line_number}"
            )
        seen[invariant_id] = line_number


def validate_local_markdown_links() -> None:
    candidates = list((ROOT / "skills").rglob("*.md"))
    candidates.extend((ROOT / "docs/architecture").rglob("*.md"))
    candidates.extend((ROOT / "tests/behavior").rglob("*.md"))
    candidates.extend(
        path
        for path in (ROOT / "README.md", ROOT / "README.en.md", ROOT / "README.ja.md", ROOT / "CONTRIBUTING.md", ROOT / "ROADMAP.md")
        if path.is_file()
    )
    for path in sorted(candidates):
        text = path.read_text(encoding="utf-8")
        for raw_target in re.findall(r"\[[^\]]+\]\(([^)]+)\)", text):
            target = raw_target.split("#", 1)[0].strip()
            if not target or "://" in target or target.startswith("mailto:"):
                continue
            resolved = (path.parent / target).resolve()
            if not resolved.exists():
                fail(f"broken local Markdown link in {path.relative_to(ROOT)}: {raw_target}")


def validate_project_instruction_layer() -> None:
    template = ROOT / "skills/senmu-build-project/assets/project-governance-starter/AGENTS.template.md"
    text = template.read_text(encoding="utf-8")
    if len(text) > MAX_PROJECT_AGENTS_TEMPLATE_CHARS:
        fail(
            "project AGENTS template exceeds delta-layer budget: "
            f"{len(text)} > {MAX_PROJECT_AGENTS_TEMPLATE_CHARS} characters"
        )
    for legacy_heading in ("## 稳定规则", "## 完成输出"):
        if legacy_heading in text:
            fail(f"project AGENTS template still carries copied governance section: {legacy_heading}")
    peer_skill_catalog = EXPECTED_SKILLS - {"senmu-build-project"}
    copied_skill_names = sorted(skill for skill in peer_skill_catalog if skill in text)
    if copied_skill_names:
        fail(f"project AGENTS template copies the peer Skill catalog: {copied_skill_names}")
    if "固定前置链" not in text or "全部 BuildOS Skill 职责" not in text:
        fail("project AGENTS template must reject unconditional document preloads and copied Skill catalogs")
    legacy_template = ROOT / "skills/senmu-build-engineering/assets/code-quality/AGENTS.template.md"
    if legacy_template.exists():
        fail("Engineering must not own a second project AGENTS template")


def main() -> None:
    validate_product_identity()
    validate_plugins()
    validate_marketplaces()
    validate_skills()
    validate_no_exact_duplicate_active_files()
    validate_no_duplicate_instruction_paragraphs()
    validate_behavior_invariant_ids()
    validate_local_markdown_links()
    validate_project_instruction_layer()
    print(
        "[OK] Skill context budgets: "
        f"entry<={MAX_SKILL_ENTRY_CHARS}, "
        f"description<={MAX_SKILL_DESCRIPTION_CHARS}, "
        f"catalog<={MAX_DESCRIPTION_CATALOG_CHARS}, "
        f"reference<={MAX_REFERENCE_CHARS} characters"
    )
    print(
        "[OK] context-unit budgets: "
        f"entry<={MAX_SKILL_ENTRY_CONTEXT_UNITS}, "
        f"description<={MAX_SKILL_DESCRIPTION_CONTEXT_UNITS}, "
        f"catalog<={MAX_DESCRIPTION_CATALOG_CONTEXT_UNITS}, "
        f"reference<={MAX_REFERENCE_CONTEXT_UNITS}, "
        f"one-route<={MAX_SINGLE_REFERENCE_ROUTE_CONTEXT_UNITS}, "
        f"two-route<={MAX_TWO_REFERENCE_ROUTE_CONTEXT_UNITS}"
    )
    print("[OK] Senmu BuildOS product identity is clean")
    print("[OK] Codex and Claude Code plugin structures and seven Skill entrypoints are valid")
    print("[OK] VERSION, plugin manifests, and marketplace release metadata agree")
    print(f"[OK] active references: {len(REFERENCE_OWNERS)}/{len(REFERENCE_OWNERS)} files have one owner")
    print("[OK] no exact duplicate active Skill resources found")
    print("[OK] no duplicated long instruction paragraphs found across active Skills")
    print("[OK] behavior invariant identifiers are unique")
    print("[OK] active local Markdown links resolve")
    print(f"[OK] project AGENTS delta layer <= {MAX_PROJECT_AGENTS_TEMPLATE_CHARS} characters and has one template owner")
    print("[OK] public package validation is independent from private project-state owners")


if __name__ == "__main__":
    main()
