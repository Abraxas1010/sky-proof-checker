#!/usr/bin/env python3
"""Cross-language CLI parity checks for the SKY proof checker."""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent


def python_runner(bundle_path: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(ROOT / "python" / "sky_checker.py"), bundle_path],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=30,
    )


def rust_runner(bundle_path: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["cargo", "run", "--quiet", "--", bundle_path],
        cwd=ROOT / "rust",
        capture_output=True,
        text=True,
        timeout=60,
    )


def go_runner(bundle_path: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["go", "run", "checker.go", bundle_path],
        cwd=ROOT / "go",
        capture_output=True,
        text=True,
        timeout=60,
    )


def ts_runner(bundle_path: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["npx", "ts-node", "src/reducer.ts", bundle_path],
        cwd=ROOT / "typescript",
        capture_output=True,
        text=True,
        timeout=60,
    )


IMPLEMENTATIONS = {
    "python": (python_runner, lambda: shutil.which(sys.executable) is not None),
    "rust": (rust_runner, lambda: shutil.which("cargo") is not None),
    "go": (go_runner, lambda: shutil.which("go") is not None),
    "typescript": (
        ts_runner,
        lambda: shutil.which("node") is not None and shutil.which("npx") is not None,
    ),
}


class CliParityTests(unittest.TestCase):
    def run_case(self, bundle: dict, expect_success: bool):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as handle:
            json.dump(bundle, handle)
            path = handle.name

        try:
            for name, (runner, available) in IMPLEMENTATIONS.items():
                if not available():
                    continue
                result = runner(path)
                if expect_success:
                    self.assertEqual(
                        result.returncode,
                        0,
                        msg=f"{name} failed: stdout={result.stdout} stderr={result.stderr}",
                    )
                else:
                    self.assertNotEqual(
                        result.returncode,
                        0,
                        msg=f"{name} unexpectedly accepted: stdout={result.stdout} stderr={result.stderr}",
                    )
        finally:
            Path(path).unlink(missing_ok=True)

    def test_trivial_true_passes_everywhere(self):
        bundle = json.loads((ROOT / "examples" / "trivial_true.sky.json").read_text())
        self.run_case(bundle, expect_success=True)

    def test_empty_bundle_is_rejected_everywhere(self):
        self.run_case({"format": "sky-bundle", "obligations": []}, expect_success=False)

    def test_bogus_false_term_is_rejected_everywhere(self):
        self.run_case(
            {
                "format": "sky-bundle",
                "obligations": [
                    {
                        "id": "bogus_false",
                        "compiled_check": ["app", ["app", "K", "S"], "Y"],
                        "expected_result": "false",
                        "fuel": 0,
                    }
                ],
            },
            expect_success=False,
        )


if __name__ == "__main__":
    unittest.main()
