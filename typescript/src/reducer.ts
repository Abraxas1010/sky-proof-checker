/**
 * SKY Proof Checker — standalone verifier for SKY combinator proof bundles.
 *
 * Verifies Lean 4 proof obligations compiled to SKY combinators using only
 * three reduction rules: S f g x -> f x (g x), K x y -> x, Y f -> f (Y f).
 */

// ── Combinator tree ─────────────────────────────────────────────────

type Comb = "S" | "K" | "Y" | ["app", Comb, Comb];

function isApp(c: Comb): c is ["app", Comb, Comb] {
  return Array.isArray(c) && c.length === 3 && c[0] === "app";
}

function app(f: Comb, a: Comb): Comb {
  return ["app", f, a];
}

// ── Reduction engine (leftmost-outermost) ───────────────────────────

function step(c: Comb): Comb | null {
  if (!isApp(c)) return null;
  const [, f, a] = c;

  // Y rule: Y f -> f (Y f)
  if (f === "Y") return app(a, app("Y", a));

  if (isApp(f)) {
    const [, ff, fa] = f;
    // K rule: K x y -> x
    if (ff === "K") return fa;

    if (isApp(ff)) {
      const [, fff, ffa] = ff;
      // S rule: S f g x -> f x (g x)
      if (fff === "S") return app(app(ffa, a), app(fa, a));
      const r = step(ff);
      if (r !== null) return app(app(r, fa), a);
    }
    const r = step(f);
    if (r !== null) return app(r, a);
    return null;
  }

  const r = step(f);
  return r !== null ? app(r, a) : null;
}

function reduce(c: Comb, fuel: number): { result: Comb; steps: number } {
  for (let i = 0; i < fuel; i++) {
    const c2 = step(c);
    if (c2 === null) return { result: c, steps: i };
    c = c2;
  }
  return { result: c, steps: fuel };
}

// ── Result decoding ─────────────────────────────────────────────────

function decodeBool(c: Comb): boolean | null {
  if (c === "K") return true;
  if (isApp(c) && isApp(c[1]) && c[1][1] === "K" && c[1][2] === "S" && c[2] === "K")
    return false;
  return null;
}

// ── Bundle verification ─────────────────────────────────────────────

interface Obligation {
  id: string;
  compiled_check: Comb;
  fuel?: number;
  expected_result?: string;
}

interface Bundle {
  format: string;
  obligations: Obligation[];
}

export function verifyBundle(bundle: Bundle, verbose = false): boolean {
  if (bundle.format !== "sky-bundle") {
    console.error(`ERROR: not an SKY bundle (format=${bundle.format})`);
    return false;
  }

  let allOk = true;
  for (const ob of bundle.obligations) {
    const fuel = ob.fuel ?? 10000;
    const expected = ob.expected_result ?? "true";
    const { result, steps } = reduce(ob.compiled_check, fuel);
    const decoded = decodeBool(result);
    const ok =
      (expected === "true" && decoded === true) ||
      (expected === "false" && decoded === false);

    if (verbose) {
      console.log(`  ${ok ? "PASS" : "FAIL"}  ${ob.id}: decoded=${decoded} steps=${steps}/${fuel}`);
    } else if (!ok) {
      console.log(`  FAIL  ${ob.id}: expected=${expected} got=${decoded} steps=${steps}`);
    }
    if (!ok) allOk = false;
  }
  return allOk;
}

// ── CLI ─────────────────────────────────────────────────────────────

import { readFileSync } from "fs";

const args = process.argv.slice(2);
const verbose = args.includes("--verbose") || args.includes("-v");
const files = args.filter((a) => !a.startsWith("-"));

if (files.length === 0) {
  console.error("Usage: npx ts-node reducer.ts [--verbose] <bundle.json>");
  process.exit(2);
}

const bundle: Bundle = JSON.parse(readFileSync(files[0], "utf-8"));
const ok = verifyBundle(bundle, verbose);
const n = bundle.obligations.length;
console.log(ok ? `VERIFIED: ${n}/${n} obligations checked` : "REJECTED: one or more obligations failed");
process.exit(ok ? 0 : 1);
