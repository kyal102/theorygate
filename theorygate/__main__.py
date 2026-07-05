"""TheoryGate CLI.

  python -m theorygate --demo               # the 60-second tour
  python -m theorygate --lab                # full 24-claim pinned corpus
  python -m theorygate '<claim json>'       # determinize one claim
  python -m theorygate --json '<claim json>'  # same, machine-readable output
"""
from __future__ import annotations

import json
import sys

from .gate import determinize


def _print_result(r, as_json: bool) -> int:
    if as_json:
        print(json.dumps(r.to_dict(), indent=2, default=str))
    else:
        print(f"{r.claim}\n  -> {r.status}")
        if r.reason:
            print(f"     {r.reason}")
        for step in r.derivation:
            print(f"     | {step}")
    return 0 if r.status == "VERIFIED" else 1


def _demo() -> int:
    print("TheoryGate demo — exact verdicts, no model.\n")

    print("1) A famous nonstandard arithmetic, judged on its own terms:")
    for claim in [
        {"type": "arithmetic", "equation": "1*1=2", "semantics": "standard"},
        {"type": "arithmetic", "equation": "1*1=2", "semantics": "repeated_addition"},
        {"type": "consistency", "equations": ["1*1=2", "2*2=4"]},
    ]:
        r = determinize(claim)
        print(f"   {r.claim:<28} -> {r.status}: {r.reason}")

    print("\n2) A 14-dimensional unification proposal's bookkeeping:")
    for claim in [
        {"type": "dimension", "kind": "spinor", "args": [7, 7], "claimed": 128},
        {"type": "branching", "n": 7, "chirality": "+",
         "claimed": {"generations": 2, "mirrors": 2, "extra": 0}},
        {"type": "branching", "n": 7, "chirality": "+",
         "claimed": {"generations": 3}},
    ]:
        r = determinize(claim)
        print(f"   {r.claim}\n      -> {r.status}: {r.reason}")

    print("\n3) And what it refuses to judge:")
    r = determinize({"type": "empirical",
                     "statement": "this theory unifies gravity and the SM"})
    print(f"   {r.claim} -> {r.status}")
    print("\nRun `python -m theorygate --lab` for the full pinned corpus.")
    return 0


def main(argv=None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    as_json = "--json" in args
    if as_json:
        args.remove("--json")
    if not args or args[0] in ("-h", "--help"):
        print(__doc__.strip())
        return 0
    if args[0] == "--demo":
        return _demo()
    if args[0] == "--lab":
        from .lab import run_lab
        out = run_lab(verbose=not as_json)
        if as_json:
            print(json.dumps(out, indent=2, default=str))
        return 0 if out["payload"]["all_expected"] else 1
    try:
        claim = json.loads(args[0])
    except json.JSONDecodeError as e:
        print(f"could not parse claim JSON: {e}", file=sys.stderr)
        return 2
    return _print_result(determinize(claim), as_json)


if __name__ == "__main__":
    sys.exit(main())
