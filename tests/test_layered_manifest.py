#!/usr/bin/env python3
from __future__ import annotations

from python.sky_checker import verify_bundle


def layered_manifest(*, receipt_status: str = "verified") -> dict:
    root_hash = "root-123"
    shard_id = "shard-abc"
    manifest = {
        "version": "1.0.0",
        "format": "sky-layered-manifest",
        "proof_root": {
            "root_hash": root_hash,
            "required_shard_ids": [shard_id],
            "dependency_edges": [],
        },
        "receipts": [
            {
                "root_hash": root_hash,
                "shard_id": shard_id,
                "status": receipt_status,
            }
        ],
        "aggregate_receipt": {
            "root_hash": root_hash,
            "missing_required_shards": [],
            "foreign_receipts": [],
            "dependency_violations": [],
            "status": "aggregate_complete" if receipt_status == "verified" else "aggregate_incomplete",
            "metrics": {
                "root_required_shards": 1,
                "receipts_present": 1,
                "missing_required_shards": 0,
                "foreign_receipts": 0,
                "dependency_violations": 0,
                "unsupported_required_shards": 0 if receipt_status == "verified" else 1,
                "completeness_ratio": 1.0 if receipt_status == "verified" else 0.0,
            },
        },
    }
    return manifest


def test_layered_manifest_accepts_matching_complete_aggregate():
    assert verify_bundle(layered_manifest(), verbose=True) is True


def test_layered_manifest_accepts_extra_operational_metrics():
    manifest = layered_manifest()
    manifest["aggregate_receipt"]["metrics"].update(
        {
            "aggregate_runtime_ms": 0.01,
            "mean_shards_per_worker": 1.0,
            "worker_count": 1,
        }
    )
    assert verify_bundle(manifest, verbose=True) is True


def test_layered_manifest_rejects_mismatched_claim():
    manifest = layered_manifest()
    manifest["aggregate_receipt"]["status"] = "aggregate_incomplete"
    assert verify_bundle(manifest, verbose=True) is False


def test_layered_manifest_rejects_incomplete_required_shard():
    assert verify_bundle(layered_manifest(receipt_status="unsupported"), verbose=True) is False
