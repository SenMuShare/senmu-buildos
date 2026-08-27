import subprocess
import tempfile
import textwrap
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
VALIDATOR = ROOT / "skills/senmu-build-learning/scripts/validate_lessons.py"
TEMPLATE = ROOT / "skills/senmu-build-learning/assets/learning-governance/LESSONS_LEARNED.template.md"


def lesson(lesson_id: str, title: str, status: str = "active", relation: str = "无", evidence: str = "commit abc123；测试通过") -> str:
    return textwrap.dedent(
        f"""
        ### {lesson_id}：{title}

        - 状态：`{status}`
        - 类型：`incident`
        - 检索标签：`release, docker`
        - 适用范围：`release pipeline`
        - 触发信号：`准备发布镜像`
        - 症状／错误：`旧镜像持续累积`
        - 已确认根因：`发布入口没有执行项目级保留策略`
        - 源头治理动作：`统一发布入口执行精确清理`
        - 必须：`保留 current 和 previous`
        - 禁止：`不得全局 prune`
        - 剩余风险：`Pin 版本需人工确认`
        - 自动检测／门禁：`运行保留策略契约测试`
        - 门禁成本与退役条件：`低成本；发布平台原生支持后复核`
        - 修复与验证证据：`{evidence}`
        - 权威规则落点：`operations/DEPLOYMENT.md`
        - 来源工作日志：`governance/logs/WORKLOG.md#2026-08-25`
        - 负责人／最后复核：`owner, 2026-08-25`
        - 替代关系：`{relation}`
        """
    )


class LessonsValidationTests(unittest.TestCase):
    def validate(self, content: str) -> subprocess.CompletedProcess[str]:
        with tempfile.TemporaryDirectory() as temporary_root:
            path = Path(temporary_root) / "LESSONS_LEARNED.md"
            path.write_text(content, encoding="utf-8")
            return subprocess.run(
                ["python3", str(VALIDATOR), str(path)],
                check=False,
                capture_output=True,
                text=True,
            )

    def test_empty_template_is_valid(self) -> None:
        result = self.validate(TEMPLATE.read_text(encoding="utf-8"))
        self.assertEqual(result.returncode, 0, result.stdout or result.stderr)
        self.assertIn("0 条", result.stdout)

    def test_valid_active_lesson_passes(self) -> None:
        result = self.validate(lesson("LES-20260825-001", "发布镜像保留策略"))
        self.assertEqual(result.returncode, 0, result.stdout or result.stderr)
        self.assertIn("1 条", result.stdout)

    def test_active_lesson_without_evidence_fails(self) -> None:
        result = self.validate(lesson("LES-20260825-001", "发布镜像保留策略", evidence="<待确认>"))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("修复与验证证据", result.stdout)

    def test_superseded_lesson_requires_existing_target(self) -> None:
        result = self.validate(
            lesson("LES-20260825-001", "旧发布规则", status="superseded", relation="superseded_by: LES-20260825-999")
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("指向不存在的替代经验", result.stdout)

    def test_duplicate_title_is_warning_not_error(self) -> None:
        result = self.validate(
            lesson("LES-20260825-001", "发布镜像保留策略")
            + lesson("LES-20260825-002", "发布镜像保留策略", evidence="commit def456；测试通过")
        )
        self.assertEqual(result.returncode, 0, result.stdout or result.stderr)
        self.assertIn("疑似重复标题", result.stdout)


if __name__ == "__main__":
    unittest.main()
