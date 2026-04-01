# Release Checks

## Goal

Every implementation in this repository must accept and reject the same bundle
shapes. A release is not valid if one language verifier drifts from the others.

## Required Commands

```bash
python3 tests/test_reducer.py
python3 tests/test_cli_parity.py
cd rust && cargo run -- ../examples/trivial_true.sky.json
cd go && go run checker.go ../examples/trivial_true.sky.json
cd typescript && npm ci && npx ts-node src/reducer.ts ../examples/trivial_true.sky.json
```

## Required Semantics

- reject non-`sky-bundle` formats
- reject empty bundles
- decode `K` as `true`
- decode both supported false encodings consistently
- reject undecodable results rather than treating them as success

## Release Rule

If one implementation diverges from Python on acceptance or rejection behavior,
stop the release and repair parity before publishing.
