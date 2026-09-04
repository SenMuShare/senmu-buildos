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
    / "repository-boundaries-and-release-units.md"
)


class PublicContributionFlowTest(unittest.TestCase):
    def test_public_pr_is_imported_as_candidate_not_source_history(self) -> None:
        text = DELIVERY.read_text(encoding="utf-8")
        for signal in (
            "a public PR is an inbound candidate",
            "import only allowlisted paths into a new internal Change Unit",
            "Never pull/merge public `main` into private main",
            "Regenerate the public projection from that internal commit onto an empty staging surface",
            "preserving author attribution/PR link",
        ):
            self.assertIn(signal, text)

    def test_public_ci_does_not_receive_private_credentials(self) -> None:
        text = DELIVERY.read_text(encoding="utf-8")
        self.assertIn("Public CI validates public content and has no private credentials", text)
        self.assertIn("Contribution intake, internal merge, and public release are separate records", text)


if __name__ == "__main__":
    unittest.main()
