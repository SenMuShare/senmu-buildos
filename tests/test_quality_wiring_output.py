"""Diagnostic matching tests; real tool behavior is exercised separately."""
import importlib.util
from pathlib import Path
import sys
import tempfile
import unittest

PATH = Path(__file__).parent / "recipes/check_quality_wiring.py"
SPEC = importlib.util.spec_from_file_location("quality_wiring", PATH)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class QualityOutputTests(unittest.TestCase):
    def invoke(self, output, status, expected):
        with tempfile.TemporaryDirectory() as directory:
            command = [sys.executable, "-c", f"import sys; print({output!r}); sys.exit({status})"]
            return MODULE.run(command, Path(directory), failure=expected)

    def test_color_does_not_hide_a_specific_failed_contract(self):
        result = self.invoke("Domain stays independent of adapters \x1b[31mBROKEN\x1b[0m", 1,
                             "Domain stays independent of adapters BROKEN")
        self.assertEqual(result["exit_code"], 1)

    def test_unrelated_failure_is_not_a_negative_control(self):
        with self.assertRaises(AssertionError):
            self.invoke("missing executable", 1, "pricing-public-entry")

    def test_zero_exit_with_matching_words_is_not_a_failure(self):
        with self.assertRaises(AssertionError):
            self.invoke("pricing-public-entry", 0, "pricing-public-entry")


if __name__ == "__main__":
    unittest.main()
