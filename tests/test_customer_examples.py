#!/usr/bin/env python3
from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


class CustomerSurfaceTests(unittest.TestCase):
    def test_customer_docs_exist(self):
        for path in [
            ROOT / "docs" / "customer_verification.md",
            ROOT / "docs" / "use_cases.md",
            ROOT / "docs" / "release_checks.md",
        ]:
            self.assertTrue(path.exists(), msg=f"missing {path}")

    def test_customer_verification_contains_replay_command(self):
        text = (ROOT / "docs" / "customer_verification.md").read_text()
        self.assertIn("python3 python/sky_checker.py bundle.sky.json", text)

    def test_use_cases_cover_primary_buyers(self):
        text = (ROOT / "docs" / "use_cases.md").read_text()
        for phrase in [
            "Smart Contract Certification",
            "Regulatory Audit",
            "Cross-Institutional Proof Sharing",
            "Verification Service Customers",
        ]:
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
