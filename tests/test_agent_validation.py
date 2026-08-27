import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
VALIDATOR = ROOT / "skills/senmu-build-workflow/scripts/validate_agents.py"
HEADINGS = (
    "角色定义",
    "使命与目标",
    "职责范围",
    "任务与成功标准",
    "输入契约",
    "输出契约",
    "工具与调用规则",
    "标准工作流与决策规则",
    "约束与禁止事项",
    "质量门禁与验收",
    "异常处理与移交",
    "版本、审计与接力",
)


def agent_definition(key: str = "review-agent", version: str = "1.2.0", status: str = "active") -> str:
    sections = "\n\n".join(f"## {heading}\n\n已校准内容。" for heading in HEADINGS)
    return (
        "# Review Agent\n\n"
        f"> Agent Key：`{key}`  \n"
        f"> Agent Version：`{version}`  \n"
        f"> 状态：`{status}`\n\n"
        f"{sections}\n"
    )


def register(key: str = "review-agent", version: str = "1.2.0", status: str = "active") -> str:
    return (
        "# Agent Register\n\n"
        "| Agent Key | Agent 名称 | Agent Version | 状态 | 定义路径 | Owner | 关联 Workflow／Harness |\n"
        "| --- | --- | --- | --- | --- | --- | --- |\n"
        f"| `{key}` | Review Agent | `{version}` | `{status}` | `agents/{key}/AGENT.md` | Team | `workflow` |\n"
    )


class AgentValidationTests(unittest.TestCase):
    def run_validator(self, root: Path, *extra: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["python3", str(VALIDATOR), "--root", str(root), *extra],
            check=False,
            capture_output=True,
            text=True,
        )

    def create_valid_project(self, root: Path) -> Path:
        definition = root / "agents/review-agent/AGENT.md"
        definition.parent.mkdir(parents=True)
        definition.write_text(agent_definition(), encoding="utf-8")
        (root / "agents/AGENT_REGISTER.md").write_text(register(), encoding="utf-8")
        return definition

    def test_strict_validation_accepts_registered_agent_contract(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_root:
            root = Path(temporary_root)
            self.create_valid_project(root)
            result = self.run_validator(root, "--strict")
            self.assertEqual(result.returncode, 0, result.stderr or result.stdout)
            self.assertIn("1 个 Agent", result.stdout)

    def test_validation_rejects_register_and_definition_mismatch(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_root:
            root = Path(temporary_root)
            definition = self.create_valid_project(root)
            definition.write_text(
                agent_definition(version="2.0.0").replace("## 输出契约", "## 已删除的输出契约"),
                encoding="utf-8",
            )
            result = self.run_validator(root)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Agent Version 与登记表不一致", result.stdout)
            self.assertIn("Agent 定义缺少核心章节", result.stdout)

    def test_validation_rejects_unregistered_agent_directory(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_root:
            root = Path(temporary_root)
            self.create_valid_project(root)
            orphan = root / "agents/orphan-agent"
            orphan.mkdir()
            (orphan / "AGENT.md").write_text(agent_definition(key="orphan-agent"), encoding="utf-8")
            result = self.run_validator(root)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Agent 目录未登记", result.stdout)


if __name__ == "__main__":
    unittest.main()
