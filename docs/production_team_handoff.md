# Production Team Handoff

## Repo Role

`sky-proof-checker` is the independent replay verifier for the SKY stack.

Its job is simple:

- accept a delivered `bundle.sky.json`
- replay the SKY reduction locally
- return `VERIFIED` or `REJECTED` without needing Lean 4, the service repo, or the upstream compiler

This is the smallest trust surface in the product family.

## Product Fit

Use this repo when the product promise is:

- "the customer can verify this artifact independently"
- "the auditor does not need our deployment stack to check the result"
- "the regulator can replay the delivered bundle with a small open verifier"

Good product uses:

- customer-side replay for delivery packs from `verified-sky-checker`
- audit and compliance evidence
- cross-institutional proof exchange
- sidecar or offline replay in internal risk workflows

Do not use this repo as:

- the buyer-facing API
- the Lean-to-SKY compiler
- the STARK or on-chain assurance lane

## How Production Teams Work With It

Typical flow:

1. `verified-sky-checker` produces `bundle.sky.json` and `manifest.json`.
2. The delivery package includes the replay command from this repo.
3. The customer or auditor runs:

```bash
python3 python/sky_checker.py bundle.sky.json
```

Operational guidance:

- keep this repo independent from the producer runtime
- ship it as documentation, a container, or a separate verification tool
- do not merge it into the main delivery API if customer independence matters

## What Has Been Tested

Current local release evidence covers:

- reducer correctness on the example corpus
- cross-language CLI parity across Python, Rust, Go, and TypeScript
- customer replay documentation and example bundles
- positive and negative replay examples

Primary verification commands:

```bash
python3 tests/test_reducer.py
python3 tests/test_cli_parity.py
python3 tests/test_customer_examples.py
```

## Release Gate

Before tagging or shipping this verifier surface, run:

```bash
python3 -m unittest discover -s tests -p 'test_*.py'
```

If the product team needs a containerized replay surface, also run:

```bash
docker build -t sky-proof-checker .
docker run --rm -v "$PWD/examples:/work:ro" sky-proof-checker /work/trivial_true.sky.json
```

## Repo Dependencies

- Upstream producer/service: `verified-sky-checker`
- Optional stronger assurance lane: `verified-sky-assurance`

This repo intentionally does not depend on the assurance lane to preserve the minimal replay story.
