#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CHECKER = ROOT / "python" / "sky_checker.py"
EXAMPLES = ROOT / "examples"


class CustomerSurfaceTests(unittest.TestCase):
    def test_customer_docs_exist(self):
        for path in [
            ROOT / "docs" / "customer_replay.md",
            ROOT / "docs" / "customer_verification.md",
            ROOT / "docs" / "use_cases.md",
            ROOT / "docs" / "release_checks.md",
        ]:
            self.assertTrue(path.exists(), msg=f"missing {path}")

    def test_customer_replay_doc_contains_replay_command(self):
        text = (ROOT / "docs" / "customer_replay.md").read_text()
        self.assertIn("python3 python/sky_checker.py bundle.sky.json", text)

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


class CustomerReplayTests(unittest.TestCase):
    def _run_checker(self, bundle_name: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(CHECKER), str(EXAMPLES / bundle_name)],
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=30,
        )

    def test_positive_examples_verify(self):
        for bundle_name in ["trivial_true.sky.json", "k_reduces.sky.json", "s_identity.sky.json"]:
            with self.subTest(bundle=bundle_name):
                result = self._run_checker(bundle_name)
                self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
                self.assertIn("VERIFIED", result.stdout)

    def test_negative_control_rejects(self):
        result = self._run_checker("negative_control.sky.json")
        self.assertNotEqual(result.returncode, 0, msg=result.stdout + result.stderr)
        self.assertIn("REJECTED", result.stdout)


if __name__ == "__main__":
    unittest.main()
