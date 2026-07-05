"""TheoryGate branching engine: exact branching rules for so(2n) spinors down
to the Standard Model group — the computation behind claims that a large
spinor (e.g. the 128 of a Spin(14)-type unification proposal) "contains the
Standard Model fermions".

Everything is exact rational arithmetic on weight systems (no floats, no
model). The chain implemented is the standard GUT-relevant one:

    so(2n) ⊃ so(10) ⊕ so(2n-10)                (coordinate split)
    so(10) ⊃ so(6) ⊕ so(4) = su(4) ⊕ su(2)_L ⊕ su(2)_R    (Pati-Salam)
    su(4)  ⊃ su(3)_c ⊕ u(1)_{B-L}
    Y = (B-L)/2 + T3_R,   Q_em = T3_L + Y

Spinor weights of so(2n) are the sign vectors (±1/2)^n; chirality is the
parity of minus signs; restriction along a coordinate split is literal
(spinor(2n) = spinor(2a) ⊗ spinor(2b) is automatic in this basis). The SM
functionals on a weight s = (s1..sn):

    color        : from the minus-count k among (s1,s2,s3):
                   k=0 or 3 -> singlet, k=2 -> 3, k=1 -> 3bar
    B-L          = -(2/3)(s1+s2+s3)
    T3_L         = (s4+s5)/2      (doublet iff s4 == s5)
    T3_R         = (s4-s5)/2
    spectators   : (s6..sn) — the so(2n-10) directions ("generation slots")

Multiplets are collected by exact state-counting (a (3,2) multiplet is exactly
6 sign-vector states) with a hard divisibility check: if states don't group
into whole multiplets the engine REFUSES rather than rounding. Signature
(e.g. Spin(7,7) vs Spin(14)) does not change weights, so the complexified
branching is identical; results are stated at that level.

Convention note: which so(10) chirality is called '16' vs '16bar' and the
overall sign of B-L are conventions; what is convention-independent — and what
this module certifies — is the PAIRING: how many exact SM-generation copies vs
mirror (CPT-conjugate) copies a given spinor contains, and which multiplets
appear with which hypercharges relative to each other.
"""
from __future__ import annotations

from collections import Counter
from fractions import Fraction
from functools import lru_cache
from itertools import product
from typing import Dict, List, Optional, Tuple

from .gate import Result, VERIFIED, REFUTED, MALFORMED

HALF = Fraction(1, 2)

# One SM generation, as (color, su2L_dim, hypercharge Y) -> multiplicity.
# Q(3,2,1/6) uc(3bar,1,-2/3) dc(3bar,1,1/3) L(1,2,-1/2) ec(1,1,1) nuc(1,1,0)
GENERATION: Counter = Counter({
    ("3", 2, Fraction(1, 6)): 1,
    ("3bar", 1, Fraction(-2, 3)): 1,
    ("3bar", 1, Fraction(1, 3)): 1,
    ("1", 2, Fraction(-1, 2)): 1,
    ("1", 1, Fraction(1)): 1,
    ("1", 1, Fraction(0)): 1,
})
# Mirror generation = CPT conjugate: color 3<->3bar, Y -> -Y.
MIRROR: Counter = Counter({
    ("3bar", 2, Fraction(-1, 6)): 1,
    ("3", 1, Fraction(2, 3)): 1,
    ("3", 1, Fraction(-1, 3)): 1,
    ("1", 2, Fraction(1, 2)): 1,
    ("1", 1, Fraction(-1)): 1,
    ("1", 1, Fraction(0)): 1,
})
# One generation = 16 Weyl states: 3*2 + 3 + 3 + 2 + 1 + 1.
GEN_WEYL_STATES = 16


def spinor_weights(n: int, chirality: Optional[str] = None) -> List[Tuple[Fraction, ...]]:
    """Weights of the so(2n) spinor: (±1/2)^n. chirality '+' = even minus
    count, '-' = odd, None = Dirac (all 2^n)."""
    out = []
    for signs in product((HALF, -HALF), repeat=n):
        neg = sum(1 for s in signs if s < 0)
        if chirality == "+" and neg % 2 == 1:
            continue
        if chirality == "-" and neg % 2 == 0:
            continue
        out.append(signs)
    return out


