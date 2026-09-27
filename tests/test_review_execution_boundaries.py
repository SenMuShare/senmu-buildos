"""Synthetic real-Git regressions: inventory, coordinates, coverage and receipt lineage."""

from __future__ import annotations

from contextlib import contextmanager, redirect_stdout
from collections import OrderedDict
from copy import deepcopy
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills/senmu-build-assurance/scripts/manage_review_execution.py"
SPEC = importlib.util.spec_from_file_location("review_boundaries_runtime", SCRIPT)
assert SPEC and SPEC.loader
m = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(m)


class FrozenReviewBoundaryTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name).resolve()
        self.repo = self.root / "repo"
        self.repo.mkdir()
        self.git("init", "-q", "-b", "main")
        self.git("config", "user.email", "fixture@example.invalid")
        self.git("config", "user.name", "Synthetic review fixture")

    def git(self, *args):
        return subprocess.check_output(["git", "-C", str(self.repo), *args],
                                       stderr=subprocess.PIPE).decode("utf-8").rstrip("\n")

    def commit(self, message):
        self.git("add", "--all")
        self.git("commit", "-qm", message)
        return self.git("rev-parse", "HEAD")

    def make_change(self, before=b"# header\nvalue=1\n", after=b"# header\nvalue=2\n", name="a.py"):
        (self.repo / name).write_bytes(before)
        base = self.commit("base")
        (self.repo / name).write_bytes(after)
        return self.new_record(base, self.commit("change"))

    def new_record(self, base, head):
        scope = {"kind": "git_review_scope", "repository_root": str(self.repo), "unit": "CU-FIX",
                 "review_base": base, "head": head, "tree": self.git("rev-parse", head + "^{tree}"),
                 "changed_paths": [item["path"] for item in m.inventory(self.repo, base, head)]}
        return m.init_record(scope, self.repo, "fixture-rules")

    def payload(self, record, item=None, ranges=None):
        item = record["items"][0] if item is None else item
        proofs = []
        for side, prefix in (("base", "old"), ("head", "new")):
            if item[prefix + "_mode"] != "000000":
                for a, z in (ranges or {}).get(side, [(None, None)]):
                    proofs.append(m.evidence(self.repo, item, side, a, z))
        return {"run_id": record["run_id"], "snapshot_identity": record["snapshot_identity"],
                "item_id": item["item_id"], "attempt": item["attempt"], "state": "completed",
                "executor": "synthetic-fixture", "summary": "Synthetic input coverage; no semantic verdict.",
                "evidence": proofs}

    def apply(self, record, payload):
        m.apply_receipt(record, self.repo, payload["item_id"], payload["state"], payload)

    def cli(self, record_path, command, *args):
        if command == "retry" and "--run-id" not in args:
            saved = m.load(record_path)
            selected = m.find_item(saved, args[args.index("--item") + 1])
            args += ("--run-id", saved["run_id"], "--expected-attempt", str(selected["attempt"]),
                     "--operation-id", "fixture-retry-" + str(selected["attempt"]))
        argv = [str(SCRIPT), command, "--repo", str(self.repo), "--record", str(record_path),
                "--rules-identity", "fixture-rules", *args]
        output = io.StringIO()
        with patch.object(sys, "argv", argv), redirect_stdout(output):
            code = m.main()
        return code, json.loads(output.getvalue())

    def test_inventory_ignores_rename_order_and_quote_configuration(self):
        (self.repo / "old.py").write_text("value=1\n")
        (self.repo / "需求.md").write_text("一\n")
        base = self.commit("base")
        (self.repo / "old.py").rename(self.repo / "new.py")
        (self.repo / "需求.md").write_text("二\n")
        head = self.commit("rename and unicode")
        expected = m.inventory(self.repo, base, head)
        order = self.root / "order"
        order.write_text("需求.md\nnew.py\n")
        for option, value in (("diff.renames", "false"), ("diff.renameLimit", "1"),
                              ("diff.orderFile", str(order)), ("core.quotePath", "true"),
                              ("diff.relative", "true"), ("diff.ignoreSubmodules", "all")):
            self.git("config", option, value)
        self.assertEqual(m.inventory(self.repo, base, head), expected)
        self.assertEqual([item["path"] for item in expected], ["new.py", "需求.md"])
        self.assertEqual(expected[0]["old_path"], "old.py")

    def test_inventory_preserves_special_names(self):
        (self.repo / "base").write_bytes(b"x")
        base = self.commit("base")
        names = [" spaced\nname.py ", 'quote".py', "制品.md", "tab\tfile.py", ":(glob)*.py"]
        for name in names:
            (self.repo / name).write_bytes(b"value=1\n")
        head = self.commit("unusual paths")
        record = self.new_record(base, head)
        self.assertEqual({item["path"] for item in record["items"]}, set(names))
        for item in record["items"]:
            self.apply(record, self.payload(record, item))
        m.validate_record(record, self.repo, "fixture-rules")

    def test_lf_coordinates_ignore_unicode_and_control_separators(self):
        after = 'text="one\u2028two\u2029three\x85four\x0bfive\x0csix"\nanswer=2\n'.encode("utf-8")
        record = self.make_change(b'text="one"\nanswer=1\n', after)
        item = record["items"][0]
        self.assertEqual(m.evidence(self.repo, item, "head")["line_end"], 2)
        self.assertEqual(m.evidence(self.repo, item, "head", 2, 2)["range_sha256"], m.sha(b"answer=2\n"))
        blame = self.git("blame", "--line-porcelain", "-L", "2,2", record["snapshot"]["head"], "--", "a.py")
        self.assertTrue(blame.endswith("\tanswer=2"))
        self.apply(record, self.payload(record))

    def test_crlf_lone_cr_and_no_final_lf_preserve_bytes(self):
        after = b'text="a\rb"\r\nanswer=2'
        record = self.make_change(b"text=1\nanswer=1\n", after)
        item = record["items"][0]
        proof = m.evidence(self.repo, item, "head", 2, 2)
        self.assertEqual(proof["range_sha256"], m.sha(b"answer=2"))
        self.assertEqual(m.evidence(self.repo, item, "head")["line_end"], 2)
        self.apply(record, self.payload(record))

    def test_unchanged_anchor_cannot_complete_a_changed_file(self):
        record = self.make_change()
        payload = self.payload(record, ranges={"base": [(1, 1)], "head": [(1, 1)]})
        with self.assertRaisesRegex(m.ReviewError, "cover every changed range"):
            self.apply(record, payload)
        self.assertEqual(record["items"][0]["state"], "pending")

    def test_multiple_changed_ranges_can_be_submitted_on_one_side(self):
        record = self.make_change(b"a=1\n# separator\nb=1\n", b"a=2\n# separator\nb=2\n")
        payload = self.payload(record, ranges={"base": [(1, 1), (3, 3)], "head": [(1, 1), (3, 3)]})
        self.apply(record, payload)
        m.validate_record(record, self.repo, "fixture-rules")
        self.assertTrue(m.summary(record)["execution_complete"])
        self.assertEqual(m.summary(record)["quality_outcome"], "not_assessed")

    def test_missing_one_changed_block_is_rejected(self):
        record = self.make_change(b"a=1\n# separator\nb=1\n", b"a=2\n# separator\nb=2\n")
        payload = self.payload(record, ranges={"base": [(1, 1)], "head": [(1, 1)]})
        with self.assertRaises(m.ReviewError):
            self.apply(record, payload)

    def test_adjacent_ranges_cover_a_contiguous_change(self):
        record = self.make_change(b"a=1\nb=1\n", b"a=2\nb=2\n")
        payload = self.payload(record, ranges={"base": [(1, 1), (2, 2)], "head": [(1, 1), (2, 2)]})
        self.apply(record, payload)
        self.assertTrue(m.summary(record)["execution_complete"])

    def test_duplicate_proof_is_rejected(self):
        record = self.make_change()
        payload = self.payload(record)
        payload["evidence"].append(deepcopy(payload["evidence"][0]))
        with self.assertRaises(m.ReviewError):
            self.apply(record, payload)

    def test_insertions_require_existing_side_boundary_evidence(self):
        record = self.make_change(b"a=1\nb=1\nc=1\n", b"a=1\nb=1\nx=2\nc=1\n")
        required = m.changed_ranges(self.repo, record["items"][0])
        self.assertEqual(required, {"base": [(2, 2)], "head": [(3, 3)]})
        self.apply(record, self.payload(record, ranges=required))

    def test_deletions_require_surviving_side_boundary_evidence(self):
        record = self.make_change(b"a=1\nx=2\nb=1\n", b"a=1\nb=1\n")
        required = m.changed_ranges(self.repo, record["items"][0])
        self.assertEqual(required, {"base": [(2, 2)], "head": [(1, 1)]})
        self.apply(record, self.payload(record, ranges=required))

    def test_modified_empty_file_and_new_empty_file(self):
        record = self.make_change(b"", b"value=1\n")
        self.assertEqual(m.changed_ranges(self.repo, record["items"][0]), {"base": [(0, 0)], "head": [(1, 1)]})
        self.apply(record, self.payload(record))
        base = record["snapshot"]["head"]
        (self.repo / "empty.py").write_bytes(b"")
        record = self.new_record(base, self.commit("empty file"))
        self.apply(record, self.payload(record))

    def test_deleting_all_content_and_deleting_file(self):
        record = self.make_change(b"value=1\n", b"")
        self.assertEqual(m.changed_ranges(self.repo, record["items"][0])["head"], [(0, 0)])
        self.apply(record, self.payload(record))
        base = record["snapshot"]["head"]
        (self.repo / "a.py").unlink()
        record = self.new_record(base, self.commit("remove empty file"))
        self.apply(record, self.payload(record))

    def test_rename_only_and_mode_only_require_full_existing_sides(self):
        (self.repo / "a.py").write_bytes(b"a=1\nb=2\n")
        base = self.commit("base")
        (self.repo / "a.py").rename(self.repo / "b.py")
        record = self.new_record(base, self.commit("rename"))
        self.assertEqual(m.changed_ranges(self.repo, record["items"][0]), {"base": [(1, 2)], "head": [(1, 2)]})
        with self.assertRaises(m.ReviewError):
            self.apply(record, self.payload(record, ranges={"base": [(1, 1)], "head": [(1, 1)]}))
        self.apply(record, self.payload(record))
        base = record["snapshot"]["head"]
        (self.repo / "b.py").chmod(0o755)
        record = self.new_record(base, self.commit("executable mode"))
        self.apply(record, self.payload(record))

    def mixed_parent(self):
        (self.repo / "a.py").write_bytes(b"a=1\n")
        (self.repo / "b.py").write_bytes(b"b=1\n")
        base = self.commit("base")
        (self.repo / "a.py").write_bytes(b"a=2\n")
        (self.repo / "b.py").write_bytes(b"b=2\n")
        head = self.commit("changes")
        a = self.new_record(base, head)
        for item in a["items"]:
            self.apply(a, self.payload(a, item))
        pa = self.root / "a.json"
        m.write(pa, a)
        b = self.new_record(base, head)
        reuse = self.payload(b, b["items"][0])
        reuse.update(state="reused", source={"record": str(pa), "receipt_identity": m.digest(a["items"][0]["receipt"])})
        self.apply(b, reuse)
        self.apply(b, self.payload(b, b["items"][1]))
        pb = self.root / "b.json"
        m.write(pb, b)
        c = self.new_record(base, head)
        payload = self.payload(c, c["items"][1])
        payload.update(state="reused", source={"record": str(pb), "receipt_identity": m.digest(b["items"][1]["receipt"])})
        return b, pb, c, payload

    def test_unrelated_reuse_does_not_block_direct_completed_source(self):
        b, pb, c, payload = self.mixed_parent()
        self.assertEqual([item["state"] for item in b["items"]], ["reused", "completed"])
        self.apply(c, payload)
        m.validate_record(c, self.repo, "fixture-rules")
        self.assertEqual(c["items"][1]["state"], "reused")

    def test_actual_reuse_chain_is_still_rejected(self):
        b, pb, c, _ = self.mixed_parent()
        payload = self.payload(c, c["items"][0])
        payload.update(state="reused", source={"record": str(pb), "receipt_identity": m.digest(b["items"][0]["receipt"])})
        with self.assertRaisesRegex(m.ReviewError, "directly completed"):
            self.apply(c, payload)

    def test_source_proof_tampering_is_not_hidden_by_targeted_validation(self):
        b, pb, c, payload = self.mixed_parent()
        b["items"][1]["receipt"]["evidence"][0]["range_sha256"] = "sha256:" + "0" * 64
        payload["source"]["receipt_identity"] = m.digest(b["items"][1]["receipt"])
        m.write(pb, b)
        with self.assertRaises(m.ReviewError):
            self.apply(c, payload)

    def test_source_inventory_tampering_is_still_rejected(self):
        b, pb, c, payload = self.mixed_parent()
        b["items"].pop(0)
        m.write(pb, b)
        with self.assertRaises(m.ReviewError):
            self.apply(c, payload)

    def test_source_missing_and_foreign_snapshot_are_rejected(self):
        b, pb, c, payload = self.mixed_parent()
        original = pb.read_bytes()
        pb.unlink()
        with self.assertRaises(m.ReviewError):
            self.apply(c, payload)
        pb.write_bytes(original)
        b["snapshot"]["rules_identity"] = "other-rules"
        b["snapshot_identity"] = m.digest(b["snapshot"])
        m.write(pb, b)
        with self.assertRaises(m.ReviewError):
            self.apply(c, payload)

    def test_legacy_schema_is_rejected_and_never_overwritten(self):
        record = self.make_change()
        legacy = deepcopy(record)
        legacy["schema_version"] = 2
        record_path = self.root / "legacy.json"
        m.write(record_path, legacy)
        before = record_path.read_bytes()
        code, output = self.cli(record_path, "status")
        self.assertEqual(code, 1)
        self.assertIn("separate schema-3 record", output["reason"])
        self.assertEqual(record_path.read_bytes(), before)
        self.assertEqual(record["schema_version"], 3)

    def test_malformed_snapshot_mutations_fail_as_json_without_writes(self):
        record = self.make_change()
        path = self.root / "malformed.json"
        for snapshot in (None, [], "invalid"):
            malformed = deepcopy(record)
            malformed["snapshot"] = snapshot
            m.write(path, malformed)
            before = path.read_bytes()
            for command, extra in (("retry", ("--item", record["items"][0]["item_id"], "--reason", "fixture")),
                                   ("receipt", ("--item", record["items"][0]["item_id"], "--state", "completed", "--receipt", str(path)))):
                with self.subTest(snapshot=snapshot, command=command):
                    code, output = self.cli(path, command, *extra)
                    self.assertEqual(code, 1)
                    self.assertEqual(output["status"], "blocked")
                    self.assertEqual(path.read_bytes(), before)

    def test_final_check_revalidates_evidence_on_every_invocation(self):
        record = self.make_change()
        self.apply(record, self.payload(record))
        path = self.root / "record.json"
        m.write(path, record)
        args = ("--base", record["snapshot"]["review_base"], "--head", record["snapshot"]["head"])
        self.assertEqual(self.cli(path, "check", *args)[0], 0)
        record["items"][0]["receipt"]["evidence"][0]["file_sha256"] = "sha256:" + "f" * 64
        m.write(path, record)
        self.assertEqual(self.cli(path, "check", *args)[0], 1)

    def test_retry_and_late_result_rules_survive_incremental_validation(self):
        record = self.make_change()
        old = self.payload(record)
        m.retry(record, old["item_id"], "interrupted fixture", run_id=record["run_id"], expected_attempt=m.find_item(record, old["item_id"])["attempt"], operation_id="fixture-retry-" + str(m.find_item(record, old["item_id"])["attempt"]))
        with self.assertRaises(m.ReviewError):
            self.apply(record, old)
        current = self.payload(record)
        self.apply(record, current)
        saved = deepcopy(record)
        self.apply(record, current)
        self.assertEqual(record, saved)
        with self.assertRaises(m.ReviewError):
            m.retry(record, current["item_id"], "erase completion", run_id=record["run_id"], expected_attempt=m.find_item(record, current["item_id"])["attempt"], operation_id="fixture-retry-" + str(m.find_item(record, current["item_id"])["attempt"]))

    def test_unsupported_content_never_becomes_completed(self):
        record = self.make_change(b"a=1\n", b"\x00binary")
        path = self.root / "record.json"
        m.write(path, record)
        code, output = self.cli(path, "evidence", "--item", record["items"][0]["item_id"], "--side", "head")
        self.assertEqual(code, 1)
        self.assertIn("binary", output["reason"])
        self.assertFalse(m.summary(record)["execution_complete"])

    def test_sensitive_old_path_is_guarded_before_any_blob_read(self):
        record = self.make_change()
        item = dict(record["items"][0], old_path=".env")
        with patch.object(m, "git", side_effect=AssertionError("content read")):
            with self.assertRaises(m.ReviewError):
                m.evidence(self.repo, item, "head")
            with _cache_scope():
                with self.assertRaises(m.ReviewError):
                    m.preload_evidence(self.repo, [item])

    def test_file_size_cap_applies_before_content_read(self):
        record = self.make_change()
        with patch.object(m, "MAX_BYTES", 8):
            with self.assertRaisesRegex(m.ReviewError, "bounded evidence support"):
                m.evidence(self.repo, record["items"][0], "head")

    def test_preload_retains_size_guard_and_bounded_fallback(self):
        record = self.make_change()
        self.apply(record, self.payload(record))
        with patch.object(m, "MAX_BYTES", 8):
            with self.assertRaisesRegex(m.ReviewError, "bounded evidence support"):
                m.validate_record(record, self.repo, "fixture-rules")
        with patch.object(m, "CACHE_BYTES", 16):
            m.validate_record(record, self.repo, "fixture-rules")
        self.assertIsNone(m._GIT_CACHE.get())

    def test_last_receipt_avoids_repeated_whole_record_git_reads(self):
        for n in range(20):
            (self.repo / f"f{n:03d}.py").write_text(f"value={n}\n")
        base = self.commit("base")
        for n in range(20):
            (self.repo / f"f{n:03d}.py").write_text(f"value={n+1}\n")
        record = self.new_record(base, self.commit("changes"))
        for item in record["items"][:-1]:
            item.update(state="completed", receipt=self.payload(record, item))
        path = self.root / "record.json"
        m.write(path, record)
        last = record["items"][-1]
        payload = self.payload(record, last)
        incoming = self.root / "incoming.json"
        incoming.write_text(json.dumps(payload))
        original_run = subprocess.run
        calls = []
        def tracked(command, *args, **kwargs):
            if command[0] == "git":
                calls.append(command[3:])
            return original_run(command, *args, **kwargs)
        with patch.object(subprocess, "run", tracked):
            code, output = self.cli(path, "receipt", "--item", last["item_id"], "--state", "completed", "--receipt", str(incoming))
        self.assertEqual(code, 0)
        self.assertTrue(output["execution_complete"])
        self.assertLess(len(calls), 50, calls)
        self.assertEqual(sum(call[:2] == ["cat-file", "--batch"] for call in calls), 1)


# Supply only a per-operation cache for the preflight guard unit test.
@contextmanager
def _cache_scope():
    token = m._GIT_CACHE.set(OrderedDict())
    try:
        yield
    finally:
        m._GIT_CACHE.reset(token)


if __name__ == "__main__":
    unittest.main()
