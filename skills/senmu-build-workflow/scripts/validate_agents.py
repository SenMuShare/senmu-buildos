#!/usr/bin/env python3
"""Validate project-local Agent definitions without third-party dependencies."""

from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from pathlib import Path


DEFAULT_DIRECTORY = Path("agents")
DEFAULT_REGISTER = Path("agents/AGENT_REGISTER.md")
AGENT_KEY = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
SEMVER = re.compile(
    r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)"
    r"(?:-[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?"
    r"(?:\+[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?$"
)
VALID_STATUSES = {"draft", "active", "deprecated", "retired"}
# Explicit authoring slots, not arbitrary XML/HTML tags or runtime variables.
# Named legacy starter slots remain readable; new starters use BUILDOS_TODO.
PLACEHOLDER = re.compile(
    r"\[\[BUILDOS_TODO:[^\]\r\n]*\]\]|<待确认(?:或不适用)?>|"
    r"<(?:confirm|unconfirmed|TBD|TODO|Agent name|agent-key|confirmed owner|"
    r"confirmed scope|existing entrypoint or not applicable)>",
    re.IGNORECASE,
)


def unresolved_placeholder(text: str) -> str | None:
    """Find declared slots, including examples, without treating paired markup as slots.

    This is deliberately not an XML validator or a semantic completeness check.
    """
    paired: set[int] = set()
    stacks: dict[str, list[int]] = {}
    tags = re.finditer(r"<(/?)([A-Za-z_][\w.:-]*)(?:\s+[^<>]*?)?(/?)>", text)
    for tag in tags:
        closing, name, self_closing = tag.groups()
        if self_closing:
            continue
        stack = stacks.setdefault(name, [])
        if closing:
            if stack:
                paired.add(stack.pop())
        else:
            stack.append(tag.start())
    for match in PLACEHOLDER.finditer(text):
        if match.group(0).startswith("<") and match.start() in paired:
            continue
        return match.group(0)
    return None

REQUIRED_HEADINGS = (
    "## 角色定义",
    "## 使命与目标",
    "## 职责范围",
    "## 任务与成功标准",
    "## 输入契约",
    "## 输出契约",
    "## 工具与调用规则",
    "## 标准工作流与决策规则",
    "## 约束与禁止事项",
    "## 质量门禁与验收",
    "## 异常处理与移交",
    "## 版本、审计与接力",
)

# Existing Chinese definitions remain valid. These English names are the default
# source outline; stable markers support any translated or deliberately merged headings.
SECTION_IDS = (
    "role", "mission", "scope", "tasks", "input", "output", "tools",
    "workflow", "constraints", "quality", "exceptions", "continuity",
)
ENGLISH_HEADINGS = (
    "Role", "Mission and Outcome", "Scope", "Tasks and Success",
    "Input Contract", "Output Contract", "Tools and Invocation",
    "Workflow and Decisions", "Constraints", "Quality and Acceptance",
    "Exceptions and Handoff", "Version and Continuity",
)
SECTION_ALIASES = {
    label.casefold(): key
    for key, english, chinese in zip(SECTION_IDS, ENGLISH_HEADINGS, REQUIRED_HEADINGS)
    for label in (english, chinese.removeprefix("## "))
}
SECTION_MARKER = re.compile(r"^\s*<!--\s*agent-section:\s*([a-z-]+)\s*-->\s*$")


def instruction_text(text: str) -> str:
    """Exclude fenced examples from structural and metadata interpretation."""
    visible: list[str] = []
    fence: str | None = None
    length = 0
    for line in text.splitlines():
        match = re.match(r"^\s{0,3}(`{3,}|~{3,})", line)
        if match:
            token = match.group(1)
            if fence is None:
                fence, length = token[0], len(token)
                visible.append("")
                continue
            if token[0] == fence and len(token) >= length and not line[match.end():].strip():
                fence = None
                visible.append("")
                continue
        visible.append(line if fence is None else "")
    return "\n".join(visible)


