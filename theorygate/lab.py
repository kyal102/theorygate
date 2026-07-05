"""TheoryGate Lab — a pinned 24-claim corpus with expected verdicts.

Two worked example corpora drawn from claims that circulate in public
discourse (paraphrased; no attribution — the gate judges claims, not people):

  Corpus A — a nonstandard arithmetic in which 1 x 1 = 2, plus associated
             geometry claims (tetrahedron packing, sqrt(2) skepticism) and
             element-table rescalings.
  Corpus B — a 14-dimensional geometric unification proposal: metric-bundle
             bookkeeping, Spin(7,7)-type spinors, and whether the Standard
             Model's three fermion generations fit inside the 128.

Expected verdicts are pinned, so this file doubles as a regression suite; the
lab emits a sealed sha256 certificate over the stable payload.

The corpus is deliberately even-handed: it VERIFIES what checks out (most of
Corpus B's dimension bookkeeping; even 1x1=2 under its own stated rule) and
REFUTES exactly what exact computation refutes. What can't be determinized
says so.

Run:  python -m theorygate --lab
"""
from __future__ import annotations

import hashlib
import json
import time
from datetime import datetime, timezone
from typing import Any, Dict, List

from .gate import determinize, PUBLIC_WORDING

SYSTEM_NAME = "TheoryGate"
LAB_VERSION = "1.1.0"


def _stable_json(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False, default=str)


# Each case: id, corpus, human claim as stated, gate claim dict, expected verdict.
CASES: List[Dict] = [
    # ---------------- Corpus A: nonstandard arithmetic ----------------
    {"id": "A-01", "corpus": "A",
     "stated": "1 x 1 = 2 (as ordinary arithmetic)",
     "claim": {"type": "arithmetic", "equation": "1*1=2", "semantics": "standard"},
     "expect": "REFUTED"},
    {"id": "A-02", "corpus": "A",
     "stated": "1 x 1 = 2 under the system's own rule (a times b = a added to itself b times)",
     "claim": {"type": "arithmetic", "equation": "1*1=2",
               "semantics": "repeated_addition"},
     "expect": "VERIFIED"},
    {"id": "A-03", "corpus": "A",
     "stated": "The system as a whole: 1x1=2 AND 2x2=4 both hold",
     "claim": {"type": "consistency", "equations": ["1*1=2", "2*2=4"]},
     "expect": "INCONSISTENT"},
    {"id": "A-04", "corpus": "A",
     "stated": "The rule applied consistently instead: 1x1=2, 2x2=6, 3x3=12",
     "claim": {"type": "consistency", "equations": ["1*1=2", "2*2=6", "3*3=12"]},
     "expect": "VERIFIED"},
    {"id": "A-05", "corpus": "A",
     "stated": "The square root of 2 is unresolvable / does not really exist",
     "claim": {"type": "geometry", "name": "sqrt2_does_not_exist"},
     "expect": "REFUTED"},
    {"id": "A-06", "corpus": "A",
     "stated": "Regular tetrahedra pack/tile space perfectly",
     "claim": {"type": "geometry", "name": "tetra_tiling"},
     "expect": "REFUTED"},
    {"id": "A-07", "corpus": "A",
     "stated": "There are no straight lines in the universe",
     "claim": {"type": "empirical",
               "statement": "there are no straight lines in the universe"},
     "expect": "NOT_DETERMINIZABLE"},
    {"id": "A-08", "corpus": "A",
     "stated": "Baseline the proposal must beat: H2O molar mass is 18.015",
     "claim": {"type": "element_mass", "formula": "H2O", "claimed_mass": 18.015},
     "expect": "VERIFIED"},
    {"id": "A-09", "corpus": "A",
     "stated": "A geometry-derived rescaling of hydrogen: H = 2.0 g/mol",
     "claim": {"type": "element_mass", "formula": "H", "claimed_mass": 2.0},
     "expect": "REFUTED"},

    # ---------------- Corpus B: 14-dimensional unification ----------------
    {"id": "B-01", "corpus": "B",
     "stated": "The total space over 4d spacetime is 14-dimensional (4 + metric fibre)",
     "claim": {"type": "dimension", "kind": "observerse", "args": [4], "claimed": 14},
     "expect": "VERIFIED"},
    {"id": "B-02", "corpus": "B",
     "stated": "The metric bundle fibre over a 4-manifold is 10-dimensional",
     "claim": {"type": "dimension", "kind": "metrics", "args": [4], "claimed": 10},
     "expect": "VERIFIED"},
    {"id": "B-03", "corpus": "B",
     "stated": "Dirac spinors of Spin(7,7) have 128 components",
     "claim": {"type": "dimension", "kind": "spinor", "args": [7, 7], "claimed": 128},
     "expect": "VERIFIED"},
    {"id": "B-04", "corpus": "B",
     "stated": "The 128 splits chirally as 64 + 64",
     "claim": {"type": "decomposition", "total": 128, "parts": [64, 64], "exact": True},
     "expect": "VERIFIED"},
    {"id": "B-05", "corpus": "B",
     "stated": "so(7,7) is 91-dimensional (adjoint = 2-forms on R^14)",
     "claim": {"type": "dimension", "kind": "group", "args": ["SO(7,7)"], "claimed": 91},
     "expect": "VERIFIED"},
    {"id": "B-06", "corpus": "B",
     "stated": "...and 2-forms on R^14 are also 91-dimensional (the coincidence the proposal leans on)",
     "claim": {"type": "dimension", "kind": "two_forms", "args": [14], "claimed": 91},
     "expect": "VERIFIED"},
    {"id": "B-07", "corpus": "B",
     "stated": "128 spinor slots ARE exactly 3 SM generations (3 x 16 Weyl fermions)",
     "claim": {"type": "decomposition", "total": 128, "parts": [16, 16, 16],
               "exact": True},
     "expect": "REFUTED"},
    {"id": "B-08", "corpus": "B",
     "stated": "3 generations at least FIT inside the 128 (necessary-condition check)",
     "claim": {"type": "decomposition", "total": 128, "parts": [16, 16, 16],
               "exact": False},
     "expect": "VERIFIED"},
    {"id": "B-09", "corpus": "B",
     "stated": "The proposal unifies gravity with the Standard Model",
     "claim": {"type": "empirical",
               "statement": "unifies gravity and the SM (no complete published "
                            "Lagrangian/quantization to check)"},
     "expect": "NOT_DETERMINIZABLE"},
    {"id": "B-10", "corpus": "B",
     "stated": "Sanity anchor: the SM gauge group piece SU(3) is 8-dimensional",
     "claim": {"type": "dimension", "kind": "group", "args": ["SU(3)"], "claimed": 8},
     "expect": "VERIFIED"},

    # ------- Branching rules: exact weights, not just counting -------
    {"id": "BR-01", "corpus": "B",
     "stated": "Anchor: the 16 of Spin(10) is exactly one SM generation "
               "(the textbook GUT fact, computed from weights)",
     "claim": {"type": "branching", "n": 5, "chirality": "+",
               "claimed": {"generations": 1, "mirrors": 0, "extra": 0}},
     "expect": "VERIFIED"},
    {"id": "BR-02", "corpus": "B",
     "stated": "The chiral 64 of Spin(7,7) = exactly 2 SM generations + 2 "
               "mirror generations, nothing left over",
     "claim": {"type": "branching", "n": 7, "chirality": "+",
               "claimed": {"generations": 2, "mirrors": 2, "extra": 0}},
     "expect": "VERIFIED"},
    {"id": "BR-03", "corpus": "B",
     "stated": "The chiral 64 contains 3 SM generations (the hope the 128 "
               "invites) — checked against the actual weights",
     "claim": {"type": "branching", "n": 7, "chirality": "+",
               "claimed": {"generations": 3}},
     "expect": "REFUTED"},
    {"id": "BR-04", "corpus": "B",
     "stated": "The chiral 64 contains exactly 2 left-handed quark doublets "
               "(3,2,Y=1/6) — one per generation slot",
     "claim": {"type": "branching", "n": 7, "chirality": "+",
               "contains": {"color": "3", "su2": 2, "Y": "1/6"},
               "claimed_count": 2},
     "expect": "VERIFIED"},
    {"id": "BR-05", "corpus": "B",
     "stated": "The full Dirac 128 = 4 generations + 4 mirrors (both "
               "chiralities together)",
     "claim": {"type": "branching", "n": 7, "chirality": "dirac",
               "claimed": {"generations": 4, "mirrors": 4, "extra": 0}},
     "expect": "VERIFIED"},
]


