# Trust Model

## Trusted Components

When you run one of the checkers in this repository, you are trusting:

1. The SKY reduction rules
2. The implementation you executed
3. The JSON parser used by that implementation

## Untrusted Upstream Components

The checker intentionally does not trust:

- the Lean compiler
- the bundle producer
- any external compilation service

If an upstream system produces a bad bundle, the reducer should reject it.

## Attestation Status

The bundle schema allows an `attestation` field, but this repository does not
verify those attestations. Treat attestation-bearing bundles exactly like any
other bundle here: only the reducer obligations are checked.
