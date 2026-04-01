#!/usr/bin/env python3
"""Cross-language parity tests for the SKY proof checker."""
import json
import subprocess
import sys
import os

EXAMPLES_DIR = os.path.join(os.path.dirname(__file__), "..", "examples")
PYTHON_CHECKER = os.path.join(os.path.dirname(__file__), "..", "python", "sky_checker.py")

PASS = 0
FAIL = 0


def check(name, condition, detail=""):
    global PASS, FAIL
    if condition:
        PASS += 1
        print(f"  PASS  {name}" + (f"  ({detail})" if detail else ""))
    else:
        FAIL += 1
        print(f"  FAIL  {name}" + (f"  ({detail})" if detail else ""))


def run_python(bundle_path):
    result = subprocess.run(
        [sys.executable, PYTHON_CHECKER, "--verbose", bundle_path],
        capture_output=True, text=True, timeout=30,
    )
    return result.returncode, result.stdout, result.stderr


def main():
    global PASS, FAIL
    print("SKY Proof Checker — Test Suite")
    print("=" * 60)

    # Test 1: trivial_true should PASS
    print("\n  Test 1: trivial_true.sky.json")
    rc, out, _ = run_python(os.path.join(EXAMPLES_DIR, "trivial_true.sky.json"))
    check("trivial_true verifies", rc == 0)
    check("output says VERIFIED", "VERIFIED" in out)

    # Test 2: k_reduces should PASS
    print("\n  Test 2: k_reduces.sky.json")
    rc, out, _ = run_python(os.path.join(EXAMPLES_DIR, "k_reduces.sky.json"))
    check("k_reduces verifies", rc == 0)
    check("K rule uses 1 step", "steps=1/" in out)

    # Test 3: s_identity should PASS
    print("\n  Test 3: s_identity.sky.json")
    rc, out, _ = run_python(os.path.join(EXAMPLES_DIR, "s_identity.sky.json"))
    check("s_identity verifies", rc == 0)
    check("Identity uses 2 steps", "steps=2/" in out)

    # Test 4: negative_control should FAIL
    print("\n  Test 4: negative_control.sky.json (must reject)")
    rc, out, _ = run_python(os.path.join(EXAMPLES_DIR, "negative_control.sky.json"))
    check("negative_control rejected", rc != 0)
    check("output says REJECTED", "REJECTED" in out)

    # Test 5: invalid format
    print("\n  Test 5: invalid bundle format")
    import tempfile
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump({"format": "not-sky", "obligations": []}, f)
        tmp = f.name
    rc, out, err = run_python(tmp)
    os.unlink(tmp)
    check("invalid format rejected", rc != 0)

    # Test 6: empty obligations
    print("\n  Test 6: empty obligations")
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump({"format": "sky-bundle", "obligations": []}, f)
        tmp = f.name
    rc, out, err = run_python(tmp)
    os.unlink(tmp)
    check("empty obligations rejected", rc != 0)

    # Summary
    print(f"\n{'=' * 60}")
    print(f"  RESULTS: {PASS}/{PASS + FAIL} tests passed")
    sys.exit(0 if FAIL == 0 else 1)


if __name__ == "__main__":
    main()
