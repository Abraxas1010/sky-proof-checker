# How SKY Proof Checking Works

## The Three Rules

The entire proof checker is built on three reduction rules from combinatory logic:

| Rule | Pattern | Result | Meaning |
|------|---------|--------|---------|
| **S** (substitution) | `S f g x` | `f x (g x)` | Apply `f` and `g` to `x`, then apply the results |
| **K** (constant) | `K x y` | `x` | Discard `y`, return `x` |
| **Y** (fixed point) | `Y f` | `f (Y f)` | Self-application for recursion |

These three rules, applied repeatedly to a tree of combinators, can compute
anything a Turing machine can compute. They were discovered by Moses Schonfinkel
(1924) and Haskell Curry (1930).

## From Lean 4 to Combinators

A Lean 4 proof obligation is a question: "does expression `e` have type `T`?"

The Heyting compilation pipeline transforms this into a combinator tree:

1. **Scott encoding**: Lean's inductive types (Nat, Bool, List, Expr) are encoded
   as lambda terms using Scott's encoding. Each constructor becomes a lambda that
   selects the right branch from a case expression.

2. **Bracket abstraction**: Lambda terms are compiled to S/K/Y combinators using
   Turner's bracket abstraction algorithm. Every lambda abstraction `fun x => body`
   becomes a combinator expression using only S, K, and Y.

3. **Kernel algorithms**: The WHNF normalizer, definitional equality checker,
   type inference, and type checking algorithms from Lean 4's kernel are all
   compiled to combinator form using steps 1 and 2.

4. **Bundle emission**: The compiled kernel algorithms, the environment (definitions
   and types), and the proof obligations are packaged into a self-contained JSON bundle.

## Verification

The verifier (this repo) takes the bundle and:

1. Feeds each obligation's combinator tree into the reducer
2. Applies S/K/Y rules in leftmost-outermost order until a normal form is reached
3. Decodes the normal form as a Church-encoded boolean (`K` = true)
4. Reports VERIFIED if all obligations decode to their expected results

## Why This Is Sound

The correctness of this approach rests on three pillars:

1. **Scott encoding correctness** (77 theorems in HeytingLean): pattern matching
   on Scott-encoded terms dispatches to the correct branch at the combinator level.

2. **Bracket abstraction correctness** (15 theorems): the compiled combinator
   behaves like the original lambda term — `([x]e) v` is joinable with `e[v/x]`.

3. **Kernel correspondence** (47 theorems): the SKY-compiled kernel algorithms
   agree with the staged reference algorithms on all supported expressions.

Together, these guarantee: if the combinator reducer says "true," the Lean 4
kernel would also accept the proof.

## TCB Analysis

The Trusted Computing Base (TCB) is what you must trust for the result to be meaningful:

| Component | Size | Why You Trust It |
|-----------|------|-----------------|
| S/K/Y rules | 3 rules | Published mathematics since 1924; trivially auditable |
| Reducer | ~50 LOC | Small enough to verify by hand in any language |
| JSON parser | Std lib | Every language has a battle-tested JSON parser |
| **Total** | **~50 LOC + 3 rules** | |

Compare: Lean 4's kernel is ~50,000 lines of C++, plus LLVM, libc, and the OS.
