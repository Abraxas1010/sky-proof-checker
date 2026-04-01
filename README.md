<img src="assets/Apoth3osis.webp" alt="Apoth3osis — Formal Mathematics and Verified Software" width="140"/>

<sub><strong>Our tech stack is ontological:</strong><br>
<strong>Hardware — Physics</strong><br>
<strong>Software — Mathematics</strong><br><br>
<strong>Our engineering workflow is simple:</strong> discover, build, grow, learn & teach</sub>

---

<sub>
<strong>Acknowledgment</strong><br>
We humbly thank the collective intelligence of humanity for providing the technology and culture we cherish. The SKY combinator calculus originates with Moses Schonfinkel (1924) and Haskell Curry (1930). Our formalization acts as a reciprocal validation — confirming the structural integrity of their original insights while securing the foundation upon which we build.
</sub>

---

[![License: Apoth3osis License Stack v1](https://img.shields.io/badge/License-Apoth3osis%20License%20Stack%20v1-blue.svg)](LICENSE.md)

# SKY Proof Checker

Standalone verifier for Lean 4 proof obligations compiled to SKY combinators.

## What Is This?

This tool checks mathematical proofs without trusting any compiler, runtime, or operating system. It uses only three reduction rules from 1920s combinatory logic:

```
S f g x  -->  f x (g x)     (substitution)
K x y    -->  x              (constant)
Y f      -->  f (Y f)        (fixed point)
```

A Lean 4 proof is compiled to a tree of S, K, and Y combinators (an "SKY bundle"). This tool reduces the tree and checks that it reaches the expected result. If it does, the proof is valid.

**No Lean 4 installation required. No compiler. No runtime. Just combinators.**

## Why Does This Matter?

| System | Trusted Computing Base |
|--------|----------------------|
| Lean 4 kernel | ~50,000 lines of C++ |
| **SKY Proof Checker** | **~50 lines of code** |

The SKY reducer is small enough to audit by hand, implement on an FPGA, or verify on a blockchain. Trusting it means trusting arithmetic.

## Quick Start

### Python

```bash
python3 python/sky_checker.py examples/trivial_true.sky.json
# VERIFIED: 1/1 obligations checked

python3 python/sky_checker.py --verbose examples/s_identity.sky.json
#   PASS  identity_combinator: decoded=True steps=2/100
# VERIFIED: 1/1 obligations checked
```

### Rust

```bash
cd rust && cargo run -- ../examples/trivial_true.sky.json
# VERIFIED: 1/1 obligations checked
```

### TypeScript

```bash
cd typescript && npx ts-node src/reducer.ts ../examples/trivial_true.sky.json
# VERIFIED: 1/1 obligations checked
```

### Go

```bash
cd go && go run checker.go ../examples/trivial_true.sky.json
# VERIFIED: 1/1 obligations checked
```

## Bundle Format

An SKY bundle is a JSON file containing:

- **Obligations**: combinator trees to reduce
- **Expected results**: what the reduced form should decode to
- **Optional STARK attestation**: cryptographic proof that reduction was performed

See [spec/bundle_format_v1.md](spec/bundle_format_v1.md) for the full specification.

## How It Works

1. A Lean 4 proof is compiled to SKY combinators via Scott encoding and bracket abstraction
2. The compiled combinator tree encodes the type-checking computation
3. The reducer applies S/K/Y rules until a normal form is reached
4. The normal form is decoded: `K` = true (proof checks), anything else = false
5. If all obligations decode to their expected results, the proof is verified

The compilation step (Lean 4 to SKY) requires the [Heyting](https://github.com/Abraxas1010/heyting) toolchain. The verification step (this repo) requires nothing but a JSON parser and the three reduction rules.

## Trust Model

When you run this checker, you are trusting:

1. **The three reduction rules** (S, K, Y) — published mathematics since 1924
2. **The ~50 lines of reducer code** — auditable by hand
3. **Your JSON parser** — standard library in every language

You are NOT trusting:
- The Lean 4 compiler or kernel
- Any C/C++/LLVM toolchain
- The compilation service that generated the bundle
- The operating system (beyond file I/O)

If the reducer says VERIFIED, the proof is valid — regardless of bugs in any upstream toolchain.

## STARK Attestation (Enterprise)

For use cases where independent re-verification is impractical (on-chain verification, audit trails, delegation trust), bundles can include a STARK attestation — a cryptographic proof that the SKY reduction was performed correctly.

The STARK verifier checks the attestation without re-running the full reduction. This is:
- **Faster** than re-running the reducer for large proofs
- **Verifiable on-chain** via a Solidity contract
- **Non-repudiable** — proves the computation happened

See [docs/stark_attestation.md](docs/stark_attestation.md) for details.

## Examples

| Bundle | What It Proves | Steps |
|--------|---------------|-------|
| `trivial_true.sky.json` | `K` is Church-encoded true | 0 |
| `k_reduces.sky.json` | K rule: `K K I` reduces to `K` | 1 |
| `s_identity.sky.json` | Identity: `S K K x` reduces to `x` | 2 |
| `negative_control.sky.json` | Intentionally fails (wrong expected result) | 1 |

## Generating Bundles

SKY bundles are generated by the Heyting compilation service. Contact [rgoodman@apoth3osis.io](mailto:rgoodman@apoth3osis.io) for API access, or visit the [AgentHALO dashboard](https://github.com/Abraxas1010/agenthalo) for self-service.

## License

[Apoth3osis License Stack v1](LICENSE.md) — free for public-good and small business use; enterprise license required for commercial certification.
