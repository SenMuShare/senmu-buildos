import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "skills/senmu-build-product/scripts/check_requirement_structure.py"
spec = importlib.util.spec_from_file_location("requirement_structure", SCRIPT)
assert spec and spec.loader
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)


def feature(name="FUN-001 Export", version="V1.2.3"):
    return f"""## {name}
需求对应版本号：`{version}`
### 1. 需求描述
用户需要取得已有结果，避免逐个下载。
### 2. 功能描述
为项目成员提供批量导出。
### 3. 功能逻辑
校验权限和完成状态；只导出已完成内容，失败保留原始数据。
### 4. 前端交互描述
未选择时禁用导出；失败提示“导出失败，请重试”，保留选择并允许重试。
"""


class RequirementStructureTests(unittest.TestCase):
    def test_each_of_multiple_features_has_its_own_sections(self):
        result = checker.check(feature() + feature("FUN-002 Download"))
        self.assertEqual(result["status"], "pass", result)
        self.assertEqual(result["features"], 2)

    def test_small_change_keeps_four_short_sections(self):
        self.assertEqual(checker.check(feature())["status"], "pass")

    def test_backend_only_keeps_explained_fourth_section_without_assets(self):
        text = feature("CAP-001 Cleanup").replace(
            "未选择时禁用导出；失败提示“导出失败，请重试”，保留选择并允许重试。",
            "不涉及前端交互：此功能仅由后台定时任务触发，结果写入运行记录。")
        self.assertEqual(checker.check(text)["status"], "pass")

    def test_late_addition_missing_section_fails(self):
        later = feature("FUN-002 Added").split("### 4. 前端交互描述")[0]
        self.assertEqual(checker.check(feature() + later)["status"], "fail")

    def test_each_feature_needs_version_not_only_document_header(self):
        second = feature("FUN-002 Added").replace("需求对应版本号：`V1.2.3`\n", "")
        self.assertEqual(checker.check(feature() + second)["status"], "fail")

    def test_extra_fifth_section_or_renamed_section_fails(self):
        for text in (feature() + "### 5. 附图\n一个附件。\n",
                     feature().replace("### 3. 功能逻辑", "### 3. 技术方案")):
            with self.subTest(text=text):
                self.assertEqual(checker.check(text)["status"], "fail")

    def test_out_of_order_and_duplicate_sections_fail(self):
        for text in (feature().replace("### 1. 需求描述", "### 2. 功能描述"),
                     feature().replace("### 3. 功能逻辑", "### 1. 需求描述")):
            self.assertEqual(checker.check(text)["status"], "fail")

    def test_empty_section_cannot_pass_with_only_comments(self):
        text = feature().replace("为项目成员提供批量导出。", "<!-- 填写能力 -->")
        self.assertEqual(checker.check(text)["status"], "fail")

    def test_commented_or_fenced_examples_are_not_features(self):
        for text in (f"<!--\n{feature()}\n-->", f"```markdown\n{feature()}\n```"):
            self.assertEqual(checker.check(text)["features"], 0)
            self.assertEqual(checker.check(text)["status"], "fail")

    def test_unknown_version_is_explicitly_draft_only(self):
        for version in ("待确认", "{{VERSION}}", "Vx.x.x", "TBD"):
            text = feature(version=version)
            self.assertEqual(checker.check(text)["status"], "fail")
            self.assertEqual(checker.check(text, draft=True)["status"], "pass")

    def test_asset_subsection_stays_inside_fourth_section(self):
        text = feature() + "#### 关联原型／UI 设计稿\n采用状态：部分采用；采用布局，不采用示例文案。\n"
        self.assertEqual(checker.check(text)["status"], "pass")
        self.assertEqual(checker.check(text)["scope"], "structure_only")

    def test_named_feature_without_id_is_supported(self):
        self.assertEqual(checker.check(feature("批量导出"))["status"], "pass")

    def test_named_feature_with_version_cannot_hide_missing_sections(self):
        for suffix in ("", "### 技术方案\n导出结果。\n"):
            for draft in (False, True):
                with self.subTest(suffix=suffix, draft=draft):
                    text = feature() + "## 批量下载\n需求对应版本号：V1.2.3\n" + suffix
                    result = checker.check(text, draft=draft)
                    self.assertEqual(result["status"], "fail", result)
                    self.assertEqual(result["features"], 2)
                    self.assertTrue(any("批量下载: require exactly four" in e for e in result["errors"]))

    def test_additional_unresolved_versions_are_draft_only(self):
        for version in ("<VERSION>", "${VERSION}", "待规划", "未排期"):
            with self.subTest(version=version):
                self.assertEqual(checker.check(feature(version=version))["status"], "fail")
                self.assertEqual(checker.check(feature(version=version), draft=True)["status"], "pass")

    def test_empty_list_skeletons_are_not_section_content(self):
        for body in ("1.", "2)", "- [ ]", "* [x]", "+", "> 1. - [ ]", "1.\n- [ ]\n*", "- <!-- explanation -->"):
            for draft in (False, True):
                with self.subTest(body=body, draft=draft):
                    text = feature().replace("为项目成员提供批量导出。", body)
                    result = checker.check(text, draft=draft)
                    self.assertEqual(result["status"], "fail", result)
                    self.assertTrue(any("2. 功能描述 has no content" in e for e in result["errors"]))

    def test_substantive_lists_and_project_versions_remain_supported(self):
        for body in ("1. 导出结果。", "- [ ] 导出结果。", "> 1. 导出结果。", "42", "1.\n- [ ] 导出结果。"):
            for version in ("V1.2.3", "2026.09", "Release Phoenix", "v2.0.0-rc.1"):
                with self.subTest(body=body, version=version):
                    text = feature(version=version).replace("为项目成员提供批量导出。", body)
                    self.assertEqual(checker.check(text)["status"], "pass")

    def test_parent_and_sections_do_not_inherit_feature_version(self):
        text = "# 版本需求\n概述。\n" + feature("批量导出")
        result = checker.check(text)
        self.assertEqual(result["status"], "pass", result)
        self.assertEqual(result["features"], 1)

    def test_cli_rejects_all_three_regressions_without_writing(self):
        cases = (
            feature() + "## 命名功能\n需求对应版本号：V2.24.1\n",
            feature(version="<VERSION>"),
            feature().replace("为项目成员提供批量导出。", "1.\n- [ ]"),
        )
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory, "PRD.md")
            for text in cases:
                with self.subTest(text=text):
                    path.write_text(text, encoding="utf-8")
                    before = path.read_bytes()
                    result = subprocess.run([sys.executable, str(SCRIPT), "--document", str(path)],
                                            capture_output=True, text=True, check=False, timeout=15)
                    self.assertEqual(result.returncode, 1)
                    self.assertEqual(json.loads(result.stdout)["status"], "fail")
                    self.assertEqual(path.read_bytes(), before)

    def test_draft_cli_allows_placeholder_but_not_missing_structure(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory, "PRD.md")
            for text, expected in ((feature(version="${VERSION}"), 0),
                                   (feature(version="待规划").replace("为项目成员提供批量导出。", "- [X]"), 1)):
                path.write_text(text, encoding="utf-8")
                result = subprocess.run([sys.executable, str(SCRIPT), "--document", str(path), "--draft"],
                                        capture_output=True, text=True, timeout=15)
                self.assertEqual(result.returncode, expected, result.stdout)

    def test_versioned_examples_do_not_create_false_features(self):
        text = "## 命名示例\n需求对应版本号：<VERSION>\n"
        for wrapper in ("<!--\n{}\n-->", "```markdown\n{}\n```", "~~~markdown\n{}\n~~~"):
            result = checker.check(feature("正常功能") + wrapper.format(text))
            self.assertEqual(result["status"], "pass", result)
            self.assertEqual(result["features"], 1)

    def test_nested_empty_markers_fail_but_real_quoted_content_passes(self):
        for body in ("> > 12) - [X]", "  + [ ]  ", "[x]", "- [ ] ** **", "> 1)\n> - [ ]"):
            self.assertEqual(checker.check(feature().replace("为项目成员提供批量导出。", body))["status"], "fail", body)
        for body in ("> > 12) - [X] 实际内容", "0", "- [ ] 0", "1. 实际内容\n2."):
            self.assertEqual(checker.check(feature().replace("为项目成员提供批量导出。", body))["status"], "pass", body)

    def test_cli_reports_missing_input_as_json(self):
        with tempfile.TemporaryDirectory() as directory:
            result = subprocess.run([sys.executable, str(SCRIPT), "--document", str(Path(directory, "missing.md"))],
                                    capture_output=True, text=True, check=False)
        self.assertEqual(result.returncode, 1)
        self.assertEqual(json.loads(result.stdout)["status"], "fail")

    def test_cli_checks_real_markdown_without_writing_it(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory, "PRD.md")
            path.write_text(feature(), encoding="utf-8")
            before = path.read_bytes()
            result = subprocess.run([sys.executable, str(SCRIPT), "--document", str(path)],
                                    capture_output=True, text=True, check=False)
            self.assertEqual(before, path.read_bytes())
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertEqual(json.loads(result.stdout)["features"], 1)


if __name__ == "__main__":
    unittest.main()
