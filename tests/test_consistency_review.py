"""Frozen grouping, environment and external-source recovery over real temporary Git."""
from collections import Counter
from copy import deepcopy
import json
import os
from pathlib import Path
from unittest.mock import patch
import unittest

import test_review_execution_boundaries as f
import test_review_recovery_lifecycle as lifecycle
m = f.m


class ConsistencyReviewTests(unittest.TestCase):
    setUp = lifecycle.ReviewRecoveryLifecycleTests.setUp
    git = lifecycle.ReviewRecoveryLifecycleTests.git
    commit = lifecycle.ReviewRecoveryLifecycleTests.commit
    make_change = lifecycle.ReviewRecoveryLifecycleTests.make_change
    new_record = lifecycle.ReviewRecoveryLifecycleTests.new_record
    payload = lifecycle.ReviewRecoveryLifecycleTests.payload
    apply = lifecycle.ReviewRecoveryLifecycleTests.apply
    cli = lifecycle.ReviewRecoveryLifecycleTests.cli
    save = lifecycle.ReviewRecoveryLifecycleTests.save
    check = lifecycle.ReviewRecoveryLifecycleTests.check
    send = lifecycle.ReviewRecoveryLifecycleTests.send
    recover = lifecycle.ReviewRecoveryLifecycleTests.recover
    reused_pair = lifecycle.ReviewRecoveryLifecycleTests.reused_pair

    def renamed(self):
        self.git('config', 'core.autocrlf', 'false')
        data = b''.join(f'line {n:04d} content here\r\n'.encode() for n in range(100))
        (self.repo/'old.py').write_bytes(data)
        base = self.commit('base')
        (self.repo/'old.py').unlink()
        (self.repo/'new.py').write_bytes(data.replace(b'\r\n', b'\n'))
        head = self.commit('rename')
        record = self.new_record(base, head)
        self.assertEqual(record['items'][0]['change_type'], 'R')
        return record

    def test_attribute_changes_do_not_reinterpret_captured_inventory(self):
        record = self.renamed()
        self.apply(record, self.payload(record))
        for location in ('.gitattributes', '.git/info/attributes'):
            p = self.repo/location
            p.write_text('* -diff\n')
            try:
                self.assertEqual(len(m.inventory(self.repo, record['snapshot']['review_base'], record['snapshot']['head'])), 2)
                m.validate_record(record, self.repo, 'fixture-rules')
            finally:
                p.unlink()

    def test_scope_pairing_survives_change_before_initialization(self):
        prior = self.renamed()
        scope = {'kind':'git_review_scope','repository_root':str(self.repo),
                 'review_base':prior['snapshot']['review_base'],'head':prior['snapshot']['head'],
                 'tree':prior['snapshot']['tree'],'changed_paths':['new.py'],
                 'inventory_items':[{k:v for k,v in prior['items'][0].items() if k not in ('state','attempt','history','receipt')}]}
        (self.repo/'.git/info/attributes').write_text('* -diff\n')
        record = m.init_record(scope, self.repo, 'fixture-rules')
        self.assertEqual(len(record['items']), 1)
        m.validate_record(record, self.repo, 'fixture-rules')

    def test_legacy_schema_three_grouping_remains_verifiable(self):
        record = self.renamed()
        record['snapshot'].pop('inventory_identity')
        record['snapshot_identity'] = m.digest(record['snapshot'])
        self.apply(record, self.payload(record))
        (self.repo/'.git/info/attributes').write_text('* -diff\n')
        m.validate_record(record, self.repo, 'fixture-rules')

    def test_missing_or_duplicate_raw_changes_still_fail(self):
        record = self.renamed()
        for changed in ([], record['items']*2):
            with self.assertRaises(ValueError):
                m._shared.frozen_inventory(self.repo, record['snapshot']['review_base'], record['snapshot']['head'], changed)

    def test_forged_pairing_or_fingerprint_fails(self):
        record = self.renamed()
        for key,value in (('old_path','unrelated.py'),('new_blob','0'*40),('item_id','sha256:'+'0'*64)):
            bad = deepcopy(record['items']);bad[0][key] = value
            with self.assertRaises(ValueError):
                m._shared.frozen_inventory(self.repo, record['snapshot']['review_base'], record['snapshot']['head'], bad)

    def test_exact_evidence_ignores_diff_environment_override(self):
        record = self.make_change(b'# first\nv=1\n# last\n',b'# first\nv=2\n# last\n')
        payload = self.payload(record, ranges={'base':[(2,2)],'head':[(2,2)]})
        with patch.dict(os.environ, {'GIT_DIFF_OPTS':'--unified=5'}):
            self.apply(record, payload)
            m.validate_record(record, self.repo, 'fixture-rules')

    def test_deep_external_json_has_partial_diagnosis_and_recovery(self):
        _, source, record, path = self.reused_pair()
        source.write_bytes(source.read_bytes().rstrip()[:-1]+b',"extra":'+b'['*10000+b'0'+b']'*10000+b'}')
        self.assertEqual(len(m.inspect_record(record,self.repo,'fixture-rules')),1)
        self.apply(record,self.payload(record,record['items'][1]))
        m.write(path,record)
        code,out = self.recover(path,record,'reopen',op='deep-source')
        self.assertEqual(code,0,out)
        saved=m.load(path)
        self.assertEqual(saved['items'][0]['state'],'pending')
        self.assertEqual(saved['items'][1]['state'],'completed')
        self.assertEqual(len(saved['items'][0]['history']),1)

    def test_deep_local_json_is_controlled_and_not_overwritten(self):
        record=self.make_change();path=self.save(record)
        path.write_bytes(path.read_bytes().rstrip()[:-1]+b',"extra":'+b'['*10000+b'0'+b']'*10000+b'}')
        before=path.read_bytes()
        code,out=self.cli(path,'status')
        self.assertEqual(code,1);self.assertEqual(out['status'],'blocked')
        self.assertEqual(path.read_bytes(),before)
        self.assertIn('nesting',out['reason'])

    def test_depth_scanner_ignores_brackets_inside_escaped_strings(self):
        path=self.root/'strings.json'
        value={'text':'\\"'+'['*10000+'}'*10000}
        path.write_text(json.dumps(value))
        self.assertEqual(m.load(path),value)
        path.write_text('{"x":1,"x":2}')
        with self.assertRaisesRegex(ValueError,'duplicate'): m.load(path)

    def test_source_is_read_once_per_operation_but_not_across_operations(self):
        for i in range(20): (self.repo/f'{i:02}.py').write_bytes(b'x=1\n')
        base=self.commit('base')
        for i in range(20): (self.repo/f'{i:02}.py').write_bytes(b'x=2\n')
        head=self.commit('head');parent=self.new_record(base,head)
        for item in parent['items']: item.update(state='completed',receipt=self.payload(parent,item))
        m.validate_record(parent,self.repo,'fixture-rules')
        path=self.save(parent,'source.json');child=self.new_record(base,head)
        for item,original in zip(child['items'],parent['items']):
            payload=self.payload(child,item)
            payload.update(state='reused',source={'record':str(path),'receipt_identity':m.digest(original['receipt'])})
            item.update(state='reused',receipt=payload)
        original_load=m.load;calls=Counter()
        def counted(p):
            calls[str(p)]+=1
            return original_load(p)
        with patch.object(m,'load',side_effect=counted):
            self.assertFalse(m.inspect_record(child,self.repo,'fixture-rules'))
        self.assertEqual(calls[str(path)],1)
        path.write_text('{')
        self.assertEqual(len(m.inspect_record(child,self.repo,'fixture-rules')),20)


if __name__=='__main__': unittest.main()
