#!/usr/bin/env python3
"""Customer-facing replay tests for shipped example bundles."""
from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CHECKER = ROOT / "python" / "sky_checker.py"
EXAMPLES = ROOT / "examples"


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
