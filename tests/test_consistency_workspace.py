"""Execute fixture setup and business checks; no host model invocation is simulated."""
import importlib.util
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
p=ROOT/'tests/behavior/workspace_fixture.py'
spec=importlib.util.spec_from_file_location('workspace_fixture',p)
f=importlib.util.module_from_spec(spec);spec.loader.exec_module(f)

class WorkspaceFixtureTests(unittest.TestCase):
    def test_real_business_test_fails_before_and_passes_after_local_fix(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);f.create(root)
            legacy=(root/'pricing/legacy_v1.py').read_bytes()
            # Both executions read source; an equal-size edit within one timestamp
            # tick must not accidentally reuse the first execution's bytecode.
            command=[sys.executable,'-B','-m','unittest','discover','-s','tests','-p','test_totals.py']
            before=subprocess.run(command,cwd=root,capture_output=True,text=True)
            self.assertNotEqual(before.returncode,0)
            p=root/'pricing/totals.py';p.write_text(p.read_text().replace('subtotal + discount','subtotal - discount'))
            after=subprocess.run(command,cwd=root,capture_output=True,text=True)
            self.assertEqual(after.returncode,0,after.stderr)
            self.assertEqual((root/'pricing/legacy_v1.py').read_bytes(),legacy)
    def test_second_setup_refuses_to_overwrite_existing_project(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);f.create(root)
            before={p.relative_to(root).as_posix():p.read_bytes() for p in root.rglob('*') if p.is_file()}
            with self.assertRaises(ValueError):f.create(root)
            after={p.relative_to(root).as_posix():p.read_bytes() for p in root.rglob('*') if p.is_file()}
            self.assertEqual(before,after)
    def test_map_points_to_real_nested_rules_and_implementation(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);f.create(root)
            for name in ('pricing/totals.py','pricing/AGENTS.md','jobs/admission.py','docs/SECURITY.md'):
                self.assertIn(name,(root/'docs/PROJECT_MAP.md').read_text());self.assertTrue((root/name).is_file())
            self.assertEqual((root/'CLAUDE.md').read_text(),'@AGENTS.md\n')

class ExtendedWorkspaceFixtureTests(unittest.TestCase):
    def test_non_git_probe_ignores_inherited_git_location_overrides(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            subprocess.run(['git', '-C', str(repo), 'init', '-q'], check=True)
            root = repo / 'documents'
            root.mkdir()
            with patch.dict(f.os.environ, {'GIT_DIR': str(repo / 'missing'),
                                           'GIT_CEILING_DIRECTORIES': str(repo)}):
                with self.assertRaisesRegex(ValueError, 'outside any Git repository'):
                    f.create(root, 'non-git')
            self.assertEqual(list(root.iterdir()), [])

    def test_non_git_case_refuses_a_repository_subdirectory_without_writes(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            subprocess.run(['git', '-C', str(repo), 'init', '-q'], check=True)
            root = repo / 'documents'
            root.mkdir()
            with self.assertRaisesRegex(ValueError, 'outside any Git repository'):
                f.create(root, 'non-git')
            self.assertEqual(list(root.iterdir()), [])

    def test_non_git_case_keeps_archive_and_has_no_repository(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            f.create(root, 'non-git')
            self.assertFalse((root / '.git').exists())
            self.assertEqual({p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file()},
                             set(f.NON_GIT_FILES))
            self.assertEqual((root / 'archive/previous.md').read_text(),
                             f.NON_GIT_FILES['archive/previous.md'])
            self.assertIn('handouts/current.md', (root / 'README.md').read_text())

    def check_repair(self, case, filename, before_text, after_text, test_name, failure_name):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            f.create(root, case)
            command = [sys.executable, '-B', '-m', 'unittest', 'discover', '-s', 'tests', '-p', test_name]
            before = subprocess.run(command, cwd=root, capture_output=True, text=True)
            self.assertNotEqual(before.returncode, 0)
            self.assertIn(failure_name, before.stderr)
            path = root / filename
            path.write_text(path.read_text().replace(before_text, after_text))
            after = subprocess.run(command, cwd=root, capture_output=True, text=True)
            self.assertEqual(after.returncode, 0, after.stderr)
            return {p.relative_to(root).as_posix(): p.read_text() for p in root.rglob('*.py')}

    def test_multistep_bug_is_observed_and_repaired_at_its_owner(self):
        self.check_repair('hard-bug', 'jobs/state.py', 'if event == "complete":',
                          'if event == "complete" and state == "running":',
                          'test_events.py', 'test_late_completion_after_cancel')

    def test_recovery_preserves_completed_scope(self):
        files = self.check_repair('resume', 'pricing/receipt.py',
                                 'return f"Total: {amount}" if amount else ""',
                                 'return f"Total: {amount}"',
                                 'test_*.py', 'test_zero')
        self.assertEqual(files['pricing/legacy_v1.py'], f.FILES['pricing/legacy_v1.py'])
        self.assertEqual(files['pricing/totals.py'], f.RESUME_FILES['pricing/totals.py'])

    def test_local_repair_is_executable_while_external_scope_waits(self):
        files = self.check_repair('waiting', 'pricing/receipt.py',
                                 'return f"Total: {amount}" if amount else ""',
                                 'return f"Total: {amount}"', 'test_*.py', 'test_zero')
        self.assertEqual(files['pricing/legacy_v1.py'], f.FILES['pricing/legacy_v1.py'])
        self.assertEqual(files['pricing/totals.py'], f.RESUME_FILES['pricing/totals.py'])

    def test_release_entry_detects_skipped_local_cleanup_and_preserves_prerequisites(self):
        self.check_repair('release-closeout', 'scripts/release.sh',
                         'bash scripts/remote-cleanup.sh\nbash scripts/cleanup.sh retention.env apply > local-cleanup.receipt',
                         'remote_rc=0\nbash scripts/remote-cleanup.sh || remote_rc=$?\n'
                         'local_rc=0\nbash scripts/cleanup.sh retention.env apply > local-cleanup.receipt || local_rc=$?\n'
                         'if (( local_rc )); then exit "$local_rc"; fi\nexit "$remote_rc"',
                         'test_release.py', 'test_remote_retention_failure')

    def test_unknown_case_does_not_write_anything(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            with self.assertRaises(ValueError):
                f.create(root, 'unknown')
            self.assertEqual(list(root.iterdir()), [])

if __name__=='__main__':unittest.main()
