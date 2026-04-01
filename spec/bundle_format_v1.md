# SKY Bundle Format v1

## Overview

An SKY bundle is a self-contained proof verification package. It encodes one or
more Lean 4 proof obligations as SKY combinator trees, along with verification
results and optional STARK attestations.

The bundle can be checked independently using only the three SKY reduction rules:

```
S f g x  -->  f x (g x)
K x y    -->  x
Y f      -->  f (Y f)
```

No Lean 4 installation, no compiler, no runtime — just these three rules applied
to a tree of combinators.

## Combinator Representation

A combinator is one of:
- `"S"` — the S combinator
- `"K"` — the K combinator
- `"Y"` — the Y (fixed-point) combinator
- `["app", <combinator>, <combinator>]` — application

Example: `K x y` is `["app", ["app", "K", x], y]`

## Bundle Schema (JSON)

```json
{
  "version": "1.0.0",
  "format": "sky-bundle",
  "source_hash": "<sha256 hex of original Lean source>",
  "obligations": [
    {
      "id": "<obligation name>",
      "kind": "check",
      "compiled_check": "<combinator tree>",
      "fuel": 10000,
      "fuel_reduce": 50000,
      "expected_result": "true"
    }
  ],
  "result": {
    "all_checked": true,
    "obligations": [
      {
        "id": "<obligation name>",
        "checked": true,
        "steps_used": 3847
      }
    ]
  },
  "attestation": null
}
```

### Fields

- `version`: Bundle format version (semver)
- `format`: Always `"sky-bundle"`
- `source_hash`: SHA-256 of the original Lean source (hex string)
- `obligations`: Array of proof obligations
  - `id`: Human-readable name
  - `kind`: One of `"check"`, `"whnf"`, `"defeq"`, `"infer"`
  - `compiled_check`: The combinator tree to reduce
  - `fuel`: Maximum reduction steps
  - `fuel_reduce`: Maximum sub-reduction steps (for nested reductions)
  - `expected_result`: What the reduced form should decode to (`"true"` for check obligations)
- `result`: Verification results
  - `all_checked`: True iff all obligations verified
  - `obligations`: Per-obligation results
- `attestation`: Optional STARK attestation (null if not requested)

### Attestation Schema

When present:
```json
{
  "type": "stark",
  "proof": "<base64-encoded STARK proof>",
  "public_inputs": "<hex hash of obligations + results>",
  "trace_length": 3847,
  "security_bits": 128
}
```

## Verification Algorithm

To verify a bundle:

1. For each obligation in `obligations`:
   a. Parse `compiled_check` as a combinator tree
   b. Reduce using leftmost-outermost S/K/Y rules, up to `fuel` steps
   c. Decode the result (Church-encoded boolean: `K` = true, `K I` = false)
   d. Compare to `expected_result`
2. If all obligations match: bundle is VERIFIED
3. If any obligation fails: bundle is REJECTED
4. If attestation is present: verify the STARK proof against the public inputs

The verifier is ~50 lines of code in any language.
