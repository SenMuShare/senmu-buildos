"""Exercise real Delivery scope -> execution inventory -> approval Git identity reads."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
DELIVERY = ROOT / "skills/senmu-build-delivery/scripts/manage_change_unit.py"
EXECUTION = ROOT / "skills/senmu-build-assurance/scripts/manage_review_execution.py"
VALIDATOR = ROOT / "skills/senmu-build-delivery/scripts/validate_change_review.py"


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


class ReviewInventoryIntegrationTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name).resolve()
        self.repo = self.root / "repo"
        self.repo.mkdir()
        self.git(self.repo, "init", "-q", "-b", "main")
        self.git(self.repo, "config", "user.email", "fixture@example.invalid")
        self.git(self.repo, "config", "user.name", "Inventory fixture")
        (self.repo / "old.py").write_bytes(b"value=1\n")
        (self.repo / "需求.md").write_text("before\n", encoding="utf-8")
        self.commit(self.repo)
        self.worktree = self.root / "worktree"
        self.command(DELIVERY, "prepare", "--repo", str(self.repo), "--target", "main",
                     "--unit", "CU-CANONICAL", "--slug", "inventory", "--worktree", str(self.worktree))
        self.runtime = module("integration_review_runtime", EXECUTION)
        self.validator = module("integration_change_review", VALIDATOR)

    def git(self, repo, *args):
        return subprocess.check_output(["git", "-C", str(repo), *args],
                                       stderr=subprocess.PIPE).decode("utf-8").rstrip("\n")

    def commit(self, repo):
        self.git(repo, "add", "--all")
        self.git(repo, "commit", "-qm", "synthetic change")

    def command(self, script, *args, expected=0):
        result = subprocess.run([sys.executable, str(script), *args], capture_output=True, text=True)
        self.assertEqual(result.returncode, expected, result.stdout + result.stderr)
        return json.loads(result.stdout)

    def verify_round_trip(self, expected_paths):
        scope = self.command(DELIVERY, "review", "--repo", str(self.worktree), "--unit", "CU-CANONICAL")
        self.assertEqual(scope["changed_paths"], sorted(expected_paths, key=lambda p: p.encode("utf-8")))
        self.assertEqual(scope["inventory_policy"], self.runtime._shared.POLICY)
        scope_file = self.root / "scope.json"
        scope_file.write_text(json.dumps(scope), encoding="utf-8")
        record_file = self.root / "record.json"
        self.command(EXECUTION, "init", "--repo", str(self.worktree), "--record", str(record_file),
                     "--rules-identity", "fixture-rules", "--scope", str(scope_file))
        record = self.runtime.load(record_file)
        self.assertEqual([item["path"] for item in record["items"]], scope["changed_paths"])
        # This checks the approval validator's Git identity component, not an approval verdict.
        approval = {"change": {"base_commit": scope["review_base"], "head_commit": scope["head"]},
                    "inventory": {"files": [{"path": path} for path in scope["changed_paths"]]}}
        self.assertEqual(self.validator.validate_git(approval, self.worktree, True), [])
        return record

    def test_configured_no_renames_does_not_split_scope_between_entrypoints(self):
        self.git(self.repo, "config", "diff.renames", "false")
        (self.worktree / "old.py").rename(self.worktree / "new.py")
        self.commit(self.worktree)
        record = self.verify_round_trip(["new.py"])
        self.assertEqual(record["items"][0]["old_path"], "old.py")
        self.git(self.repo, "config", "diff.renames", "copies")
        self.git(self.repo, "config", "diff.renameLimit", "1")
        self.runtime.validate_record(record, self.worktree, "fixture-rules")

    def test_unicode_spaces_newlines_and_pathspec_like_names_round_trip(self):
        names = [" spaced\nname.py ", 'quote".py', ":(glob)*.py"]
        for name in names:
            (self.worktree / name).write_bytes(b"value=2\n")
        (self.worktree / "需求.md").write_text("after\n", encoding="utf-8")
        self.commit(self.worktree)
        self.verify_round_trip([*names, "需求.md"])

    def test_order_file_and_relative_config_do_not_change_frozen_inventory(self):
        (self.worktree / "old.py").rename(self.worktree / "new.py")
        (self.worktree / "需求.md").write_text("after\n", encoding="utf-8")
        self.commit(self.worktree)
        order = self.root / "diff-order"
        order.write_text("需求.md\nnew.py\n")
        self.git(self.repo, "config", "diff.orderFile", str(order))
        self.git(self.repo, "config", "diff.relative", "true")
        record = self.verify_round_trip(["new.py", "需求.md"])
        order.write_text("new.py\n需求.md\n")
        self.runtime.validate_record(record, self.worktree, "fixture-rules")

    def test_delete_and_add_are_not_lost_from_scope(self):
        (self.worktree / "old.py").unlink()
        (self.worktree / "different.py").write_bytes(b"unrelated_content=True\n")
        self.commit(self.worktree)
        self.verify_round_trip(["different.py", "old.py"])


if __name__ == "__main__":
    unittest.main()
