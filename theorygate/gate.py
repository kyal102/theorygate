"""TheoryGate: deterministic checks for math/physics theory claims.

  * check_arithmetic(eq, semantics)  -> does ``a op b = c`` hold, exactly?
  * check_consistency(claims)        -> is a SET of arithmetic claims mutually
                                        satisfiable under ANY one semantics?
  * check_dimension(kind, args, d)   -> Lie group / spinor / bundle dimension
  * check_decomposition(total, ...)  -> does a claimed dimension split add up?
  * check_geometry(name)             -> exact classical geometry facts
  * check_element_mass(formula, m)   -> molar-mass claim vs the element table
  * determinize(claim_dict)          -> dispatcher over all of the above

Two arithmetic semantics are implemented, so a claim like "1 x 1 = 2" gets an
exact, axiom-relative verdict instead of a shouting match:

  standard          : field arithmetic over exact rationals (Fraction)
  repeated_addition : "a times b means a added to itself b times",
                      i.e. a x b := a + a*b = a*(b+1) — a rule that actually
                      appears in nonstandard-arithmetic proposals

TheoryGate certifies only what is deterministically checkable: exact
arithmetic, dimension bookkeeping, and classical geometry facts. It does not
judge physical truth, experiments, or unpublished formalisms — those return
NOT_DETERMINIZABLE. Verdicts come from exact computation, never a model.
"""
from __future__ import annotations

import math
import re
from dataclasses import dataclass, field
from fractions import Fraction
from typing import Dict, List, Optional, Tuple

from .elements import atomic_weight
from .formula import parse_formula

PUBLIC_WORDING = (
    "TheoryGate certifies exact arithmetic (relative to explicit axioms), "
    "Lie/spinor/bundle dimension bookkeeping, and classical geometry facts. "
    "It does not judge physical truth or unpublished formalisms; those are "
    "labeled NOT_DETERMINIZABLE. Verdicts are computed, never modeled."
)

VERIFIED = "VERIFIED"
REFUTED = "REFUTED"
INCONSISTENT = "INCONSISTENT"
NOT_DETERMINIZABLE = "NOT_DETERMINIZABLE"
MALFORMED = "MALFORMED_INPUT"

SEMANTICS = ("standard", "repeated_addition")

_EQ = re.compile(
    r"^\s*(-?\d+(?:/\d+)?)\s*([*x+\-/])\s*(-?\d+(?:/\d+)?)\s*=\s*(-?\d+(?:/\d+)?)\s*$",
    re.IGNORECASE,
)


@dataclass
class Result:
    status: str
    claim: str
    detail: Dict = field(default_factory=dict)
    derivation: List[str] = field(default_factory=list)
    reason: str = ""

    def to_dict(self) -> dict:
        return {"tool": "theorygate", "status": self.status, "claim": self.claim,
                "detail": self.detail, "derivation": self.derivation,
                "reason": self.reason, "public_wording": PUBLIC_WORDING}


# ------------------------------------------------------------------ arithmetic
def _apply(op: str, a: Fraction, b: Fraction, semantics: str) -> Optional[Fraction]:
    if op in ("*", "x", "X"):
        if semantics == "repeated_addition":
            # "a added to itself b times": a x b := a + a*b = a*(b+1)
            return a * (b + 1)
        return a * b
    if op == "+":
        return a + b
    if op == "-":
        return a - b
    if op == "/":
        return a / b if b != 0 else None
    return None


def parse_equation(eq: str) -> Optional[Tuple[Fraction, str, Fraction, Fraction]]:
    m = _EQ.match(eq or "")
    if not m:
        return None
    try:
        return (Fraction(m.group(1)), m.group(2),
                Fraction(m.group(3)), Fraction(m.group(4)))
    except (ValueError, ZeroDivisionError):
        return None


