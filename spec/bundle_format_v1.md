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

## Combinator Representation

A combinator is one of:

- `"S"`
- `"K"`
- `"Y"`
- `["app", <combinator>, <combinator>]`

Example:

```json
["app", ["app", "K", "S"], "K"]
```

## Verification Rules

Current implementations in this repository must:

1. reject bundles whose `format` is not `sky-bundle`
2. reject bundles with zero obligations
3. reduce each `compiled_check` term using leftmost-outermost SKY reduction
4. decode the reduced term as a boolean
5. reject the bundle if any obligation does not match `expected_result`

## Boolean Decoding

- `K` decodes to `true`
- `["app", ["app", "K", "S"], "K"]` decodes to `false`
- `["app", "K", ["app", ["app", "S", "K"], "K"]]` also decodes to `false`

## Attestation Field

`attestation` is reserved metadata. Current CLIs in this repository ignore it.
It may be used by upstream services, but it is not part of the verifier
semantics implemented here.
