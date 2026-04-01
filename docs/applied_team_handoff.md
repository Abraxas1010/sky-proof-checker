# Applied Team Handoff

## Utility

`sky-proof-checker` is the independent replay surface. Its job is not to compile proofs or run the customer-facing API. Its job is to let another party verify the delivered SKY bundle with a tiny trust boundary.

## How the Applied Team Uses It

- include the replay command in customer documentation
- use it in audit rehearsals before delivery
- keep it out of the core production API path so customers can run it independently

## Google Cloud Position

This repo is usually not the primary Google Cloud deployment target.

Instead, the applied team should:

1. deploy `verified-sky-checker` on Google Cloud
2. deliver bundles and manifests generated there
3. point the customer or regulator to `sky-proof-checker` for replay

If an internal compliance workflow wants hosted replay, run this repo as a separate job or sidecar, not as a replacement for the buyer-facing service.
