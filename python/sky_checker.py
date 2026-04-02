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

def parse_dependency_edges(root: dict[str, Any]) -> list[tuple[str, str]]:
    out: list[tuple[str, str]] = []
    for edge in list(root.get("dependency_edges") or []):
        shard_id = str(edge.get("shard_id") or "")
        dependency_id = str(edge.get("dependency_id") or "")
        if shard_id and dependency_id:
            out.append((shard_id, dependency_id))
    return out


def aggregate_receipts(root: dict[str, Any], receipts: list[dict[str, Any]]) -> dict[str, Any]:
    required = list(root.get("required_shard_ids") or [])
    required_set = set(required)
    receipt_by_shard = {str(receipt.get("shard_id")): receipt for receipt in receipts}
    missing_required = [shard_id for shard_id in required if shard_id not in receipt_by_shard]
    foreign_receipts = [
        str(receipt.get("shard_id"))
        for receipt in receipts
        if str(receipt.get("root_hash")) != str(root.get("root_hash")) or str(receipt.get("shard_id")) not in required_set
    ]
    dependency_violations: list[dict[str, str]] = []
    for shard_id, dependency_id in parse_dependency_edges(root):
        shard_receipt = receipt_by_shard.get(shard_id)
        dependency_receipt = receipt_by_shard.get(dependency_id)
        shard_ok = bool(shard_receipt) and str(shard_receipt.get("status")) == "verified"
        dependency_ok = bool(dependency_receipt) and str(dependency_receipt.get("status")) == "verified"
        if not (shard_ok and dependency_ok):
            dependency_violations.append({"shard_id": shard_id, "dependency_id": dependency_id})
    unsupported_required = [
        shard_id
        for shard_id in required
        if shard_id in receipt_by_shard and str(receipt_by_shard[shard_id].get("status")) != "verified"
    ]
    verified_required = [
        shard_id
        for shard_id in required
        if shard_id in receipt_by_shard and str(receipt_by_shard[shard_id].get("status")) == "verified"
    ]
    metrics = {
        "root_required_shards": len(required),
        "receipts_present": len(receipts),
        "missing_required_shards": len(missing_required),
        "foreign_receipts": len(foreign_receipts),
        "dependency_violations": len(dependency_violations),
        "unsupported_required_shards": len(unsupported_required),
        "completeness_ratio": (len(verified_required) / len(required)) if required else 1.0,
    }
    status = (
        "aggregate_complete"
        if not missing_required and not foreign_receipts and not dependency_violations and not unsupported_required
        else "aggregate_incomplete"
    )
    return {
        "root_hash": str(root.get("root_hash") or ""),
        "missing_required_shards": missing_required,
        "foreign_receipts": foreign_receipts,
        "dependency_violations": dependency_violations,
        "status": status,
        "metrics": metrics,
    }


CORE_AGGREGATE_METRIC_KEYS = [
    "root_required_shards",
    "receipts_present",
    "missing_required_shards",
    "foreign_receipts",
    "dependency_violations",
    "unsupported_required_shards",
    "completeness_ratio",
]


def _closure_metrics(metrics: dict[str, Any]) -> dict[str, Any]:
    return {key: metrics.get(key) for key in CORE_AGGREGATE_METRIC_KEYS}


def verify_layered_manifest(manifest: dict[str, Any], verbose: bool = False) -> bool:
    root = manifest.get("proof_root")
    receipts = manifest.get("receipts")
    aggregate_receipt = manifest.get("aggregate_receipt")
    if not isinstance(root, dict) or not isinstance(receipts, list) or not isinstance(aggregate_receipt, dict):
        print("ERROR: layered manifest missing proof_root / receipts / aggregate_receipt", file=sys.stderr)
        return False
    derived = aggregate_receipts(root, receipts)
    compare_fields = [
        "root_hash",
        "missing_required_shards",
        "foreign_receipts",
        "dependency_violations",
        "status",
    ]
    mismatches = [
        field
        for field in compare_fields
        if aggregate_receipt.get(field) != derived.get(field)
    ]
    if _closure_metrics(dict(aggregate_receipt.get("metrics") or {})) != _closure_metrics(dict(derived.get("metrics") or {})):
        mismatches.append("metrics")
    if verbose:
        print(
            f"  LAYERED  status={derived['status']} required={derived['metrics']['root_required_shards']} "
            f"receipts={derived['metrics']['receipts_present']}"
        )
    if mismatches:
        print(f"ERROR: layered aggregate mismatch in fields {mismatches}", file=sys.stderr)
        return False
    return derived["status"] == "aggregate_complete"

def verify_bundle(bundle: dict, verbose: bool = False) -> bool:
    if bundle.get("format") == "sky-layered-manifest":
        return verify_layered_manifest(bundle, verbose=verbose)
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
        if bundle.get("format") == "sky-layered-manifest":
            metrics = dict((bundle.get("aggregate_receipt") or {}).get("metrics") or {})
            required = int(metrics.get("root_required_shards") or 0)
            print(f"VERIFIED: layered aggregate complete over {required} required shards")
        else:
            n = len(bundle.get("obligations", []))
            print(f"VERIFIED: {n}/{n} obligations checked")
    else:
        print("REJECTED: one or more obligations failed")
    sys.exit(0 if ok else 1)

if __name__ == "__main__":
    main()
