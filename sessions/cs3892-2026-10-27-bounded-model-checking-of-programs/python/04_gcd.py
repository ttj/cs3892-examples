# FIGURE: figures/gcd.svg   (Euclid's loop as a transition system, drawn -- scripts/draw_models.py)
"""Session 17 -- Euclid's algorithm by subtraction, and a specification that is too weak.

c/gcd.c computes g = gcd(a0, b0) for every a0, b0 from 1 to 20 and checks two claims:
"g divides both" and "no larger number divides both". -DBROKEN makes gcd return 1, which
divides everything; -DWEAK keeps only the first claim.

  --unwind 20                   both claims hold: the full specification, every input
  --unwind 20 -DBROKEN          "divides both" still holds; "the greatest" fails
  --unwind 20 -DBROKEN -DWEAK   SUCCESSFUL: the weak specification cannot tell
  --unwind 19                   the unwinding assertion fails on a0 = 20, b0 = 1

The same loop as an SMV model, every input pair at once, is smv/04_gcd.smv (NuSMV or nuXmv).

Expected: the assertions at the bottom hold.
"""
import re
from pathlib import Path

from cbmc_cli import run

C = Path(__file__).resolve().parent.parent / "c"


def show(*args):
    out = run("cbmc", C / "gcd.c", *args)
    print("$ cbmc gcd.c " + " ".join(map(str, args)))
    for l in out.splitlines():
        if re.search(r"unwinding assertion loop 0: FAILURE|\] line \d+ assertion |VERIFICATION", l):
            print("   " + re.sub(r"^\[[^\]]*\] ", "", l.strip()))
    return out


DIV = "assertion a0 % g == 0 && b0 % g == 0"
BIG = "assertion !(a0 % d == 0 && b0 % d == 0)"

full = show("--unwind", 20)
assert f"{DIV}: SUCCESS" in full and f"{BIG}: SUCCESS" in full and "VERIFICATION SUCCESSFUL" in full
print("   ^ the full specification holds for every a0, b0 in 1..20\n")

broken = show("--unwind", 20, "-DBROKEN", "--trace")
assert f"{DIV}: SUCCESS" in broken and f"{BIG}: FAILURE" in broken
a0, b0 = (int(re.search(v + r"=(\d+)u", broken).group(1)) for v in ("a0", "b0"))
print("   counterexample: a0 = %d, b0 = %d -- gcd is not 1, and the broken code says 1\n" % (a0, b0))
assert any(a0 % d == 0 and b0 % d == 0 for d in range(2, 21))

weak = show("--unwind", 20, "-DBROKEN", "-DWEAK")
assert f"{DIV}: SUCCESS" in weak and "VERIFICATION SUCCESSFUL" in weak and BIG not in weak
print('   ^ SUCCESSFUL, and wrong: "divides both" is true of 1, for every input\n')

short = show("--unwind", 19, "--trace")
assert "unwinding assertion loop 0: FAILURE" in short
euclid = short.split("Trace for gcd.unwind.0:")[1].split("Trace for")[0]      # the gcd loop's trace
a0, b0 = (int(re.search(v + r"=(\d+)u", euclid).group(1)) for v in ("a0", "b0"))
print("   ^ the bound is one short: a0 = %d, b0 = %d goes round Euclid's loop 19 times" % (a0, b0))
assert {a0, b0} == {20, 1}
