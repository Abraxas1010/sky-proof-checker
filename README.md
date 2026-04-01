<img src="assets/Apoth3osis.webp" alt="Apoth3osis — Formal Mathematics and Verified Software" width="140"/>

<sub><strong>Our tech stack is ontological:</strong><br>
<strong>Hardware — Physics</strong><br>
<strong>Software — Mathematics</strong><br><br>
<strong>Our engineering workflow is simple:</strong> discover, build, grow, learn & teach</sub>

---

[![License: Apoth3osis License Stack v1](https://img.shields.io/badge/License-Apoth3osis%20License%20Stack%20v1-blue.svg)](LICENSE.md)

# SKY Proof Checker

Standalone SKY bundle verifier implemented in Python, Rust, TypeScript, and Go.

## What This Repo Ships

- independent bundle replay across four implementations
- minimal trust boundary around SKY reduction
- local release and customer verification checks

## What This Repo Does Not Ship

- Lean source compilation
- attestation verification in this base repo
- on-chain verification in this base repo

For cryptographic attestation and registry workflows, use the separate assurance
lane: `verified-sky-assurance`.

## Quick Start

```bash
python3 python/sky_checker.py examples/trivial_true.sky.json
```

## Which Repo Does What?

- `verified-sky-checker`: service deployment and delivery packaging
- `sky-proof-checker`: independent customer replay
- `verified-sky-assurance`: separate STARK/ZK and on-chain assurance lane

## Customer Verification

See:

- `docs/customer_verification.md`
- `docs/use_cases.md`
- `docs/release_checks.md`
- `docs/applied_team_handoff.md`

## Test Commands

```bash
python3 tests/test_reducer.py
python3 tests/test_cli_parity.py
python3 tests/test_customer_examples.py
```

## License

[Apoth3osis License Stack v1](LICENSE.md)
