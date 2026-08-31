import unittest

from scripts.extract_release_notes import ReleaseNotesError, extract_release_notes


NOTES = """# 用户更新日志

## [2.0.0] - 2026-08-31

### 主要更新

- 新增更清楚的项目入口。

### 修复问题

- 修复普通任务重复读取资料的问题。

## [1.0.0] - 2026-08-30

### 主要更新

- 首次发布。

### 修复问题

- 修复安装说明缺失的问题。
"""


class ReleaseNotesTests(unittest.TestCase):
    def test_extracts_only_the_requested_user_sections(self) -> None:
        body = extract_release_notes(NOTES, "2.0.0")
        self.assertEqual(
            body,
            "## 主要更新\n\n- 新增更清楚的项目入口。\n\n"
            "## 修复问题\n\n- 修复普通任务重复读取资料的问题。\n",
        )
        self.assertNotIn("1.0.0", body)

    def test_rejects_missing_version(self) -> None:
        with self.assertRaisesRegex(ReleaseNotesError, "no section"):
            extract_release_notes(NOTES, "3.0.0")

    def test_rejects_missing_required_section(self) -> None:
        incomplete = """## [2.0.0]\n\n### 主要更新\n\n- 一项更新。\n"""
        with self.assertRaisesRegex(ReleaseNotesError, "主要更新 and 修复问题"):
            extract_release_notes(incomplete, "2.0.0")

    def test_rejects_empty_section(self) -> None:
        empty = """## [2.0.0]\n\n### 主要更新\n\n### 修复问题\n\n- 一项修复。\n"""
        with self.assertRaisesRegex(ReleaseNotesError, "主要更新 must contain"):
            extract_release_notes(empty, "2.0.0")


if __name__ == "__main__":
    unittest.main()
