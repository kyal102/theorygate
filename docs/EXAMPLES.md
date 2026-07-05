# Examples

All claims are JSON dicts passed to `python -m theorygate '<json>'` (or
`determinize(claim)` from Python). Exit code is 0 for `VERIFIED`, 1 otherwise.

## Arithmetic, on explicit axioms

```bash
python -m theorygate '{"type":"arithmetic","equation":"1*1=2","semantics":"standard"}'
# REFUTED — with the field-axiom collapse in the derivation

python -m theorygate '{"type":"arithmetic","equation":"1*1=2","semantics":"repeated_addition"}'
# VERIFIED — under the rule a x b := a + a*b
```

## Consistency of a claim set

```bash
python -m theorygate '{"type":"consistency","equations":["1*1=2","2*2=4"]}'
# INCONSISTENT — no semantics satisfies both; witness printed

python -m theorygate '{"type":"consistency","equations":["1*1=2","2*2=6","3*3=12"]}'
# VERIFIED — consistent under repeated_addition (and only that)
```

## Dimension bookkeeping

```bash
python -m theorygate '{"type":"dimension","kind":"spinor","args":[7,7],"claimed":128}'
python -m theorygate '{"type":"dimension","kind":"group","args":["SO(7,7)"],"claimed":91}'
python -m theorygate '{"type":"dimension","kind":"two_forms","args":[14],"claimed":91}'
python -m theorygate '{"type":"dimension","kind":"observerse","args":[4],"claimed":14}'
# all VERIFIED
```

## Decompositions (remainders reported, never hidden)

```bash
python -m theorygate '{"type":"decomposition","total":128,"parts":[64,64],"exact":true}'
# VERIFIED

python -m theorygate '{"type":"decomposition","total":128,"parts":[16,16,16],"exact":true}'
# REFUTED — remainder 80 is unaccounted for
```

## Branching rules (the flagship)

```bash
# textbook anchor: the 16 of Spin(10) is exactly one SM generation
python -m theorygate '{"type":"branching","n":5,"chirality":"+","claimed":{"generations":1,"mirrors":0,"extra":0}}'

# the chiral 64 of a Spin(14)-type proposal: 2 generations + 2 mirrors, exactly
python -m theorygate '{"type":"branching","n":7,"chirality":"+","claimed":{"generations":2,"mirrors":2,"extra":0}}'

# the hope: 3 chiral generations — refuted against the actual weights
python -m theorygate '{"type":"branching","n":7,"chirality":"+","claimed":{"generations":3}}'

# multiplet containment: exactly 2 left-handed quark doublets (3,2,Y=1/6)
python -m theorygate '{"type":"branching","n":7,"chirality":"+","contains":{"color":"3","su2":2,"Y":"1/6"},"claimed_count":2}'
```

Use `--json` for the full decomposition (per-slot content, all multiplets with
hypercharges):

```bash
python -m theorygate --json '{"type":"branching","n":7,"chirality":"+","claimed":{"generations":2,"mirrors":2,"extra":0}}'
```

## Geometry and elements

```bash
python -m theorygate '{"type":"geometry","name":"tetra_tiling"}'
# REFUTED — dihedral angle gap + Dehn invariant, derivation included

python -m theorygate '{"type":"element_mass","formula":"H2O","claimed_mass":18.015}'
# VERIFIED
```

## What it refuses

```bash
python -m theorygate '{"type":"empirical","statement":"this theory unifies gravity and the SM"}'
# NOT_DETERMINIZABLE — no deterministic check exists; TheoryGate refuses to guess
```
