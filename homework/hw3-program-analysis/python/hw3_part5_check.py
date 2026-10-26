"""HW3 Part 5 -- check contracts for the three functions in c/part5_functions.c.

    python3 hw3_part5_check.py                    uses c/contracts.h
    python3 hw3_part5_check.py my_contracts.h     uses another header

For each function it runs three checks with CBMC:

  holds    goto-instrument --enforce-contract, then cbmc --function <name>: does the
           function satisfy its contract? "+ overflow" means CBMC also found an arithmetic
           overflow that the precondition does not rule out.
           (A contract the real function fails is wrong -- or the function is.)
  mutant   the same, on a deliberately wrong version (-DMUTANT_<NAME>). A contract the
           mutant ALSO satisfies does not tell the two apart: it is too weak to catch that bug.
  meetable a harness assumes the precondition and asserts false. If CBMC says SUCCESSFUL,
           no input satisfies the precondition: every postcondition then "holds", vacuously.

Exits 0 whatever the results.
"""
import shutil
import sys
import tempfile
from pathlib import Path

from cbmc_cli import run

C = Path(__file__).resolve().parent.parent / "c"
FUNCS = {"sat_add": ("a, b, limit", "SAT_ADD"), "abs_diff": ("a, b", "ABS_DIFF"),
         "median3": ("a, b, c", "MEDIAN3")}


def verdict(out):
    """The ensures clause's verdict, plus a note if any other check (e.g. overflow) fails."""
    ens = [l for l in out.splitlines() if "Check ensures clause" in l]
    if not ens:
        return "ERROR: " + " ".join(l.strip() for l in out.splitlines() if "error" in l.lower())[:200]
    v = "holds" if all(l.rstrip().endswith("SUCCESS") for l in ens) else "FAILS"
    other = [l for l in out.splitlines() if l.rstrip().endswith("FAILURE") and "ensures" not in l]
    if not other:
        return v
    return v + (" + overflow" if any("overflow" in l for l in other) else " + %d other failures" % len(other))


def enforce(d, fn, macro, mutant):
    gb, gb2 = d / f"{fn}{mutant}.gb", d / f"{fn}{mutant}_c.gb"
    flags = [f"-DMUTANT_{macro}"] if mutant else []
    cc = run("goto-cc", d / "part5_functions.c", "-o", gb, *flags)
    if not gb.exists():
        err = next((l for l in cc.splitlines() if "error" in l.lower()), cc.strip()[:120])
        return "does not compile: " + err.split("error:")[-1].strip()[:60]
    run("goto-instrument", "--enforce-contract", fn, gb, gb2)
    return verdict(run("cbmc", gb2, "--function", fn))


def meetable(d, fn, params, macro):
    decl = " ".join(f"int {p.strip()} = nondet_int();" for p in params.split(","))
    (d / "meet.c").write_text('#include "contracts.h"\nint nondet_int(void);\n'
                              f"int main(void) {{ {decl} __CPROVER_assume(REQUIRES_{macro}); "
                              "__CPROVER_assert(0, \"nothing gets here\"); return 0; }\n")
    line = next((l for l in run("cbmc", d / "meet.c").splitlines() if "nothing gets here" in l), "")
    if line.rstrip().endswith("FAILURE"):
        return "yes"                       # some input reached the assert: the precondition can be met
    if line.rstrip().endswith("SUCCESS"):
        return "NO - no input meets it"
    return "ERROR"


if __name__ == "__main__":
    header = Path(sys.argv[1]) if len(sys.argv) > 1 else C / "contracts.h"
    print("contracts from", header)
    with tempfile.TemporaryDirectory() as d:
        d = Path(d)
        shutil.copy(C / "part5_functions.c", d)
        shutil.copy(header, d / "contracts.h")
        print("   %-9s %-20s %-20s %s" % ("function", "the function", "its mutant", "precondition meetable?"))
        for fn, (params, macro) in FUNCS.items():
            print("   %-9s %-20s %-20s %s" % (fn, enforce(d, fn, macro, ""), enforce(d, fn, macro, "m"),
                                             meetable(d, fn, params, macro)))
    print("\n   'its mutant: holds' means the contract cannot tell the buggy version from the real one.")
