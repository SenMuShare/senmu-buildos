"""Exercise map-language contracts, real initializer output and nonfatal JSON warnings."""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT / 'skills/senmu-build-project/scripts'


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    value = importlib.util.module_from_spec(spec)
    sys.modules[name] = value
    spec.loader.exec_module(value)
    return value


lessons = module('consistency_lessons', ROOT/'skills/senmu-build-learning/scripts/validate_lessons.py')


def lesson(title='### LES-20260926-001: A concrete lesson', incomplete=False, candidate=False):
    fields = {key:'confirmed fixture value' for key in lessons.REQUIRED_FIELDS}
    fields.update({'状态':'candidate' if candidate else 'active', '类型':'practice'})
    if incomplete:
        fields['修复与验证证据'] = '<待确认>'
    if candidate:
        fields['触发信号'] = '<待确认>'
    return title+'\n'+'\n'.join('- '+key+'：'+value for key,value in sorted(fields.items()))+'\n'


class ConsistencyLessonsTests(unittest.TestCase):
    def test_both_colons_validate_the_same_real_entry(self):
        for delimiter in (':', '：'):
            errors, warnings, count = lessons.validate(lesson(title='### LES-20260926-001'+delimiter+' A concrete lesson'))
            self.assertEqual((errors,warnings,count), ([],[],1))

    def test_ascii_colon_does_not_hide_missing_active_evidence(self):
        errors, _, count = lessons.validate(lesson(incomplete=True))
        self.assertEqual(count,1)
        self.assertTrue(any('修复与验证证据' in item for item in errors))

    def test_malformed_candidates_cannot_be_reported_as_empty_success(self):
        for heading in ('## LES-20260926-001: wrong level','### LES-bad: broken id',
                        '### LES-20260926-001 - wrong separator','### LES-20260926-001: '):
            with self.subTest(heading=heading):
                errors, _, count = lessons.validate(heading+'\n')
                self.assertTrue(errors)
                self.assertEqual(count,0)

    def test_empty_and_fenced_examples_are_not_real_entries(self):
        for text in ('# Register\n', '```md\n### LES-bad: example\n```\n',
                     '~~~\n'+lesson(incomplete=True)+'~~~\n'):
            self.assertEqual(lessons.validate(text), ([],[],0))

    def test_fenced_fields_cannot_complete_a_real_entry(self):
        text = '### LES-20260926-001: incomplete\n```\n'+lesson()+'```\n'
        self.assertTrue(lessons.validate(text)[0])


class ConsistencyMapTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.validator = module('consistency_governance', PROJECT/'validate_project_governance.py')

    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)/'project'

    def initialize(self):
        result = subprocess.run([sys.executable,str(PROJECT/'init_project_governance.py'),
            '--mode','initialize-new','--root',str(self.root),'--project-name','Consistency fixture',
            '--project-type','software','--profile','standard'], capture_output=True,text=True,timeout=30)
        self.assertEqual(result.returncode,0,result.stderr)
        return json.loads((self.root/'.senmu-buildos/config.json').read_text())

    def command(self, script, *args):
        result = subprocess.run([sys.executable,str(script), '--root',str(self.root),*args],
                                capture_output=True,text=True,timeout=30)
        return result, json.loads(result.stdout)

    def test_legacy_and_explicit_section_roles_share_one_contract(self):
        v = self.validator
        self.assertEqual(v.project_map_headings(), v.PROJECT_MAP_REQUIRED_HEADINGS)
        self.assertEqual(v.project_map_headings({'project_map_sections':None}),v.PROJECT_MAP_REQUIRED_HEADINGS)
        headings = {'capabilities':'## Capabilities','standards':'## Standards'}
        self.assertEqual(v.project_map_headings({'project_map_sections':headings}),tuple(headings.values()))
        for bad in ([], {'capabilities':'bad'}, {'unknown':'## A'},
                    {'capabilities':'## X','standards':'## X'},
                    {'capabilities':'# X','standards':'## Y'}):
            with self.assertRaises(ValueError): v.project_map_headings({'project_map_sections':bad})

    def localized(self):
        policy = self.initialize()
        self.assertIn('project_map_sections',policy)
        policy['project_map_sections'] = {'capabilities':'## Capabilities','standards':'## Standards'}
        (self.root/'.senmu-buildos/config.json').write_text(json.dumps(policy))
        (self.root/'src').mkdir(exist_ok=True);(self.root/'tests').mkdir(exist_ok=True)
        (self.root/'src/orders.py').write_text('def total(unit, count):\n    return unit * count\n')
        (self.root/'tests/test_orders.py').write_text('"""Test route fixture."""\n')
        (self.root/'engineering/contracts.md').write_text('Order totals are pure integer arithmetic.\n')
        path=self.root/'governance/PROJECT_MAP.md'
        lines=path.read_text().splitlines()
        found=[i for i,line in enumerate(lines) if line.startswith('| `<实际业务能力>`')]
        self.assertEqual(len(found),1)
        lines[found[0]]='| Order checkout | total | `src/orders.py` | [contract](../engineering/contracts.md) | `tests/test_orders.py` | pure result |'
        text='\n'.join(lines)+'\n'
        text=text.replace('## 责任与入口地图','## Capabilities').replace('## 项目规范索引','## Standards')
        path.write_text(text)
        return path

    def test_real_initialized_english_map_works_in_both_consumers(self):
        path=self.localized()
        result,out=self.command(PROJECT/'prepare_task_context.py','--map','governance/PROJECT_MAP.md','--capability','Order checkout')
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertEqual(out['status'],'selected')
        self.assertFalse(out['semantic_route_verified'])
        result,out=self.command(self.root/'.senmu-buildos/validate.py','--json')
        self.assertEqual(result.returncode,0,out)
        self.assertEqual(out['errors'],[])
        self.assertIn('## Capabilities',path.read_text())

    def test_heading_conflict_is_not_silently_overridden(self):
        self.localized()
        result,out=self.command(PROJECT/'prepare_task_context.py','--map','governance/PROJECT_MAP.md',
                                '--capability','Order checkout','--heading','## Other')
        self.assertNotEqual(result.returncode,0)
        self.assertEqual(out['status'],'blocked')

    def test_duplicate_section_is_rejected_by_both_consumers(self):
        path=self.localized();path.write_text(path.read_text()+'\n## Capabilities\n')
        result,out=self.command(PROJECT/'prepare_task_context.py','--map','governance/PROJECT_MAP.md','--capability','Order checkout')
        self.assertNotEqual(result.returncode,0)
        result,out=self.command(self.root/'.senmu-buildos/validate.py','--json')
        self.assertNotEqual(result.returncode,0)
        self.assertTrue(any('重复' in e['message'] for e in out['errors']))

    def test_nonfatal_lesson_warning_is_inside_one_json_document(self):
        policy=self.initialize()
        (self.root/policy['lessons_path']).write_text(lesson(candidate=True))
        result,out=self.command(self.root/'.senmu-buildos/validate.py','--json')
        self.assertEqual(result.returncode,0,out)
        self.assertTrue(any(w['code']=='lessons.validator_warning' for w in out['warnings']))
        self.assertNotIn('[LESSONS]',result.stdout)


if __name__=='__main__': unittest.main()
