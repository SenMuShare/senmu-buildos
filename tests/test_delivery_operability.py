"""Protect changed template contracts, not claim agent or production performance.

Runtime identity and native cleanup behavior remain covered by the existing
release-identity and resource-closeout tests. Host scenarios are separate.
"""
from __future__ import annotations

import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "skills/senmu-build-delivery/assets/delivery-governance"


class DeliveryOperabilityTemplateTests(unittest.TestCase):
    def test_single_source_default_preserves_additive_composition_fields(self):
        data = json.loads((ASSETS / "ARTIFACT_MANIFEST.template.json").read_text(encoding="utf-8"))
        self.assertEqual(data["schema_version"], "1.1.0")
        self.assertIsNone(data["composition"])
        self.assertEqual(data["status"], "candidate")
        self.assertEqual(set(data["source"]), {"repository", "revision", "tag", "dirty"})
        self.assertEqual(set(data["build"]), {"id", "entrypoint", "environment_ref", "created_at"})
        artifact, = data["artifacts"]
        self.assertEqual(artifact["selection"], "new")
        self.assertIsNone(artifact["provenance_ref"])
        self.assertIsNone(artifact["component_id"])
        self.assertIsNone(artifact["component_version"])
        self.assertEqual(artifact["consumer_refs"], [])
        self.assertTrue({"id", "kind", "location", "sha256", "size_bytes", "target_platform",
                         "configuration_schema_ref"}.issubset(artifact))

    def test_deployment_template_does_not_reimpose_serial_cleanup_success(self):
        text = (ASSETS / "DEPLOYMENT.template.md").read_text(encoding="utf-8")
        line, = [line for line in text.splitlines() if line.startswith("- 发布收口脚本：")]
        self.assertNotIn("并在运行端成功后执行构建端收口", line)
        self.assertIn("只有目标版本、健康和受影响主流程通过后", line)
        self.assertIn("RELEASE_CLOSEOUT_AUTHORIZED=1", line)
        self.assertIn("共享或未知依赖仍联动", line)
        self.assertIn("每组结果分别保留", line)


if __name__ == "__main__":
    unittest.main()
