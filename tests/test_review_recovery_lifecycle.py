"""Real Git lifecycle regressions, not model-attention or semantic-review evidence."""
from __future__ import annotations

from copy import deepcopy
import json
import os
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch

import test_review_execution_boundaries as fixtures

m = fixtures.m
SCRIPT = fixtures.SCRIPT


class ReviewRecoveryLifecycleTests(unittest.TestCase):
    setUp = fixtures.FrozenReviewBoundaryTests.setUp
    git = fixtures.FrozenReviewBoundaryTests.git
    commit = fixtures.FrozenReviewBoundaryTests.commit
    make_change = fixtures.FrozenReviewBoundaryTests.make_change
    new_record = fixtures.FrozenReviewBoundaryTests.new_record
    payload = fixtures.FrozenReviewBoundaryTests.payload
    apply = fixtures.FrozenReviewBoundaryTests.apply

    def cli(self, path, command, *args, cwd=None, env=None):
        result = subprocess.run([sys.executable, str(SCRIPT), command, '--repo', str(self.repo),
                                 '--record', str(path), '--rules-identity', 'fixture-rules', *args],
                                cwd=cwd, env=env, text=True, capture_output=True, timeout=15)
        return result.returncode, json.loads(result.stdout)

    def save(self, record, name='review.json'):
        path = self.root / name
        m.write(path, record)
        return path

    def check(self, path, record, **kwargs):
        return self.cli(path, 'check', '--base', record['snapshot']['review_base'],
                        '--head', record['snapshot']['head'], **kwargs)

    def send(self, path, record, item=None, state='completed', source=None, **kwargs):
        payload = self.payload(record, item)
        payload['state'] = state
        if source is not None:
            payload['source'] = source
        if state == 'failed':
            payload['reason'] = 'fixture interruption'
        incoming = self.root / 'incoming.json'
        incoming.write_text(json.dumps(payload), encoding='utf-8')
        return self.cli(path, 'receipt', '--item', payload['item_id'], '--state', state,
                        '--receipt', str(incoming), **kwargs)

    def recover(self, path, record, command='retry', item=None, op='op-1', attempt=None,
                run_id=None, reason='fixture recovery'):
        item = record['items'][0] if item is None else item
        return self.cli(path, command, '--item', item['item_id'], '--reason', reason,
                        '--run-id', run_id or record['run_id'],
                        '--expected-attempt', str(item['attempt'] if attempt is None else attempt),
                        '--operation-id', op)

    def reused_pair(self, count=2):
        for n in range(count):
            (self.repo / f'{n}.py').write_bytes(b'v=1\n')
        base = self.commit('base')
        for n in range(count):
            (self.repo / f'{n}.py').write_bytes(b'v=2\n')
        head = self.commit('head')
        parent = self.new_record(base, head)
        self.apply(parent, self.payload(parent))
        source_path = self.save(parent, 'source.json')
        child = self.new_record(base, head)
        payload = self.payload(child)
        payload.update(state='reused', source={'record': str(source_path),
                       'receipt_identity': m.digest(parent['items'][0]['receipt'])})
        self.apply(child, payload)
        path = self.save(child)
        return parent, source_path, child, path

    def test_blob_replacement_cannot_change_frozen_evidence(self):
        record = self.make_change()
        item = record['items'][0]
        expected = m.evidence(self.repo, item, 'head')
        replacement = subprocess.check_output(['git', '-C', str(self.repo), 'hash-object', '-w', '--stdin'],
                                             input=b'# header\nvalue=999\n').decode().strip()
        self.git('replace', item['new_blob'], replacement)
        # Establish that the local replacement really affects ordinary Git reads.
        self.assertIn('999', self.git('cat-file', 'blob', item['new_blob']))
        self.assertEqual(m.evidence(self.repo, item, 'head'), expected)
        self.apply(record, self.payload(record))
        code, output = self.check(self.save(record), record)
        self.assertEqual(code, 0, output)

    def test_commit_replacement_does_not_rewrite_frozen_snapshot(self):
        record = self.make_change()
        original = record['snapshot']['head']
        (self.repo / 'a.py').write_text('other=999\n')
        self.commit('alternative tree')
        alternate_tree = self.git('rev-parse', 'HEAD^{tree}')
        alternate = self.git('commit-tree', alternate_tree, '-p', record['snapshot']['review_base'], '-m', 'replacement')
        self.git('replace', original, alternate)
        m.validate_record(record, self.repo, 'fixture-rules')
        self.assertEqual(m.inventory(self.repo, record['snapshot']['review_base'], original)[0]['new_blob'],
                         record['items'][0]['new_blob'])

    def test_batch_preload_ignores_replacements(self):
        record = self.make_change()
        self.apply(record, self.payload(record))
        replacement = subprocess.check_output(['git', '-C', str(self.repo), 'hash-object', '-w', '--stdin'],
                                             input=b'changed replacement\n').decode().strip()
        self.git('replace', record['items'][0]['new_blob'], replacement)
        m.validate_record(record, self.repo, 'fixture-rules')
        self.assertEqual(self.check(self.save(record), record)[0], 0)

    def test_environment_cannot_redirect_explicit_repository(self):
        record = self.make_change()
        path = self.save(record)
        for name in ('GIT_DIR', 'GIT_WORK_TREE', 'GIT_COMMON_DIR', 'GIT_OBJECT_DIRECTORY',
                     'GIT_ALTERNATE_OBJECT_DIRECTORIES', 'GIT_SHALLOW_FILE', 'GIT_INDEX_FILE'):
            with self.subTest(variable=name):
                env = dict(os.environ, **{name: str(self.root / 'foreign-metadata')})
                code, output = self.cli(path, 'status', env=env)
                self.assertEqual(code, 0, output)
                self.assertEqual(output['total'], 1)

    def test_environment_configuration_injection_does_not_change_source(self):
        record = self.make_change()
        env = dict(os.environ, GIT_CONFIG_COUNT='1', GIT_CONFIG_KEY_0='core.worktree',
                   GIT_CONFIG_VALUE_0=str(self.root / 'other'), GIT_NO_REPLACE_OBJECTS='0')
        code, output = self.cli(self.save(record), 'status', env=env)
        self.assertEqual(code, 0, output)

    def test_raw_blob_verification_rejects_content_under_wrong_id(self):
        record = self.make_change()
        item = record['items'][0]
        ordinary = m.git
        def altered(repo, *args, **kwargs):
            if args == ('cat-file', 'blob', item['new_blob']):
                return b'# header\nvalue=999\n'
            return ordinary(repo, *args, **kwargs)
        with patch.object(m, 'git', altered), self.assertRaises(ValueError):
            m.evidence(self.repo, item, 'head')

    def test_absolute_source_survives_working_directory_change(self):
        _, _, record, path = self.reused_pair(count=1)
        for cwd in (self.root, self.repo):
            code, output = self.check(path, record, cwd=cwd)
            self.assertEqual(code, 0, output)
            self.assertEqual(output['reused'], 1)

    def test_relative_source_is_rejected_at_admission_without_write(self):
        parent, source, child, path = self.reused_pair(count=1)
        child = self.new_record(child['snapshot']['review_base'], child['snapshot']['head'])
        m.write(path, child)
        before = path.read_bytes()
        code, output = self.send(path, child, state='reused', source={
            'record': source.name, 'receipt_identity': m.digest(parent['items'][0]['receipt'])}, cwd=self.root)
        self.assertEqual(code, 1, output)
        self.assertIn('absolute', output['reason'])
        self.assertEqual(path.read_bytes(), before)

    def test_noncanonical_source_path_is_rejected(self):
        parent, source, child, path = self.reused_pair(count=1)
        child = self.new_record(child['snapshot']['review_base'], child['snapshot']['head'])
        m.write(path, child)
        code, _ = self.send(path, child, state='reused', source={
            'record': str(self.root) + '/./source.json',
            'receipt_identity': m.digest(parent['items'][0]['receipt'])})
        self.assertEqual(code, 1)

    def test_source_loss_is_diagnostic_not_total_status_failure(self):
        _, source, record, path = self.reused_pair()
        source.unlink()
        before = path.read_bytes()
        code, output = self.cli(path, 'status', '--limit', '1')
        self.assertEqual(code, 0, output)
        self.assertEqual(output['total'], 2)
        self.assertEqual(output['invalid_source'], 1)
        self.assertEqual(output['pending'], 1)
        self.assertEqual(output['reused'], 0)
        self.assertFalse(output['execution_complete'])
        self.assertEqual(output['remaining'][0]['recovery'], 'restore_source_or_reopen')
        self.assertEqual(path.read_bytes(), before)

    def test_source_loss_never_passes_final_check(self):
        _, source, record, path = self.reused_pair(count=1)
        source.unlink()
        code, output = self.check(path, record)
        self.assertEqual(code, 1)
        self.assertFalse(output['execution_complete'])
        self.assertEqual(output['invalid_source'], 1)

    def test_unrelated_work_can_finish_while_source_is_missing(self):
        _, source, record, path = self.reused_pair()
        source.unlink()
        code, output = self.send(path, record, record['items'][1])
        self.assertEqual(code, 0, output)
        self.assertEqual(output['completed'], 1)
        self.assertEqual(output['invalid_source'], 1)
        self.assertFalse(output['execution_complete'])
        self.assertEqual(m.load(path)['items'][0]['receipt'], record['items'][0]['receipt'])

    def test_reopen_preserves_original_receipt_then_can_complete(self):
        _, source, record, path = self.reused_pair(count=1)
        original = deepcopy(record['items'][0]['receipt'])
        source.unlink()
        code, output = self.recover(path, record, 'reopen')
        self.assertEqual(code, 0, output)
        current = m.load(path)
        item = current['items'][0]
        self.assertEqual(item['attempt'], 2)
        self.assertEqual(item['history'][0]['receipt'], original)
        self.assertTrue(item['history'][0]['invalidation_reason'])
        self.assertEqual(self.send(path, current)[0], 0)
        self.assertEqual(self.check(path, current)[0], 0)

    def test_restoring_source_restores_validity_without_mutation(self):
        parent, source, record, path = self.reused_pair(count=1)
        source.unlink()
        before = path.read_bytes()
        self.assertEqual(self.check(path, record)[0], 1)
        m.write(source, parent)
        self.assertEqual(self.check(path, record)[0], 0)
        self.assertEqual(path.read_bytes(), before)

    def test_reopen_does_not_erase_valid_reuse(self):
        _, _, record, path = self.reused_pair(count=1)
        before = path.read_bytes()
        code, output = self.recover(path, record, 'reopen')
        self.assertEqual(code, 1, output)
        self.assertEqual(path.read_bytes(), before)

    def test_reopen_does_not_erase_direct_completion(self):
        record = self.make_change()
        self.apply(record, self.payload(record))
        path = self.save(record)
        before = path.read_bytes()
        self.assertEqual(self.recover(path, record, 'reopen')[0], 1)
        self.assertEqual(path.read_bytes(), before)

    def test_corrupted_local_proof_blocks_diagnosis_and_reopen(self):
        _, source, record, path = self.reused_pair()
        source.unlink()
        record['items'][0]['receipt']['evidence'][0]['range_sha256'] = 'sha256:' + '0'*64
        m.write(path, record)
        before = path.read_bytes()
        self.assertEqual(self.cli(path, 'status')[0], 1)
        self.assertEqual(self.recover(path, record, 'reopen')[0], 1)
        self.assertEqual(path.read_bytes(), before)

    def test_corrupted_envelope_is_not_treated_as_external_loss(self):
        _, source, record, path = self.reused_pair()
        source.unlink()
        record['items'].pop()
        m.write(path, record)
        before = path.read_bytes()
        self.assertEqual(self.cli(path, 'status')[0], 1)
        self.assertEqual(self.recover(path, record, 'reopen')[0], 1)
        self.assertEqual(path.read_bytes(), before)

    def test_malformed_external_source_is_locally_recoverable(self):
        _, source, record, path = self.reused_pair(count=1)
        source.write_text('{not valid JSON', encoding='utf-8')
        self.assertEqual(self.cli(path, 'status')[1]['invalid_source'], 1)
        self.assertEqual(self.recover(path, record, 'reopen')[0], 0)

    def test_legacy_relative_source_never_uses_current_directory(self):
        _, source, record, path = self.reused_pair(count=1)
        record['items'][0]['receipt']['source']['record'] = source.name
        m.write(path, record)
        for cwd in (self.root, self.repo):
            code, output = self.cli(path, 'status', cwd=cwd)
            self.assertEqual(code, 0, output)
            self.assertEqual(output['invalid_source'], 1)
        self.assertEqual(self.recover(path, record, 'reopen')[0], 0)

    def test_source_symlink_cannot_be_followed_during_recovery(self):
        parent, source, record, path = self.reused_pair(count=1)
        source.unlink()
        alternate = self.save(parent, 'alternate.json')
        source.symlink_to(alternate)
        self.assertEqual(self.cli(path, 'status')[1]['invalid_source'], 1)
        self.assertEqual(self.recover(path, record, 'reopen')[0], 0)
        self.assertTrue(source.is_symlink())

    def test_duplicate_retry_preserves_current_attempt_and_bytes(self):
        record = self.make_change()
        path = self.save(record)
        code, output = self.recover(path, record)
        self.assertEqual(code, 0, output)
        attempt2 = m.load(path)
        before = path.read_bytes()
        code, output = self.recover(path, record)
        self.assertEqual(code, 0, output)
        self.assertTrue(output['transition']['replayed'])
        self.assertEqual(output['transition']['to_attempt'], 2)
        self.assertEqual(path.read_bytes(), before)
        self.assertEqual(self.send(path, attempt2)[0], 0)

    def test_late_new_retry_request_cannot_cancel_new_attempt(self):
        record = self.make_change()
        path = self.save(record)
        self.assertEqual(self.recover(path, record)[0], 0)
        before = path.read_bytes()
        self.assertEqual(self.recover(path, record, op='late-other-request')[0], 1)
        self.assertEqual(path.read_bytes(), before)

    def test_conflicting_replay_reason_is_rejected(self):
        record = self.make_change()
        path = self.save(record)
        self.assertEqual(self.recover(path, record)[0], 0)
        before = path.read_bytes()
        self.assertEqual(self.recover(path, record, reason='different intent')[0], 1)
        self.assertEqual(path.read_bytes(), before)

    def test_foreign_run_recovery_cannot_change_record(self):
        record = self.make_change()
        path = self.save(record)
        before = path.read_bytes()
        self.assertEqual(self.recover(path, record, run_id='0'*32)[0], 1)
        self.assertEqual(path.read_bytes(), before)

    def test_intentional_second_retry_requires_current_attempt(self):
        record = self.make_change()
        path = self.save(record)
        self.assertEqual(self.recover(path, record)[0], 0)
        current = m.load(path)
        self.assertEqual(self.recover(path, current, op='op-2')[0], 0)
        self.assertEqual(m.load(path)['items'][0]['attempt'], 3)
        # An old idempotent replay never regresses attempt 3.
        before = path.read_bytes()
        code, output = self.recover(path, record)
        self.assertEqual(code, 0, output)
        self.assertEqual(output['transition']['to_attempt'], 2)
        self.assertEqual(path.read_bytes(), before)

    def test_retry_replay_after_completion_is_noop(self):
        record = self.make_change()
        path = self.save(record)
        self.assertEqual(self.recover(path, record)[0], 0)
        self.assertEqual(self.send(path, m.load(path))[0], 0)
        before = path.read_bytes()
        self.assertEqual(self.recover(path, record)[0], 0)
        self.assertEqual(path.read_bytes(), before)

    def test_reopen_duplicate_and_old_result_do_not_interfere(self):
        _, source, record, path = self.reused_pair(count=1)
        old = deepcopy(record['items'][0]['receipt'])
        source.unlink()
        self.assertEqual(self.recover(path, record, 'reopen')[0], 0)
        before = path.read_bytes()
        self.assertEqual(self.recover(path, record, 'reopen')[0], 0)
        self.assertEqual(path.read_bytes(), before)
        incoming = self.root/'late.json'
        incoming.write_text(json.dumps(old))
        code, _ = self.cli(path, 'receipt', '--item', old['item_id'], '--state', 'reused', '--receipt', str(incoming))
        self.assertEqual(code, 1)
        self.assertEqual(self.send(path, m.load(path))[0], 0)

    def test_mutation_lock_still_serializes_recovery(self):
        record = self.make_change()
        path = self.save(record)
        before = path.read_bytes()
        with m.locked(path):
            self.assertEqual(self.recover(path, record)[0], 1)
        self.assertEqual(path.read_bytes(), before)
        self.assertEqual(self.recover(path, record)[0], 0)

    def test_separate_git_directory_rejects_record_before_any_write(self):
        metadata = self.root/'git-store'
        self.git('init', '-q', '--separate-git-dir', str(metadata))
        record = self.make_change()
        scope = {**record['snapshot'], 'kind':'git_review_scope',
                 'changed_paths':[x['path'] for x in record['items']]}
        scope_path = self.root/'scope.json'
        scope_path.write_text(json.dumps(scope))
        path = metadata/'new-folder'/'review.json'
        before = set(metadata.rglob('*'))
        code, output = self.cli(path, 'init', '--scope', str(scope_path))
        self.assertEqual(code, 1, output)
        self.assertFalse(path.exists())
        self.assertEqual(set(metadata.rglob('*')), before)

    def test_linked_worktree_common_and_private_metadata_are_protected(self):
        metadata = self.root/'git-store'
        self.git('init', '-q', '--separate-git-dir', str(metadata))
        self.make_change()
        worktree = self.root/'linked'
        self.git('worktree', 'add', '-qb', 'linked', str(worktree))
        for flag in ('--git-dir', '--git-common-dir'):
            directory = Path(subprocess.check_output(['git', '-C', str(worktree), 'rev-parse',
                            '--path-format=absolute', flag], text=True).strip())
            with self.subTest(flag=flag), self.assertRaises(m.ReviewError):
                m.record_destination(directory/'review.json', worktree)
        self.assertEqual(m.record_destination(self.root/'allowed.json', worktree), self.root/'allowed.json')

    def test_schema3_normal_records_need_no_migration(self):
        record = self.make_change()
        self.assertEqual(record['schema_version'], 3)
        self.apply(record, self.payload(record))
        code, output = self.check(self.save(record), record)
        self.assertEqual(code, 0, output)
        self.assertEqual(output['approval_outcome'], 'not_assessed')

    def test_legacy_retry_history_stays_readable(self):
        record = self.make_change()
        item = record['items'][0]
        item['history'].append({'attempt':1,'state':'pending','receipt':None,'reason':'legacy interruption'})
        item['attempt'] = 2
        m.validate_record(record, self.repo, 'fixture-rules')
        code, output = self.recover(self.save(record), record)
        self.assertEqual(code, 0, output)

    def test_missing_retry_identity_flags_cannot_mutate(self):
        record = self.make_change()
        path = self.save(record)
        before = path.read_bytes()
        result = subprocess.run([sys.executable, str(SCRIPT), 'retry', '--repo', str(self.repo),
                    '--record', str(path), '--rules-identity', 'fixture-rules',
                    '--item', record['items'][0]['item_id'], '--reason','ambiguous'], capture_output=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(path.read_bytes(), before)


if __name__ == '__main__':
    unittest.main()
