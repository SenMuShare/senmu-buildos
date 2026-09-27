"""Exercise bounded navigation against actual temporary maps and files."""
import importlib.util
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("entry_context", ROOT / "skills/senmu-build-project/scripts/prepare_task_context.py")
m = importlib.util.module_from_spec(SPEC); SPEC.loader.exec_module(m)

class TaskEntryTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.root = Path(self.tmp.name)
        for name in ("src/order.py", "src/media.py", "tests/test_order.py", "engineering/contracts.md"):
            p = self.root/name; p.parent.mkdir(parents=True, exist_ok=True); p.write_text("fixture\n")
        self.path = self.root / "governance/PROJECT_MAP.md"; self.path.parent.mkdir()
        self.text = """# Map
## 责任与入口地图
| Capability | Responsibility | Implementation | Contract | Verification | State/delivery |
| --- | --- | --- | --- | --- | --- |
| Order checkout | settle an order | `src/order.py` | [contract](../engineering/contracts.md) | `tests/test_order.py` | order store/application |
| Media rendering | render a video | `src/media.py` | not yet calibrated | not yet calibrated | worker |
## Other
Not part of the table.
"""
        self.path.write_text(self.text)
    def tearDown(self): self.tmp.cleanup()
    def get(self, **kwargs):
        return m.prepare(self.root, "governance/PROJECT_MAP.md", kwargs.pop("capability", "Order checkout"), **kwargs)
    def test_exact_owner_and_nearest_check_without_source_reads(self):
        result = self.get()
        self.assertEqual(result["status"], "selected")
        self.assertNotIn("Media rendering", str(result))
        self.assertEqual({x["target"] for x in result["targets"]}, {"src/order.py", "engineering/contracts.md", "tests/test_order.py"})
        self.assertEqual(result["source_bodies_read"], 0)
        self.assertFalse(result["semantic_route_verified"])
    def test_planned_or_unresolved_is_not_verified(self):
        result = self.get(capability="Media rendering")
        self.assertEqual(result["status"], "gaps")
        self.assertTrue(result["gaps"])
    def test_stale_implementation_is_visible(self):
        (self.root/"src/order.py").unlink()
        self.assertIn("route missing", str(self.get()["gaps"]))
    def test_unknown_or_ambiguous_owner_not_guessed(self):
        with self.assertRaises(ValueError): self.get(capability="Order")
        self.path.write_text(self.text.replace("| Media rendering |", "| Order checkout |"))
        with self.assertRaises(ValueError): self.get()
    def test_embedded_shell_is_never_executed(self):
        self.path.write_text(self.text.replace("`tests/test_order.py`", "`touch SENTINEL`"))
        result = self.get()
        self.assertEqual(result["commands_executed"], 0)
        self.assertFalse((self.root/"SENTINEL").exists())
        self.assertEqual(result["status"], "gaps")
    def test_outside_link_stays_a_gap(self):
        self.path.write_text(self.text.replace("../engineering/contracts.md", "../../outside.md"))
        self.assertIn("route outside", str(self.get()["gaps"]))
    def test_map_identity_changes_not_mutated(self):
        before = self.path.read_bytes(); a = self.get()
        self.assertEqual(before, self.path.read_bytes())
        self.path.write_text(self.text + "Updated note.\n")
        self.assertNotEqual(a["map_sha256"], self.get()["map_sha256"])
    def test_localized_heading(self):
        self.path.write_text(self.text.replace("## 责任与入口地图", "## Capabilities"))
        self.assertEqual(self.get(heading="## Capabilities")["status"], "selected")
    def test_invalid_path_and_symlink(self):
        with self.assertRaises(ValueError): m.prepare(self.root, "../map.md", "Order checkout")
        link = self.root/"alias.md"; link.symlink_to(self.path)
        with self.assertRaises(ValueError): m.prepare(self.root, "alias.md", "Order checkout")
    def test_fenced_fake_owner_is_not_selected(self):
        self.path.write_text("```md\n"+self.text+"```\n")
        with self.assertRaises(ValueError): self.get()
    def test_oversized_map_is_bounded(self):
        self.path.write_bytes(b"x"*(m.MAX_MAP_BYTES+1))
        with self.assertRaises(ValueError): self.get()

if __name__ == "__main__": unittest.main()
