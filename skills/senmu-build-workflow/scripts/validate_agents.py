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
PLACEHOLDER = re.compile(r"<待确认(?:或不适用)?>|<[^>\n]{1,100}>")
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


def metadata_value(text: str, label: str) -> str | None:
    match = re.search(
        rf"^>\s*{re.escape(label)}[：:]\s*`?([^`\n]+?)`?\s*$",
        text,
        re.MULTILINE,
    )
    return match.group(1).strip() if match else None


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
        actual_key = metadata_value(text, "Agent Key")
        actual_version = metadata_value(text, "Agent Version")
        actual_status = metadata_value(text, "状态")
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
        for heading in REQUIRED_HEADINGS:
            if heading not in text:
                errors.append(f"Agent 定义缺少核心章节：{record.key} {heading}")
        if strict:
            placeholder = PLACEHOLDER.search(text)
            if placeholder:
                errors.append(
                    f"Agent 定义仍有未校准占位符：{record.definition_path}: {placeholder.group(0)}"
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
