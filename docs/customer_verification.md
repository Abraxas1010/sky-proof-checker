# Customer Verification

## Goal

A customer receives a `sky-bundle` and verifies it locally without installing
Lean 4.

## Replay Command

```bash
python3 python/sky_checker.py bundle.sky.json
```

Equivalent replay commands exist in Rust, Go, and TypeScript.

## Assurance Note

If a package includes `attestation`, that field belongs to the separate
assurance lane. The base checker intentionally ignores it.
