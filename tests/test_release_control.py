from __future__ import annotations

import copy
import importlib.util
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills/senmu-build-delivery/scripts/validate_release_control.py"
TEMPLATE = ROOT / "skills/senmu-build-delivery/assets/delivery-governance/RELEASE_CONTROL.template.json"
SPEC = importlib.util.spec_from_file_location("validate_release_control", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class ReleaseControlTests(unittest.TestCase):
    def valid_closed_record(self) -> dict:
        record = json.loads(TEMPLATE.read_text(encoding="utf-8"))
        record["release"].update(
            {
                "candidate_commit": "abc123",
                "authorization_ref": "user-request-2026-09-02",
                "release_record_ref": "governance/releases/REL-0001.md",
                "status": "closed",
            }
        )
        record["requirements"] = [
            {"id": "REQ-1", "disposition": "include", "evidence_refs": ["task:REQ-1"], "reason": None}
        ]
        record["change_units"] = [
            {
                "unit": "TASK-1",
                "branch": "codex/task-1",
                "source_commit": "source123",
                "disposition": "include",
                "evidence_refs": ["change-unit:TASK-1"],
                "test_refs": ["test:unit"],
                "integration_commit": "integrated123",
                "reason": None,
            }
        ]
        for gate in record["gates"]:
            gate.update({"status": "passed", "evidence_refs": [f"evidence:{gate['id']}"]})
        record["cleanup"] = [
            {
                "unit": "TASK-1",
                "branch": "codex/task-1",
                "worktree": "/tmp/task-1",
                "disposition": "removed",
                "evidence_refs": ["git:worktree-list"],
                "owner": None,
                "exit_condition": None,
            }
        ]
        return record

    def test_valid_closed_record_is_accepted(self) -> None:
        self.assertEqual(MODULE.validate_record(self.valid_closed_record()), [])

    def test_later_gate_cannot_close_before_an_earlier_gate(self) -> None:
        record = self.valid_closed_record()
        record["release"]["status"] = "candidate"
        record["gates"][1].update({"status": "pending", "evidence_refs": []})
        errors = MODULE.validate_record(record)
        self.assertTrue(any("cannot close before an earlier unfinished gate" in error for error in errors))

    def test_scope_gate_rejects_unaccounted_requirement(self) -> None:
        record = self.valid_closed_record()
        record["release"]["status"] = "planning"
        record["requirements"][0].update({"disposition": "pending", "evidence_refs": []})
        errors = MODULE.validate_record(record)
        self.assertIn("scope_accounted cannot pass while requirements are pending or blocked", errors)

    def test_git_closeout_requires_cleanup_for_each_included_unit(self) -> None:
        record = self.valid_closed_record()
        record["cleanup"] = []
        errors = MODULE.validate_record(record)
        self.assertTrue(any("missing cleanup rows" in error for error in errors))

    def test_retained_cleanup_requires_owner_and_exit_condition(self) -> None:
        record = copy.deepcopy(self.valid_closed_record())
        record["cleanup"][0].update({"disposition": "retained", "owner": None, "exit_condition": None})
        errors = MODULE.validate_record(record)
        self.assertTrue(any("requires owner and exit_condition" in error for error in errors))

    def test_git_closeout_rejects_any_unfinished_cleanup_row(self) -> None:
        record = self.valid_closed_record()
        record["cleanup"].append(
            {
                "unit": "TASK-2",
                "branch": "codex/task-2",
                "worktree": "/tmp/task-2",
                "disposition": "pending",
                "evidence_refs": [],
                "owner": None,
                "exit_condition": None,
            }
        )
        errors = MODULE.validate_record(record)
        self.assertTrue(any("unfinished cleanup rows" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
