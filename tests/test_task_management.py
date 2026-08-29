import json
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
INIT = ROOT / "skills/senmu-build-project/scripts/init_project_governance.py"
ASSESS = ROOT / "skills/senmu-build-project/scripts/assess_project_governance.py"
VALIDATOR = ROOT / "skills/senmu-build-project/scripts/validate_project_governance.py"
PROJECT_TYPES = ("software", "script", "workflow", "media", "poc", "mixed")
PROFILES = ("core", "standard", "release")


class ProjectGovernanceScaffoldTests(unittest.TestCase):
    def run_command(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(args, check=False, capture_output=True, text=True)

    def initialize(self, target: Path, project_type: str, profile: str = "standard", *extra: str):
        return self.run_command(
            "python3", str(INIT), "--mode", "initialize-new", "--root", str(target),
            "--project-name", "BuildOS Test", "--project-type", project_type,
            "--profile", profile, *extra,
        )

    def test_new_project_requires_explicit_classification_and_profile(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_root:
            target = Path(temporary_root) / "project"
            result = self.run_command(
                "python3", str(INIT), "--mode", "initialize-new", "--root", str(target),
                "--project-name", "BuildOS Test",
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("--project-type", result.stderr)
            self.assertIn("--profile", result.stderr)
            self.assertFalse(target.exists())

    def test_plan_new_is_zero_write_and_reports_candidate_layout(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_root:
            target = Path(temporary_root) / "poc"
            result = self.run_command(
                "python3", str(INIT), "--mode", "plan-new", "--root", str(target),
                "--project-name", "POC Test", "--project-type", "poc", "--profile", "core",
            )
            self.assertEqual(result.returncode, 0, result.stderr or result.stdout)
            report = json.loads(result.stdout)
            self.assertEqual(report["mode"], "plan-new")
            self.assertEqual(report["selected_modules"], ["poc", "code", "git"])
            self.assertTrue(report["planned"])
            self.assertEqual(report["generated"], [])
            self.assertFalse(target.exists())

    def test_explicit_modules_override_recommended_directory_set(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_root:
            target = Path(temporary_root) / "small-tool"
            result = self.initialize(
                target, "software", "standard", "--modules", "code", "git",
            )
            self.assertEqual(result.returncode, 0, result.stderr or result.stdout)
            policy = json.loads((target / ".senmu-buildos/config.json").read_text(encoding="utf-8"))
            self.assertEqual(policy["selected_modules"], ["code", "git"])
            self.assertEqual(policy["schema_version"], "3.0.0")
            self.assertEqual(policy["git_management"]["main_mode"], "release_ready")
            self.assertFalse(policy["git_management"]["direct_main_writes"])
            self.assertEqual(policy["git_management"]["worktree_root"], ".worktrees")
            self.assertIsNone(policy["release_policy"])
            self.assertTrue((target / "engineering/CODE_QUALITY.md").is_file())
            self.assertTrue((target / "delivery/BRANCHING.md").is_file())
            branching = (target / "delivery/BRANCHING.md").read_text(encoding="utf-8")
            self.assertIn("默认一个权威事实源", branching)
            self.assertIn("未来可新增会话", branching)
            self.assertIn("没有 Remote 不构成缺陷", branching)
            self.assertIn("所有源码修改自动使用任务短分支", branching)
            self.assertIn("未来可新增会话或已知并行再增加独立 worktree", branching)
            self.assertIn("不得机械全合并", branching)
            self.assertIn("Change Unit", branching)
            self.assertIn("接收矩阵", branching)
            self.assertIn("未提交源码只能是 `in_progress`", branching)
            self.assertIn("Hotfix 前向传播检查点", branching)
            self.assertIn("传播通知边界", branching)
            self.assertIn("每个源修复只维护一行", branching)
            self.assertFalse((target / "product").exists())
            self.assertFalse((target / "engineering/ARCHITECTURE.md").exists())
            self.assertFalse((target / "delivery/RELEASE_PLAN.md").exists())

    def test_release_scaffold_keeps_remote_and_platform_optional(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_root:
            target = Path(temporary_root) / "local-release"
            result = self.initialize(target, "software", "release")
            self.assertEqual(result.returncode, 0, result.stderr or result.stdout)
            release = (target / "delivery/RELEASE_PLAN.md").read_text(encoding="utf-8")
            changelog_policy = (target / "delivery/CHANGELOG_POLICY.md").read_text(encoding="utf-8")
            self.assertIn("本地 Git 可独立形成完整版本线", release)
            self.assertIn("没有 Remote 不构成失败", release)
            self.assertIn("不因使用 Git 自动启用", release)
            self.assertIn("自然语言发布入口", release)
            self.assertIn("用户不负责决定合并", release)
            self.assertIn("不为每个机械 commit", changelog_policy)

    def test_empty_module_override_creates_only_profile_owners(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_root:
            target = Path(temporary_root) / "governance-only"
            result = self.initialize(target, "software", "core", "--modules")
            self.assertEqual(result.returncode, 0, result.stderr or result.stdout)
            policy = json.loads((target / ".senmu-buildos/config.json").read_text(encoding="utf-8"))
            self.assertEqual(policy["selected_modules"], [])
            self.assertTrue((target / "governance/GOVERNANCE.md").is_file())
            for directory in ("product", "engineering", "delivery", "workflows", "experiments", "agents"):
                self.assertFalse((target / directory).exists())

    def test_all_project_types_and_profiles_generate_valid_layouts(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_root:
            base = Path(temporary_root)
            for project_type in PROJECT_TYPES:
                for profile in PROFILES:
                    with self.subTest(project_type=project_type, profile=profile):
                        workspace = base / f"{project_type}-{profile}"
                        result = self.initialize(workspace, project_type, profile)
                        self.assertEqual(result.returncode, 0, result.stderr or result.stdout)
                        expected_layout = "software-repository" if project_type in {"software", "script"} else "project-system"
                        project_root = workspace if expected_layout == "software-repository" else workspace / "00-project-system"
                        policy = json.loads((project_root / ".senmu-buildos/config.json").read_text(encoding="utf-8"))
                        self.assertEqual(policy["schema_version"], "3.0.0")
                        self.assertEqual(policy["layout"], expected_layout)
                        self.assertEqual(policy["publication"]["model"], "private_only")
                        self.assertEqual(policy["release_channels"], [])
                        self.assertEqual(policy["artifact_kinds"], [])
                        if "git" in policy["selected_modules"]:
                            self.assertEqual(policy["git_management"]["main_mode"], "release_ready")
                            self.assertFalse(policy["git_management"]["direct_main_writes"])
                        else:
                            self.assertIsNone(policy["git_management"])
                        if "delivery" in policy["selected_modules"]:
                            self.assertEqual(
                                policy["release_policy"],
                                {
                                    "official_tag_semantics": "verified_release",
                                    "candidate_identity": "commit_and_artifact",
                                    "authorization_mode": "bounded_release_session",
                                },
                            )
                        else:
                            self.assertIsNone(policy["release_policy"])
                        self.assertTrue((project_root / ".git").exists())
                        self.assertIn(".worktrees/", (project_root / ".gitignore").read_text(encoding="utf-8"))
                        governance = project_root / "governance/GOVERNANCE.md"
                        self.assertTrue(governance.is_file())
                        self.assertFalse((project_root / "governance/PROJECT_GOVERNANCE.md").exists())
                        governance_text = governance.read_text(encoding="utf-8")
                        self.assertIn("项目治理章程", governance_text)
                        self.assertIn("治理版本：`1.0.0`", governance_text)
                        agents_text = (project_root / "AGENTS.md").read_text(encoding="utf-8")
                        self.assertLessEqual(len(agents_text), 2_300)
                        self.assertIn("## 项目差异与覆盖", agents_text)
                        self.assertIn("## 冲突处理", agents_text)
                        self.assertNotIn("## 稳定规则", agents_text)
                        self.assertNotIn("## 完成输出", agents_text)
                        if profile in {"standard", "release"}:
                            self.assertTrue((project_root / "governance/tasks/TASK_REGISTER.md").is_file())
                            self.assertTrue((project_root / ".senmu-buildos/templates/TASK.md").is_file())
                            self.assertTrue((project_root / ".senmu-buildos/validate_lessons.py").is_file())
                            self.assertIsNotNone(policy["task_management"])
                            self.assertIsNotNone(policy["lessons_validation"])
                        else:
                            self.assertFalse((project_root / "governance/tasks").exists())
                            self.assertFalse((project_root / ".senmu-buildos/templates/TASK.md").exists())
                            self.assertFalse((project_root / ".senmu-buildos/validate_lessons.py").exists())
                            self.assertIsNone(policy["task_management"])
                            self.assertIsNone(policy["lessons_validation"])
                        self.assertFalse((project_root / ".senmu-buildos/templates/task-package").exists())
                        if profile in {"standard", "release"}:
                            self.assertEqual(
                                policy["lessons_validation"]["command"],
                                "python3 .senmu-buildos/validate_lessons.py governance/lessons/LESSONS_LEARNED.md",
                            )
                        self.assertFalse((project_root / "governance/tasks/RESEARCH.md").exists())
                        self.assertFalse((project_root / "governance/tasks/VALIDATION.md").exists())
                        if profile in {"standard", "release"}:
                            self.assertEqual(policy["task_management"]["task_file_format"], "TASK-NNNN-slug.md")
                        self.assertNotIn("agents", policy["selected_modules"])
                        self.assertIsNone(policy["agent_management"])
                        self.assertFalse((project_root / "agents").exists())
                        project_map = project_root / "governance/PROJECT_MAP.md"
                        if profile in {"standard", "release"}:
                            self.assertTrue(project_map.is_file())
                            project_map_text = project_map.read_text(encoding="utf-8")
                            self.assertIn("## 项目规范索引", project_map_text)
                            self.assertIn("完整规则、理由、例外和命令", project_map_text)
                        else:
                            self.assertFalse(project_map.exists())
                        adr_template = project_root / ".senmu-buildos/templates/ADR.md"
                        if profile in {"standard", "release"} and "architecture" in policy["selected_modules"]:
                            self.assertTrue(adr_template.is_file())
                            self.assertFalse((project_root / "engineering/decisions").exists())
                        else:
                            self.assertFalse(adr_template.exists())
                        cleanup = project_root / "operations/scripts/cleanup-release-assets.sh"
                        retention_test = project_root / "operations/scripts/test-release-retention.sh"
                        retention_config = project_root / "operations/release-retention.env"
                        self.assertFalse(cleanup.exists())
                        self.assertFalse(retention_test.exists())
                        self.assertFalse(retention_config.exists())
                        self.assertIsNone(policy["release_retention"])
                        if expected_layout == "project-system":
                            for directory in ("01-sources", "02-workspace", "03-deliveries", "04-archive"):
                                self.assertTrue((workspace / directory).is_dir())
                                self.assertFalse((workspace / directory / ".git").exists())
                        validate = self.run_command("python3", str(project_root / ".senmu-buildos/validate.py"), "--root", str(project_root))
                        self.assertEqual(validate.returncode, 0, validate.stderr or validate.stdout)

    def test_explicit_project_system_layout_is_available_for_software(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_root:
            workspace = Path(temporary_root) / "software-delivery"
            result = self.initialize(workspace, "software", "standard", "--layout", "project-system")
            self.assertEqual(result.returncode, 0, result.stderr or result.stdout)
            policy = json.loads((workspace / "00-project-system/.senmu-buildos/config.json").read_text(encoding="utf-8"))
            self.assertEqual(policy["layout"], "project-system")
            self.assertEqual(policy["workspace_root"], "..")

    def test_agent_governance_is_explicit_and_structurally_valid(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_root:
            target = Path(temporary_root) / "agent-project"
            result = self.initialize(target, "software", "standard", "--with-agents")
            self.assertEqual(result.returncode, 0, result.stderr or result.stdout)
            policy = json.loads((target / ".senmu-buildos/config.json").read_text(encoding="utf-8"))
            self.assertIn("agents", policy["selected_modules"])
            self.assertEqual(policy["agent_management"]["register_path"], "agents/AGENT_REGISTER.md")
            self.assertTrue((target / "agents/AGENT_REGISTER.md").is_file())
            self.assertTrue((target / ".senmu-buildos/templates/agent/AGENT.md").is_file())
            self.assertTrue((target / ".senmu-buildos/validate_agents.py").is_file())
            self.assertTrue((target / ".senmu-buildos/validate_agents.py").stat().st_mode & 0o111)
            validate = self.run_command(
                "python3", str(target / ".senmu-buildos/validate.py"), "--root", str(target)
            )
            self.assertEqual(validate.returncode, 0, validate.stderr or validate.stdout)

    def test_project_validator_runs_agent_validation(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_root:
            target = Path(temporary_root) / "agent-project"
            result = self.initialize(target, "software", "standard", "--with-agents")
            self.assertEqual(result.returncode, 0, result.stderr or result.stdout)
            register = target / "agents/AGENT_REGISTER.md"
            separator = "| --- | --- | --- | --- | --- | --- | --- |\n"
            row = (
                "| `missing-agent` | Missing | `1.0.0` | `active` | "
                "`agents/missing-agent/AGENT.md` | Team | `workflow` |\n"
            )
            register.write_text(
                register.read_text(encoding="utf-8").replace(separator, separator + row, 1),
                encoding="utf-8",
            )
            validate = self.run_command(
                "python3", str(target / ".senmu-buildos/validate.py"), "--root", str(target)
            )
            self.assertNotEqual(validate.returncode, 0)
            self.assertIn("Agent 定义校验失败", validate.stdout)
            self.assertIn("Agent 定义不存在", validate.stdout)

    def test_specialists_and_poc_use_formal_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_root:
            base = Path(temporary_root)
            product = base / "product"
            experiment = base / "experiment"
            self.assertEqual(self.initialize(product, "software").returncode, 0)
            self.assertTrue((product / ".senmu-buildos/templates/REQUIREMENT.md").is_file())
            self.assertTrue((product / ".senmu-buildos/templates/REQUIREMENT_REVIEW.md").is_file())
            self.assertTrue((product / ".senmu-buildos/templates/TECHNICAL_DESIGN.md").is_file())
            self.assertTrue((product / ".senmu-buildos/templates/TECHNICAL_REVIEW.md").is_file())
            self.assertTrue((product / ".senmu-buildos/templates/ADR.md").is_file())
            self.assertEqual(self.initialize(experiment, "poc").returncode, 0)
            project_root = experiment / "00-project-system"
            self.assertTrue((project_root / "experiments/EXPERIMENT_REGISTER.md").is_file())
            for name in ("EXPERIMENT.md", "PLAN.md", "RESULTS.md", "DECISION.md", "experiment-manifest.json"):
                self.assertTrue((project_root / ".senmu-buildos/templates/experiment-package" / name).is_file())

    def test_release_profile_retention_contract(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_root:
            target = Path(temporary_root) / "release-project"
            result = self.initialize(
                target,
                "software",
                "release",
                "--release-channel",
                "container_image",
                "--artifact-kind",
                "container_image",
            )
            self.assertEqual(result.returncode, 0, result.stderr or result.stdout)
            contract = self.run_command(str(target / "operations/scripts/test-release-retention.sh"))
            self.assertEqual(contract.returncode, 0, contract.stderr or contract.stdout)
            self.assertIn("release_retention_contract=passed", contract.stdout)
            cleanup_text = (target / "operations/scripts/cleanup-release-assets.sh").read_text(encoding="utf-8")
            for forbidden in ("docker system prune", "docker image prune", "docker builder prune", "--volumes", "rm -rf"):
                self.assertNotIn(forbidden, cleanup_text)

    def test_release_without_artifact_has_no_artifact_lifecycle(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_root:
            target = Path(temporary_root) / "source-release"
            result = self.initialize(
                target,
                "software",
                "release",
                "--publication-model",
                "public_native",
                "--release-channel",
                "public_source_repository",
            )
            self.assertEqual(result.returncode, 0, result.stderr or result.stdout)
            policy = json.loads((target / ".senmu-buildos/config.json").read_text(encoding="utf-8"))
            self.assertEqual(policy["artifact_kinds"], [])
            self.assertIsNone(policy["release_retention"])
            self.assertFalse((target / "operations/release-retention.env").exists())
            self.assertTrue((target / "VERSION").is_file())
            self.assertTrue((target / "CHANGELOG.md").is_file())

    def test_publication_workspace_uses_relative_roles_and_no_absolute_paths(self) -> None:
        with tempfile.TemporaryDirectory(prefix="private-user-workspace-") as temporary_root:
            workspace = Path(temporary_root) / "workspace with spaces"
            result = self.initialize(
                workspace,
                "software",
                "release",
                "--publication-model",
                "private_authority_public_projection",
                "--release-channel",
                "public_source_repository",
                "--release-channel",
                "marketplace_install",
                "--authority-path",
                "private-source",
                "--public-projection-path",
                "open-source",
                "--release-staging-path",
                ".promotion-staging",
            )
            self.assertEqual(result.returncode, 0, result.stderr or result.stdout)
            authority = workspace / "private-source"
            policy = json.loads((authority / ".senmu-buildos/config.json").read_text(encoding="utf-8"))
            self.assertEqual(policy["layout"], "publication-workspace")
            self.assertEqual(policy["workspace_root"], "..")
            self.assertEqual(policy["path_roles"]["authority_root"], "private-source")
            self.assertEqual(policy["path_roles"]["public_projection_root"], "open-source")
            self.assertTrue((authority / "delivery/PUBLICATION.md").is_file())
            self.assertTrue((workspace / "open-source/.git").is_dir())
            self.assertTrue((workspace / ".promotion-staging").is_dir())
            leaked_root = str(workspace.resolve())
            for path in authority.rglob("*"):
                if path.is_file() and ".git" not in path.parts:
                    try:
                        text = path.read_text(encoding="utf-8")
                    except UnicodeDecodeError:
                        continue
                    self.assertNotIn(leaked_root, text, path)

    def test_initializer_rejects_absolute_persisted_role_paths(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_root:
            target = Path(temporary_root) / "workspace"
            result = self.initialize(
                target,
                "software",
                "standard",
                "--publication-model",
                "private_authority_public_projection",
                "--public-projection-path",
                "/" + "Users/example/public",
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("必须是相对工作区的路径", result.stderr or result.stdout)

    def test_validator_rejects_task_directory(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_root:
            target = Path(temporary_root) / "project"
            self.assertEqual(self.initialize(target, "script", "standard").returncode, 0)
            (target / "governance/tasks/random-notes").mkdir()
            validate = self.run_command("python3", str(VALIDATOR), "--root", str(target))
            self.assertNotEqual(validate.returncode, 0)
            self.assertIn("任务计划不得使用独立目录", validate.stdout)

    def test_validator_accepts_numbered_task_plan_file(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_root:
            target = Path(temporary_root) / "project"
            self.assertEqual(self.initialize(target, "script", "standard").returncode, 0)
            task = target / "governance/tasks/TASK-0001-review-code.md"
            task.write_text("# TASK-0001：评审代码\n", encoding="utf-8")
            validate = self.run_command("python3", str(VALIDATOR), "--root", str(target))
            self.assertEqual(validate.returncode, 0, validate.stdout or validate.stderr)

    def test_strict_placeholder_scan_can_exclude_generic_source_docs(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_root:
            target = Path(temporary_root) / "project"
            self.assertEqual(self.initialize(target, "script", "standard").returncode, 0)
            generic_doc = target / "GENERIC.md"
            generic_doc.write_text("# API\n\nUse `v<version>` and `TASK-<NNNN>`.\n", encoding="utf-8")
            policy_path = target / ".senmu-buildos/config.json"
            policy = json.loads(policy_path.read_text(encoding="utf-8"))
            policy["initialization_status"] = "active"
            policy["required_paths"].append("GENERIC.md")
            policy["placeholder_scan_paths"] = ["governance/logs/WORKLOG.md"]
            policy_path.write_text(json.dumps(policy, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

            validate = self.run_command("python3", str(VALIDATOR), "--root", str(target), "--strict")
            self.assertEqual(validate.returncode, 0, validate.stdout or validate.stderr)

            worklog = target / "governance/logs/WORKLOG.md"
            worklog.write_text(worklog.read_text(encoding="utf-8") + "\n<待确认>\n", encoding="utf-8")
            validate = self.run_command("python3", str(VALIDATOR), "--root", str(target), "--strict")
            self.assertNotEqual(validate.returncode, 0)
            self.assertIn("严格校验发现未校准占位符", validate.stdout)

    def test_validator_rejects_nonstandard_task_file(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_root:
            target = Path(temporary_root) / "project"
            self.assertEqual(self.initialize(target, "script", "standard").returncode, 0)
            (target / "governance/tasks/notes.md").write_text("# 临时笔记\n", encoding="utf-8")
            validate = self.run_command("python3", str(VALIDATOR), "--root", str(target))
            self.assertNotEqual(validate.returncode, 0)
            self.assertIn("任务目录包含非标准文件", validate.stdout)

    def test_validator_rejects_project_map_without_standards_index(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_root:
            target = Path(temporary_root) / "project"
            self.assertEqual(self.initialize(target, "software", "standard").returncode, 0)
            project_map = target / "governance/PROJECT_MAP.md"
            project_map.write_text(
                project_map.read_text(encoding="utf-8").replace("## 项目规范索引", "## 已删除的索引"),
                encoding="utf-8",
            )
            validate = self.run_command("python3", str(VALIDATOR), "--root", str(target))
            self.assertNotEqual(validate.returncode, 0)
            self.assertIn("Project Map 缺少必要索引区：## 项目规范索引", validate.stdout)

    def test_project_validator_runs_lessons_validation(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_root:
            target = Path(temporary_root) / "project"
            self.assertEqual(self.initialize(target, "script", "standard").returncode, 0)
            lessons = target / "governance/lessons/LESSONS_LEARNED.md"
            lessons.write_text(
                "### LES-20260825-001：缺少证据的活动经验\n\n"
                "- 状态：`active`\n"
                "- 类型：`incident`\n",
                encoding="utf-8",
            )
            validate = self.run_command("python3", str(VALIDATOR), "--root", str(target))
            self.assertNotEqual(validate.returncode, 0)
            self.assertIn("经验台账校验失败", validate.stdout)
            self.assertIn("active 条目缺少可执行事实", validate.stdout)

    def test_initializer_refuses_established_project_without_writes(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_root:
            target = Path(temporary_root) / "established"
            target.mkdir()
            (target / "README.md").write_text("# Existing\n", encoding="utf-8")
            result = self.initialize(target, "software")
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("assess_project_governance.py", result.stderr or result.stdout)
            self.assertEqual([path.name for path in target.iterdir()], ["README.md"])

    def test_assessor_separates_declared_current_retired_and_task_instance_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_root:
            target = Path(temporary_root) / "established"
            unit = target / "projects/current"
            (target / ".git").mkdir(parents=True)
            unit.joinpath(".git").mkdir(parents=True)
            unit.joinpath("db").mkdir(parents=True)
            unit.joinpath("jobs/episode-01").mkdir(parents=True)
            target.joinpath("80_POC实验区/demo").mkdir(parents=True)
            target.joinpath(".runtime/identity-backups").mkdir(parents=True)
            target.joinpath(".playwright-profile/Default").mkdir(parents=True)
            target.joinpath("81_数据临时区/00_迁移核验凭证/01_恢复包").mkdir(parents=True)
            target.joinpath(".remotion/chrome-headless-shell").mkdir(parents=True)
            (target / "README.md").write_text("# Established\n", encoding="utf-8")
            (target / "AGENTS.md").write_text("# Root project facts\n", encoding="utf-8")
            (unit / "README.md").write_text("# Current\n", encoding="utf-8")
            (unit / "AGENTS.md").write_text("# Unit override\n", encoding="utf-8")
            (unit / "db/current.sqlite").write_text("", encoding="utf-8")
            (unit / "jobs/episode-01/production-job.json").write_text("{}\n", encoding="utf-8")
            (unit / "jobs/episode-01/task-timing.json").write_text("{}\n", encoding="utf-8")
            (target / "80_POC实验区/demo/package.json").write_text("{}\n", encoding="utf-8")
            (target / ".runtime/identity-backups/old.sqlite").write_text("", encoding="utf-8")
            (target / ".playwright-profile/Default/browser.db").write_text("", encoding="utf-8")
            (target / "81_数据临时区/00_迁移核验凭证/01_恢复包/retired.sqlite").write_text("", encoding="utf-8")
            (target / ".remotion/chrome-headless-shell/VERSION").write_text("1\n", encoding="utf-8")
            (target / "VERSION").write_text("1.0.0\n", encoding="utf-8")
            (target / "Dockerfile").write_text("FROM scratch\n", encoding="utf-8")
            registry = {
                "repositories": [
                    {
                        "repository_id": "current",
                        "path": "projects/current",
                        "ledger": "projects/current/db/current.sqlite",
                    }
                ],
                "legacy_authority": {
                    "database": "81_数据临时区/00_迁移核验凭证/01_恢复包/retired.sqlite",
                    "status": "retired_evidence_only",
                },
            }
            (target / "repositories.json").write_text(json.dumps(registry), encoding="utf-8")

            result = self.run_command("python3", str(ASSESS), "--root", str(target), "--verbose")
            self.assertEqual(result.returncode, 0, result.stderr or result.stdout)
            report = json.loads(result.stdout)
            release_units = {item["path"]: item for item in report["authority_evidence"]["release_units"]}
            self.assertEqual(release_units["projects/current"]["status"], "declared")
            self.assertEqual(
                report["authority_evidence"]["declared_state_owners"][0]["path"],
                "projects/current/db/current.sqlite",
            )
            self.assertNotIn("durable_task_state", report["candidate_mappings"])
            self.assertEqual(report["candidate_mappings"]["task_instance_state"]["count"], 1)
            run_state_paths = {item["path"] for item in report["full_candidate_inventory"].get("run_state", [])}
            self.assertNotIn("projects/current/db/current.sqlite", run_state_paths)
            self.assertEqual(report["candidate_mappings"]["experiment_evidence"]["count"], 1)
            production_paths = {item["path"] for item in report["full_candidate_inventory"]["production_truth"]}
            self.assertEqual(production_paths, {"VERSION"})
            capability = report["capability_assessment"]
            self.assertEqual(capability["status"], "candidate_signals_require_contract_confirmation")
            self.assertEqual(capability["signals"]["container_candidate"]["examples"], ["Dockerfile"])
            self.assertIn("不自动创建制品目录", capability["decision_rule"])
            excluded_paths = {
                path
                for items in report["full_excluded_inventory"].values()
                for path in items
            }
            self.assertIn(".remotion/", excluded_paths)
            self.assertIn("81_数据临时区/", excluded_paths)
            self.assertIn(".runtime/identity-backups/", excluded_paths)
            self.assertIn(".playwright-profile/", excluded_paths)
            layering = report["instruction_layering_review"]
            self.assertEqual(layering["status"], "semantic_review_required")
            self.assertEqual(layering["entrypoints"], ["AGENTS.md", "projects/current/AGENTS.md"])
            self.assertFalse(layering["write_default_agents_template"])
            self.assertIn("remove_buildos_duplicate", layering["required_actions"])
            self.assertIn(
                "replace_unconditional_cross_domain_preload_with_signal_routing",
                layering["required_actions"],
            )
            self.assertIn("remove_generic_skill_catalog_from_project_delta", layering["required_actions"])
            runtime_validation = layering["runtime_validation"]
            self.assertEqual(runtime_validation["status"], "required_before_routing_claim")
            self.assertEqual(runtime_validation["maximum_unverified_claim"], "structural_routing_prepared")
            self.assertEqual(len(runtime_validation["scenarios"]), 3)

    def test_initializer_can_resume_its_own_draft(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_root:
            target = Path(temporary_root) / "draft"
            first = self.initialize(target, "script", "core")
            second = self.initialize(target, "script", "core")
            self.assertEqual(first.returncode, 0, first.stderr or first.stdout)
            self.assertEqual(second.returncode, 0, second.stderr or second.stdout)
            result = json.loads(second.stdout.split("[NEXT]", 1)[0])
            self.assertEqual(result["generated"], [])
            self.assertIn(".senmu-buildos/config.json", result["skipped"])

    def test_initializer_can_create_scoped_baseline_commit(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_root:
            target = Path(temporary_root) / "baseline"
            first = self.initialize(target, "software", "core")
            self.assertEqual(first.returncode, 0, first.stderr or first.stdout)
            self.assertEqual(self.run_command("git", "-C", str(target), "config", "user.name", "BuildOS Test").returncode, 0)
            self.assertEqual(self.run_command("git", "-C", str(target), "config", "user.email", "buildos@example.test").returncode, 0)

            second = self.initialize(target, "software", "core", "--commit-baseline")
            self.assertEqual(second.returncode, 0, second.stderr or second.stdout)
            result = json.loads(second.stdout.split("[NEXT]", 1)[0])
            self.assertEqual(result["baseline_commit"]["status"], "committed")
            self.assertEqual(
                self.run_command("git", "-C", str(target), "log", "-1", "--pretty=%s").stdout.strip(),
                "chore: initialize project governance",
            )
            self.assertEqual(self.run_command("git", "-C", str(target), "tag", "--list").stdout.strip(), "")
            self.assertEqual(self.run_command("git", "-C", str(target), "status", "--short").stdout.strip(), "")

    def test_dry_run_has_no_writes(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_root:
            target = Path(temporary_root) / "dry-run"
            result = self.run_command(
                "python3", str(INIT), "--mode", "initialize-new", "--root", str(target),
                "--project-name", "Dry Run", "--project-type", "media", "--profile", "standard", "--dry-run",
            )
            self.assertEqual(result.returncode, 0, result.stderr or result.stdout)
            self.assertFalse(target.exists())
            report = json.loads(result.stdout)
            self.assertEqual(report["generated"], [])
            self.assertEqual(len(report["planned"]), len(set(report["planned"])))
            self.assertIn(".senmu-buildos/config.json", report["planned"])

    def test_core_script_stays_small_and_merges_optional_owners(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_root:
            target = Path(temporary_root) / "small-script"
            result = self.initialize(target, "script", "core", "--dry-run")
            self.assertEqual(result.returncode, 0, result.stderr or result.stdout)
            report = json.loads(result.stdout)
            self.assertEqual(
                set(report["planned"]),
                {
                    ".gitignore",
                    "README.md",
                    "AGENTS.md",
                    "governance/GOVERNANCE.md",
                    ".senmu-buildos/validate.py",
                    ".senmu-buildos/config.json",
                },
            )


if __name__ == "__main__":
    unittest.main()
