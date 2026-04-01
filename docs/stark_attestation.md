# Attestation Field Status

The bundle format reserves space for an `attestation` object so an upstream
assurance lane can attach cryptographic proof material.

This base verifier does not verify that material.

## Current Behavior

- Python CLI: ignores `attestation`
- Rust CLI: ignores `attestation`
- TypeScript CLI: ignores `attestation`
- Go CLI: ignores `attestation`

## Assurance Lane

Use `verified-sky-assurance` if you need cryptographic attestation or on-chain
registry workflows. Keep this base repo minimal.
