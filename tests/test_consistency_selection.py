"""Selection accuracy and bounded display, without source scanning or model calls."""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
ROOT=Path(__file__).resolve().parents[1]
SCRIPT=ROOT/'skills/senmu-build-engineering/scripts/resolve_engineering_guidance.py'
spec=importlib.util.spec_from_file_location('consistency_selector',SCRIPT)
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

class ConsistencySelectionTests(unittest.TestCase):
    def setUp(self):
        d=tempfile.TemporaryDirectory();self.addCleanup(d.cleanup);self.root=Path(d.name)
        names={m.ENGINEERING+x for x in m.PROFILES.values()}|{m.DEPLOYMENT,m.ENGINEERING+'application-security-and-abuse.md',m.ENGINEERING+'stack-profiles/dependency-and-ci-review.md',m.ENGINEERING+'stack-profiles/schema-and-migration-review.md',m.ENGINEERING+'backend-services-and-data-contracts.md'}
        for name in names:
            p=self.root/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text('Synthetic reference\n')
    def select(self,paths,**kw):return m.select(paths,[],root=self.root,**kw)
    def test_notebook_is_not_assumed_to_be_python(self):
        out=self.select(['a.ipynb']);self.assertEqual(out['status'],'partial');self.assertEqual(out['references'],[])
    def test_notebook_languages_are_path_scoped(self):
        out=self.select(['a.ipynb','b.ipynb'],notebook_languages={'a.ipynb':'python','b.ipynb':'julia'})
        self.assertEqual(out['status'],'partial');self.assertEqual(out['references'][0]['subjects'],['a.ipynb'])
        self.assertEqual(out['unresolved'][0]['path'],'b.ipynb')
    def test_missing_role_information_stays_partial(self):
        self.assertEqual(self.select(['app/config.yaml'])['status'],'partial')
        self.assertEqual(self.select(['k8s/deployment.yaml'])['status'],'partial')
    def test_declared_deployment_roles_route_without_reading_yaml(self):
        for role in m.FILE_ROLES:
            result=self.select(['app/config.yaml'],file_roles={'app/config.yaml':role})
            self.assertEqual(result['references'][0]['reference'],m.DEPLOYMENT)
            self.assertFalse(result['source_scanned'])
    def test_common_compose_and_terraform_variants(self):
        for name in ('compose.prod.yaml','docker-compose.override.yml','terraform.tfvars.json','infra/main.tf.json'):
            with self.subTest(path=name): self.assertEqual(self.select([name])['references'][0]['reference'],m.DEPLOYMENT)
    def test_roles_cannot_silently_target_another_path(self):
        with self.assertRaises(ValueError):self.select(['a.yaml'],file_roles={'b.yaml':'compose'})
        with self.assertRaises(ValueError):self.select(['a.py'],notebook_languages={'a.py':'python'})
        with self.assertRaises(ValueError):self.select(['a.yaml'],file_roles={'a.yaml':'other'})
    def test_conflicting_duplicate_declarations_fail(self):
        with self.assertRaises(ValueError):m.declarations(['a.ipynb=python','a.ipynb=rust'])
    def test_summary_identity_and_totals_preserve_complete_mapping(self):
        paths=[f'src/feature-{n:03d}/long_component_name.rs' for n in range(200)]
        full=self.select(paths);brief=m.summarize(full)
        self.assertEqual(brief['reference_selection_identity'],full['reference_selection_identity'])
        self.assertEqual(brief['path_count'],200);self.assertEqual(brief['references'][0]['subject_count'],200)
        self.assertEqual(len(brief['references'][0]['subject_examples']),3)
        self.assertLess(len(json.dumps(brief)),len(json.dumps(full))//3)
        self.assertEqual(full['paths'],sorted(paths))
    def test_unresolved_summary_never_hides_the_total(self):
        out=self.select([f'x{i}.unknown' for i in range(50)]);brief=m.summarize(out)
        self.assertEqual(brief['unresolved_count'],50);self.assertEqual(len(brief['unresolved_examples']),3)
        self.assertEqual(brief['status'],'partial')
    def test_cli_default_summary_and_full_are_explicit(self):
        common=[sys.executable,str(SCRIPT),'--path','src/x.rs']
        brief=json.loads(subprocess.check_output(common));full=json.loads(subprocess.check_output(common+['--format','full']))
        self.assertEqual(brief['format'],'summary');self.assertEqual(full['paths'],['src/x.rs'])
        self.assertEqual(brief['reference_selection_identity'],full['reference_selection_identity'])

if __name__=='__main__':unittest.main()
