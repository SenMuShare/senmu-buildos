#!/usr/bin/env python3
"""Protect the private-authority/public-projection contribution boundary."""

from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
DELIVERY = (
    ROOT
    / "skills"
    / "senmu-build-delivery"
    / "references"
    / "仓库边界与发布单元治理规范.md"
)


class PublicContributionFlowTest(unittest.TestCase):
    def test_public_pr_is_imported_as_candidate_not_source_history(self) -> None:
        text = DELIVERY.read_text(encoding="utf-8")
        for signal in (
            "公开 Pull Request 是入站候选",
            "公开白名单路径导入新的内部 Change Unit",
            "禁止把公开 `main` 直接 pull／merge 到私有主线",
            "重新生成空暂存面的公开投影",
            "保留作者归属和 PR 链接",
        ):
            self.assertIn(signal, text)

    def test_public_ci_does_not_receive_private_credentials(self) -> None:
        text = DELIVERY.read_text(encoding="utf-8")
        self.assertIn("公开 CI 只验证公开面，不持有私有仓凭据", text)
        self.assertIn("接收贡献、内部合并和公开发布分别登记", text)


if __name__ == "__main__":
    unittest.main()
