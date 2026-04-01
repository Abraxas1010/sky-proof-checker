# STARK Attestation

## Overview

STARK (Scalable Transparent ARgument of Knowledge) attestation provides a
cryptographic proof that the SKY reduction was performed correctly, without
requiring the verifier to re-run the full reduction.

## When to Use STARK Attestation

| Use Case | Why STARK? |
|----------|-----------|
| On-chain verification | Smart contracts can't run the full reducer; they CAN verify a STARK proof |
| Audit trails | Provable record that verification happened at a specific time |
| Delegation trust | Customer A verifies for Customer B; B wants proof, not just A's word |
| Large proofs | STARK verification is O(log n) in proof size; re-running is O(n) |

## How It Works

### 1. Trace Recording

During SKY reduction, each step is recorded as a trace row:

```
(step_index, fuel_remaining, term_commitment, rule_applied)
```

Where `rule_applied` is one of:
- 0: HALT (normal form or fuel exhausted)
- 1: S rule applied
- 2: K rule applied
- 3: Y rule applied

### 2. Arithmetization

The trace is encoded as polynomial constraints (AIR — Algebraic Intermediate
Representation):

- **Transition constraint**: the term commitment after applying the rule matches
  the next row's commitment
- **Boundary constraint**: first row commits to the input bundle; last row commits
  to the output result
- **Rule validity**: each `rule_applied` value is in {0, 1, 2, 3}

### 3. FRI Commitment

The trace polynomials are committed via FRI (Fast Reed-Solomon IOP of Proximity):

- Polynomial evaluation over a large domain
- Merkle tree commitment of evaluations
- Interactive oracle proof folded to non-interactive via Fiat-Shamir

### 4. Verification

The STARK verifier (open-source, in this repo) checks:

1. FRI commitments are valid (low-degree test)
2. Boundary constraints hold (input = bundle, output = result)
3. Transition constraints hold (each step is a valid S/K/Y rule)

Verification time: O(log n) where n is the trace length.
Verification does NOT require re-running the reduction.

## Security Parameters

| Parameter | Value | Meaning |
|-----------|-------|---------|
| Security bits | 128 | Probability of forging a valid proof: < 2^-128 |
| Hash function | SHA-256 or Poseidon | Collision-resistant commitment |
| Field | BN254 scalar field | For EVM compatibility |
| Blowup factor | 8 | FRI domain expansion |

## Integration

### Generating Attestations

```bash
# Via the Heyting service
curl -X POST https://api.apoth3osis.io/sky/attest \
  -H 'Authorization: Bearer <token>' \
  -d @bundle.sky.json
```

### Verifying Attestations

```bash
# Offline, with the open-source verifier
python3 python/sky_checker.py --verify-stark attested_bundle.sky.json
```

### On-Chain Verification

```solidity
// Solidity contract verifies STARK proof
SKYVerifier verifier = SKYVerifier(VERIFIER_ADDRESS);
bool valid = verifier.verify(proof, publicInputs);
require(valid, "STARK attestation invalid");
```
