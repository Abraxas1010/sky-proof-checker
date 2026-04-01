# SKY Bundle Format v1

## Overview

A SKY bundle is a JSON document containing one or more verification obligations.
Each obligation carries a SKY combinator tree plus an expected boolean result.

## Required Top-Level Fields

```json
{
  "version": "1.0.0",
  "format": "sky-bundle",
  "source_hash": "<optional sha256 hex>",
  "obligations": [
    {
      "id": "trivial_true",
      "kind": "check",
      "compiled_check": "K",
      "fuel": 10000,
      "fuel_reduce": 50000,
      "expected_result": "true"
    }
  ],
  "result": {},
  "attestation": null
}
```

## Verification Rules

Current implementations in this repository must:

1. reject bundles whose `format` is not `sky-bundle`
2. reject bundles with zero obligations
3. reduce each `compiled_check` term using leftmost-outermost SKY reduction
4. decode the reduced term as a boolean
5. reject the bundle if any obligation does not match `expected_result`

## Attestation Field

`attestation` is reserved metadata for the separate assurance lane. Current CLIs
in this repository ignore it, and it is not part of the verifier semantics
implemented here.