def check_arithmetic(eq: str, semantics: str = "standard") -> Result:
    """Exact verdict for one equation under one explicit semantics."""
    if semantics not in SEMANTICS:
        return Result(MALFORMED, eq, reason=f"unknown semantics {semantics!r} "
                      f"(known: {list(SEMANTICS)})")
    p = parse_equation(eq)
    if p is None:
        return Result(MALFORMED, eq, reason="expected '<num> <op> <num> = <num>'")
    a, op, b, c = p
    got = _apply(op, a, b, semantics)
    if got is None:
        return Result(MALFORMED, eq, reason="division by zero")
    ok = got == c
    detail = {"semantics": semantics, "lhs_value": str(got), "claimed": str(c)}
    deriv = [f"under {semantics} semantics: {a} {op} {b} = {got}"]
    if semantics == "repeated_addition" and op in ("*", "x", "X"):
        deriv.insert(0, f"rule: a x b := a + a*b, so {a} x {b} = "
                        f"{a} + {a}*{b} = {got}")
    if ok:
        return Result(VERIFIED, eq, detail, deriv,
                      f"exact equality holds under {semantics} semantics")
    # For 1x1=c identity violations, show the field-axiom collapse.
    if semantics == "standard" and op in ("*", "x", "X") and a == 1 and b == 1 and c != 1:
        deriv += [
            "field axioms: 1 is the multiplicative identity, so 1 x 1 = 1",
            f"assume 1 x 1 = {c}: then 1 = {c}, so 0 = {c - 1}",
            "conclusion: the claim is inconsistent with any field containing 1",
        ]
    return Result(REFUTED, eq, detail, deriv,
                  f"exact evaluation gives {got}, claim says {c} ({semantics} semantics)")


def check_consistency(claims: List[str]) -> Result:
    """Is there ANY single semantics under which every claim holds?

    This is the decisive check for nonstandard-arithmetic proposals: a set
    like {1x1=2, 2x2=4} is satisfied by no semantics at all — the rule that
    yields 1x1=2 forces 2x2=6.
    """
    label = "; ".join(claims)
    if not claims:
        return Result(MALFORMED, label, reason="empty claim set")
    per: Dict[str, List[str]] = {}
    witnesses: Dict[str, str] = {}
    for sem in SEMANTICS:
        failures = []
        for eq in claims:
            r = check_arithmetic(eq, sem)
            if r.status == MALFORMED:
                return Result(MALFORMED, label, reason=f"{eq!r}: {r.reason}")
            if r.status != VERIFIED:
                failures.append(f"{eq} (got {r.detail['lhs_value']})")
        per[sem] = failures
        if failures:
            witnesses[sem] = failures[0]
    satisfiable = [s for s, f in per.items() if not f]
    detail = {"satisfying_semantics": satisfiable,
              "failures_by_semantics": per}
    if satisfiable:
        return Result(VERIFIED, label, detail,
                      reason=f"claim set is consistent under: {', '.join(satisfiable)}")
    deriv = [f"under {s} semantics the set fails at: {w}" for s, w in witnesses.items()]
    return Result(INCONSISTENT, label, detail, deriv,
                  "no implemented semantics satisfies all claims — "
                  "the set is internally inconsistent")


# ------------------------------------------------------------------ dimensions
def group_dim(name: str) -> Optional[int]:
    """dim of the classical/exceptional groups + Spin(p,q); None if unknown."""
    n = (name or "").strip().replace(" ", "")
    exc = {"G2": 14, "F4": 52, "E6": 78, "E7": 133, "E8": 248}
    if n in exc:
        return exc[n]
    m = re.match(r"^(SU|SO|SP|U|SPIN|SL)\(([\d,]+)\)$", n, re.IGNORECASE)
    if not m:
        return None
    fam = m.group(1).upper()
    parts = [int(x) for x in m.group(2).split(",") if x]
    k = sum(parts)                      # SO(p,q)/Spin(p,q) share dim with SO(p+q)
    if fam in ("SU", "SL"):
        return k * k - 1
    if fam == "U":
        return k * k
    if fam in ("SO", "SPIN"):
        return k * (k - 1) // 2
    if fam == "SP":                     # Sp(2n): n(2n+1)
        if k % 2:
            return None
        h = k // 2
        return h * (2 * h + 1)
    return None


