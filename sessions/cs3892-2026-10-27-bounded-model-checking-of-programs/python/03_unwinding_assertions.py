# FIGURE: figures/retry.svg   (the retry loop as a transition system, drawn -- scripts/draw_models.py)
"""Session 17 -- what an unwinding assertion protects you from.

c/retry.c retries a flaky call at most max_retries times (an input from 0 to 5) and
claims the loop never makes more than 3 attempts. That claim is false.

  --unwind 3 --no-unwinding-assertions   CBMC looks only at runs that leave the loop
                                         within 3 iterations, and says SUCCESSFUL.
  --unwind 3                             the unwinding assertion (on by default since
                                         CBMC 6) fails: some run is LONGER than the bound,
                                         so the answer above was about the wrong runs.
  --unwind 6                             enough unwindings: the unwinding assertion holds,
                                         and the real counterexample appears.

It also prints what CBMC hands the solver at bound 2 (--show-vcc): one copy of each
variable per assignment (static single assignment), the loop guards as Booleans, and,
last, the assertion. The solver is asked for inputs that make every constraint true and
that last line false; if it finds them, they are a counterexample.

Expected: the assertions at the bottom hold.
"""
import re
from pathlib import Path

from cbmc_cli import run

C = Path(__file__).resolve().parent.parent / "c"


def show(args):
    out = run("cbmc", C / "retry.c", *args)
    print("$ cbmc retry.c " + " ".join(map(str, args)))
    for l in out.splitlines():
        if "unwinding assertion" in l or "assertion attempts" in l or "VERIFICATION" in l:
            print("   " + l.strip())
    return out


a = show(["--unwind", 3, "--no-unwinding-assertions"])
assert "assertion attempts <= 3: SUCCESS" in a and "VERIFICATION SUCCESSFUL" in a
print("   ^ wrong: it only considered runs that finish within 3 iterations\n")

b = show(["--unwind", 3])
assert "unwinding assertion loop 0: FAILURE" in b and "VERIFICATION FAILED" in b
print("   ^ the bound is too small, and CBMC says so\n")

c = show(["--unwind", 6, "--trace"])
assert "unwinding assertion loop 0: SUCCESS" in c and "assertion attempts <= 3: FAILURE" in c
m = int(re.search(r"max_retries=(\d+)", c).group(1))
print("   counterexample: max_retries = %d, and every attempt fails" % m)
assert m in (4, 5)

print("\n$ cbmc retry.c --unwind 2 --no-unwinding-assertions --show-vcc   (names shortened)")
vcc = run("cbmc", C / "retry.c", "--unwind", 2, "--no-unwinding-assertions", "--show-vcc")
body = vcc[vcc.index("VERIFICATION CONDITIONS"):]
keep = []
for l in body.splitlines():
    l = re.sub(r"main::1::(\w+)!0@1#(\d+)", r"\1_\2", l)
    l = re.sub(r"main::\$tmp::return_value_nondet_int(\$0)?!0@(\d)#2", r"input", l)
    l = l.replace("goto_symex::\\guard#", "g")
    if re.search(r"\b(max_retries|attempts|ok)_\d|^\{1\}|\bg\d", l) and "CPROVER" not in l:
        keep.append("   " + re.sub(r"^\{-?\d+\}\s*", "", l).strip())
print("\n".join(keep))
assert any("attempts_3 = 1" in l for l in keep) and any("attempts_4 = 2" in l for l in keep)
assert keep[-1].strip().startswith("¬(attempts_5 ≥ 4)")       # the assertion, attempts <= 3, comes last
