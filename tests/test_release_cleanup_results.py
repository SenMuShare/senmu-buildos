"""Release cleanup uses disposable files and a fake Docker boundary only."""
from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'skills/senmu-build-delivery/assets/delivery-governance/CLEANUP_RELEASE_ASSETS.template.sh'
FAKE_DOCKER = r'''#!/usr/bin/env python3
import json, os, pathlib, sys
args = sys.argv[1:]
if args[:1] == ['--context']: args = args[2:]
state = json.loads(pathlib.Path(os.environ['FAKE_DOCKER_STATE']).read_text())
if os.environ.get('FAIL_DOCKER_COMMAND') == ' '.join(args[:2]):
    print('synthetic Docker failure', file=sys.stderr); sys.exit(42)
if args == ['context', 'show']: print('fixture-context')
elif args[:1] == ['info']: print('fixture-engine')
elif args[:2] == ['image', 'inspect']:
    ref = args[-1]
    if ref not in state['refs']: sys.exit(1)
    print(state['refs'][ref])
elif args[:2] == ['ps', '-a']: print('\n'.join(state['container_refs']))
elif args[:2] == ['ps', '-aq']: print('\n'.join(state['containers']))
elif args[:1] == ['inspect']: print(state['containers'][args[-1]])
elif args[:2] == ['image', 'ls']:
    if os.environ.get('MUTATE_ARTIFACT'): pathlib.Path(os.environ['MUTATE_ARTIFACT']).write_text('concurrent modification')
    for ref, sha in state['refs'].items(): print(ref + '|' + sha)
elif args[:2] == ['image', 'rm']:
    with open(os.environ['FAKE_REMOVALS'], 'a') as f: f.write(args[-1] + '\n')
    state['refs'].pop(args[-1], None)
    pathlib.Path(os.environ['FAKE_DOCKER_STATE']).write_text(json.dumps(state))
else:
    print('Unexpected Docker command: ' + repr(args), file=sys.stderr); sys.exit(50)
'''


