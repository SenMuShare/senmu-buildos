"""Run the documented caller against native local cleanup and a fake Docker boundary.

No real Docker, host model, user data or disk-pressure measurement is involved.
The existing helper remains unmodified; its per-plan safety boundary is tested.
"""
import importlib.util
import os
import re
import signal
import time
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "resource_workspace_fixture", ROOT / "tests/behavior/workspace_fixture.py")
FIXTURE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(FIXTURE)
TEMPLATE = ROOT / "skills/senmu-build-delivery/assets/delivery-governance/VERSION_AND_RELEASE.template.md"


def documented_driver():
    text = TEMPLATE.read_text(encoding="utf-8")
    section = text.split("<!-- independent-retention-example:start -->", 1)[1]
    section = section.split("<!-- independent-retention-example:end -->", 1)[0]
    return re.search(r"```(?:bash|python)\n(.*?)```", section, re.S).group(1)


class ResourceCloseoutGuidanceTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        FIXTURE.create(self.root, "release-closeout")
        local = (self.root / "retention.env").read_text()
        image = ("ARTIFACT_CLEANUP_ENABLED=0\nDOCKER_IMAGE_CLEANUP_ENABLED=1\n"
                 "MANAGED_IMAGE_REPOSITORIES=fixture/app\nCURRENT_IMAGES=fixture/app:current\n")
        (self.root / "retention-local.env").write_text(local)
        (self.root / "retention-images.env").write_text(image)
        (self.root / "retention.env").write_text(
            local.replace("DOCKER_IMAGE_CLEANUP_ENABLED=0", "DOCKER_IMAGE_CLEANUP_ENABLED=1")
            + "MANAGED_IMAGE_REPOSITORIES=fixture/app\nCURRENT_IMAGES=fixture/app:current\n")
        (self.root / "retention-scope.txt").write_text("independent\n")
        for name in ("current", "rollback", "old"):
            directory = self.root / "artifacts" / name
            directory.mkdir(parents=True)
            (directory / "manifest").write_text(name)
        self.expect_missing_current = False
        self.helper = (self.root / "scripts/cleanup.sh").read_bytes()
        binaries = self.root / "fixture-bin"
        binaries.mkdir()
        docker = binaries / "docker"
        docker.write_text("#!" + sys.executable + "\n" + '''import os, sys
from pathlib import Path
args = sys.argv[1:]
with Path("docker.calls").open("a") as stream:
    stream.write(" ".join(args) + "\\n")
if args == ["context", "show"]:
    print("fixture")
elif args and args[0] == "info":
    code = int(os.environ.get("FIXTURE_DOCKER_STATUS", "23"))
    if code:
        print("fixture engine unavailable", file=sys.stderr)
        raise SystemExit(code)
    print("fixture-engine")
elif args[:2] == ["image", "inspect"]:
    print("sha256:fixture-current")
elif args[:2] == ["image", "ls"] or (args and args[0] == "ps"):
    pass
else:
    raise SystemExit("Unexpected fake Docker request: " + repr(args))
''')
        docker.chmod(0o700)
        self.receipts_root = self.root / "run-receipts"
        self.receipts_root.mkdir()
        self.last_receipt_dir = self.root
        self.environment = {**os.environ,
                            "RETENTION_RECEIPT_ROOT": str(self.receipts_root),
                            "PATH": str(binaries) + os.pathsep + os.environ.get("PATH", ""),
                            "RETENTION_PROJECT_ROOT": str(self.root),
                            "RELEASE_CLOSEOUT_AUTHORIZED": "1",
                            "FIXTURE_DOCKER_STATUS": "23",
                            "VERIFY_STATUS": "0"}

    def run_driver(self, *, documented=True, **environment):
        driver = (documented_driver() if documented else
                  "#!/usr/bin/env bash\nset -euo pipefail\n"
                  "bash scripts/verify.sh\n"
                  "bash scripts/cleanup.sh retention.env apply > coupled-cleanup.receipt\n")
        (self.root / "scripts/release.sh").write_text(driver)
        before = set(self.receipts_root.iterdir())
        interpreter = sys.executable if driver.startswith("#!/usr/bin/env python3") else "bash"
        result = subprocess.run([interpreter, "scripts/release.sh"], cwd=self.root,
                                env={**self.environment, **environment},
                                capture_output=True, text=True, timeout=20)
        created = set(self.receipts_root.iterdir()) - before
        self.assertLessEqual(len(created), 1)
        self.last_receipt_dir = next(iter(created)) if created else self.root
        self.assertEqual((self.root / "scripts/cleanup.sh").read_bytes(), self.helper)
        for name in ("current", "rollback"):
            path = self.root / "artifacts" / name / "manifest"
            if name == "current" and self.expect_missing_current:
                self.assertFalse(path.exists())
                continue
            self.assertEqual(path.read_text(), name)
        return result

    def receipt_path(self, name):
        return self.last_receipt_dir / name

    def receipt(self, name):
        return self.receipt_path(name).read_text()

    def test_combined_plan_keeps_local_artifacts_when_engine_is_unknown(self):
        result = self.run_driver(documented=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertTrue((self.root / "artifacts/old").exists())
        self.assertIn("release_retention_status=blocked", self.receipt("coupled-cleanup.receipt"))
        self.assertIn("artifacts_removed=0", self.receipt("coupled-cleanup.receipt"))

    def test_independent_local_cleanup_survives_engine_failure_without_hiding_it(self):
        result = self.run_driver()
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse((self.root / "artifacts/old").exists())
        self.assertIn("release_retention_status=completed", self.receipt("local-cleanup.receipt"))
        self.assertIn("release_retention_status=blocked", self.receipt("image-cleanup.receipt"))
        self.assertIn("local_rc=0 image_rc=2", self.receipt("retention-groups.receipt"))
        self.assertIn("space_reclaimed=not_measured", self.receipt("local-cleanup.receipt"))

    def test_independent_groups_both_succeed(self):
        result = self.run_driver(FIXTURE_DOCKER_STATUS="0")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse((self.root / "artifacts/old").exists())
        self.assertIn("release_retention_status=no_candidates", self.receipt("image-cleanup.receipt"))
        self.assertIn("local_rc=0 image_rc=0", self.receipt("retention-groups.receipt"))

    def test_shared_dependencies_keep_the_combined_safety_boundary(self):
        (self.root / "retention-scope.txt").write_text("coupled\n")
        result = self.run_driver()
        self.assertNotEqual(result.returncode, 0)
        self.assertTrue((self.root / "artifacts/old").exists())
        self.assertTrue(self.receipt_path("coupled-cleanup.receipt").exists())
        self.assertFalse(self.receipt_path("local-cleanup.receipt").exists())
        self.assertFalse(self.receipt_path("image-cleanup.receipt").exists())

    def test_unknown_dependencies_do_not_self_authorize_splitting(self):
        (self.root / "retention-scope.txt").write_text("unknown\n")
        result = self.run_driver()
        self.assertNotEqual(result.returncode, 0)
        self.assertTrue((self.root / "artifacts/old").exists())
        self.assertFalse((self.root / "docker.calls").exists())
        self.assertFalse(self.receipt_path("local-cleanup.receipt").exists())

    def test_missing_authority_keeps_all_artifacts(self):
        result = self.run_driver(RELEASE_CLOSEOUT_AUTHORIZED="0")
        self.assertNotEqual(result.returncode, 0)
        self.assertTrue((self.root / "artifacts/old").exists())
        self.assertFalse((self.root / "docker.calls").exists())

    def test_failed_target_verification_stops_all_cleanup(self):
        result = self.run_driver(VERIFY_STATUS="7")
        self.assertEqual(result.returncode, 7)
        self.assertTrue((self.root / "artifacts/old").exists())
        self.assertFalse((self.root / "docker.calls").exists())
        self.assertFalse(self.receipt_path("local-cleanup.receipt").exists())

    def test_missing_current_blocks_only_its_independent_group(self):
        self.expect_missing_current = True
        (self.root / "artifacts/current/manifest").unlink()
        (self.root / "artifacts/current").rmdir()
        result = self.run_driver(FIXTURE_DOCKER_STATUS="0")
        self.assertNotEqual(result.returncode, 0)
        self.assertTrue((self.root / "artifacts/old").exists())
        self.assertIn("release_retention_status=blocked", self.receipt("local-cleanup.receipt"))
        self.assertIn("release_retention_status=no_candidates", self.receipt("image-cleanup.receipt"))
        self.assertIn("local_rc=2 image_rc=0", self.receipt("retention-groups.receipt"))

    def test_both_failures_remain_visible(self):
        path = self.root / "retention-local.env"
        path.write_text(path.read_text().replace("ARTIFACT_ROOT=artifacts", "ARTIFACT_ROOT=missing"))
        result = self.run_driver()
        self.assertNotEqual(result.returncode, 0)
        self.assertTrue((self.root / "artifacts/old").exists())
        self.assertIn("local_rc=2 image_rc=2", self.receipt("retention-groups.receipt"))

    def test_pinned_recovery_artifact_is_retained(self):
        with (self.root / "retention-local.env").open("a") as stream:
            stream.write("PINNED_ARTIFACTS=old\n")
        result = self.run_driver(FIXTURE_DOCKER_STATUS="0")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue((self.root / "artifacts/old").exists())
        self.assertIn("release_retention_status=no_candidates", self.receipt("local-cleanup.receipt"))

    def test_nested_repository_blocks_local_group_without_modifying_it(self):
        nested = self.root / "artifacts/old/.git"
        nested.write_text("synthetic protected metadata\n")
        result = self.run_driver(FIXTURE_DOCKER_STATUS="0")
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(nested.read_text(), "synthetic protected metadata\n")
        self.assertIn("local_rc=2 image_rc=0", self.receipt("retention-groups.receipt"))

    def test_repeated_attempt_does_not_recreate_completed_local_work(self):
        first = self.run_driver()
        first_directory = self.last_receipt_dir
        first_receipt = self.receipt("local-cleanup.receipt")
        second = self.run_driver()
        self.assertNotEqual(first.returncode, 0)
        self.assertNotEqual(second.returncode, 0)
        self.assertNotEqual(first_directory, self.last_receipt_dir, "retry reused its prior receipt directory")
        self.assertEqual((first_directory / "local-cleanup.receipt").read_text(), first_receipt)
        self.assertIn("release_retention_status=completed", first_receipt)
        self.assertFalse((self.root / "artifacts/old").exists())
        self.assertIn("release_retention_status=no_candidates", self.receipt("local-cleanup.receipt"))
        self.assertIn("local_rc=0 image_rc=2", self.receipt("retention-groups.receipt"))


    def test_material_role_route_remains_explicit(self):
        route = (ROOT / "skills/senmu-build-workflow/SKILL.md").read_text()
        self.assertTrue(any("material roles" in line.lower() and "workflow-materials-and-deliverables.md" in line
                            for line in route.splitlines()))

    def test_cross_enabled_image_config_stops_before_any_apply(self):
        (self.root / "retention-images.env").write_text((self.root / "retention.env").read_text())
        result = self.run_driver(FIXTURE_DOCKER_STATUS="0")
        self.assertNotEqual(result.returncode, 0)
        self.assertTrue((self.root / "artifacts/old").exists())
        self.assertFalse((self.root / "docker.calls").exists())
        self.assertFalse(self.receipt_path("local-cleanup.receipt").exists())

    def test_cross_enabled_local_config_stops_before_any_apply(self):
        (self.root / "retention-local.env").write_text((self.root / "retention.env").read_text())
        result = self.run_driver(FIXTURE_DOCKER_STATUS="0")
        self.assertNotEqual(result.returncode, 0)
        self.assertTrue((self.root / "artifacts/old").exists())
        self.assertFalse((self.root / "docker.calls").exists())

    def test_duplicate_partition_flag_is_rejected_before_apply(self):
        with (self.root / "retention-images.env").open("a") as stream:
            stream.write("ARTIFACT_CLEANUP_ENABLED=1\n")
        result = self.run_driver(FIXTURE_DOCKER_STATUS="0")
        self.assertNotEqual(result.returncode, 0)
        self.assertTrue((self.root / "artifacts/old").exists())
        self.assertFalse((self.root / "docker.calls").exists())

    def test_linked_source_config_cannot_be_laundered_by_snapshot(self):
        config = self.root / "retention-images.env"
        data = config.read_bytes()
        config.unlink()
        target = self.root / "linked-input.env"
        target.write_bytes(data)
        config.symlink_to(target)
        result = self.run_driver(FIXTURE_DOCKER_STATUS="0")
        self.assertNotEqual(result.returncode, 0)
        self.assertTrue((self.root / "artifacts/old").exists())
        self.assertFalse((self.root / "docker.calls").exists())

    def test_validated_configs_are_frozen_before_common_verification(self):
        # The later change cannot turn the image-only invocation into a second local cleanup.
        config = self.root / "retention-local.env"
        config.write_text(config.read_text().replace("ARTIFACT_ROOT=artifacts", "ARTIFACT_ROOT=missing"))
        (self.root / "scripts/verify.sh").write_text(
            "#!/usr/bin/env bash\ncp retention.env retention-images.env\n")
        result = self.run_driver(FIXTURE_DOCKER_STATUS="0")
        self.assertNotEqual(result.returncode, 0)
        self.assertTrue((self.root / "artifacts/old").exists())
        self.assertIn("local_rc=2 image_rc=0", self.receipt("retention-groups.receipt"))
        self.assertIn("ARTIFACT_CLEANUP_ENABLED=0", (self.last_receipt_dir / "retention-images.env").read_text())


    def test_receipt_owner_inside_cleanup_root_is_rejected_before_apply(self):
        self.receipts_root = self.root / "artifacts/old/receipts"
        self.receipts_root.mkdir()
        self.environment["RETENTION_RECEIPT_ROOT"] = str(self.receipts_root)
        result = self.run_driver(FIXTURE_DOCKER_STATUS="0")
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual((self.root / "artifacts/old/manifest").read_text(), "old")
        self.assertFalse((self.root / "docker.calls").exists())
        self.assertFalse(self.receipt_path("local-cleanup.receipt").exists())

    def check_parent_cancellation(self, signum):
        # Keep the real cleanup helper. Substitute its leaf find command to observe signals and exit.
        executable = self.root / "fixture-bin/find"
        executable.write_text("#!" + sys.executable + "\n" + """import os, signal, time
from pathlib import Path

def stop(signum, frame):
    time.sleep(0.15)
    Path("cleanup.finished").write_text(str(signum))
    raise SystemExit(128 + signum)

signal.signal(signal.SIGTERM, stop)
signal.signal(signal.SIGINT, stop)
Path("cleanup.started").write_text(str(os.getpid()))
while True:
    time.sleep(0.05)
""")
        executable.chmod(0o700)
        driver = documented_driver()
        (self.root / "scripts/release.sh").write_text(driver)
        interpreter = sys.executable if driver.startswith("#!/usr/bin/env python3") else "bash"
        process = subprocess.Popen([interpreter, "scripts/release.sh"], cwd=self.root,
                                   env=self.environment, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                   text=True, start_new_session=True)
        leaf_pid = None
        try:
            deadline = time.monotonic() + 5
            started = self.root / "cleanup.started"
            while not started.exists() and time.monotonic() < deadline and process.poll() is None:
                time.sleep(0.02)
            self.assertTrue(started.exists(), "cleanup did not reach the observed leaf operation")
            leaf_pid = int(started.read_text())
            os.kill(process.pid, signum)  # Deliberately signal only the caller, not its process group.
            try:
                stdout, stderr = process.communicate(timeout=3)
            except subprocess.TimeoutExpired:
                self.fail("parent-only cancellation did not terminate and reconcile the active cleanup child")
            self.assertEqual(process.returncode, 128 + signum, stderr)
            self.assertTrue((self.root / "cleanup.finished").exists())
            with self.assertRaises(ProcessLookupError):
                os.kill(leaf_pid, 0)
            self.assertFalse((self.root / "docker.calls").exists())
            self.assertTrue((self.root / "artifacts/old").exists())
            self.assertEqual((self.root / "scripts/cleanup.sh").read_bytes(), self.helper)
            for name in ("current", "rollback"):
                self.assertEqual((self.root / "artifacts" / name / "manifest").read_text(), name)
            directories = list(self.receipts_root.iterdir())
            self.assertEqual(len(directories), 1)
            self.last_receipt_dir = directories[0]
            self.assertIn("image_rc=not_called", self.receipt("retention-groups.receipt"))
            self.assertIn("release_retention_status=failed", self.receipt("local-cleanup.receipt"))
        finally:
            # Last-resort teardown is limited to this test's known temporary leaf/caller processes.
            if leaf_pid is not None:
                try:
                    os.kill(leaf_pid, signal.SIGTERM)
                except ProcessLookupError:
                    pass
            if process.poll() is None:
                try:
                    process.communicate(timeout=2)
                except subprocess.TimeoutExpired:
                    os.killpg(process.pid, signal.SIGKILL)
                    process.communicate(timeout=2)

    def test_parent_only_termination_stops_cleanup_child_and_next_group(self):
        self.check_parent_cancellation(signal.SIGTERM)

    def test_parent_only_interrupt_stops_cleanup_child_and_next_group(self):
        self.check_parent_cancellation(signal.SIGINT)


if __name__ == "__main__":
    unittest.main()
