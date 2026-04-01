# Trust Model

## Trusted Components

When you run one of the checkers in this repository, you are trusting:

1. the SKY reduction rules
2. the specific implementation you executed
3. the JSON parser used by that implementation

## What You Do Not Need To Trust

- the Lean compiler
- the service that generated the bundle
- any upstream compilation backend

If the producer hands you a bad bundle, the open checker should reject it.

## Assurance Lane

The bundle schema can carry an `attestation` field, but this repository does not
verify that material. Cryptographic attestation and registry workflows live in
the separate assurance lane: `verified-sky-assurance`.
