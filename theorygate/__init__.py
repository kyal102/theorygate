"""TheoryGate — a deterministic determinizer for math/physics theory claims.

Reduces a theory claim to its checkable core and returns an exact verdict:
VERIFIED / REFUTED / INCONSISTENT / NOT_DETERMINIZABLE. Pure stdlib; verdicts
come from exact computation (Fractions, weight systems), never a model.
"""
from .gate import (
    determinize, check_arithmetic, check_consistency, check_dimension,
    check_decomposition, check_geometry, check_element_mass,
    group_dim, spinor_dim, metric_bundle_dim, two_form_dim,
    VERIFIED, REFUTED, INCONSISTENT, NOT_DETERMINIZABLE, MALFORMED,
    PUBLIC_WORDING, Result,
)
from .branching import (
    check_branching, decompose_spinor_sm, spinor_weights, sm_classify,
    collect_sm_multiplets, GENERATION, MIRROR,
)

__version__ = "0.1.0"

__all__ = [
    "determinize", "check_arithmetic", "check_consistency", "check_dimension",
    "check_decomposition", "check_geometry", "check_element_mass",
    "check_branching", "decompose_spinor_sm", "spinor_weights", "sm_classify",
    "collect_sm_multiplets", "GENERATION", "MIRROR",
    "group_dim", "spinor_dim", "metric_bundle_dim", "two_form_dim",
    "VERIFIED", "REFUTED", "INCONSISTENT", "NOT_DETERMINIZABLE", "MALFORMED",
    "PUBLIC_WORDING", "Result",
]
