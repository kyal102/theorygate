# Limitations

TheoryGate is honest about its edges. Read this before citing a verdict.

## Verdicts are axiom-relative, not cosmic

`REFUTED` for an arithmetic claim means *refuted under the named semantics* (field
axioms, or the repeated-addition rule). The `consistency` check is exhaustive only
over the semantics the gate implements (`standard`, `repeated_addition`). A claim
set labeled `INCONSISTENT` is inconsistent with respect to those two rules — if you
believe a third rule rescues the set, encode it and re-run; the gate's answer is
only as broad as its semantics list.

## Branching results are convention-dependent in naming, not in content

Which so(10) chirality is called "16" vs "16bar", and the overall sign of B−L, are
conventions. What the gate certifies is convention-independent: the *pairing*
(how many exact SM-generation copies vs mirror copies a spinor contains) and the
*relative* hypercharges. Also: the branching is computed at the level of
complexified weight systems, so `Spin(7,7)` and `Spin(14)` give identical
decompositions — real-form-specific statements (unitarity, which real slices exist)
are out of scope.

## Counting multiplets is necessary, not sufficient

"The chiral 64 contains 2 generations + 2 mirrors" is a statement about group
representation content. It does not say the proposal's dynamics select those
states, give them the right masses, or remove the mirrors. A theory can pass every
TheoryGate check and still be physically wrong. (The converse is stronger: failing
these checks is fatal.)

## Dimension formulas cover the classical families + G2/F4/E6/E7/E8

Exotic constructions (affine algebras, super-algebras, non-compact real-form
subtleties) return `MALFORMED_INPUT`, not a guess.

## Geometry facts are a small pinned library

`tetra_tiling` and `sqrt2_*` are implemented. It is a lookup of exact classical
results with derivations, not a general theorem prover.

## Element masses use standard atomic weights

Averaged terrestrial isotopic composition, ~1% default tolerance. Not isotope-
resolved.

## `NOT_DETERMINIZABLE` is a feature

Empirical, philosophical, or unpublished-formalism claims are refused, never
scored. If TheoryGate gave an opinion on whether a theory "unifies gravity and the
Standard Model", it would be exactly the kind of confident guess this tool exists
to replace.