def sm_classify(w: Tuple[Fraction, ...]) -> Dict:
    """SM quantum numbers of one spinor weight (needs n >= 5)."""
    c = w[:3]
    k = sum(1 for s in c if s < 0)
    color = {0: "1", 1: "3bar", 2: "3", 3: "1"}[k]
    b_minus_l = Fraction(-2, 3) * sum(c)
    t3l = (w[3] + w[4]) / 2
    t3r = (w[3] - w[4]) / 2
    y = b_minus_l / 2 + t3r
    return {"color": color, "B-L": b_minus_l, "T3L": t3l, "T3R": t3r,
            "Y": y, "Q_em": t3l + y, "spectators": tuple(w[5:])}


def collect_sm_multiplets(weights: List[Tuple[Fraction, ...]]) -> Counter:
    """Group weight states into whole SM multiplets, exactly.

    Returns Counter[(color, su2L_dim, Y, spectators)] -> multiplicity.
    Raises ValueError if states do not divide into whole multiplets — the
    engine refuses to round.
    """
    groups: Counter = Counter()
    for w in weights:
        if len(w) < 5:
            raise ValueError("SM chain needs so(2n) with n >= 5")
        k = sum(1 for s in w[:3] if s < 0)
        is_doublet = (w[3] == w[4])
        t3r = Fraction(0) if is_doublet else (w[3] - w[4]) / 2
        groups[(k, is_doublet, t3r, tuple(w[5:]))] += 1

    mult: Counter = Counter()
    for (k, is_doublet, t3r, spec), count in groups.items():
        dim_c = 3 if k in (1, 2) else 1
        dim_2 = 2 if is_doublet else 1
        size = dim_c * dim_2
        if count % size:
            raise ValueError(
                f"{count} states in class (k={k}, doublet={is_doublet}, "
                f"T3R={t3r}, spec={spec}) do not fill whole "
                f"({dim_c},{dim_2}) multiplets of size {size}")
        color = {0: "1", 1: "3bar", 2: "3", 3: "1"}[k]
        b_minus_l = Fraction(-2, 3) * (Fraction(3, 2) - k)   # sum(s1..s3) = 3/2 - k
        y = b_minus_l / 2 + t3r
        mult[(color, dim_2, y, spec)] += count // size
    return mult


def _aggregate(mult: Counter) -> Counter:
    """Sum multiplicities over spectator slots -> Counter[(color, su2, Y)]."""
    agg: Counter = Counter()
    for (color, d2, y, _spec), m in mult.items():
        agg[(color, d2, y)] += m
    return agg


