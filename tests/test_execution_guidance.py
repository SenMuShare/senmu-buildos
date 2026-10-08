"""Executable routing and real Git lifecycle checks, not native model evaluations."""
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills/senmu-build-engineering/scripts/resolve_engineering_guidance.py"
SPEC = importlib.util.spec_from_file_location("execution_guidance_under_test", SCRIPT)
GUIDE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(GUIDE)
TASK = "skills/senmu-build-project/references/task-execution-and-state-management.md"
ECONOMY = GUIDE.ENGINEERING + "implementation-economy-and-overengineering.md"
TESTING = GUIDE.ENGINEERING + "software-testing-and-quality-verification.md"
CU = ROOT / "skills/senmu-build-delivery/scripts/manage_change_unit.py"

class ExecutionGuidanceTests(unittest.TestCase):
    def test_normal_route_is_unchanged_without_a_concern(self):
        ordinary = GUIDE.select(["app.py"], [])
        explicit_empty = GUIDE.select(["app.py"], [], concerns=[])
        self.assertEqual(ordinary, explicit_empty)
        self.assertNotIn("concerns", ordinary)
        self.assertNotIn(TASK, [x["reference"] for x in ordinary["references"]])
        self.assertNotIn(TESTING, [x["reference"] for x in ordinary["references"]])

    def test_method_routing_crosses_languages_without_losing_risk(self):
        for filename in ("src/task.py", "web/report.ts", "src/worker.rs"):
            with self.subTest(filename=filename):
                result = GUIDE.select([filename], ["paid-api"], concerns=["verification", "complexity"])
                routes = {x["reference"] for x in result["references"]}
                self.assertIn(TESTING, routes)
                self.assertIn(ECONOMY, routes)
                self.assertIn(GUIDE.ENGINEERING + "application-security-and-abuse.md", routes)
                self.assertFalse(result["source_scanned"])
                self.assertFalse(result["project_rules_included"])
                for item in result["references"]:
                    self.assertEqual(item["sha256"], hashlib.sha256((ROOT / item["reference"]).read_bytes()).hexdigest())

    def test_noncode_coordination_needs_no_engineering_profile(self):
        result = GUIDE.select([], [], concerns=["coordination"])
        self.assertEqual([TASK], [x["reference"] for x in result["references"]])
        self.assertEqual("selected", result["status"])
        self.assertIsNone(result["token_usage"])

    def test_unlisted_concern_is_retained_and_routed_not_ignored(self):
        result = GUIDE.select([], [], concerns=["unfamiliar-obstruction"])
        self.assertEqual("partial", result["status"])
        self.assertEqual(["unfamiliar-obstruction"], result["concerns"])
        self.assertEqual("unfamiliar-obstruction", result["unresolved"][0]["concern"])
        self.assertEqual([TASK], [x["reference"] for x in result["references"]])

    def test_declared_concerns_are_deduplicated_and_bounded(self):
        a = GUIDE.select([], [], concerns=["coordination", "complexity", "coordination"])
        b = GUIDE.select([], [], concerns=["complexity", "coordination"])
        self.assertEqual(a, b)
        for values in ("verification", [None], ["../escape"], ["x\ncommand"], ["x" * 65], ["x"] * 9):
            with self.subTest(values=values), self.assertRaises(ValueError):
                GUIDE.select([], [], concerns=values)

    def test_cli_handles_known_unknown_and_empty_without_writes(self):
        with tempfile.TemporaryDirectory() as directory:
            for arguments, status, code in ((["--concern", "coordination"], "selected", 0),
                                            (["--concern", "unfamiliar-obstruction"], "partial", 0),
                                            ([], "blocked", 1)):
                run = subprocess.run([sys.executable, str(SCRIPT), *arguments], cwd=directory,
                                     capture_output=True, text=True)
                self.assertEqual(code, run.returncode, run.stderr)
                self.assertEqual(status, json.loads(run.stdout)["status"])
                self.assertEqual([], list(Path(directory).iterdir()))

class OpenBatchLifecycleTests(unittest.TestCase):
    def test_review_repair_and_seal_use_one_unit_without_weakening_guards(self):
        with tempfile.TemporaryDirectory() as directory:
            home = Path(directory)
            repo, work = home / "repo", home / "work"
            repo.mkdir()
            def git(where, *args):
                return subprocess.check_output(["git", "-C", str(where), *args], text=True, stderr=subprocess.STDOUT).strip()
            def cu(command, where, *args, code=0):
                result = subprocess.run([sys.executable, str(CU), command, "--repo", str(where),
                                         "--unit", "TASK-SLICE", *args], capture_output=True, text=True)
                self.assertEqual(code, result.returncode, result.stdout + result.stderr)
                return result
            git(repo, "init", "--initial-branch=main")
            git(repo, "config", "user.email", "fixture@example.invalid")
            git(repo, "config", "user.name", "Disposable fixture")
            (repo / "result.txt").write_text("baseline\n")
            git(repo, "add", ".")
            git(repo, "commit", "-m", "fixture baseline")
            cu("prepare", repo, "--slug", "slice", "--target", "main", "--worktree", str(work))
            (work / "result.txt").write_text("first revision\n")
            git(work, "add", ".")
            git(work, "commit", "-m", "first revision")
            record = next((repo / ".git/senmu-buildos/change-units").glob("*.json"))
            before = record.read_bytes()
            cu("review", work)
            self.assertEqual(before, record.read_bytes())
            self.assertEqual("in_progress", json.loads(before)["state"])
            (work / "result.txt").write_text("review repair\n")
            cu("verify", work)
            git(work, "add", ".")
            git(work, "commit", "-m", "repair in same batch")
            cu("review", work)
            self.assertEqual(1, len(list(record.parent.glob("*.json"))))
            cu("seal", work)
            sealed = record.read_bytes()
            self.assertEqual("sealed", json.loads(sealed)["state"])
            cu("verify", work, code=1)
            self.assertEqual(sealed, record.read_bytes())
            self.assertEqual("baseline", (repo / "result.txt").read_text().strip())

if __name__ == "__main__":
    unittest.main()
