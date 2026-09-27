"""Cross-entry contracts over real temporary projects; not native model results."""
from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest

import test_review_execution_boundaries as fixtures
from test_change_review import approved_record

ROOT = Path(__file__).resolve().parents[1]
GATE = ROOT/'skills/senmu-build-delivery/scripts/validate_change_review.py'
UNIT = ROOT/'skills/senmu-build-delivery/scripts/manage_change_unit.py'
LESSONS = ROOT/'skills/senmu-build-learning/scripts/validate_lessons.py'
ENTRY = ROOT/'skills/senmu-build-project/scripts/prepare_task_context.py'
MAP = ROOT/'skills/senmu-build-project/scripts/validate_project_governance.py'
m = fixtures.m


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    sys.modules[name] = result
    spec.loader.exec_module(result)
    return result


lesson = module('closeout_lessons', LESSONS)
nav = module('closeout_navigation', MAP)


class GateConnectionTests(unittest.TestCase):
    setUp = fixtures.FrozenReviewBoundaryTests.setUp
    git = fixtures.FrozenReviewBoundaryTests.git
    commit = fixtures.FrozenReviewBoundaryTests.commit
    make_change = fixtures.FrozenReviewBoundaryTests.make_change
    new_record = fixtures.FrozenReviewBoundaryTests.new_record
    payload = fixtures.FrozenReviewBoundaryTests.payload
    apply = fixtures.FrozenReviewBoundaryTests.apply
    cli = fixtures.FrozenReviewBoundaryTests.cli

    def approval(self, execution):
        record = approved_record()
        record['change'].update(base_commit=execution['snapshot']['review_base'],
                                head_commit=execution['snapshot']['head'])
        record['approval']['reviewed_head'] = execution['snapshot']['head']
        template = record['inventory']['files'][0]
        record['inventory']['files'] = []
        for number, item in enumerate(execution['items'], 1):
            entry = deepcopy(template)
            entry.update(id=f'FILE-{number:04d}', path=item['path'],
                         change_type={'A':'added','D':'deleted','R':'renamed','M':'modified','T':'modified'}[item['change_type']])
            entry['changed_units']['items'][0]['id'] = f'UNIT-{number:04d}'
            record['inventory']['files'].append(entry)
        return record

    def gate(self, execution, approval=None, extra=(), linked=True, rules='fixture-rules'):
        ep = self.root/'execution.json'
        ep.write_text(json.dumps(execution), encoding='utf-8')
        ap = self.root/'approval.json'
        ap.write_text(json.dumps(approval if approval is not None else self.approval(execution)), encoding='utf-8')
        command = [sys.executable,str(GATE),'--record',str(ap),'--repo',str(self.repo),
                   '--require-current-head','--required-review','peer']
        if linked:
            command += ['--execution-record',str(ep),'--rules-identity',rules]
        command.extend(extra)
        result = subprocess.run(command,capture_output=True,text=True,timeout=30)
        self.assertEqual(json.loads(ep.read_text()), execution)
        return result

    def complete(self, record):
        for item in record['items']:
            self.apply(record, self.payload(record,item))
        return record

    def test_real_delivery_runtime_approval_survive_attribute_change(self):
        data = b''.join(f'line {i:04d} content here\r\n'.encode() for i in range(100))
        (self.repo/'old.py').write_bytes(data)
        self.commit('base')
        original = self.repo
        worktree = self.root/'task-worktree'
        result = subprocess.run([sys.executable,str(UNIT),'prepare','--repo',str(original),
            '--unit','CU-CLOSEOUT','--slug','closeout','--worktree',str(worktree)],
            capture_output=True,text=True,timeout=30)
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)
        self.repo = worktree
        (worktree/'old.py').unlink()
        (worktree/'new.py').write_bytes(data.replace(b'\r\n',b'\n'))
        self.commit('rename')
        result = subprocess.run([sys.executable,str(UNIT),'review','--repo',str(worktree),
            '--unit','CU-CLOSEOUT'],capture_output=True,text=True,timeout=30)
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)
        scope = json.loads(result.stdout)
        self.assertEqual(scope['inventory_items'][0]['change_type'],'R')
        execution = self.complete(m.init_record(scope,worktree,'fixture-rules'))
        for location in (worktree/'.gitattributes',original/'.git/info/attributes'):
            location.write_text('* -diff\n')
            try:
                self.assertEqual(len(m.inventory(worktree,scope['review_base'],scope['head'])),2)
                ep = self.root/'runtime.json'; m.write(ep,execution)
                code,out = self.cli(ep,'check','--base',scope['review_base'],'--head',scope['head'])
                self.assertEqual(code,0,out)
                result = self.gate(execution)
                self.assertEqual(result.returncode,0,result.stdout+result.stderr)
            finally:
                location.unlink()

    def test_legacy_invocation_still_works_without_execution(self):
        record = self.make_change()
        result = self.gate(record,linked=False)
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)

    def test_adopted_pending_failed_and_empty_coverage_block(self):
        record = self.make_change()
        for state in ('pending','failed'):
            copy = deepcopy(record)
            if state == 'failed':
                payload = self.payload(copy); payload.update(state='failed',reason='stopped')
                payload.pop('evidence'); self.apply(copy,payload)
            self.assertNotEqual(self.gate(copy).returncode,0)
        base = record['snapshot']['head']
        empty = self.new_record(base,base)
        self.assertNotEqual(self.gate(empty).returncode,0)

    def test_complete_coverage_does_not_promote_draft_or_failed_checks(self):
        record = self.complete(self.make_change())
        for kind in ('draft','checks','identity'):
            approval = self.approval(record)
            if kind == 'draft': approval['status'] = 'draft'
            if kind == 'checks': approval['quality_checks'][0]['status'] = 'failed'
            if kind == 'identity': approval['approval']['review_identity'] = 'evidence_based_self_review'
            result = self.gate(record,approval)
            self.assertNotEqual(result.returncode,0,result.stdout)

    def test_expected_rules_and_exact_target_must_match(self):
        record = self.complete(self.make_change())
        self.assertNotEqual(self.gate(record,rules='different-rules').returncode,0)
        for key in ('base_commit','head_commit'):
            approval = self.approval(record)
            approval['change'][key] = approval['change'][key][:12]
            if key == 'head_commit': approval['approval']['reviewed_head'] = approval['change'][key]
            self.assertNotEqual(self.gate(record,approval).returncode,0)

    def test_missing_parameters_do_not_fall_back_to_legacy(self):
        record = self.complete(self.make_change())
        ap = self.root/'approval.json';ap.write_text(json.dumps(self.approval(record)))
        ep = self.root/'execution.json';ep.write_text(json.dumps(record))
        base = [sys.executable,str(GATE),'--record',str(ap)]
        for args in (['--execution-record',str(ep)], ['--rules-identity','fixture-rules'],
                     ['--execution-record',str(ep),'--rules-identity','fixture-rules'],
                     ['--repo',str(self.repo),'--execution-record',str(ep),'--rules-identity',' ']):
            result = subprocess.run(base+args,capture_output=True,text=True,timeout=30)
            self.assertNotEqual(result.returncode,0,result.stdout)

    def test_tampered_proof_or_inventory_is_not_counted(self):
        record = self.complete(self.make_change())
        for kind in ('proof','inventory'):
            copy = deepcopy(record)
            if kind == 'proof': copy['items'][0]['receipt']['evidence'][0]['range_sha256'] = 'sha256:'+'0'*64
            else: copy['items'] = []
            self.assertNotEqual(self.gate(copy).returncode,0)

    def test_missing_reuse_source_blocks_gate(self):
        source = self.complete(self.make_change())
        sp = self.root/'source.json';m.write(sp,source)
        record = self.new_record(source['snapshot']['review_base'],source['snapshot']['head'])
        payload = self.payload(record)
        payload.update(state='reused',source={'record':str(sp),'receipt_identity':m.digest(source['items'][0]['receipt'])})
        self.apply(record,payload)
        self.assertEqual(self.gate(record).returncode,0)
        sp.unlink()
        self.assertNotEqual(self.gate(record).returncode,0)

    def test_current_head_check_remains_effective(self):
        record = self.complete(self.make_change())
        (self.repo/'later.py').write_text('later=1\n');self.commit('later')
        self.assertNotEqual(self.gate(record).returncode,0)


