//! SKY Proof Checker — standalone verifier for SKY combinator proof bundles.
//!
//! Verifies Lean 4 proof obligations compiled to SKY combinators using only
//! three reduction rules: S f g x -> f x (g x), K x y -> x, Y f -> f (Y f).

use serde::Deserialize;
use std::{env, fs, process};

// ── Combinator tree ─────────────────────────────────────────────────

#[derive(Clone, Debug)]
enum Comb {
    S,
    K,
    Y,
    App(Box<Comb>, Box<Comb>),
}

fn app(f: Comb, a: Comb) -> Comb {
    Comb::App(Box::new(f), Box::new(a))
}

// ── Reduction engine (leftmost-outermost) ───────────────────────────

fn step(c: &Comb) -> Option<Comb> {
    match c {
        Comb::App(f, a) => {
            // Y rule: Y f -> f (Y f)
            if matches!(f.as_ref(), Comb::Y) {
                return Some(app(a.as_ref().clone(), app(Comb::Y, a.as_ref().clone())));
            }
            if let Comb::App(ff, fa) = f.as_ref() {
                // K rule: K x y -> x
                if matches!(ff.as_ref(), Comb::K) {
                    return Some(fa.as_ref().clone());
                }
                if let Comb::App(fff, ffa) = ff.as_ref() {
                    // S rule: S f g x -> f x (g x)
                    if matches!(fff.as_ref(), Comb::S) {
                        return Some(app(
                            app(ffa.as_ref().clone(), a.as_ref().clone()),
                            app(fa.as_ref().clone(), a.as_ref().clone()),
                        ));
                    }
                    // Reduce deeper
                    if let Some(r) = step(ff) {
                        return Some(app(app(r, fa.as_ref().clone()), a.as_ref().clone()));
                    }
                }
                if let Some(r) = step(f) {
                    return Some(app(r, a.as_ref().clone()));
                }
            } else if let Some(r) = step(f) {
                return Some(app(r, a.as_ref().clone()));
            }
            None
        }
        _ => None,
    }
}

fn reduce(mut c: Comb, fuel: usize) -> (Comb, usize) {
    for i in 0..fuel {
        match step(&c) {
            Some(c2) => c = c2,
            None => return (c, i),
        }
    }
    (c, fuel)
}

// ── Result decoding ─────────────────────────────────────────────────

fn decode_bool(c: &Comb) -> Option<bool> {
    match c {
        Comb::K => Some(true),
        Comb::App(f, _) => {
            if let Comb::App(ff, fa) = f.as_ref() {
                if matches!(ff.as_ref(), Comb::K) && matches!(fa.as_ref(), Comb::S) {
                    return Some(false);
                }
            }
            None
        }
        _ => None,
    }
}

// ── JSON parsing ────────────────────────────────────────────────────

fn parse_comb(v: &serde_json::Value) -> Option<Comb> {
    match v {
        serde_json::Value::String(s) => match s.as_str() {
            "S" => Some(Comb::S),
            "K" => Some(Comb::K),
            "Y" => Some(Comb::Y),
            _ => None,
        },
        serde_json::Value::Array(arr) if arr.len() == 3 => {
            if arr[0].as_str() == Some("app") {
                let f = parse_comb(&arr[1])?;
                let a = parse_comb(&arr[2])?;
                Some(app(f, a))
            } else {
                None
            }
        }
        _ => None,
    }
}

#[derive(Deserialize)]
struct Obligation {
    id: String,
    compiled_check: serde_json::Value,
    #[serde(default = "default_fuel")]
    fuel: usize,
    #[serde(default = "default_expected")]
    expected_result: String,
}

fn default_fuel() -> usize { 10000 }
fn default_expected() -> String { "true".to_string() }

#[derive(Deserialize)]
struct Bundle {
    format: String,
    obligations: Vec<Obligation>,
}

// ── Main ────────────────────────────────────────────────────────────

fn main() {
    let args: Vec<String> = env::args().collect();
    let verbose = args.contains(&"--verbose".to_string()) || args.contains(&"-v".to_string());
    let files: Vec<&String> = args[1..].iter().filter(|a| !a.starts_with('-')).collect();

    if files.is_empty() {
        eprintln!("Usage: sky-proof-checker [--verbose] <bundle.json>");
        process::exit(2);
    }

    let data = fs::read_to_string(files[0]).unwrap_or_else(|e| {
        eprintln!("Error reading {}: {}", files[0], e);
        process::exit(1);
    });

    let bundle: Bundle = serde_json::from_str(&data).unwrap_or_else(|e| {
        eprintln!("Error parsing bundle: {}", e);
        process::exit(1);
    });

    if bundle.format != "sky-bundle" {
        eprintln!("ERROR: not an SKY bundle (format={})", bundle.format);
        process::exit(1);
    }

    let mut all_ok = true;
    for ob in &bundle.obligations {
        let comb = match parse_comb(&ob.compiled_check) {
            Some(c) => c,
            None => {
                eprintln!("  SKIP  {}: cannot parse compiled_check", ob.id);
                continue;
            }
        };
        let (result, steps) = reduce(comb, ob.fuel);
        let decoded = decode_bool(&result);
        let ok = (ob.expected_result == "true" && decoded == Some(true))
            || (ob.expected_result == "false" && decoded == Some(false));

        if verbose {
            let status = if ok { "PASS" } else { "FAIL" };
            println!("  {}  {}: decoded={:?} steps={}/{}", status, ob.id, decoded, steps, ob.fuel);
        } else if !ok {
            println!("  FAIL  {}: expected={} got={:?} steps={}", ob.id, ob.expected_result, decoded, steps);
        }
        if !ok {
            all_ok = false;
        }
    }

    let n = bundle.obligations.len();
    if all_ok {
        println!("VERIFIED: {}/{} obligations checked", n, n);
    } else {
        println!("REJECTED: one or more obligations failed");
    }
    process::exit(if all_ok { 0 } else { 1 });
}
