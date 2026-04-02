# SKY Layered Manifest v1

## Overview

A layered manifest is the replay-oriented wrapper for decentralized composite
verification artifacts.

It does not replace the flat SKY bundle format. Instead, it carries:

1. a committed `proof_root`
2. the list of worker `receipts`
3. the claimed `aggregate_receipt`

The open checker re-derives aggregate closure from `proof_root + receipts` and
rejects the manifest if the claimed aggregate receipt disagrees.

## Required Top-Level Fields

```json
{
  "version": "1.0.0",
  "format": "sky-layered-manifest",
  "proof_root": {
    "root_hash": "<sha256>",
    "required_shard_ids": ["<shard-id>"],
    "dependency_edges": []
  },
  "receipts": [
    {
      "root_hash": "<sha256>",
      "shard_id": "<shard-id>",
      "status": "verified"
    }
  ],
  "aggregate_receipt": {
    "root_hash": "<sha256>",
    "status": "aggregate_complete",
    "missing_required_shards": [],
    "foreign_receipts": [],
    "dependency_violations": [],
    "metrics": {
      "root_required_shards": 1,
      "receipts_present": 1,
      "missing_required_shards": 0,
      "foreign_receipts": 0,
      "dependency_violations": 0,
      "unsupported_required_shards": 0,
      "completeness_ratio": 1.0
    }
  }
}
```

## Verification Rules

Current Python replay in this repository must:

1. reject manifests without `proof_root`, `receipts`, or `aggregate_receipt`
2. recompute aggregate closure from `proof_root` and `receipts`
3. reject the manifest if the recomputed closure differs from the claimed
   `aggregate_receipt`
4. reject the manifest if recomputed status is not `aggregate_complete`

## Trust Boundary

This manifest validates omission-resistant aggregate closure over the committed
shard set. It does not by itself prove recursive proof composition or on-chain
assurance semantics.
