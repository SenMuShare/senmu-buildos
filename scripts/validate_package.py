#!/usr/bin/env python3
"""Validate the current Senmu BuildOS product package."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from urllib.parse import unquote

from extract_release_notes import ReleaseNotesError, extract_release_notes
from manage_github_product_surface import ProductSurfaceError, validate_local_surface

ROOT = Path(__file__).resolve().parent.parent
EXPECTED_SKILLS = {
    "senmu-build-project",
    "senmu-build-product",
    "senmu-build-design",
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
    "界面文案与内容设计规范.md": "senmu-build-product",
    "界面文案中文规范.md": "senmu-build-product",
    "界面文案英文规范.md": "senmu-build-product",
    "界面视觉与设计系统规范.md": "senmu-build-design",
    "交互动效与可访问性规范.md": "senmu-build-design",
    "原型探索与界面评审规范.md": "senmu-build-design",
    "参考界面解析与还原规范.md": "senmu-build-design",
    "design-library/INDEX.md": "senmu-build-design",
    "design-library/页面结构与视觉方向.md": "senmu-build-design",
    "design-library/组件设计模式.md": "senmu-build-design",
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
    "前端工程契约与验证规范.md": "senmu-build-engineering",
    "后端服务与数据契约规范.md": "senmu-build-engineering",
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
MAX_SKILL_ENTRY_CONTEXT_UNITS = 1_050
MAX_SKILL_DESCRIPTION_CONTEXT_UNITS = 90
MAX_DESCRIPTION_CATALOG_CONTEXT_UNITS = 425
MAX_REFERENCE_CONTEXT_UNITS = 5_500
MAX_SINGLE_REFERENCE_ROUTE_CONTEXT_UNITS = 6_500
MAX_TWO_REFERENCE_ROUTE_CONTEXT_UNITS = 12_000
MAX_REFERENCE_CHAIN_CONTEXT_UNITS = 12_000


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


def reference_graph(skill_root: Path, references: list[Path]) -> dict[Path, set[Path]]:
    """Return links from the entry/reference files to references in the same Skill."""
    entry = (skill_root / "SKILL.md").resolve()
    resolved_references = {path.resolve() for path in references}
    graph = {path: set() for path in (entry, *resolved_references)}
    for source in graph:
        text = source.read_text(encoding="utf-8")
        for raw_target in re.findall(r"\[[^\]]+\]\(([^)]+)\)", text):
            target = raw_target.split("#", 1)[0].strip()
            if not target or "://" in target or target.startswith("mailto:"):
                continue
            resolved = (source.parent / target).resolve()
            if resolved in resolved_references:
                graph[source].add(resolved)
    return graph


def reachable_references(entry: Path, graph: dict[Path, set[Path]]) -> set[Path]:
    pending = [entry.resolve()]
    seen: set[Path] = set()
    while pending:
        current = pending.pop()
        for target in graph[current]:
            if target in seen:
                continue
            seen.add(target)
            pending.append(target)
    return seen


def largest_reference_chain(
    entry: Path,
    graph: dict[Path, set[Path]],
    context_units: dict[Path, int],
) -> tuple[int, list[Path]]:
    """Measure the largest progressive-disclosure route; reject routing cycles."""
    resolved_entry = entry.resolve()
    visiting: set[Path] = set()
    cache: dict[Path, tuple[int, list[Path]]] = {}

    def visit(current: Path) -> tuple[int, list[Path]]:
        if current in visiting:
            raise ValueError(f"reference routing cycle reaches {current}")
        if current in cache:
            return cache[current]
        visiting.add(current)
        best_units = context_units[current]
        best_path = [current]
        for target in graph[current]:
            child_units, child_path = visit(target)
            candidate_units = context_units[current] + child_units
            if candidate_units > best_units:
                best_units = candidate_units
                best_path = [current, *child_path]
        visiting.remove(current)
        cache[current] = (best_units, best_path)
        return cache[current]

    return visit(resolved_entry)


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
        references_root = skill_root / "references"
        references = sorted(references_root.rglob("*.md"))
        reference_units: list[tuple[int, Path]] = []
        context_units = {(skill_root / "SKILL.md").resolve(): entry_units}
        for reference in references:
            reference_text = reference.read_text(encoding="utf-8")
            if len(reference_text) > MAX_REFERENCE_CHARS:
                fail(f"{reference} exceeds {MAX_REFERENCE_CHARS} characters")
            units = estimate_context_units(reference_text)
            if units > MAX_REFERENCE_CONTEXT_UNITS:
                fail(f"{reference} exceeds {MAX_REFERENCE_CONTEXT_UNITS} context units")
            relative = reference.relative_to(references_root).as_posix()
            if reference.parent == references_root and f"references/{relative}" not in text:
                fail(f"{reference} is not directly routed from its owner SKILL.md")
            if relative in seen_references:
                fail(f"reference has duplicate active owners: {relative}")
            seen_references[relative] = skill_name
            reference_units.append((units, reference))
            context_units[reference.resolve()] = units
        graph = reference_graph(skill_root, references)
        reachable = reachable_references(skill_root / "SKILL.md", graph)
        unresolved = sorted(
            (reference.resolve() for reference in references if reference.resolve() not in reachable),
            key=lambda path: path.as_posix(),
        )
        if unresolved:
            names = [path.relative_to(skill_root.resolve()).as_posix() for path in unresolved]
            fail(f"{skill_name} has references unreachable from SKILL.md: {names}")
        try:
            chain_units, chain = largest_reference_chain(
                skill_root / "SKILL.md", graph, context_units
            )
        except ValueError as exc:
            fail(f"{skill_name} has cyclic progressive reference routing: {exc}")
        if chain_units > MAX_REFERENCE_CHAIN_CONTEXT_UNITS:
            chain_names = [path.relative_to(skill_root.resolve()).as_posix() for path in chain]
            fail(
                f"{skill_name} progressive reference chain {chain_names} exceeds "
                f"{MAX_REFERENCE_CHAIN_CONTEXT_UNITS} context units"
            )
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
        ROOT / "GITHUB_PRODUCT_SURFACE.json",
        ROOT / "RELEASE_NOTES.md",
        ROOT / ".github/workflows/release.yml",
        ROOT / "scripts/bump_version.py",
        ROOT / "scripts/extract_release_notes.py",
        ROOT / "scripts/manage_github_product_surface.py",
        ROOT / "scripts/validate_distillation_batch.py",
        ROOT / "scripts/validate_distillation_evaluation.py",
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
    if "scripts/extract_release_notes.py" not in release_workflow or "--notes-file" not in release_workflow:
        fail("release workflow must publish the curated user release notes")
    if "scripts/manage_github_product_surface.py" not in release_workflow:
        fail("release workflow must validate the reviewed GitHub product surface")
    if "--generate-notes" in release_workflow:
        fail("release workflow must not replace curated user notes with generated commit notes")
    version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    try:
        extract_release_notes((ROOT / "RELEASE_NOTES.md").read_text(encoding="utf-8"), version)
    except (OSError, ReleaseNotesError) as exc:
        fail(f"current user release notes are invalid: {exc}")
    try:
        validate_local_surface(ROOT)
    except (OSError, ProductSurfaceError) as exc:
        fail(f"current GitHub product surface is invalid: {exc}")
    validation_workflow = (ROOT / ".github/workflows/validate.yml").read_text(encoding="utf-8")
    if "python3 scripts/validate_public_surface.py" not in validation_workflow:
        fail("validation workflow must validate the public source boundary")
    if "scripts/manage_github_product_surface.py" not in validation_workflow:
        fail("validation workflow must validate the reviewed GitHub product surface")


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
        candidates.extend(sorted((skill_root / "references").rglob("*.md")))
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


def strip_fenced_code_blocks(text: str) -> str:
    """Mask fenced code without changing the surrounding line structure."""

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


def find_matching_markdown_delimiter(
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


def parse_markdown_link_destination(content: str) -> str | None:
    content = content.strip()
    if not content:
        return None
    if content.startswith("<"):
        closing = content.find(">", 1)
        if closing < 0:
            return None
        destination = content[1:closing]
    else:
        escaped = False
        destination_characters: list[str] = []
        for character in content:
            if escaped:
                destination_characters.append(character)
                escaped = False
                continue
            if character == "\\":
                escaped = True
                continue
            if character.isspace():
                break
            destination_characters.append(character)
        destination = "".join(destination_characters)
    return destination.strip() or None


def extract_markdown_link_targets(text: str) -> list[str]:
    """Return inline Markdown link targets, excluding fenced examples."""

    visible = strip_fenced_code_blocks(text)
    targets: list[str] = []
    index = 0
    while index < len(visible):
        opening = visible.find("[", index)
        if opening < 0:
            break
        closing = find_matching_markdown_delimiter(visible, opening, "[", "]")
        if closing is None:
            break
        cursor = closing + 1
        while cursor < len(visible) and visible[cursor] in " \t":
            cursor += 1
        if cursor >= len(visible) or visible[cursor] != "(":
            index = closing + 1
            continue
        destination_end = find_matching_markdown_delimiter(
            visible, cursor, "(", ")"
        )
        if destination_end is None:
            index = cursor + 1
            continue
        target = parse_markdown_link_destination(
            visible[cursor + 1 : destination_end]
        )
        if target is not None:
            targets.append(target)
        index = destination_end + 1
    return targets


def local_markdown_target_error(
    source: Path, raw_target: str, authority_root: Path
) -> str | None:
    target = raw_target.strip()
    if (
        not target
        or target.startswith(("#", "//"))
        or re.match(r"^[A-Za-z][A-Za-z0-9+.-]*:", target)
    ):
        return None
    path_part = unquote(target.split("#", 1)[0].split("?", 1)[0]).strip()
    if not path_part:
        return None
    resolved = (source.parent / path_part).resolve()
    try:
        resolved.relative_to(authority_root.resolve())
    except ValueError:
        return f"local Markdown link escapes the authority root: {raw_target}"
    if not resolved.exists():
        return f"broken local Markdown link: {raw_target}"
    return None


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
        for raw_target in extract_markdown_link_targets(text):
            error = local_markdown_target_error(path, raw_target, ROOT)
            if error is not None:
                fail(f"{error} in {path.relative_to(ROOT)}")


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
        f"two-route<={MAX_TWO_REFERENCE_ROUTE_CONTEXT_UNITS}, "
        f"reference-chain<={MAX_REFERENCE_CHAIN_CONTEXT_UNITS}"
    )
    print("[OK] Senmu BuildOS product identity is clean")
    print("[OK] Codex and Claude Code plugin structures and eight Skill entrypoints are valid")
    print("[OK] VERSION, plugin manifests, and marketplace release metadata agree")
    print(
        f"[OK] active references: {len(REFERENCE_OWNERS)}/{len(REFERENCE_OWNERS)} "
        "files have one owner and an acyclic route from SKILL.md"
    )
    print("[OK] no exact duplicate active Skill resources found")
    print("[OK] no duplicated long instruction paragraphs found across active Skills")
    print("[OK] behavior invariant identifiers are unique")
    print("[OK] active local Markdown links resolve")
    print(f"[OK] project AGENTS delta layer <= {MAX_PROJECT_AGENTS_TEMPLATE_CHARS} characters and has one template owner")
    print("[OK] public package validation is independent from private project-state owners")


if __name__ == "__main__":
    main()
