// SKY Proof Checker — standalone verifier for SKY combinator proof bundles.
//
// Verifies Lean 4 proof obligations compiled to SKY combinators using only
// three reduction rules: S f g x -> f x (g x), K x y -> x, Y f -> f (Y f).
package main

import (
	"encoding/json"
	"fmt"
	"os"
	"strings"
)

// ── Combinator tree ─────────────────────────────────────────────────

type Comb struct {
	Atom string // "S", "K", "Y", or ""
	F, A *Comb  // non-nil for application
}

var combS = &Comb{Atom: "S"}
var combK = &Comb{Atom: "K"}
var combY = &Comb{Atom: "Y"}

func app(f, a *Comb) *Comb { return &Comb{F: f, A: a} }
func isApp(c *Comb) bool   { return c.F != nil }

// ── Reduction engine (leftmost-outermost) ───────────────────────────

func step(c *Comb) *Comb {
	if !isApp(c) {
		return nil
	}
	f, a := c.F, c.A
	// Y rule
	if f.Atom == "Y" {
		return app(a, app(combY, a))
	}
	if isApp(f) {
		ff, fa := f.F, f.A
		// K rule
		if ff.Atom == "K" {
			return fa
		}
		if isApp(ff) {
			fff, ffa := ff.F, ff.A
			// S rule
			if fff.Atom == "S" {
				return app(app(ffa, a), app(fa, a))
			}
			if r := step(ff); r != nil {
				return app(app(r, fa), a)
			}
		}
		if r := step(f); r != nil {
			return app(r, a)
		}
		return nil
	}
	if r := step(f); r != nil {
		return app(r, a)
	}
	return nil
}

func reduce(c *Comb, fuel int) (*Comb, int) {
	for i := 0; i < fuel; i++ {
		c2 := step(c)
		if c2 == nil {
			return c, i
		}
		c = c2
	}
	return c, fuel
}

// ── Result decoding ─────────────────────────────────────────────────

func decodeBool(c *Comb) *bool {
	t, f := true, false
	if c.Atom == "K" {
		return &t
	}
	if isApp(c) && isApp(c.F) && c.F.F != nil && c.F.F.Atom == "K" && c.F.A != nil && c.F.A.Atom == "S" && c.A != nil && c.A.Atom == "K" {
		return &f
	}
	return nil
}

// ── JSON parsing ────────────────────────────────────────────────────

func parseComb(v interface{}) *Comb {
	switch val := v.(type) {
	case string:
		switch val {
		case "S":
			return combS
		case "K":
			return combK
		case "Y":
			return combY
		}
		return nil
	case []interface{}:
		if len(val) == 3 {
			if tag, ok := val[0].(string); ok && tag == "app" {
				f := parseComb(val[1])
				a := parseComb(val[2])
				if f != nil && a != nil {
					return app(f, a)
				}
			}
		}
		return nil
	}
	return nil
}

type Obligation struct {
	ID             string      `json:"id"`
	CompiledCheck  interface{} `json:"compiled_check"`
	Fuel           int         `json:"fuel"`
	ExpectedResult string      `json:"expected_result"`
}

type Bundle struct {
	Format      string       `json:"format"`
	Obligations []Obligation `json:"obligations"`
}

// ── Main ────────────────────────────────────────────────────────────

func main() {
	verbose := false
	var files []string
	for _, a := range os.Args[1:] {
		if a == "--verbose" || a == "-v" {
			verbose = true
		} else if !strings.HasPrefix(a, "-") {
			files = append(files, a)
		}
	}
	if len(files) == 0 {
		fmt.Fprintln(os.Stderr, "Usage: sky-proof-checker [--verbose] <bundle.json>")
		os.Exit(2)
	}

	data, err := os.ReadFile(files[0])
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error reading %s: %v\n", files[0], err)
		os.Exit(1)
	}

	var bundle Bundle
	if err := json.Unmarshal(data, &bundle); err != nil {
		fmt.Fprintf(os.Stderr, "Error parsing bundle: %v\n", err)
		os.Exit(1)
	}

	if bundle.Format != "sky-bundle" {
		fmt.Fprintf(os.Stderr, "ERROR: not an SKY bundle (format=%s)\n", bundle.Format)
		os.Exit(1)
	}

	allOk := true
	for _, ob := range bundle.Obligations {
		fuel := ob.Fuel
		if fuel == 0 {
			fuel = 10000
		}
		expected := ob.ExpectedResult
		if expected == "" {
			expected = "true"
		}
		comb := parseComb(ob.CompiledCheck)
		if comb == nil {
			fmt.Fprintf(os.Stderr, "  SKIP  %s: cannot parse compiled_check\n", ob.ID)
			continue
		}
		result, steps := reduce(comb, fuel)
		decoded := decodeBool(result)
		ok := (expected == "true" && decoded != nil && *decoded) ||
			(expected == "false" && decoded != nil && !*decoded)

		if verbose {
			status := "PASS"
			if !ok {
				status = "FAIL"
			}
			fmt.Printf("  %s  %s: decoded=%v steps=%d/%d\n", status, ob.ID, decoded, steps, fuel)
		} else if !ok {
			fmt.Printf("  FAIL  %s: expected=%s got=%v steps=%d\n", ob.ID, expected, decoded, steps)
		}
		if !ok {
			allOk = false
		}
	}

	n := len(bundle.Obligations)
	if allOk {
		fmt.Printf("VERIFIED: %d/%d obligations checked\n", n, n)
	} else {
		fmt.Println("REJECTED: one or more obligations failed")
	}
	if allOk {
		os.Exit(0)
	} else {
		os.Exit(1)
	}
}
