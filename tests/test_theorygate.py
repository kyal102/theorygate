"""TheoryGate regression suite — pinned verdicts for the public engine."""
import re

from theorygate import (
    determinize, check_arithmetic, check_consistency, check_dimension,
    check_decomposition, check_geometry, decompose_spinor_sm, GENERATION,
    VERIFIED, REFUTED, INCONSISTENT, NOT_DETERMINIZABLE, MALFORMED,
)
from theorygate.lab import run_lab


def test_one_times_one_standard_refuted():
    r = check_arithmetic("1*1=2", "standard")
    assert r.status == REFUTED
    assert any("multiplicative identity" in s for s in r.derivation)


def test_one_times_one_repeated_addition_verified():
    assert check_arithmetic("1*1=2", "repeated_addition").status == VERIFIED


def test_mixed_claim_set_is_internally_inconsistent():
    r = check_consistency(["1*1=2", "2*2=4"])
    assert r.status == INCONSISTENT
    assert r.detail["satisfying_semantics"] == []


def test_pure_repeated_addition_set_is_consistent():
    r = check_consistency(["1*1=2", "2*2=6", "3*3=12"])
    assert r.status == VERIFIED
    assert r.detail["satisfying_semantics"] == ["repeated_addition"]


def test_dimension_bookkeeping():
    assert check_dimension("observerse", [4], 14).status == VERIFIED
    assert check_dimension("spinor", [7, 7], 128).status == VERIFIED
    assert check_dimension("group", ["SO(7,7)"], 91).status == VERIFIED
    assert check_dimension("two_forms", [14], 91).status == VERIFIED
    assert check_dimension("group", ["SU(3)"], 8).status == VERIFIED
    assert check_dimension("group", ["SU(3)"], 9).status == REFUTED


def test_generation_counting_reports_remainder():
    r = check_decomposition(128, [16, 16, 16], exact=True)
    assert r.status == REFUTED and r.detail["remainder"] == 80
    assert check_decomposition(128, [64, 64], exact=True).status == VERIFIED
    assert check_decomposition(128, [16, 16, 16], exact=False).status == VERIFIED


def test_tetra_tiling_refuted():
    r = check_geometry("tetra_tiling")
    assert r.status == REFUTED
    assert abs(r.detail["gap_at_5_deg"] - 7.356103) < 1e-3


def test_empirical_claims_are_refused_not_guessed():
    r = determinize({"type": "empirical", "statement": "no straight lines exist"})
    assert r.status == NOT_DETERMINIZABLE


def test_malformed_inputs_never_crash():
    assert determinize({}).status == MALFORMED
    assert determinize({"type": "arithmetic", "equation": "banana"}).status == MALFORMED
    assert check_arithmetic("1/0=5").status == MALFORMED
    assert check_arithmetic("1*1=2", "made_up").status == MALFORMED


def test_element_mass_claims():
    assert determinize({"type": "element_mass", "formula": "H2O",
                        "claimed_mass": 18.015}).status == VERIFIED
    assert determinize({"type": "element_mass", "formula": "H",
                        "claimed_mass": 2.0}).status == REFUTED


def test_lab_corpus_all_expected():
    out = run_lab(verbose=False)
    assert out["payload"]["all_expected"]
    assert out["certificate"]["n_cases"] == 24


# ----------------------------- branching rules -------------------------------
def test_spin10_weyl_spinor_is_exactly_one_sm_generation():
    d = decompose_spinor_sm(5, "+")
    assert (d["generations"], d["mirrors"]) == (1, 0)
    assert d["extra_multiplets"] == {}
    assert d["multiplets"] == {f"({c},{d2},Y={y})": 1
                               for (c, d2, y) in GENERATION}
    dm = decompose_spinor_sm(5, "-")
    assert (dm["generations"], dm["mirrors"]) == (0, 1)


def test_chiral_64_is_two_generations_plus_two_mirrors():
    d = decompose_spinor_sm(7, "+")
    assert d["n_states"] == 64
    assert (d["generations"], d["mirrors"]) == (2, 2)
    assert d["extra_multiplets"] == {}
    assert sorted(d["slots"].values()) == ["generation", "generation",
                                           "mirror", "mirror"]


def test_branching_claims_through_dispatcher():
    ok = determinize({"type": "branching", "n": 7, "chirality": "+",
                      "claimed": {"generations": 2, "mirrors": 2, "extra": 0}})
    assert ok.status == VERIFIED
    hope = determinize({"type": "branching", "n": 7, "chirality": "+",
                        "claimed": {"generations": 3}})
    assert hope.status == REFUTED
    q = determinize({"type": "branching", "n": 7, "chirality": "+",
                     "contains": {"color": "3", "su2": 2, "Y": "1/6"},
                     "claimed_count": 2})
    assert q.status == VERIFIED
    assert determinize({"type": "branching", "n": 99}).status == MALFORMED


def test_branching_state_bookkeeping_is_exact():
    # states = 16*(gens+mirrors) + extra-multiplet states, exactly, at every n
    for n in (5, 6, 7):
        for ch in ("+", "-", None):
            d = decompose_spinor_sm(n, ch)
            extra_states = 0
            for key, m in d["extra_multiplets"].items():
                c, d2 = re.match(r"\((\w+),(\d+),", key).groups()
                extra_states += (3 if c in ("3", "3bar") else 1) * int(d2) * m
            assert 16 * (d["generations"] + d["mirrors"]) + extra_states == d["n_states"]
