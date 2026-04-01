# Attestation Field Status

The bundle format reserves space for an `attestation` object so upstream
services can attach external proof material.

This repository does not currently verify that material.

## Current Behavior

- Python CLI: ignores `attestation`
- Rust CLI: ignores `attestation`
- TypeScript CLI: ignores `attestation`
- Go CLI: ignores `attestation`

## Guidance

If you need cryptographic attestation verification, treat it as an upstream
service concern or implement a dedicated verifier in a separate audited module.
Do not rely on this repository for that capability.
