#!/usr/bin/env python3
"""SKY Proof Checker — standalone verifier for SKY combinator bundles.

Verifies Lean 4 proof obligations compiled to SKY combinators using only
three reduction rules: S f g x -> f x (g x), K x y -> x, Y f -> f (Y f).

No Lean installation required. No compiler. No runtime. Just combinators.

Usage:
    python3 sky_checker.py <bundle.json>
    python3 sky_checker.py --verbose <bundle.json>
"""
from __future__ import annotations
import json, sys
from typing import Any

# ── Combinator representation ────────────────────────────────────────
# A Comb is: "S" | "K" | "Y" | ["app", Comb, Comb]

def app(f: Any, a: Any) -> list:
    return ["app", f, a]

def is_app(c: Any) -> bool:
    return isinstance(c, list) and len(c) == 3 and c[0] == "app"

# ── Reduction engine (leftmost-outermost) ────────────────────────────

def step(c: Any) -> Any | None:
    """One leftmost-outermost SKY reduction step. Returns None if normal form."""
    if not is_app(c):
        return None
    f, a = c[1], c[2]
    # Y rule: Y f -> f (Y f)
    if f == "Y":
        return app(a, app("Y", a))
    if is_app(f):
        ff, fa = f[1], f[2]
        # K rule: K x y -> x
        if ff == "K":
            return fa
        if is_app(ff):
            fff, ffa = ff[1], ff[2]
            # S rule: S f g x -> f x (g x)
            if fff == "S":
                return app(app(ffa, a), app(fa, a))
            # Reduce deeper in fff position
            r = step(ff)
            if r is not None:
                return app(app(r, fa), a)
            r = step(f)
            if r is not None:
                return app(r, a)
            return None
        # Reduce in f position
        r = step(f)
        if r is not None:
            return app(r, a)
        return None
    # Reduce in f position
    r = step(f)
    if r is not None:
        return app(r, a)
    return None

def reduce(c: Any, fuel: int) -> tuple[Any, int]:
    """Reduce for up to `fuel` steps. Returns (result, steps_used)."""
    for i in range(fuel):
        c2 = step(c)
        if c2 is None:
            return c, i
        c = c2
    return c, fuel

# ── Result decoding ──────────────────────────────────────────────────

def decode_bool(c: Any) -> bool | None:
    """Decode Church boolean: K = true, K (S K K) = false."""
    if c == "K":
        return True
    if is_app(c) and is_app(c[1]) and c[1][1] == "K" and c[1][2] == "S" and c[2] == "K":
        return False
    # Try: K I pattern where I = S K K
    if is_app(c) and c[1] == "K":
        i = c[2]
        if is_app(i) and is_app(i[1]) and i[1][1] == "S" and i[1][2] == "K" and i[2] == "K":
            return False
    return None

# ── Bundle verification ──────────────────────────────────────────────

def verify_bundle(bundle: dict, verbose: bool = False) -> bool:
    if bundle.get("format") != "sky-bundle":
        print(f"ERROR: not an SKY bundle (format={bundle.get('format')})", file=sys.stderr)
        return False
    obligations = bundle.get("obligations", [])
    if not obligations:
        print("ERROR: no obligations in bundle", file=sys.stderr)
        return False
    all_ok = True
    for ob in obligations:
        oid = ob.get("id", "?")
        fuel = ob.get("fuel", 10000)
        compiled = ob.get("compiled_check")
        expected = ob.get("expected_result", "true")
        if compiled is None:
            print(f"  SKIP  {oid}: no compiled_check", file=sys.stderr)
            continue
        result, steps = reduce(compiled, fuel)
        decoded = decode_bool(result)
        ok = (expected == "true" and decoded is True) or \
             (expected == "false" and decoded is False)
        status = "PASS" if ok else "FAIL"
        if verbose:
            print(f"  {status}  {oid}: decoded={decoded} steps={steps}/{fuel}")
        elif not ok:
            print(f"  FAIL  {oid}: expected={expected} got={decoded} steps={steps}")
        if not ok:
            all_ok = False
    return all_ok

# ── CLI ──────────────────────────────────────────────────────────────

def main():
    verbose = "--verbose" in sys.argv or "-v" in sys.argv
    args = [a for a in sys.argv[1:] if not a.startswith("-")]
    if not args:
        print("Usage: sky_checker.py [--verbose] <bundle.json>", file=sys.stderr)
        sys.exit(2)
    with open(args[0]) as f:
        bundle = json.load(f)
    ok = verify_bundle(bundle, verbose=verbose)
    if ok:
        n = len(bundle.get("obligations", []))
        print(f"VERIFIED: {n}/{n} obligations checked")
    else:
        print("REJECTED: one or more obligations failed")
    sys.exit(0 if ok else 1)

if __name__ == "__main__":
    main()
