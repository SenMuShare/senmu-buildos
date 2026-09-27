"""Exercise the installed reference selector, not model adherence or token savings."""
import importlib.util
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("guidance", ROOT / "skills/senmu-build-engineering/scripts/resolve_engineering_guidance.py")
m = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(m)

class GuidanceSelectionTests(unittest.TestCase):
    def refs(self, result):
        return [Path(x["reference"]).name for x in result["references"]]
    def test_python_does_not_preload_other_languages(self):
        result = m.select(["src/a.py"], [])
        self.assertEqual(self.refs(result), ["python-engineering-profile.md"])
        self.assertFalse(result["project_rules_included"])
        self.assertIsNone(result["token_usage"])
    def test_every_supported_extension_routes_to_existing_reference(self):
        for ext, language in m.EXTENSIONS.items():
            with self.subTest(ext=ext):
                self.assertIn(Path(m.PROFILES[language]).name, self.refs(m.select(["src/a" + ext], [])))
    def test_rust_manifest_and_cost_boundary_are_composed(self):
        result = m.select(["src/task.rs", "Cargo.toml"], ["paid-api"])
        self.assertEqual(set(self.refs(result)), {"rust-engineering-profile.md", "dependency-and-ci-review.md", "application-security-and-abuse.md"})
    def test_shared_profiles_are_not_duplicated(self):
        result = m.select(["src/a.cpp", "src/b.c"], [])
        self.assertEqual(len(result["references"]), 1)
        self.assertEqual(len(result["references"][0]["subjects"]), 2)
    def test_header_requires_language(self):
        result = m.select(["include/a.h"], [])
        self.assertEqual(result["status"], "partial")
        self.assertEqual(result["references"], [])
        self.assertEqual(len(m.select(["include/a.h"], [], header_language="c")["references"]), 1)
    def test_node_typescript_loads_runtime_browser_does_not(self):
        self.assertIn("javascript-node-engineering-profile.md", self.refs(m.select(["src/a.ts"], [], "node")))
        self.assertNotIn("javascript-node-engineering-profile.md", self.refs(m.select(["src/a.ts"], [], "browser")))
    def test_public_service_includes_both_security_owners(self):
        self.assertEqual(set(self.refs(m.select([], ["public-service"]))), {"application-security-and-abuse.md", "public-service-security-baseline.md"})
    def test_file_roles_not_just_suffix(self):
        self.assertIn("dependency-and-ci-review.md", self.refs(m.select([".github/workflows/test.yml"], [])))
        self.assertIn("public-service-security-baseline.md", self.refs(m.select(["compose.yaml"], [])))
        self.assertEqual(m.select(["misc.yaml"], [])["status"], "partial")
    def test_schema_roles(self):
        for name in ("db/a.sql", "api/a.proto", "api/a.graphql", "prisma/schema.prisma"):
            self.assertIn("schema-and-migration-review.md", self.refs(m.select([name], [])))
    def test_order_and_duplicates_do_not_change_identity(self):
        a = m.select(["a.py", "b.rs", "a.py"], ["paid-api", "dependency"])
        b = m.select(["b.rs", "a.py"], ["dependency", "paid-api"])
        self.assertEqual(a["reference_selection_identity"], b["reference_selection_identity"])
    def test_changed_selected_reference_changes_identity(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            p = root / m.ENGINEERING / m.PROFILES["python"]
            p.parent.mkdir(parents=True); p.write_text("first")
            a = m.select(["a.py"], [], root=root)
            p.write_text("second")
            b = m.select(["a.py"], [], root=root)
            self.assertNotEqual(a["reference_selection_identity"], b["reference_selection_identity"])
    def test_bad_input_is_rejected(self):
        for path in ("../a.py", "/a.py", "C:/a.py", "a\\b.py", "a\nb.py", "./a.py"):
            with self.subTest(path=path), self.assertRaises(ValueError): m.select([path], [])
        with self.assertRaises(ValueError): m.select([], [])
        with self.assertRaises(ValueError): m.select(["a.py"], ["unknown"])
    def test_unknown_stack_stays_explicit(self):
        result = m.select(["a.m", "README.md", "a.nim"], [])
        self.assertEqual(len(result["unresolved"]), 3)
        self.assertFalse(result["source_scanned"])
    def test_missing_reference_cannot_produce_a_valid_identity(self):
        with tempfile.TemporaryDirectory() as raw, self.assertRaises(ValueError):
            m.select(["a.py"], [], root=Path(raw))

if __name__ == "__main__": unittest.main()