@unittest.skipUnless(shutil.which('bash'), 'Bash is required by the generated template')
class ReleaseCleanupResultsTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.artifacts = self.root / 'delivery/artifacts'
        for name in ('current', 'previous', 'old'):
            path = self.artifacts / name
            path.mkdir(parents=True)
            (path / 'manifest').write_text('synthetic')
        self.config = self.root / 'retention.env'
        self.bin = self.root / 'bin'; self.bin.mkdir()
        self.docker = self.bin / 'docker'; self.docker.write_text(FAKE_DOCKER); self.docker.chmod(0o755)
        self.state = self.root / 'docker.json'
        self.state.write_text(json.dumps({
            'refs': {'example/app:current': 'sha256:current', 'example/app:previous': 'sha256:previous',
                     'example/app:old': 'sha256:old', 'example/app:alias': 'sha256:current',
                     'example/app:<none>': 'sha256:unowned'},
            'container_refs': ['example/app:previous'], 'containers': {}}))
        self.removals = self.root / 'removed.txt'
        self.env = {**os.environ, 'RETENTION_PROJECT_ROOT': str(self.root),
                    'PATH': str(self.bin) + os.pathsep + os.environ['PATH'],
                    'FAKE_DOCKER_STATE': str(self.state), 'FAKE_REMOVALS': str(self.removals),
                    'RELEASE_CLOSEOUT_AUTHORIZED': '1'}

    def run_cleanup(self, *, artifacts=True, images=False, mode='apply', extra='', failure=None):
        self.config.write_text(
            f'ARTIFACT_CLEANUP_ENABLED={int(artifacts)}\nARTIFACT_ROOT=delivery/artifacts\n'
            'CURRENT_ARTIFACT=current\nPREVIOUS_ARTIFACT=previous\n'
            f'DOCKER_IMAGE_CLEANUP_ENABLED={int(images)}\nMANAGED_IMAGE_REPOSITORIES=example/app\n'
            'CURRENT_IMAGES=example/app:current\nPREVIOUS_IMAGES=example/app:previous\n'
            'PINNED_IMAGES=\nRESOURCE_SURFACE=fixture-builder\n' + extra)
        env = dict(self.env)
        if failure: env['FAIL_DOCKER_COMMAND'] = failure
        return subprocess.run(['bash', str(SCRIPT), str(self.config), mode], env=env,
                              text=True, capture_output=True, timeout=60)

    def test_git_metadata_cannot_be_configured_as_artifact_root(self):
        metadata = self.root / '.git'
        for name in ('current', 'previous', 'objects'):
            (metadata / name).mkdir(parents=True, exist_ok=True)
        self.config.write_text('ARTIFACT_CLEANUP_ENABLED=1\nARTIFACT_ROOT=.git\nCURRENT_ARTIFACT=current\nPREVIOUS_ARTIFACT=previous\nDOCKER_IMAGE_CLEANUP_ENABLED=0\n')
        result = subprocess.run(['bash', str(SCRIPT), str(self.config), 'apply'], env=self.env, text=True, capture_output=True, timeout=60)
        self.assertNotEqual(result.returncode, 0)
        self.assertTrue((metadata / 'objects').exists())
        self.assertIn('Git metadata', result.stderr)

    def test_disabled_is_not_completed_or_authorized_cleanup(self):
        self.env.pop('RELEASE_CLOSEOUT_AUTHORIZED')
        for mode in ('apply', 'dry-run'):
            result = self.run_cleanup(artifacts=False, mode=mode)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn('release_retention_status=disabled', result.stdout)
            self.assertTrue((self.artifacts / 'old').exists())

    def test_dry_run_reports_plan_not_actual_removals(self):
        result = self.run_cleanup(images=True, mode='dry-run')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('release_retention_status=planned', result.stdout)
        self.assertIn('artifacts_planned=1 artifacts_removed=0', result.stdout)
        self.assertIn('images_planned=1 images_removed=0', result.stdout)
        self.assertTrue((self.artifacts / 'old').exists())
        self.assertFalse(self.removals.exists())

    def test_success_removes_only_authorized_artifact_and_image_reference(self):
        result = self.run_cleanup(images=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('release_retention_status=completed', result.stdout)
        self.assertIn('artifacts_planned=1 artifacts_removed=1', result.stdout)
        self.assertEqual(self.removals.read_text().splitlines(), ['example/app:old'])
        self.assertFalse((self.artifacts / 'old').exists())
        self.assertTrue((self.artifacts / 'current').exists())
        self.assertTrue((self.artifacts / 'previous').exists())
        self.assertIn('space_reclaimed=not_measured', result.stdout)
        self.assertIn('docker_engine_id=fixture-engine', result.stdout)

    def test_empty_enabled_scope_is_distinct_from_disabled(self):
        shutil.rmtree(self.artifacts / 'old')
        result = self.run_cleanup()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('release_retention_status=no_candidates', result.stdout)

    def test_each_failed_docker_inventory_blocks_all_deletions(self):
        for command in ('image ls', 'ps -aq', 'ps -a', 'image inspect', 'info --format'):
            with self.subTest(command=command):
                result = self.run_cleanup(images=True, failure=command)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn('release_retention_status=blocked', result.stdout)
                self.assertTrue((self.artifacts / 'old').exists())
                self.assertFalse(self.removals.exists())

    def test_stopped_container_and_alias_protection_stays(self):
        state = json.loads(self.state.read_text()); state['containers']['stopped'] = 'sha256:old'
        self.state.write_text(json.dumps(state))
        result = self.run_cleanup(artifacts=False, images=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('kept_image=example/app:old', result.stdout)
        self.assertIn('images_unowned=1', result.stdout)
        self.assertFalse(self.removals.exists())

    def test_missing_rollback_blocks_before_any_delete(self):
        shutil.rmtree(self.artifacts / 'previous')
        result = self.run_cleanup(images=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertTrue((self.artifacts / 'old').exists())
        self.assertFalse(self.removals.exists())

    def test_pinned_artifact_is_not_selected(self):
        result = self.run_cleanup(extra='PINNED_ARTIFACTS=old\n')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('release_retention_status=no_candidates', result.stdout)
        self.assertTrue((self.artifacts / 'old').exists())

    def test_repository_descendant_retains_whole_artifact(self):
        (self.artifacts / 'old/nested/.git').mkdir(parents=True)
        result = self.run_cleanup()
        self.assertNotEqual(result.returncode, 0)
        self.assertTrue((self.artifacts / 'old/manifest').exists())

    def test_bare_repository_descendant_retains_whole_artifact(self):
        nested = self.artifacts / 'old/repo'; nested.mkdir()
        (nested / 'HEAD').write_text('ref: refs/heads/main')
        (nested / 'objects').mkdir(); (nested / 'refs').mkdir()
        result = self.run_cleanup()
        self.assertNotEqual(result.returncode, 0)
        self.assertTrue((self.artifacts / 'old/manifest').exists())

    def test_native_failure_after_artifact_removal_is_partial_not_completed(self):
        result = self.run_cleanup(images=True, failure='image rm')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('release_retention_status=failed', result.stdout)
        self.assertIn('artifacts_removed=1', result.stdout)
        self.assertIn('images_removed=0', result.stdout)

    def test_linked_descendant_blocks_whole_artifact(self):
        target = self.root / 'unique.txt'; target.write_text('unique')
        try:
            (self.artifacts / 'old/link').symlink_to(target)
        except OSError:
            self.skipTest('symlinks unavailable')
        result = self.run_cleanup()
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(target.read_text(), 'unique')
        self.assertTrue((self.artifacts / 'old/manifest').exists())

    def test_changed_artifact_metadata_blocks_before_removal(self):
        self.env['MUTATE_ARTIFACT'] = str(self.artifacts / 'old/manifest')
        result = self.run_cleanup(images=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('release_retention_status=blocked', result.stdout)
        self.assertTrue((self.artifacts / 'old/manifest').exists())
        self.assertFalse(self.removals.exists())

    def test_reentry_only_handles_still_existing_resources(self):
        first = self.run_cleanup(images=True)
        self.assertEqual(first.returncode, 0, first.stderr)
        second = self.run_cleanup(images=True)
        self.assertEqual(second.returncode, 0, second.stderr)
        self.assertIn('release_retention_status=no_candidates', second.stdout)
        self.assertEqual(self.removals.read_text().splitlines(), ['example/app:old'])

    def test_apply_requires_existing_closeout_authority(self):
        self.env.pop('RELEASE_CLOSEOUT_AUTHORIZED')
        result = self.run_cleanup()
        self.assertNotEqual(result.returncode, 0)
        self.assertTrue((self.artifacts / 'old').exists())


if __name__ == '__main__':
    unittest.main()
