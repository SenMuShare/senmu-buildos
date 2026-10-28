"""Exercise actual offline runner outcomes; these are not model observations."""
import importlib.util
from pathlib import Path
import subprocess
import tempfile
import unittest

SPEC = importlib.util.spec_from_file_location('adoption_fixture', Path(__file__).parent / 'behavior/workspace_fixture.py')
FIXTURE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(FIXTURE)

# A known minimal repair proves that the fixture detects and admits real behavior.
# This oracle is never part of the generated workspace or model prompt.
REPAIR = '''#!/usr/bin/env bash
set -euo pipefail
if [ "${1:-}" != --resume ]; then bash scripts/deploy.sh; fi
bash scripts/verify.sh
status=0
bash scripts/remote-cleanup.sh || status=$?
bash scripts/cleanup.sh retention.env apply > local-cleanup.receipt || status=$?
exit "$status"
'''


class ReleaseAdoptionFixtureTests(unittest.TestCase):
    def workspace(self):
        temp = tempfile.TemporaryDirectory(); self.addCleanup(temp.cleanup)
        root = Path(temp.name)
        FIXTURE.create(root, 'release-adoption')
        return root

    def run_checks(self, root):
        return subprocess.run(['python3', '-B', '-m', 'unittest', 'discover', '-s', 'tests'],
                              cwd=root, capture_output=True, text=True)

    def test_fixture_detects_skipped_closeout_and_replayed_deployment(self):
        result = self.run_checks(self.workspace())
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('independent local cleanup was skipped', result.stderr)
        self.assertIn('verified deployment was replayed', result.stderr)

    def test_real_repair_passes_without_replacing_helper_or_tests(self):
        root = self.workspace()
        preserved = {p: (root / p).read_bytes() for p in ('scripts/cleanup.sh', 'tests/test_release.py')}
        (root / 'scripts/release.sh').write_text(REPAIR)
        result = self.run_checks(root)
        self.assertEqual(result.returncode, 0, result.stderr)
        for path, content in preserved.items():
            self.assertEqual((root / path).read_bytes(), content)

    def test_scaffold_refuses_nonempty_directory(self):
        root = self.workspace()
        before = (root / 'scripts/release.sh').read_bytes()
        with self.assertRaises(ValueError): FIXTURE.create(root, 'release-adoption')
        self.assertEqual((root / 'scripts/release.sh').read_bytes(), before)


if __name__ == '__main__': unittest.main()