def _peel(agg: Counter, table: Counter) -> int:
    """Max whole copies of `table` that fit in `agg`; subtracts them in place."""
    n = min(agg.get(key, 0) // need for key, need in table.items())
    if n > 0:
        for key, need in table.items():
            agg[key] -= need * n
    return n


@lru_cache(maxsize=64)
def decompose_spinor_sm(n: int, chirality: Optional[str]) -> Dict:
    """Full SM decomposition of the so(2n) spinor (n >= 5), exact.

    Returns generations/mirrors counts, leftover multiplets, per-spectator
    slot content, and total state bookkeeping.
    """
    ws = spinor_weights(n, chirality)
    mult = collect_sm_multiplets(ws)
    agg = _aggregate(mult)
    gens = _peel(agg, GENERATION)
    mirrors = _peel(agg, MIRROR)
    extra = {f"({c},{d2},Y={y})": m for (c, d2, y), m in sorted(
        agg.items(), key=lambda kv: str(kv[0])) if m}

    # Which spectator slots hold a whole generation / mirror on their own?
    slots: Dict[Tuple, str] = {}
    specs = {spec for (_c, _d, _y, spec) in mult}
    for spec in sorted(specs):
        sub = Counter({(c, d2, y): m for (c, d2, y, sp), m in mult.items()
                       if sp == spec})
        if sub == GENERATION:
            slots[spec] = "generation"
        elif sub == MIRROR:
            slots[spec] = "mirror"
        else:
            slots[spec] = "mixed"
    return {
        "algebra": f"so({2*n})", "chirality": chirality or "dirac",
        "n_states": len(ws), "generations": gens, "mirrors": mirrors,
        "extra_multiplets": extra,
        "slots": {str(tuple(str(x) for x in k)): v for k, v in slots.items()},
        "multiplets": {f"({c},{d2},Y={y})": m
                       for (c, d2, y), m in sorted(_aggregate(mult).items(),
                                                   key=lambda kv: str(kv[0]))},
    }


_CHAIN_DERIVATION = [
    "chain: so(2n) > so(10) + so(2n-10) > [su(4)+su(2)L+su(2)R] > SM "
    "(Pati-Salam route; signature does not change weights)",
    "spinor weights = (+-1/2)^n; chirality = parity of minus signs; "
    "restriction along a coordinate split is exact in this basis",
    "functionals: B-L = -(2/3)(s1+s2+s3), T3L = (s4+s5)/2, "
    "T3R = (s4-s5)/2, Y = (B-L)/2 + T3R, Q = T3L + Y",
    "multiplets collected by exact state-counting with a hard divisibility "
    "check; generation/mirror copies peeled as whole 16-plets",
    "convention-independent content: generation-vs-mirror pairing and "
    "relative hypercharges (which chirality is named '16' is convention)",
]


def check_branching(claim: dict) -> Result:
    """Verdict for a branching claim.

    Count form:
      {"type":"branching", "n":7, "chirality":"+"|"-"|"dirac",
       "claimed": {"generations":2, "mirrors":2, "extra":0}}
    Containment form:
      {"type":"branching", "n":7, "chirality":"+",
       "contains": {"color":"3","su2":2,"Y":"1/6"}, "claimed_count":2}
    """
    try:
        n = int(claim["n"])
    except (KeyError, TypeError, ValueError):
        return Result(MALFORMED, str(claim), reason="branching claim needs integer 'n'")
    if not 5 <= n <= 12:
        return Result(MALFORMED, str(claim),
                      reason="n must be in 5..12 (so(10)..so(24))")
    ch = claim.get("chirality", "dirac")
    ch_arg = {"+": "+", "-": "-", "weyl+": "+", "weyl-": "-",
              "dirac": None}.get(str(ch).lower())
    if ch_arg is None and str(ch).lower() != "dirac":
        return Result(MALFORMED, str(claim), reason=f"unknown chirality {ch!r}")

    try:
        dec = decompose_spinor_sm(n, ch_arg)
    except ValueError as e:
        return Result(MALFORMED, str(claim), reason=str(e))

    if "contains" in claim:
        want = claim["contains"]
        try:
            key = (str(want["color"]), int(want["su2"]), Fraction(str(want["Y"])))
        except (KeyError, ValueError, TypeError) as e:
            return Result(MALFORMED, str(claim), reason=f"bad 'contains': {e}")
        label = (f"so({2*n}) spinor ({dec['chirality']}) contains "
                 f"({key[0]},{key[1]},Y={key[2]}) x {claim.get('claimed_count')}")
        got = dec["multiplets"].get(f"({key[0]},{key[1]},Y={key[2]})", 0)
        claimed = int(claim.get("claimed_count", 0))
        detail = {"computed_count": got, "claimed_count": claimed,
                  "decomposition": dec}
        if got == claimed:
            return Result(VERIFIED, label, detail, _CHAIN_DERIVATION,
                          f"exact multiplicity is {got}")
        return Result(REFUTED, label, detail, _CHAIN_DERIVATION,
                      f"exact multiplicity is {got}, claim says {claimed}")

    want = claim.get("claimed", {})
    label = (f"so({2*n}) spinor ({dec['chirality']}, {dec['n_states']} states) = "
             f"{want.get('generations', '?')} generation(s) + "
             f"{want.get('mirrors', '?')} mirror(s)"
             + (" + nothing else" if want.get("extra", None) == 0 else ""))
    n_extra = sum(dec["extra_multiplets"].values())
    checks = []
    if "generations" in want:
        checks.append(int(want["generations"]) == dec["generations"])
    if "mirrors" in want:
        checks.append(int(want["mirrors"]) == dec["mirrors"])
    if "extra" in want and want["extra"] is not None:
        checks.append(int(want["extra"]) == n_extra)
    if not checks:
        return Result(MALFORMED, str(claim),
                      reason="claimed must state generations/mirrors/extra")
    detail = {"computed": {"generations": dec["generations"],
                           "mirrors": dec["mirrors"], "extra_multiplets": n_extra},
              "claimed": want, "decomposition": dec}
    reason = (f"computed: {dec['generations']} generation(s), {dec['mirrors']} "
              f"mirror(s), {n_extra} extra multiplet(s); slots: {dec['slots']}")
    if all(checks):
        return Result(VERIFIED, label, detail, _CHAIN_DERIVATION, reason)
    return Result(REFUTED, label, detail, _CHAIN_DERIVATION, reason)
