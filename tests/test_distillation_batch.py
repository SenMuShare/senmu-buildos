import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
VALIDATOR = ROOT / "scripts" / "validate_distillation_batch.py"


def valid_batch() -> dict:
    return {
        "schema_version": 1,
        "batch_id": "KD-20260827-001",
        "scope": "跨语言代码评审",
        "read_boundary": "只读公开材料，不安装或执行外部项目",
        "sources": [
            {
                "type": "web",
                "locator": "temporary-official-page",
                "scope_read": "评审标准与检查项",
            }
        ],
        "candidates": [
            {
                "candidate_id": "C-001",
                "domain": "review",
                "statement": "代码评审应改善整体代码健康，而不是追求脱离风险的完美。",
                "decision": "决定一项意见是否阻断合并。",
                "trigger": "评审者发现非阻断性的局部改进。",
                "action": "区分阻断问题、需要确认的风险和可选改进。",
                "exceptions": "安全、数据、权限和明确退化仍然阻断。",
                "verification": "评审输出标明严重程度、证据、影响和未验证盲区。",
                "scope": "跨语言代码评审",
                "suggested_owner": "skills/senmu-build-engineering/references/源代码工程质量与AI协作规范.md",
                "disposition": "merge",
                "existing_rule": "AI 与人工评审契约",
            }
        ],
    }


class DistillationBatchTests(unittest.TestCase):
    def run_validator(
        self, batch: dict, *extra_args: str
    ) -> subprocess.CompletedProcess[str]:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "batch.json"
            path.write_text(json.dumps(batch, ensure_ascii=False), encoding="utf-8")
            return subprocess.run(
                [
                    sys.executable,
                    str(VALIDATOR),
                    str(path),
                    "--limit",
                    "1",
                    *extra_args,
                ],
                cwd=ROOT,
                check=False,
                capture_output=True,
                text=True,
            )

    def test_valid_batch_passes(self) -> None:
        result = self.run_validator(valid_batch())
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("1 candidates", result.stdout)
        self.assertIn("merge=1", result.stdout)

    def test_duplicate_candidate_statement_fails(self) -> None:
        batch = valid_batch()
        duplicate = dict(batch["candidates"][0])
        duplicate["candidate_id"] = "C-002"
        batch["candidates"].append(duplicate)
        result = self.run_validator(batch)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("duplicate candidate statements", result.stderr)

    def test_add_requires_gap(self) -> None:
        batch = valid_batch()
        batch["candidates"][0]["disposition"] = "add"
        batch["candidates"][0].pop("existing_rule")
        result = self.run_validator(batch)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("C-001.gap", result.stderr)

    def test_external_active_root_is_supported(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            active_root = Path(temp_dir) / "rules"
            active_root.mkdir()
            (active_root / "standard.md").write_text(
                "- 代码评审应改善整体代码健康，而不是追求脱离风险的完美。\n",
                encoding="utf-8",
            )
            result = self.run_validator(
                valid_batch(), "--active-root", str(active_root), "--similarity", "0.5"
            )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("standard.md", result.stdout)


if __name__ == "__main__":
    unittest.main()
