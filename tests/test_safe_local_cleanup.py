import importlib.util
from pathlib import Path
import tempfile
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
