# TheoryGate

![python](https://img.shields.io/badge/python-3.9%2B-blue) ![license](https://img.shields.io/badge/license-MIT-green) ![deps](https://img.shields.io/badge/dependencies-stdlib--only-blue)

**A deterministic determinizer for math/physics theory claims.**

Give it a claim; it reduces the claim to its checkable core and returns an exact verdict — `VERIFIED`, `REFUTED`, `INCONSISTENT`, or `NOT_DETERMINIZABLE` — computed with exact rational arithmetic. Never a model, never a vibe.

```bash
python -m theorygate --demo
```
```text
1) A famous nonstandard arithmetic, judged on its own terms:
   1*1=2                        -> REFUTED: exact evaluation gives 1, claim says 2 (standard semantics)
   1*1=2                        -> VERIFIED: exact equality holds under repeated_addition semantics
   1*1=2; 2*2=4                 -> INCONSISTENT: no implemented semantics satisfies all claims — the set is internally inconsistent
```

That third line is the interesting one: the gate doesn't just say "1×1=2 is wrong" — it grants the claim its own stated rule ("a times b means a added to itself b times"), verifies that the rule really does give 1×1=2, and then proves that **no rule at all** can satisfy the system's claims *simultaneously* (the rule that yields 1×1=2 forces 2×2=6, not 4). Judged on its own terms, the system contradicts itself.

## The flagship computation: does the Standard Model fit in a 128?

Several unification proposals hang on a 128-dimensional spinor of a Spin(14)-type group and hope the Standard Model's three fermion generations live inside it. TheoryGate doesn't count — it **computes the actual branching rules** on the spinor weight system, in exact `Fraction` arithmetic, down the standard chain:

```
so(14) ⊃ so(10) ⊕ so(4) ⊃ [su(4) ⊕ su(2)_L ⊕ su(2)_R] ⊃ su(3) ⊕ su(2) ⊕ u(1)_Y
```

```bash
python -m theorygate '{"type":"branching","n":7,"chirality":"+","claimed":{"generations":2,"mirrors":2,"extra":0}}'
```
```text
so(14) spinor (+, 64 states) = 2 generation(s) + 2 mirror(s) + nothing else
  -> VERIFIED
```

The certified result: **the chiral 64 = exactly 2 Standard Model generations + 2 mirror (CPT-conjugate) generations, nothing left over** — each spectator slot is a whole generation or a whole mirror, with all hypercharges landing where they should. The hoped-for "3 chiral generations" is `REFUTED` against the actual weights, not by arithmetic hand-waving.

Sanity anchor: fed `Spin(10)` instead, the engine reproduces the textbook GUT fact — the 16 is exactly one generation, all six multiplets, all six hypercharges — from nothing but sign vectors:

```bash
python -m theorygate '{"type":"branching","n":5,"chirality":"+","claimed":{"generations":1,"mirrors":0,"extra":0}}'
```

## What it checks

| Claim type | Example | Method |
|---|---|---|
| `arithmetic` | `1*1=2` under explicit semantics | exact `Fraction` evaluation |
| `consistency` | is a claim *set* satisfiable by any semantics? | exhaustive per-semantics check |
| `dimension` | `dim Spin(7,7) spinor = 128`, `dim SU(3) = 8` | closed-form Lie/spinor/bundle formulas |
| `decomposition` | `128 = 64 + 64`? remainder reported | exact sums |
| `branching` | generations inside a spinor, multiplet contents | weight-system branching, exact |
| `geometry` | tetrahedra tiling space, √2 existence | classical exact facts (Dehn invariant, parity proof) |
| `element_mass` | `H2O = 18.015 g/mol` | vendored element table |
| `empirical` | "this unifies gravity and the SM" | **refused: `NOT_DETERMINIZABLE`** |

That last row is the point. Ask a chatbot whether a grand unified theory is true and you'll get a confident essay. Ask TheoryGate and you get `NOT_DETERMINIZABLE` — it certifies exactly what is deterministically checkable and refuses to guess about the rest.

## The lab: 24 pinned claims

```bash
python -m theorygate --lab
```

Two worked corpora drawn from claims that circulate in public discourse (paraphrased, unattributed — the gate judges claims, not people): a nonstandard arithmetic (Corpus A) and a 14-dimensional geometric unification proposal (Corpus B). Expected verdicts are pinned, the run emits a sealed sha256 certificate, and the corpus is deliberately even-handed — most of Corpus B's dimension bookkeeping **verifies**, and Corpus A's headline equation **verifies under its own rule** before the system is proven inconsistent as a whole.

## Install / run

No dependencies — pure Python standard library.

```bash
git clone https://github.com/kyal102/theorygate
cd theorygate
python -m theorygate --demo
python -m pytest tests/ -q        # 15 pinned regressions
```

## What it does — and doesn't

> TheoryGate certifies **exact arithmetic (relative to explicit axioms), dimension bookkeeping, and classical geometry facts**. It does not judge physical truth, experiments, or unpublished formalisms; those are labeled `NOT_DETERMINIZABLE`.

See [docs/LIMITATIONS.md](docs/LIMITATIONS.md) for the honest list, including the convention-dependence caveat on the branching results.

## Related gates

Part of a family of small deterministic verifiers: [unitgate](https://github.com/kyal102/unitgate) (dimensional analysis) · [elementgate](https://github.com/kyal102/elementgate) (chemistry) · [claimgate](https://github.com/kyal102/claimgate) · [claimlint](https://github.com/kyal102/claimlint) · [evidencepack](https://github.com/kyal102/evidencepack) · [replaygate](https://github.com/kyal102/replaygate)

MIT license.
