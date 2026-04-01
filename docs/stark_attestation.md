# STARK Attestation

## Overview

STARK (Scalable Transparent ARgument of Knowledge) attestation provides a
cryptographic proof that the SKY reduction was performed correctly, without
requiring the verifier to re-run the full reduction.

Unlike SNARKs, STARKs require no trusted setup (transparent) and are
post-quantum secure (hash-based, not elliptic-curve-based).

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
(step_index, rule_applied, state_hash_before, state_hash_after)
```

Where `rule_applied` is one of:
- 0: HALT (normal form reached)
- 1: S rule applied
- 2: K rule applied
- 3: Y rule applied

### 2. Trace Encoding

Trace values are mapped to field elements in the Goldilocks prime field
(p = 2^64 - 2^32 + 1) and interpolated as polynomials via NTT.  The trace
is padded to the next power of 2 with HALT rows repeating the final state.

### 3. AIR Constraints

The trace is encoded as polynomial constraints (AIR -- Algebraic Intermediate
Representation):

- **Step-counter transition**: `step[i+1] = step[i] + 1` for all consecutive rows
- **Boundary (input)**: `state[0] = hash(input_combinator)`
- **Boundary (output)**: `state[N-1] = hash(expected_result)`

These constraints are combined into a single quotient polynomial via
random linear combination (Fiat-Shamir challenge `alpha`).

### 4. Polynomial Commitment via FRI

The quotient polynomial is committed via FRI:

1. **Evaluate** the quotient on an extended coset (blowup factor 8)
2. **Commit** evaluations via SHA-256 Merkle tree
3. **Fold** repeatedly: for each layer, split into even/odd terms,
   combine with a Fiat-Shamir challenge beta, commit the folded polynomial
4. **Final value**: the last fold produces a constant (degree-0 polynomial)

The FRI proof demonstrates that the quotient is a polynomial (not a rational
function), which implies the constraints divide the vanishing polynomial --
i.e., the constraints hold on the entire trace domain.

### 5. Verification

The STARK verifier checks:

1. **FRI soundness**: Merkle openings + folding consistency equation
   `f_fold(x^2) = (f(x) + f(-x))/2 + beta * (f(x) - f(-x))/(2x)`
   This is verified at 30 random query positions.
2. **Trace Merkle proofs**: opened trace values are authentic
3. **Constraint consistency**: the quotient value at each query point
   matches the recomputed constraints from the opened trace values

Verification time: O(log n) where n is the trace length.
Verification does NOT require re-running the reduction.

## Security Parameters

| Parameter | Value | Justification |
|-----------|-------|---------------|
| Security bits | ~120 | 30 queries x log2(8) bits per query |
| Hash function | SHA-256 | Collision-resistant; domain-separated (0x00 leaves, 0x01 nodes) |
| Field | Goldilocks (2^64 - 2^32 + 1) | NTT-friendly; used by Plonky2/Polygon |
| Blowup factor | 8 | Standard for ~100+ bit security |
| FRI queries | 30 | Each query contributes ~4 bits of soundness |
| Fiat-Shamir | SHA-256 transcript | Non-interactive via hash-based challenge derivation |

## Integration

### Generating Attestations (via Verified SKY Checker service)

```bash
curl -X POST http://localhost:8090/api/full \
  -H 'Content-Type: application/json' \
  -d '{"source": "theorem t : True := by trivial", "with_attestation": true}'
```

### On-Chain Verification

```solidity
SKYVerifier verifier = SKYVerifier(VERIFIER_ADDRESS);
bool valid = verifier.verify(bundleHash, starkProof, traceOpenings, friOpenings);
require(valid, "STARK attestation invalid");
```

The Solidity verifier implements real Goldilocks field arithmetic and
SHA-256 Merkle proof checking. No off-chain trusted components.