def run_lab(verbose: bool = True) -> Dict:
    t0 = time.perf_counter()
    rows, mismatches = [], []
    for case in CASES:
        r = determinize(case["claim"])
        ok = r.status == case["expect"]
        if not ok:
            mismatches.append((case["id"], case["expect"], r.status))
        rows.append({"id": case["id"], "corpus": case["corpus"],
                     "stated": case["stated"],
                     "verdict": r.status, "expected": case["expect"], "match": ok,
                     "reason": r.reason, "derivation": r.derivation,
                     "detail": r.detail})
    dt = time.perf_counter() - t0

    by_corpus: Dict[str, Dict[str, int]] = {}
    for row in rows:
        b = by_corpus.setdefault(row["corpus"], {})
        b[row["verdict"]] = b.get(row["verdict"], 0) + 1

    payload = {"system": SYSTEM_NAME, "lab_version": LAB_VERSION,
               "cases": rows, "summary": by_corpus,
               "all_expected": not mismatches,
               "public_wording": PUBLIC_WORDING}
    cert = {"sha256": hashlib.sha256(_stable_json(payload).encode()).hexdigest(),
            "generated_utc": datetime.now(timezone.utc).isoformat(),
            "elapsed_s": round(dt, 4), "n_cases": len(rows)}

    if verbose:
        print(f"TheoryGate Lab v{LAB_VERSION} — {len(rows)} claims determinized "
              f"in {dt*1000:.1f} ms\n")
        for row in rows:
            flag = "" if row["match"] else "  << EXPECTED " + row["expected"]
            print(f"  [{row['id']}] {row['verdict']:<19} {row['stated']}{flag}")
            print(f"          -> {row['reason']}")
        print("\nSummary by corpus:")
        for corpus, counts in by_corpus.items():
            parts = ", ".join(f"{k} {v}" for k, v in sorted(counts.items()))
            print(f"  Corpus {corpus}:  {parts}")
        print(f"\nRegression: {'ALL EXPECTED' if not mismatches else mismatches}")
        print(f"Certificate sha256: {cert['sha256']}")
    return {"payload": payload, "certificate": cert}


if __name__ == "__main__":
    out = run_lab()
    raise SystemExit(0 if out["payload"]["all_expected"] else 1)
