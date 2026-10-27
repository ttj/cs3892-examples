# FIGURE: figures/shipping.svg   (c/shipping.c as a transition system, drawn -- scripts/draw_models.py)
"""Session 18 -- generating tests with a model checker: cbmc --cover branch.

Each branch of shipping() becomes a goal: "make the solver reach this edge". CBMC
asks for one input per goal and prints the inputs it found -- a test suite with
measured branch coverage. This file then compiles shipping.c with gcc, runs every
generated test, and checks each result against an independent Python model of the
function. Coverage says which branches the tests reached; it does not say the
outputs were right, which is why the outputs are checked here separately.

Expected: the assertions at the bottom hold.
"""
import re
import subprocess
import tempfile
from pathlib import Path

from cbmc_cli import run

C = Path(__file__).resolve().parent.parent / "c"

out = run("cbmc", C / "shipping.c", "--function", "shipping", "--cover", "branch", "--show-test-suite")
print("$ cbmc shipping.c --function shipping --cover branch --show-test-suite")
cov = re.search(r"\*\* (\d+) of (\d+) covered \(([\d.]+)%\)", out)
tests = [tuple(int(v) for v in re.findall(r"=(-?\d+)", l)) for l in out.splitlines() if l.startswith("weight_g=")]
print("   %s of %s branch goals covered (%s%%) by %d tests:" % (cov[1], cov[2], cov[3], len(tests)))
for w, e in tests:
    print("     weight_g = %-6d express = %d" % (w, e))
assert cov[1] == cov[2] and float(cov[3]) == 100.0 and len(tests) >= 3


def model(weight_g, express):
    if weight_g <= 0:
        return -1
    cost = 500 + (300 if weight_g > 2000 else 0)
    return cost * 2 if express else cost


with tempfile.TemporaryDirectory() as d:
    main = Path(d) / "main.c"
    calls = "".join('    printf("%%d\\n", shipping(%d, %d));\n' % t for t in tests)
    main.write_text('#include <stdio.h>\nint shipping(int, int);\nint main(void) {\n' + calls + '    return 0;\n}\n')
    exe = Path(d) / "t"
    subprocess.run(["gcc", "-o", str(exe), str(C / "shipping.c"), str(main)], check=True)
    got = [int(x) for x in subprocess.run([str(exe)], capture_output=True, text=True, check=True).stdout.split()]

print("\n   running them (gcc):")
for (w, e), g in zip(tests, got):
    print("     shipping(%d, %d) = %d   (model: %d)" % (w, e, g, model(w, e)))
assert got == [model(w, e) for w, e in tests]
print("\n   Note the inputs: 1048576 for 'express' is a solver's idea of a true value.")
print("   Generated tests reach every branch; a person still decides what the right outputs are.")
