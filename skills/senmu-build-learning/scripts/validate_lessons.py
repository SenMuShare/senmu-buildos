#!/usr/bin/env python3
"""Validate a Markdown Lessons Learned Register without third-party dependencies."""

from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from pathlib import Path


ENTRY = re.compile(r"^###\s+(LES-\d{8}-\d{3})：(.+?)\s*$", re.MULTILINE)
FIELD = re.compile(r"^-\s+([^：:\n]+)[：:]\s*(.*?)\s*$", re.MULTILINE)
VALID_STATUSES = {"candidate", "active", "superseded", "retired"}
VALID_TYPES = {"incident", "practice", "governance"}
REQUIRED_FIELDS = {
    "状态",
    "类型",
    "检索标签",
    "适用范围",
    "触发信号",
    "症状／错误",
    "已确认根因",
    "源头治理动作",
    "必须",
    "禁止",
    "剩余风险",
    "自动检测／门禁",
    "门禁成本与退役条件",
    "修复与验证证据",
    "权威规则落点",
    "来源工作日志",
    "负责人／最后复核",
    "替代关系",
}
ACTIVE_CONCRETE_FIELDS = {
    "检索标签",
    "适用范围",
    "触发信号",
    "已确认根因",
    "源头治理动作",
    "必须",
    "禁止",
    "修复与验证证据",
    "权威规则落点",
    "负责人／最后复核",
}
PLACEHOLDER = re.compile(r"<[^>]+>|\b(?:TBD|TODO|UNKNOWN)\b|待确认|待补充|未知", re.IGNORECASE)
ABSOLUTE_PRIVATE_PATH = re.compile(r"(?:/Users/[^/\s]+|/home/[^/\s]+|[A-Za-z]:\\Users\\[^\\\s]+)")
SECRET_VALUE = re.compile(
    r"(?i)\b(?:api[_-]?key|access[_-]?token|secret|password|passwd)\b\s*[:=]\s*[`'\"]?([A-Za-z0-9_./+=-]{10,})"
)


@dataclass(frozen=True)
class Lesson:
    lesson_id: str
    title: str
    fields: dict[str, str]
    body: str


def clean_value(value: str) -> str:
    return value.strip().strip("`").strip()


def is_concrete(value: str) -> bool:
    cleaned = clean_value(value)
    return bool(cleaned) and not PLACEHOLDER.search(cleaned)


def normalize(value: str) -> str:
    return re.sub(r"[^a-z0-9\u4e00-\u9fff]+", "", value.lower())


def parse_lessons(text: str) -> list[Lesson]:
    matches = list(ENTRY.finditer(text))
    lessons: list[Lesson] = []
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        body = text[match.end():end]
        fields = {name.strip(): clean_value(value) for name, value in FIELD.findall(body)}
        lessons.append(Lesson(match.group(1), match.group(2).strip(), fields, body))
    return lessons


def validate(text: str) -> tuple[list[str], list[str], int]:
    errors: list[str] = []
    warnings: list[str] = []
    lessons = parse_lessons(text)
    by_id: dict[str, Lesson] = {}

    for lesson in lessons:
        if lesson.lesson_id in by_id:
            errors.append(f"经验 ID 重复：{lesson.lesson_id}")
        else:
            by_id[lesson.lesson_id] = lesson

    for lesson in lessons:
        prefix = lesson.lesson_id
        missing = sorted(REQUIRED_FIELDS - set(lesson.fields))
        if missing:
            errors.append(f"{prefix} 缺少字段：{', '.join(missing)}")

        status = lesson.fields.get("状态", "")
        lesson_type = lesson.fields.get("类型", "")
        if status not in VALID_STATUSES:
            errors.append(f"{prefix} 状态无效：{status or '<空>'}")
        if lesson_type not in VALID_TYPES:
            errors.append(f"{prefix} 类型无效：{lesson_type or '<空>'}")

        if status == "active":
            incomplete = sorted(
                field for field in ACTIVE_CONCRETE_FIELDS
                if not is_concrete(lesson.fields.get(field, ""))
            )
            if incomplete:
                errors.append(f"{prefix} active 条目缺少可执行事实：{', '.join(incomplete)}")
        elif status == "candidate":
            incomplete = sorted(
                field for field in ("检索标签", "适用范围", "触发信号", "来源工作日志")
                if not is_concrete(lesson.fields.get(field, ""))
            )
            if incomplete:
                warnings.append(f"{prefix} candidate 条目不易检索或追溯：{', '.join(incomplete)}")

        relation = lesson.fields.get("替代关系", "")
        if status == "superseded":
            targets = [candidate for candidate in re.findall(r"LES-\d{8}-\d{3}", relation) if candidate != prefix]
            if not targets:
                errors.append(f"{prefix} superseded 条目必须指向替代经验")
            for target in targets:
                if target not in by_id:
                    errors.append(f"{prefix} 指向不存在的替代经验：{target}")
        if status == "retired":
            for field in ("门禁成本与退役条件", "负责人／最后复核"):
                if not is_concrete(lesson.fields.get(field, "")):
                    errors.append(f"{prefix} retired 条目缺少退出依据：{field}")

        if ABSOLUTE_PRIVATE_PATH.search(lesson.body):
            warnings.append(f"{prefix} 可能包含个人绝对路径，请确认是否应脱敏")
        if SECRET_VALUE.search(lesson.body):
            warnings.append(f"{prefix} 可能包含密钥或口令值，请立即核对")

    seen_titles: dict[str, str] = {}
    seen_causes: dict[str, str] = {}
    for lesson in lessons:
        title_key = normalize(lesson.title)
        if title_key and title_key in seen_titles:
            warnings.append(f"疑似重复标题：{seen_titles[title_key]} 与 {lesson.lesson_id}")
        elif title_key:
            seen_titles[title_key] = lesson.lesson_id

        cause = lesson.fields.get("已确认根因", "")
        cause_key = normalize(cause) if is_concrete(cause) else ""
        if cause_key and cause_key in seen_causes:
            warnings.append(f"疑似重复根因：{seen_causes[cause_key]} 与 {lesson.lesson_id}")
        elif cause_key:
            seen_causes[cause_key] = lesson.lesson_id

    return errors, warnings, len(lessons)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("register", type=Path, help="Lessons Learned Register Markdown path")
    args = parser.parse_args()
    if not args.register.is_file():
        raise SystemExit(f"[ERROR] 经验台账不存在：{args.register}")

    errors, warnings, count = validate(args.register.read_text(encoding="utf-8"))
    for warning in warnings:
        print(f"[WARNING] {warning}")
    for error in errors:
        print(f"[ERROR] {error}")
    if errors:
        raise SystemExit(1)
    print(f"[OK] 经验台账校验通过：{count} 条；{len(warnings)} 个警告")


if __name__ == "__main__":
    main()