def definition_sections(text: str) -> tuple[set[str], list[str]]:
    """Check discoverable section roles, not natural-language business correctness."""
    found: dict[str, int] = {}
    errors: list[str] = []
    section: int | None = None
    for number, line in enumerate(instruction_text(text).splitlines(), start=1):
        heading = re.match(r"^##\s+(.+?)\s*#*\s*$", line)
        keys: list[str] = []
        if heading:
            section = number
            alias = SECTION_ALIASES.get(heading.group(1).strip().casefold())
            if alias:
                keys.append(alias)
        marker = SECTION_MARKER.fullmatch(line)
        if marker:
            key = marker.group(1)
            if key not in SECTION_IDS:
                errors.append(f"Unknown agent section marker: {key}")
            elif section is None:
                errors.append(f"Agent section marker has no section heading: {key}")
            else:
                keys.append(key)
        for key in keys:
            if key in found and found[key] != section:
                errors.append(f"Duplicate agent section role: {key}")
            else:
                assert section is not None
                found[key] = section
    return set(found), errors


@dataclass(frozen=True)
class AgentRecord:
    key: str
    name: str
    version: str
    status: str
    definition_path: str


def clean_cell(raw: str) -> str:
    value = raw.strip()
    if value.startswith("`") and value.endswith("`") and len(value) >= 2:
        value = value[1:-1].strip()
    link = re.fullmatch(r"\[[^\]]+\]\(([^)]+)\)", value)
    return link.group(1).strip() if link else value


def parse_register(path: Path) -> tuple[list[AgentRecord], list[str]]:
    errors: list[str] = []
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    header_index = next(
        (index for index, line in enumerate(lines) if line.strip().startswith("| Agent Key |")),
        None,
    )
    if header_index is None:
        return [], ["Agent Register 缺少以 Agent Key 开头的登记表"]
    if header_index + 1 >= len(lines) or "---" not in lines[header_index + 1]:
        return [], ["Agent Register 登记表缺少 Markdown 分隔行"]

    records: list[AgentRecord] = []
    for line in lines[header_index + 2 :]:
        if not line.strip().startswith("|"):
            break
        cells = [clean_cell(cell) for cell in line.strip().strip("|").split("|")]
        if not any(cells):
            continue
        if len(cells) < 7:
            errors.append(f"Agent Register 行字段不足：{line.strip()}")
            continue
        records.append(
            AgentRecord(
                key=cells[0],
                name=cells[1],
                version=cells[2],
                status=cells[3],
                definition_path=cells[4],
            )
        )
    return records, errors


def metadata_values(text: str, label: str) -> list[str]:
    """Read every declared value without consuming the following line when empty."""
    matches = re.finditer(
        rf"^>[ \t]*{re.escape(label)}[：:][ \t]*([^\n]*)$",
        text, re.MULTILINE,
    )
    return [match.group(1).strip().strip("`").strip() for match in matches]


def metadata_value(text: str, label: str) -> str | None:
    """Compatibility helper: return only a unique, non-empty field value."""
    values = set(metadata_values(text, label))
    return next(iter(values)) if len(values) == 1 and "" not in values else None


def unique_metadata(text: str, labels: tuple[str, ...]) -> tuple[str | None, str | None]:
    values = {value for label in labels for value in metadata_values(text, label)}
    if len(values) > 1:
        return None, f"Conflicting {labels[0]} metadata"
    if "" in values:
        return None, f"Empty {labels[0]} metadata"
    # Repeated identical declarations/legacy aliases are unambiguous and accepted.
    return (next(iter(values)) if values else None), None


def within(root: Path, target: Path) -> bool:
    try:
        target.resolve().relative_to(root.resolve())
    except ValueError:
        return False
    return True


