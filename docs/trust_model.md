# Trust Model

## What You Are Trusting

When you run `sky_checker.py <bundle.json>` and it says VERIFIED, you are trusting:

### 1. The Three Reduction Rules (Mathematical Axioms)

```
S f g x  -->  f x (g x)
K x y    -->  x
Y f      -->  f (Y f)
```

These are not assumptions we invented. They are the defining equations of
combinatory logic, published by Moses Schonfinkel in 1924 and formalized
by Haskell Curry in the 1930s. They are among the most studied and simplest
computational primitives in the history of mathematics.

If these rules are wrong, combinatory logic is wrong, and a century of
mathematics built on it collapses. This is not a realistic threat model.

### 2. The Reducer Implementation (~50 Lines)

The reducer applies the three rules to a tree data structure in
leftmost-outermost order. Each implementation (Python, Rust, TypeScript, Go)
is under 200 lines including JSON parsing and CLI.

You can audit the reducer yourself. The core logic — `step()` and `reduce()` —
is ~30 lines in any language. If you don't trust our implementation, write
your own. The spec is the three rules above.

### 3. Your JSON Parser

The bundle is JSON. You are trusting your language's JSON parser to correctly
decode the combinator tree. This is a standard library component with decades
of battle-testing in every major language.

## What You Are NOT Trusting

### The Lean 4 Compiler

The Lean 4 compiler (written in C++ and Lean itself) is not in the trust path.
Even if the Lean compiler has a bug that accepts an invalid proof, the SKY
bundle encodes the type-checking computation independently. The reducer either
confirms the computation or it doesn't.

### The Compilation Service

The Heyting service that generates SKY bundles could be buggy or malicious.
But the bundle is self-contained: it encodes the complete type-checking
computation. If the service generates a wrong bundle, the reducer will reject it.
A malicious service cannot make the reducer accept an invalid proof — it can
only generate a bundle that fails verification.

### LLVM, libc, the Operating System

The reducer uses no system calls beyond file I/O. It does not link against
LLVM, does not use libc math functions, and does not depend on OS-specific
behavior. The computation is pure tree transformation.

### The STARK Prover (When Attestation Is Used)

The STARK attestation is verified by the open-source STARK verifier, which
checks the proof without the prover. Even if the prover is buggy, the
verifier will reject invalid proofs. The prover cannot forge valid attestations
(assuming hash collision resistance and FRI soundness).

## Threat Analysis

| Threat | Mitigated By |
|--------|-------------|
| Lean 4 kernel bug accepts invalid proof | SKY reducer independently checks |
| Compilation service generates wrong bundle | Reducer rejects wrong bundles |
| Reducer implementation has a bug | 4 independent implementations; audit the ~50 LOC |
| Adversarial bundle crafted to exploit reducer | Reducer has no state, no I/O, no memory allocation beyond the tree; attack surface is minimal |
| STARK prover forges attestation | STARK verifier checks independently (hash + FRI soundness) |
| Fuel exhaustion on valid proof | Increase fuel; report inconclusive, not verified |

## Comparison

| Verification System | TCB Size | Trust Boundary |
|-------------------|----------|---------------|
| Lean 4 (direct) | ~50K lines C++ | Lean compiler, LLVM, libc, OS |
| Coq (direct) | ~30K lines OCaml | Coq kernel, OCaml compiler |
| Metamath (direct) | ~500 lines C | Metamath verifier, C compiler |
| **SKY Proof Checker** | **~50 lines** | **3 math rules + JSON parser** |
| SKY + STARK | ~200 lines | 3 math rules + hash + FRI |
