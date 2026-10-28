import importlib.util
from pathlib import Path
import tempfile
import subprocess
import sys
import unittest
from unittest.mock import patch

FILE = Path(__file__).resolve().parents[1] / 'skills/senmu-build-workflow/scripts/safe_local_cleanup.py'
spec = importlib.util.spec_from_file_location('cleanup', FILE)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class CleanupTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name).resolve()
        self.root = self.base / 'project'
        self.root.mkdir()
        self.trash = self.base / 'fixture-trash'
        self.trash.mkdir()
        self.calls = []

    def file(self, name='cache/file'):
        p = self.root / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text('fixture')
        return p

    def plan(self, *targets):
        return m.make_plan(str(self.root), [str(p) for p in targets], 'fixture-authority')

    def move(self, p):
        self.calls.append(p)
        dest = self.trash / p.name
        p.rename(dest)
        return {'ok': True, 'destination': str(dest)}

    def test_file_and_directory_receipts(self):
        for directory in (False, True):
            f = self.file('dir' + str(directory) + '/file')
            p = f.parent if directory else f
            result = m.execute(self.plan(p), True, self.move)
            self.assertTrue(result['complete'])
            self.assertEqual(result['results'][0]['status'], 'confirmed_trashed')
            self.assertEqual(result['disk_bytes_reclaimed'], 'not_measured')

    def test_root_outside_traversal_wildcards(self):
        f = self.file()
        for target in (self.root, self.base, str(self.root) + '/cache/../cache/file', str(self.root) + '/*', ''):
            with self.subTest(target=target), self.assertRaises((m.Rejected, OSError)):
                self.plan(target)

    def test_nested_git_file_and_directory_reject_parent(self):
        for directory in (False, True):
            p = self.file(str(directory) + '/nested/file').parent
            git = p / '.git'
            git.mkdir() if directory else git.write_text('gitdir: fixture')
            with self.assertRaises(m.Rejected):
                self.plan(p.parent)
            with self.assertRaises(m.Rejected):
                self.plan(p / 'file')

    def test_symlink_descendant_and_ancestor(self):
        f = self.file()
        (f.parent / 'link').symlink_to(f)
        with self.assertRaises(m.Rejected):
            self.plan(f.parent)
        link = self.root / 'alias'
        link.symlink_to(f.parent)
        with self.assertRaises(m.Rejected):
            self.plan(link / 'file')

    def test_overlapping_and_duplicate_targets(self):
        f = self.file()
        for targets in ((f, f), (f.parent, f)):
            with self.assertRaises(m.Rejected):
                self.plan(*targets)

    def test_scan_limits_and_mount_reject(self):
        f = self.file()
        for name, value in (('MAX_ITEMS', 1), ('MAX_DEPTH', 0), ('MAX_SECONDS', -1)):
            with patch.object(m, name, value), self.assertRaises(m.Rejected):
                self.plan(f.parent)
        with patch.object(m.os.path, 'ismount', return_value=True), self.assertRaises(m.Rejected):
            self.plan(f)

    def test_unreadable_descendant(self):
        f = self.file()
        f.chmod(0)
        try:
            with self.assertRaises(m.Rejected):
                self.plan(f.parent)
        finally:
            f.chmod(0o600)

    def test_changed_or_tampered_plan_zero_calls(self):
        f = self.file()
        plan = self.plan(f.parent)
        f.write_text('modified')
        with self.assertRaises(m.Rejected):
            m.execute(plan, True, self.move)
        plan = self.plan(f)
        plan['items'][0]['path'] = str(self.root)
        with self.assertRaises(m.Rejected):
            m.execute(plan, True, self.move)
        self.assertEqual(self.calls, [])

    def test_writer_assertion_and_unsupported_platform(self):
        plan = self.plan(self.file())
        with self.assertRaises(m.Rejected):
            m.execute(plan, False, self.move)
        with patch.object(m.platform, 'system', return_value='Windows'), self.assertRaises(m.Rejected):
            m.execute(plan, True)
        self.assertEqual(self.calls, [])

    def test_partial_batch_stops(self):
        a, b, c = [self.file(n) for n in ('a', 'b', 'c')]
        def backend(p):
            if p == b:
                raise OSError('fixture failure')
            return self.move(p)
        r = m.execute(self.plan(a, b, c), True, backend)
        self.assertEqual([i['status'] for i in r['results']], ['confirmed_trashed', 'confirmed_retained', 'not_called'])
        self.assertFalse(r['complete'])
        self.assertTrue(c.exists())

    def test_cancel_after_move_stops(self):
        a, b = self.file('a'), self.file('b')
        def backend(p):
            return dict(self.move(p), cancelled=True)
        r = m.execute(self.plan(a, b), True, backend)
        self.assertEqual([i['status'] for i in r['results']], ['confirmed_trashed', 'not_called'])
        self.assertFalse(r['complete'])

    def test_missing_receipt_is_unknown(self):
        a, b = self.file('a'), self.file('b')
        def backend(p):
            self.move(p)
            raise TimeoutError()
        r = m.execute(self.plan(a, b), True, backend)
        self.assertEqual([i['status'] for i in r['results']], ['unknown', 'not_called'])

    def test_partial_directory_change_is_unknown(self):
        f = self.file()
        def backend(p):
            self.move(f)
            raise OSError()
        r = m.execute(self.plan(f.parent), True, backend)
        self.assertEqual(r['results'][0]['status'], 'unknown')

    def test_change_remaining_target_during_batch(self):
        a, b = self.file('a'), self.file('b')
        def backend(p):
            b.write_text('changed')
            return self.move(p)
        r = m.execute(self.plan(a, b), True, backend)
        self.assertEqual([i['status'] for i in r['results']], ['confirmed_trashed', 'rejected_before_call'])
        self.assertEqual(self.calls, [a])

    def test_native_backend_has_no_delete_fallback(self):
        self.assertIn('trashItemAtURLResultingItemURLError', m.JXA)
        self.assertIn('NSURLVolumeIsLocalKey', m.JXA)
        self.assertNotIn('removeItem', m.JXA)
        self.assertNotIn('unlink', FILE.read_text().split('def native_trash')[1].split('def execute')[0].replace('remove/unlink/purge', ''))

    @unittest.skipUnless(sys.platform == 'darwin' and Path('/usr/bin/osascript').is_file(), 'macOS JXA bridge required')
    def test_native_object_out_parameters_with_readonly_foundation_calls(self):
        # Exercise the production receipt code with real NSObject out values.
        # Replace only the mutating call; this test never invokes native Trash.
        source = self.file()
        call = '$.NSFileManager.defaultManager.trashItemAtURLResultingItemURLError(url, destination, error)'
        self.assertIn(call, m.JXA)
        for readonly, expected in (
            ('url.getResourceValueForKeyError(destination, $.NSURLParentDirectoryURLKey, error)',
             {'ok': True, 'destination': str(source.parent), 'error': None, 'cancelled': False}),
            ("!$.NSFileManager.defaultManager.attributesOfItemAtPathError(argv[0] + '.missing', error).isNil()",
             {'ok': False, 'destination': None, 'error': 'native_error_260', 'cancelled': False}),
        ):
            with self.subTest(expected=expected), patch.object(m, 'JXA', m.JXA.replace(call, readonly)):
                self.assertEqual(m.native_trash(source), expected)
        self.assertTrue(source.exists())

    def process_backend(self, mode):
        """Exercise subprocess results using ordinary fixture moves, never Trash."""
        real_run = subprocess.run
        code = '''import json, os, signal, sys, time
from pathlib import Path
source, destination, mode = sys.argv[1:]
Path(source).rename(destination)
output = json.dumps({'ok': True, 'destination': destination})
if mode in ('missing', 'timeout_missing'): output = ''
if mode == 'malformed': output = '{'
if mode == 'oversized': output = 'x' * 8193
if mode == 'invalid_protocol': output = json.dumps({'ok': 'yes', 'destination': destination})
if mode == 'mismatched_identity':
    decoy = destination + '-decoy'
    Path(decoy).write_text('fixture')
    output = json.dumps({'ok': True, 'destination': decoy})
print(output, flush=True)
if mode.startswith('timeout'): time.sleep(5)
if mode == 'signal': os.kill(os.getpid(), signal.SIGTERM)
sys.exit(19)
'''
        def backend(path):
            def run(command, **kwargs):
                self.assertEqual(command[:3], ['/usr/bin/osascript', '-l', 'JavaScript'])
                kwargs['timeout'] = 0.5 if mode.startswith('timeout') else 5
                return real_run([sys.executable, '-c', code, str(path), str(self.trash / path.name), mode], **kwargs)
            with patch.object(m.subprocess, 'run', side_effect=run):
                return m.native_trash(path)
        return backend

    def test_nonzero_process_receipt_is_verified_but_stops_batch(self):
        a, b = self.file('a'), self.file('b')
        r = m.execute(self.plan(a, b), True, self.process_backend('nonzero'))
        item = r['results'][0]
        self.assertEqual([i['status'] for i in r['results']], ['confirmed_trashed', 'not_called'])
        self.assertEqual(item['destination'], str(self.trash / 'a'))
        self.assertEqual(item['backend_returncode'], 19)
        self.assertFalse(item['backend_ok'])
        self.assertFalse(r['complete'])
        self.assertTrue(b.exists())

    def test_signal_process_receipt_keeps_signal_and_stops_batch(self):
        a, b = self.file('a'), self.file('b')
        r = m.execute(self.plan(a, b), True, self.process_backend('signal'))
        item = r['results'][0]
        self.assertEqual([i['status'] for i in r['results']], ['confirmed_trashed', 'not_called'])
        self.assertEqual(item['backend_returncode'], -15)
        self.assertEqual(item['backend_signal'], 15)
        self.assertFalse(item['backend_ok'])
        self.assertFalse(r['complete'])

    def test_timeout_complete_receipt_is_verified_but_stops_batch(self):
        a, b = self.file('a'), self.file('b')
        r = m.execute(self.plan(a, b), True, self.process_backend('timeout'))
        item = r['results'][0]
        self.assertEqual([i['status'] for i in r['results']], ['confirmed_trashed', 'not_called'])
        self.assertTrue(item['backend_timeout'])
        self.assertFalse(item['backend_ok'])
        self.assertFalse(r['complete'])

    def test_nonzero_process_without_valid_receipt_remains_unknown(self):
        for mode in ('missing', 'malformed', 'oversized', 'invalid_protocol', 'mismatched_identity'):
            with self.subTest(mode=mode):
                a, b = self.file('a-' + mode), self.file('b-' + mode)
                r = m.execute(self.plan(a, b), True, self.process_backend(mode))
                item = r['results'][0]
                self.assertEqual([i['status'] for i in r['results']], ['unknown', 'not_called'])
                self.assertIsNone(item['destination'])
                self.assertEqual(item['backend_returncode'], 19)
                self.assertFalse(item['backend_ok'])
                self.assertFalse(r['complete'])

    def test_timeout_without_receipt_remains_unknown_and_stops_batch(self):
        a, b = self.file('a'), self.file('b')
        r = m.execute(self.plan(a, b), True, self.process_backend('timeout_missing'))
        item = r['results'][0]
        self.assertEqual([i['status'] for i in r['results']], ['unknown', 'not_called'])
        self.assertIsNone(item['destination'])
        self.assertTrue(item['backend_timeout'])
        self.assertFalse(item['backend_ok'])
        self.assertFalse(r['complete'])

    def init_git(self, path, bare=False):
        subprocess.run(['git', 'init', '-q'] + (['--bare'] if bare else []) + [str(path)], check=True)

    def test_bare_storage_target_ancestor_and_descendant_rejected(self):
        repo = self.root / 'cache' / 'repository'
        self.init_git(repo, bare=True)
        for target in (repo, repo.parent, repo / 'objects'):
            with self.subTest(target=target), self.assertRaises(m.Rejected):
                m.execute(self.plan(target), True, self.move)
        # Choosing a subdirectory inside metadata as the project root cannot bypass protection.
        with self.assertRaises(m.Rejected):
            m.make_plan(str(repo / 'objects'), [str(repo / 'objects' / 'info')], 'fixture')
        self.assertEqual(self.calls, [])

    def test_normal_cache_in_current_git_worktree_and_head_file_allowed(self):
        self.init_git(self.root)
        f = self.file('cache/HEAD')
        self.assertTrue(m.execute(self.plan(f.parent), True, self.move)['complete'])

    def test_git_file_worktree_target_and_parent_rejected(self):
        repository = self.base / 'source'
        self.init_git(repository)
        subprocess.run(['git', '-C', str(repository), '-c', 'user.name=Fixture',
                        '-c', 'user.email=fixture@example.invalid', 'commit', '--allow-empty', '-qm', 'fixture'], check=True)
        target = self.root / 'cache' / 'linked'
        subprocess.run(['git', '-C', str(repository), 'worktree', 'add', '--detach', str(target)], check=True, capture_output=True)
        for p in (target, target.parent, target / '.git'):
            with self.assertRaises(m.Rejected):
                m.execute(self.plan(p), True, self.move)
        self.assertEqual(self.calls, [])

    def test_plan_then_create_bare_repository_calls_no_backend(self):
        f = self.file()
        plan = self.plan(f.parent)
        self.init_git(f.parent / 'new-bare', bare=True)
        with self.assertRaises(m.Rejected):
            m.execute(plan, True, self.move)
        self.assertEqual(self.calls, [])

    def test_git_probe_failure_or_timeout_fails_closed(self):
        repo = self.root / 'bare'
        self.init_git(repo, bare=True)
        for error in (FileNotFoundError(), subprocess.TimeoutExpired('git', 2)):
            with patch.object(m.subprocess, 'run', side_effect=error), self.assertRaises(m.Rejected):
                m.execute(self.plan(repo), True, self.move)
        self.assertEqual(self.calls, [])

    def test_damaged_git_storage_is_retained(self):
        repo = self.root / 'damaged'
        repo.mkdir()
        (repo / 'HEAD').write_text('not a valid git head')
        (repo / 'objects').mkdir()
        (repo / 'refs').mkdir()
        with self.assertRaises(m.Rejected):
            self.plan(repo)
        self.assertEqual(self.calls, [])