def validate(root: Path, directory: Path, register: Path, strict: bool) -> list[str]:
    errors: list[str] = []
    root = root.resolve()
    agents_root = (root / directory).resolve()
    register_path = (root / register).resolve()

    if not within(root, agents_root) or not within(root, register_path):
        return ["Agent 目录或登记表越出项目根"]
    if not agents_root.is_dir():
        return [f"缺少 Agent 目录：{directory}"]
    if not register_path.is_file():
        return [f"缺少 Agent Register：{register}"]

    records, register_errors = parse_register(register_path)
    errors.extend(register_errors)
    if strict and not records:
        errors.append("严格校验要求 Agent Register 至少登记一个 Agent")

    seen: set[str] = set()
    expected_paths: dict[str, Path] = {}
    directory_prefix = directory.as_posix().rstrip("/")
    for record in records:
        if record.key in seen:
            errors.append(f"Agent Key 重复：{record.key}")
            continue
        seen.add(record.key)
        if not AGENT_KEY.fullmatch(record.key):
            errors.append(f"Agent Key 必须使用小写 kebab-case：{record.key}")
        if not SEMVER.fullmatch(record.version):
            errors.append(f"Agent Version 不是 SemVer：{record.key}={record.version}")
        if record.status not in VALID_STATUSES:
            errors.append(f"Agent 状态无效：{record.key}={record.status}")

        expected_rel = f"{directory_prefix}/{record.key}/AGENT.md"
        if record.definition_path != expected_rel:
            errors.append(
                f"Agent 定义路径必须为 {expected_rel}：{record.key}={record.definition_path}"
            )
        definition = (root / record.definition_path).resolve()
        expected_paths[record.key] = definition
        if not within(root, definition):
            errors.append(f"Agent 定义路径越出项目根：{record.definition_path}")
            continue
        if not definition.is_file():
            errors.append(f"Agent 定义不存在：{record.definition_path}")
            continue

        text = definition.read_text(encoding="utf-8")
        visible = instruction_text(text)
        actual_key, key_error = unique_metadata(visible, ("Agent Key",))
        actual_version, version_error = unique_metadata(visible, ("Agent Version",))
        actual_status, status_error = unique_metadata(visible, ("Status", "状态"))
        for error in (key_error, version_error, status_error):
            if error:
                errors.append(f"{error}: {record.key}")
        if actual_key != record.key:
            errors.append(f"Agent Key 与目录／登记表不一致：{record.key} != {actual_key}")
        if actual_version != record.version:
            errors.append(
                f"Agent Version 与登记表不一致：{record.key} {record.version} != {actual_version}"
            )
        if actual_status != record.status:
            errors.append(
                f"Agent 状态与登记表不一致：{record.key} {record.status} != {actual_status}"
            )
        sections, section_errors = definition_sections(text)
        errors.extend(f"{record.key}: {error}" for error in section_errors)
        for key in SECTION_IDS:
            if key not in sections:
                errors.append(f"Agent 定义缺少核心章节：{record.key} {key}")
        if strict:
            # Check explicit slots in the full source, including fenced examples.
            placeholder = unresolved_placeholder(text)
            if placeholder:
                errors.append(
                    f"Agent 定义仍有未校准占位符：{record.definition_path}: {placeholder}"
                )

    for child in sorted(agents_root.iterdir()):
        if child.name.startswith(".") or not child.is_dir():
            continue
        if not AGENT_KEY.fullmatch(child.name):
            errors.append(f"Agent 目录命名无效：{child.relative_to(root)}")
            continue
        if child.name not in seen:
            errors.append(f"Agent 目录未登记：{child.relative_to(root)}")
        elif expected_paths.get(child.name) != (child / "AGENT.md").resolve():
            errors.append(f"Agent 目录与登记路径不一致：{child.relative_to(root)}")
    return errors


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--directory", type=Path, default=DEFAULT_DIRECTORY)
    parser.add_argument("--register", type=Path, default=DEFAULT_REGISTER)
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()
    errors = validate(args.root, args.directory, args.register, args.strict)
    if errors:
        for error in errors:
            print(f"[ERROR] {error}")
        raise SystemExit(1)
    mode = "严格" if args.strict else "结构"
    records, _ = parse_register((args.root.resolve() / args.register).resolve())
    print(f"[OK] Agent 定义{mode}校验通过：{len(records)} 个 Agent")


if __name__ == "__main__":
    main()
