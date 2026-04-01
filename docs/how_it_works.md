# How SKY Proof Checking Works

## Core Reduction Model

Every implementation in this repository reduces combinator trees built from:

- `S`
- `K`
- `Y`
- `["app", f, a]`

using leftmost-outermost reduction.

## Verification Algorithm

For each obligation in a bundle:

1. Parse `compiled_check`
2. Reduce the term up to `fuel` steps
3. Decode the normal form as a boolean
4. Compare the decoded result with `expected_result`

The bundle is accepted only if:

- `format == "sky-bundle"`
- the bundle contains at least one obligation
- every obligation decodes to its expected result

## What This Repository Does Not Do

This repository does not:

- compile Lean source into SKY bundles
- verify STARK attestations
- prove correspondence with the upstream compiler on its own

Those concerns belong to the upstream toolchain and service layer.