class LessonAmbiguityTests(unittest.TestCase):
    def entry(self, missing=False):
        fields = {name:'confirmed' for name in lesson.REQUIRED_FIELDS}
        fields.update({'状态':'active','类型':'practice'})
        if missing: fields['修复与验证证据'] = '<待确认>'
        return '### LES-20260927-001: Example\n'+'\n'.join(f'- {name}: {value}' for name,value in sorted(fields.items()))+'\n'

    def test_duplicate_status_never_weakens_missing_evidence(self):
        errors,_,count = lesson.validate(self.entry(True)+'- 状态: candidate\n')
        self.assertEqual(count,1)
        self.assertTrue(any('字段重复' in e and '状态' in e for e in errors),errors)
        self.assertTrue(any('修复与验证证据' in e for e in errors),errors)

    def test_duplicate_evidence_and_identical_fields_are_explicit_errors(self):
        for field,value in (('修复与验证证据','confirmed'),('状态','active')):
            errors,_,_ = lesson.validate(self.entry()+f'- {field}: {value}\n')
            self.assertTrue(any('字段重复' in e for e in errors),errors)

    def test_empty_field_does_not_consume_following_field(self):
        text = self.entry().replace('- 修复与验证证据: confirmed','- 修复与验证证据: ')
        parsed = lesson.parse_lessons(text)[0]
        self.assertEqual(parsed.fields['修复与验证证据'],'')
        self.assertIn('状态',parsed.fields)
        self.assertTrue(lesson.validate(text)[0])

    def test_complete_examples_and_empty_register_remain_valid(self):
        for text in ('# Empty\n','```markdown\n'+self.entry(True)+'```\n','~~~md\n'+self.entry(True)+'~~~~\n'):
            self.assertEqual(lesson.validate(text),( [],[],0 ))
        self.assertFalse(lesson.validate('```md\n'+self.entry(True)+'```\n'+self.entry())[0])

    def test_unclosed_examples_cannot_hide_following_entries(self):
        for marker in ('```markdown','~~~md'):
            errors,_,_ = lesson.validate(marker+'\n'+self.entry(True))
            self.assertTrue(any('未闭合' in e and '第 1 行' in e for e in errors),errors)

    def test_fence_with_trailing_text_is_not_a_closing_fence(self):
        text = '```md\nexample\n```not-a-close\n'+self.entry(True)
        self.assertTrue(any('未闭合' in e for e in lesson.validate(text)[0]))

    def test_cli_rejects_ambiguity_without_modifying_register(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary)/'LESSONS.md'
            for text in (self.entry(True)+'- 状态: candidate\n','```\n'+self.entry(True)):
                path.write_text(text,encoding='utf-8')
                result = subprocess.run([sys.executable,str(LESSONS),str(path)],capture_output=True,text=True,timeout=10)
                self.assertEqual(result.returncode,1,result.stdout+result.stderr)
                self.assertNotIn('[OK]',result.stdout)
                self.assertEqual(path.read_text(),text)


class NavigationIdentityTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(); self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name).resolve()
        for name in ('src','tests','governance','engineering'):(self.root/name).mkdir()
        for name in ('src/service.py','tests/test_service.py','engineering/contract.md'):
            (self.root/name).write_text('fixture\n')
        self.map = self.root/'governance/PROJECT_MAP.md'

    def write_map(self, implementation, contract='[Contract](../engineering/contract.md)'):
        text = ('# Map\n\n## 责任与入口地图\n\n'
          '| Capability | Responsibility | Implementation | Contract | Verification | State |\n'
          '| --- | --- | --- | --- | --- | --- |\n'
          f'| Order checkout | Total | {implementation} | {contract} | [Test](../tests/test_service.py) | approved |\n\n'
          '## 项目规范索引\n\n| Kind | Scope | Role | Target | Status |\n| --- | --- | --- | --- | --- |\n'
          f'| Quality | checkout | owner | {contract} | active |\n')
        self.map.write_text(text,encoding='utf-8')
        return text

    def run_entry(self):
        result = subprocess.run([sys.executable,str(ENTRY),'--root',str(self.root),'--map','governance/PROJECT_MAP.md',
                                 '--capability','Order checkout'],capture_output=True,text=True,timeout=10)
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)
        return json.loads(result.stdout)

    def index_errors(self, text):
        errors=[]; warnings=[]
        stats={'standards_rows':0,'active_standards_rows':0,'active_index_targets_checked':0,'project_map_links_checked':0}
        nav.validate_project_map_index(self.root,self.map,text,errors,warnings,stats)
        return errors

    def test_display_styles_have_identical_routes_in_both_consumers(self):
        expected=None
        for label in ('service.py','`service.py`','中文入口','``service.py``'):
            text=self.write_map(f'[{label}](../src/service.py)','[`contract.md`](../engineering/contract.md)')
            out=self.run_entry()
            self.assertEqual(out['status'],'selected',out)
            self.assertFalse(self.index_errors(text))
            if expected is None: expected=out['targets']
            self.assertEqual(out['targets'],expected)

    def test_equivalent_targets_are_reported_once(self):
        self.write_map('[`service.py`](../src/service.py) and [other](../src/service.py) and `src/service.py`')
        out=self.run_entry()
        self.assertEqual(out['status'],'selected',out)
        self.assertEqual(len([t for t in out['targets'] if t['field']=='implementation']),1)

    def test_standalone_missing_and_outside_paths_still_surface(self):
        for target,reason in (('`src/missing.py`','missing'),('[entry](../../outside.py)','outside')):
            self.write_map(target)
            out=self.run_entry()
            self.assertEqual(out['status'],'gaps')
            self.assertTrue(any(t['status']==reason for t in out['targets']),out)

    def test_missing_real_destination_is_not_hidden_by_a_valid_label(self):
        text=self.write_map('[`src/service.py`](../src/absent.py)')
        out=self.run_entry()
        self.assertEqual(out['status'],'gaps',out)
        self.assertTrue(self.index_errors(text))

    def test_external_link_label_is_not_a_local_file_request(self):
        self.write_map('[`ghost.py`](https://example.invalid/service)')
        out=self.run_entry()
        self.assertFalse(any(t['status']=='missing' for t in out['targets']),out)
        self.assertTrue(any(t['status']=='external_or_anchor_unverified' for t in out['targets']))
        self.assertFalse(out['semantic_route_verified'])

    def test_example_command_is_executable_from_documented_product_root(self):
        self.write_map('[service.py](../src/service.py)')
        document=(ROOT/'skills/senmu-build-project/references/task-entry-and-maintenance-economy.md').read_text()
        matches=re.findall(r'^python3 skills/senmu-build-project/scripts/prepare_task_context.py .+$',document,re.M)
        self.assertEqual(len(matches),1)
        import shlex
        argv=shlex.split(matches[0])
        argv[0]=sys.executable
        argv=[str(self.root) if value=='/absolute/path/to/project' else value for value in argv]
        result=subprocess.run(argv,cwd=ROOT,capture_output=True,text=True,timeout=10)
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)
        self.assertEqual(json.loads(result.stdout)['status'],'selected')


if __name__=='__main__': unittest.main()
