<img src="assets/Apoth3osis.webp" alt="Apoth3osis — Formal Mathematics and Verified Software" width="140"/>

<sub><strong>Our tech stack is ontological:</strong><br>
<strong>Hardware — Physics</strong><br>
<strong>Software — Mathematics</strong><br><br>
<strong>Our engineering workflow is simple:</strong> discover, build, grow, learn & teach</sub>

---

[![License: Apoth3osis License Stack v1](https://img.shields.io/badge/License-Apoth3osis%20License%20Stack%20v1-blue.svg)](LICENSE.md)

# SKY Proof Checker

Standalone SKY bundle verifier implemented in Python, Rust, TypeScript, and Go.

## Implemented Scope

- Parse `sky-bundle` JSON files
- Reduce SKY combinator trees using the `S`, `K`, and `Y` rules
- Decode boolean verification results (`K = true`, `K (S K K) = false`)
- Reject malformed or empty bundles consistently across implementations

## Out of Scope in This Repository

- Lean source compilation
- STARK proof verification
- On-chain verification

The `attestation` field in the bundle schema is reserved for upstream systems.
Current CLIs ignore it and verify only the core reducer obligations.

## Quick Start

### Python

```bash
python3 python/sky_checker.py examples/trivial_true.sky.json
python3 python/sky_checker.py --verbose examples/s_identity.sky.json
```

### Rust

```bash
cd rust && cargo run -- ../examples/trivial_true.sky.json
```

### TypeScript

```bash
cd typescript
npm install
npx ts-node src/reducer.ts ../examples/trivial_true.sky.json
```

### Go

```bash
cd go && go run checker.go ../examples/trivial_true.sky.json
```

## Trust Model

When a checker says `VERIFIED`, you are trusting:

1. The three SKY reduction rules
2. The implementation you ran
3. Your JSON parser

You are not trusting:

- the Lean compiler
- the service that produced the bundle
- any attestation verifier in this repository, because none is implemented here

## Examples

| Bundle | Purpose |
|--------|---------|
| `trivial_true.sky.json` | `K` decodes to true |
| `k_reduces.sky.json` | K-rule reduction |
| `s_identity.sky.json` | `S K K x` behaves like identity |
| `negative_control.sky.json` | intentional reject case |

## Test Commands

```bash
python3 tests/test_reducer.py
python3 tests/test_cli_parity.py
```

`test_cli_parity.py` runs all locally available implementations and skips any
toolchain that is missing on the current machine.

## Release Operations

- Release checklist: `docs/release_checks.md`
- CI workflow: `.github/workflows/ci.yml`

## License

[Apoth3osis License Stack v1](LICENSE.md) — free for public-good and small
business use; enterprise license required for commercial certification.
