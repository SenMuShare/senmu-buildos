"""Real-Git and CLI regressions for frozen review execution, not model-quality tests."""

from copy import deepcopy
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills/senmu-build-assurance/scripts/manage_review_execution.py"
SPEC = importlib.util.spec_from_file_location("review_execution", SCRIPT)
assert SPEC and SPEC.loader
m = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(m)


class ReviewExecutionTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name).resolve()
        self.repo = self.root / "repo"
        self.repo.mkdir()
        self.git("init", "-b", "main")
        self.git("config", "user.email", "test@example.invalid")
        self.git("config", "user.name", "Test")
        (self.repo / "a.py").write_bytes(b"x = 1\ny = 2\n")
        (self.repo / "removed.py").write_bytes(b"obsolete = True\n")
        self.base = self.commit("base")
        (self.repo / "a.py").write_bytes(b"x = 1\ny = 3\n")
        (self.repo / "removed.py").unlink()
        (self.repo / "empty.py").write_bytes(b"")
        self.head = self.commit("change")
        self.scope = {"kind": "git_review_scope", "repository_root": str(self.repo),
                      "unit": "CU-TEST", "review_base": self.base, "head": self.head,
                      "tree": self.git("rev-parse", "HEAD^{tree}"),
                      "changed_paths": [x["path"] for x in m.inventory(self.repo, self.base, self.head)]}
        self.record = m.init_record(self.scope, self.repo, "rules-and-context-v1")
        self.path = self.root / "review.json"
        self.scope_path = self.root / "scope.json"
        self.scope_path.write_text(json.dumps(self.scope), encoding="utf-8")

    def git(self, *args):
        result = subprocess.run(["git", "-C", str(self.repo), *args], capture_output=True, check=True)
        return result.stdout.decode().rstrip("\n")

    def commit(self, message):
        self.git("add", "-A")
        self.git("commit", "-m", message)
        return self.git("rev-parse", "HEAD")

    def item(self, name="a.py", record=None):
        return next(x for x in (record or self.record)["items"] if x["path"] == name)

    def payload(self, item=None, state="completed", record=None):
        record = record or self.record
        item = item or self.item(record=record)
        payload = {"run_id": record["run_id"], "snapshot_identity": record["snapshot_identity"],
                   "item_id": item["item_id"], "attempt": item["attempt"],
                   "executor": "fixture-reviewer", "state": state}
        if state == "failed":
            payload["reason"] = "executor interrupted"
        else:
            payload["summary"] = "Fixture inspects both frozen sides; semantic quality is not assessed."
            payload["evidence"] = [m.evidence(self.repo, item, side)
                                   for side, prefix in (("base", "old"), ("head", "new"))
                                   if item[prefix + "_mode"] != "000000"]
        return payload

    def apply(self, payload, record=None):
        m.apply_receipt(record or self.record, self.repo, payload["item_id"], payload["state"], payload)

    def validate(self, record=None):
        m.validate_record(record or self.record, self.repo, "rules-and-context-v1")

    def cli(self, command, *args, expected=0):
        if command == "retry" and "--run-id" not in args:
            saved = m.load(self.path)
            selected = m.find_item(saved, args[args.index("--item") + 1])
            args += ("--run-id", saved["run_id"], "--expected-attempt", str(selected["attempt"]),
                     "--operation-id", "fixture-retry-" + str(selected["attempt"]))
        result = subprocess.run([sys.executable, str(SCRIPT), command, "--repo", str(self.repo),
                                 "--record", str(self.path), "--rules-identity", "rules-and-context-v1",
                                 *args], capture_output=True, text=True)
        self.assertEqual(result.returncode, expected, result.stdout + result.stderr)
        return json.loads(result.stdout)

    def test_inventory_and_initial_state(self):
        self.validate()
        self.assertEqual(m.summary(self.record)["pending"], 3)
        self.assertFalse(m.summary(self.record)["execution_complete"])

    def test_real_evidence_and_idempotent_receipt(self):
        payload = self.payload()
        self.apply(payload)
        before = deepcopy(self.record)
        self.apply(payload)
        self.assertEqual(before, self.record)
        self.validate()
        self.assertEqual(m.summary(self.record)["completed"], 1)

    def test_deleted_file_uses_base_evidence(self):
        payload = self.payload(self.item("removed.py"))
        self.assertEqual(payload["evidence"][0]["side"], "base")
        self.apply(payload)
        self.validate()

    def test_empty_file_has_explicit_zero_range(self):
        payload = self.payload(self.item("empty.py"))
        self.assertEqual(payload["evidence"][0]["line_start"], 0)
        self.apply(payload)
        self.validate()

    def test_wrong_fingerprint_rejected(self):
        payload = self.payload()
        payload["evidence"][0]["range_sha256"] = "sha256:" + "0" * 64
        with self.assertRaises(m.ReviewError):
            self.apply(payload)
        self.assertEqual(self.item()["state"], "pending")

    def test_missing_and_boolean_line_numbers_rejected(self):
        for change in ({"line_start": True}, {"line_end": 999}, {"side": "other"}):
            payload = self.payload()
            payload["evidence"][0].update(change)
            with self.subTest(change=change), self.assertRaises(m.ReviewError):
                self.apply(payload)
        payload = self.payload()
        del payload["evidence"][0]["line_start"]
        with self.assertRaises(m.ReviewError):
            self.apply(payload)

    def test_both_existing_sides_are_required(self):
        payload = self.payload()
        payload["evidence"] = payload["evidence"][1:]
        with self.assertRaises(m.ReviewError):
            self.apply(payload)

    def test_receipt_state_override_rejected(self):
        payload = self.payload()
        payload["state"] = "failed"
        with self.assertRaises(m.ReviewError):
            m.apply_receipt(self.record, self.repo, payload["item_id"], "completed", payload)

    def test_conflicting_terminal_receipt_rejected(self):
        self.apply(self.payload())
        with self.assertRaises(m.ReviewError):
            self.apply(self.payload(state="failed"))

    def test_failed_then_retry_then_success_preserves_history(self):
        self.apply(self.payload(state="failed"))
        self.assertFalse(m.summary(self.record)["execution_complete"])
        m.retry(self.record, self.item()["item_id"], "retry after resolving executor failure", run_id=self.record["run_id"], expected_attempt=m.find_item(self.record, self.item()["item_id"])["attempt"], operation_id="fixture-retry-"+str(m.find_item(self.record, self.item()["item_id"])["attempt"]))
        self.apply(self.payload())
        self.validate()
        self.assertEqual(self.item()["attempt"], 2)
        self.assertEqual(self.item()["history"][0]["receipt"]["state"], "failed")

    def test_late_receipt_from_previous_attempt_is_rejected(self):
        late = self.payload()
        m.retry(self.record, self.item()["item_id"], "replace interrupted attempt", run_id=self.record["run_id"], expected_attempt=m.find_item(self.record, self.item()["item_id"])["attempt"], operation_id="fixture-retry-"+str(m.find_item(self.record, self.item()["item_id"])["attempt"]))
        with self.assertRaises(m.ReviewError):
            self.apply(late)
        self.apply(self.payload())
        self.validate()

    def test_completed_item_cannot_be_retried(self):
        self.apply(self.payload())
        with self.assertRaises(m.ReviewError):
            m.retry(self.record, self.item()["item_id"], "erase result", run_id=self.record["run_id"], expected_attempt=m.find_item(self.record, self.item()["item_id"])["attempt"], operation_id="fixture-retry-"+str(m.find_item(self.record, self.item()["item_id"])["attempt"]))

    def test_foreign_run_snapshot_and_item_are_rejected(self):
        for key in ("run_id", "snapshot_identity", "item_id"):
            payload = self.payload()
            payload[key] = "foreign"
            with self.subTest(key=key), self.assertRaises(m.ReviewError):
                self.apply(payload)

    def test_rules_identity_cannot_be_omitted_or_changed(self):
        for rules in (None, "", "rules-v2"):
            with self.subTest(rules=rules), self.assertRaises(m.ReviewError):
                m.validate_record(self.record, self.repo, rules)

    def test_inventory_omission_duplicate_and_forged_state_rejected(self):
        for mutation in ("omit", "duplicate", "state", "receipt", "blob"):
            record = deepcopy(self.record)
            if mutation == "omit":
                record["items"] = []
            elif mutation == "duplicate":
                record["items"][1] = deepcopy(record["items"][0])
            elif mutation == "state":
                record["items"][0]["state"] = "waived"
            elif mutation == "receipt":
                record["items"][0]["state"] = "completed"
            else:
                record["items"][0]["old_blob"] = "0" * 40
            with self.subTest(mutation=mutation), self.assertRaises(m.ReviewError):
                self.validate(record)

    def test_stored_evidence_is_revalidated(self):
        self.apply(self.payload())
        self.item()["receipt"]["evidence"][0]["file_sha256"] = "sha256:" + "0" * 64
        with self.assertRaises(m.ReviewError):
            self.validate()

    def test_invalid_schema_and_scope_are_rejected(self):
        for schema in (1, m.SCHEMA - 1, m.SCHEMA + 1, True):
            record = deepcopy(self.record)
            record["schema_version"] = schema
            with self.assertRaises(m.ReviewError):
                self.validate(record)
        scope = dict(self.scope, changed_paths=[])
        with self.assertRaises(m.ReviewError):
            m.init_record(scope, self.repo, "r1")

    def test_floating_refs_are_rejected(self):
        scope = dict(self.scope, head="HEAD")
        with self.assertRaises(m.ReviewError):
            m.init_record(scope, self.repo, "r1")

    def test_nonancestor_is_rejected(self):
        scope = dict(self.scope, review_base=self.head, head=self.base,
                     tree=self.git("rev-parse", self.base + "^{tree}"))
        with self.assertRaises(m.ReviewError):
            m.init_record(scope, self.repo, "r1")

    def test_worktree_edits_do_not_replace_frozen_evidence(self):
        payload = self.payload()
        (self.repo / "a.py").write_text("different content\n", encoding="utf-8")
        self.apply(payload)
        self.validate()

    def test_reuse_requires_a_valid_completed_source(self):
        self.apply(self.payload())
        parent_path = self.root / "parent.json"
        m.write(parent_path, self.record)
        child = m.init_record(self.scope, self.repo, "rules-and-context-v1")
        item = self.item(record=child)
        payload = self.payload(item, "reused", child)
        payload["source"] = {"record": str(parent_path),
                             "receipt_identity": m.digest(self.item()["receipt"])}
        self.apply(payload, child)
        self.validate(child)
        self.assertEqual(m.summary(child)["reused"], 1)
        parent_path.unlink()
        with self.assertRaises(m.ReviewError):
            self.validate(child)

    def test_unlinked_reuse_cannot_pass(self):
        payload = self.payload(state="reused")
        with self.assertRaises(m.ReviewError):
            self.apply(payload)

    def test_init_retry_is_nondestructive_and_status_is_read_only(self):
        first = self.cli("init", "--scope", str(self.scope_path))
        before = self.path.read_bytes()
        second = self.cli("init", "--scope", str(self.scope_path))
        self.assertEqual(first["run_id"], second["run_id"])
        self.assertEqual(before, self.path.read_bytes())
        listing = {p.name for p in self.root.iterdir()}
        self.cli("status")
        self.assertEqual(listing, {p.name for p in self.root.iterdir()})
        self.assertEqual(before, self.path.read_bytes())

    def test_init_does_not_overwrite_foreign_file(self):
        self.path.write_text("keep this work", encoding="utf-8")
        self.cli("init", "--scope", str(self.scope_path), expected=1)
        self.assertEqual(self.path.read_text(), "keep this work")

    def test_check_rejects_partial_and_wrong_target_and_never_approves(self):
        m.write(self.path, self.record)
        self.cli("check", "--base", self.base, "--head", self.head, expected=1)
        for item in self.record["items"]:
            self.apply(self.payload(item))
        m.write(self.path, self.record)
        result = self.cli("check", "--base", self.base, "--head", self.head)
        self.assertTrue(result["execution_complete"])
        self.assertEqual(result["approval_outcome"], "not_assessed")
        self.cli("check", "--base", self.base, "--head", self.base, expected=1)

    def test_empty_review_is_skipped_not_approved(self):
        scope = dict(self.scope, review_base=self.head, changed_paths=[])
        record = m.init_record(scope, self.repo, "r1")
        result = m.summary(record)
        self.assertEqual(result["execution_state"], "skipped")
        self.assertFalse(result["execution_complete"])

    def test_pagination_preserves_total(self):
        m.write(self.path, self.record)
        result = self.cli("status", "--limit", "1")
        self.assertEqual(result["total"], 3)
        self.assertEqual(len(result["remaining"]), 1)
        self.assertEqual(result["next_offset"], 1)
        self.cli("status", "--limit", "0", expected=1)

    def test_protected_paths_and_symlinks(self):
        for name in (".env", "nested/.ssh/id_rsa", ".npmrc"):
            item = dict(self.item(), old_path=name)
            with self.subTest(name=name), self.assertRaises(m.ReviewError):
                m.evidence(self.repo, item, "head")
        item = dict(self.item(), new_mode="120000")
        with self.assertRaises(m.ReviewError):
            m.evidence(self.repo, item, "head")
        target = self.root / "target.json"
        target.write_text("protected", encoding="utf-8")
        self.path.symlink_to(target)
        self.cli("init", "--scope", str(self.scope_path), expected=1)
        self.assertEqual(target.read_text(), "protected")

    def test_record_cannot_be_written_into_reviewed_worktree(self):
        with self.assertRaises(m.ReviewError):
            m.record_destination(self.repo / "review.json", self.repo)

    def test_lock_contention_fails_without_mutation(self):
        self.cli("init", "--scope", str(self.scope_path))
        before = self.path.read_bytes()
        with m.locked(self.path):
            self.cli("retry", "--item", self.item()["item_id"], "--reason", "interrupted", expected=1)
        self.assertEqual(before, self.path.read_bytes())
        self.cli("retry", "--item", self.item()["item_id"], "--reason", "interrupted")

    def test_crlf_and_unusual_filenames_use_exact_bytes(self):
        name = " spaced\nname.py "
        (self.repo / name).write_bytes(b"a = 1\r\nb = 2\r\n")
        head = self.commit("unusual path")
        files = m.inventory(self.repo, self.head, head)
        self.assertEqual(files[0]["path"], name)
        proof = m.evidence(self.repo, files[0], "head", 2, 2)
        self.assertEqual(proof["range_sha256"], m.sha(b"b = 2\r\n"))

    def test_cli_receipt_and_recovery_round_trip(self):
        self.cli("init", "--scope", str(self.scope_path))
        record = m.load(self.path)
        item = self.item(record=record)
        payload = self.payload(item, "failed", record)
        receipt_path = self.root / "receipt.json"
        receipt_path.write_text(json.dumps(payload), encoding="utf-8")
        self.cli("receipt", "--item", item["item_id"], "--state", "failed", "--receipt", str(receipt_path))
        self.cli("retry", "--item", item["item_id"], "--reason", "resolved executor issue")
        record = m.load(self.path)
        payload = self.payload(self.item(record=record), record=record)
        receipt_path.write_text(json.dumps(payload), encoding="utf-8")
        result = self.cli("receipt", "--item", item["item_id"], "--state", "completed", "--receipt", str(receipt_path))
        self.assertEqual(result["completed"], 1)

    def test_duplicate_json_keys_are_rejected(self):
        self.path.write_text('{"schema_version": 2, "schema_version": 1}', encoding="utf-8")
        with self.assertRaises(m.ReviewError):
            m.load(self.path)

    def test_rename_inventory_retains_both_paths(self):
        self.git("mv", "a.py", "renamed.py")
        head = self.commit("rename")
        files = m.inventory(self.repo, self.head, head)
        self.assertEqual(files[0]["change_type"], "R")
        self.assertEqual(files[0]["old_path"], "a.py")
        self.assertEqual(files[0]["path"], "renamed.py")


if __name__ == "__main__":
    unittest.main()