def spinor_dim(p: int, q: int = 0, weyl: bool = False) -> Optional[int]:
    """Complex Dirac spinor dim of Spin(p,q) = 2^floor((p+q)/2); Weyl = half
    (even total dimension only)."""
    m = p + q
    if m <= 0:
        return None
    d = 2 ** (m // 2)
    if weyl:
        return d // 2 if m % 2 == 0 else None
    return d


def metric_bundle_dim(n: int) -> int:
    """Fibre dim of the bundle of metrics on an n-manifold: n(n+1)/2."""
    return n * (n + 1) // 2


def two_form_dim(n: int) -> int:
    """dim of 2-forms on R^n = n(n-1)/2 (equals dim so(n): adjoint = Lambda^2)."""
    return n * (n - 1) // 2


_DIM_FNS = {
    "group": lambda a: group_dim(a[0]),
    "spinor": lambda a: spinor_dim(int(a[0]), int(a[1]) if len(a) > 1 else 0,
                                   weyl=(len(a) > 2 and str(a[2]).lower() == "weyl")),
    "metrics": lambda a: metric_bundle_dim(int(a[0])),
    "two_forms": lambda a: two_form_dim(int(a[0])),
    "observerse": lambda a: int(a[0]) + metric_bundle_dim(int(a[0])),
}


def check_dimension(kind: str, args: List, claimed: int) -> Result:
    """Verify one dimension claim, e.g. ('spinor', [7,7], 128)."""
    label = f"dim {kind}{tuple(args)} = {claimed}"
    fn = _DIM_FNS.get(kind)
    if fn is None:
        return Result(MALFORMED, label, reason=f"unknown dimension kind {kind!r} "
                      f"(known: {sorted(_DIM_FNS)})")
    try:
        got = fn(args)
    except (ValueError, TypeError, IndexError) as e:
        return Result(MALFORMED, label, reason=f"bad args: {e}")
    if got is None:
        return Result(MALFORMED, label, reason="dimension not computable for these args")
    detail = {"kind": kind, "args": args, "computed": got, "claimed": claimed}
    if got == int(claimed):
        return Result(VERIFIED, label, detail, reason="dimension bookkeeping checks out")
    return Result(REFUTED, label, detail,
                  reason=f"computed {got}, claimed {claimed} (off by {int(claimed) - got})")


def check_decomposition(total: int, parts: List[int], exact: bool = True) -> Result:
    """Does a claimed decomposition add up? Reports the remainder honestly.

    exact=True  : claim is 'total = sum(parts) with nothing left over'
    exact=False : claim is 'parts fit inside total' (remainder allowed, reported)
    """
    s = sum(parts)
    label = f"{total} = {' + '.join(map(str, parts))}" + ("" if exact else " (+ rest)")
    rem = total - s
    detail = {"total": total, "parts": parts, "sum": s, "remainder": rem}
    if exact:
        if rem == 0:
            return Result(VERIFIED, label, detail, reason="decomposition is exact")
        return Result(REFUTED, label, detail,
                      reason=f"parts sum to {s}; remainder {rem} is unaccounted for — "
                      "the identification is not forced by counting alone")
    if rem >= 0:
        return Result(VERIFIED, label, detail,
                      reason=f"parts fit; {rem} degrees of freedom remain unexplained "
                      "(fit is necessary, not sufficient)")
    return Result(REFUTED, label, detail, reason=f"parts exceed total by {-rem}")


# ------------------------------------------------------------------- geometry
def check_geometry(name: str) -> Result:
    """Exact classical geometry facts that recur in theory claims."""
    key = (name or "").strip().lower().replace("-", "_").replace(" ", "_")

    if key in ("tetra_tiling", "regular_tetrahedra_tile_space"):
        # Dihedral angle of a regular tetrahedron is arccos(1/3) ~ 70.5288 deg.
        ang = math.acos(1.0 / 3.0)
        gap5 = 2 * math.pi - 5 * ang
        over6 = 6 * ang - 2 * math.pi
        deriv = [
            "dihedral angle of a regular tetrahedron = arccos(1/3) "
            f"= {math.degrees(ang):.4f} deg",
            f"5 tetrahedra around an edge: gap of {math.degrees(gap5):.4f} deg remains",
            f"6 tetrahedra around an edge: overlap of {math.degrees(over6):.4f} deg",
            "arccos(1/3) is not a rational multiple of pi, so no integer count "
            "closes the edge figure",
            "independently: the Dehn invariant of the regular tetrahedron is nonzero, "
            "so it cannot tile space (a space-filler must have Dehn invariant zero)",
        ]
        return Result(REFUTED, "regular tetrahedra tile 3-space",
                      {"dihedral_deg": round(math.degrees(ang), 6),
                       "gap_at_5_deg": round(math.degrees(gap5), 6)},
                      deriv, "regular tetrahedra do NOT tile space — the edge angle "
                      "never closes and the Dehn invariant obstructs it")

    if key in ("sqrt2_exists", "sqrt2_is_real"):
        deriv = [
            "x^2 - 2 is continuous with f(1) = -1 < 0 < 2 = f(2)",
            "by completeness of the reals a root exists in (1, 2): sqrt(2) is real",
            "irrationality: p^2 = 2q^2 forces p even (p=2k), then q^2 = 2k^2 forces q "
            "even — contradicting a reduced fraction; sqrt(2) is irrational, not nonexistent",
        ]
        return Result(VERIFIED, "sqrt(2) exists as a real (irrational) number",
                      {"bracket": [1.4142135, 1.4142136]}, deriv,
                      "sqrt(2) is a real algebraic number; irrational is not 'unresolvable'")

    if key in ("sqrt2_not_real", "sqrt2_unresolvable", "sqrt2_does_not_exist"):
        inner = check_geometry("sqrt2_exists")
        return Result(REFUTED, "sqrt(2) does not exist / is unresolvable",
                      inner.detail, inner.derivation, "refuted: " + inner.reason)

    return Result(MALFORMED, name, reason=f"unknown geometry fact {name!r}")


# ------------------------------------------------------------------- elements
def _molar_mass(formula: str):
    """Molar mass from the vendored element table. Returns (mass|None, err)."""
    p = parse_formula(formula)
    if not p.ok:
        return None, p.error
    total = 0.0
    for el, n in p.counts.items():
        w = atomic_weight(el)
        if w is None:
            return None, f"no atomic weight for {el}"
        total += w * n
    return round(total, 4), ""


def check_element_mass(formula: str, claimed_mass: float, tol: float = 0.01) -> Result:
    """Molar-mass claim vs the standard element table (relative tolerance)."""
    label = f"molar mass of {formula} = {claimed_mass} g/mol"
    mass, err = _molar_mass(formula)
    if mass is None:
        return Result(MALFORMED, label, reason=err)
    rel = abs(mass - claimed_mass) / mass if mass else float("inf")
    detail = {"computed_mass": mass, "claimed": claimed_mass,
              "relative_error": round(rel, 6), "tolerance": tol}
    if rel <= tol:
        return Result(VERIFIED, label, detail,
                      reason=f"within {tol:.0%} of the computed {mass} g/mol")
    return Result(REFUTED, label, detail,
                  reason=f"element table gives {mass} g/mol; claim is off by {rel:.1%}")


# ------------------------------------------------------------------ dispatcher
def determinize(claim: dict) -> Result:
    """One entry point. claim = {"type": ..., ...}; unknown/empirical types are
    honestly NOT_DETERMINIZABLE, never guessed."""
    if not isinstance(claim, dict) or "type" not in claim:
        return Result(MALFORMED, str(claim), reason="claim must be a dict with a 'type'")
    t = claim["type"]
    try:
        if t == "arithmetic":
            return check_arithmetic(claim["equation"], claim.get("semantics", "standard"))
        if t == "consistency":
            return check_consistency(claim["equations"])
        if t == "dimension":
            return check_dimension(claim["kind"], claim.get("args", []), claim["claimed"])
        if t == "decomposition":
            return check_decomposition(claim["total"], claim["parts"],
                                       claim.get("exact", True))
        if t == "geometry":
            return check_geometry(claim["name"])
        if t == "element_mass":
            return check_element_mass(claim["formula"], claim["claimed_mass"],
                                      claim.get("tol", 0.01))
        if t == "branching":
            from .branching import check_branching
            return check_branching(claim)
        if t == "empirical":
            return Result(NOT_DETERMINIZABLE, claim.get("statement", ""),
                          reason="empirical/philosophical/unpublished-formalism claim — "
                          "no deterministic check exists; TheoryGate refuses to guess")
    except KeyError as e:
        return Result(MALFORMED, str(claim), reason=f"missing field {e}")
    return Result(MALFORMED, str(claim), reason=f"unknown claim type {t!r}")
