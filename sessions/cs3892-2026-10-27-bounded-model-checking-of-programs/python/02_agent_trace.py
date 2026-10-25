# FIGURE: figures/agent_c.svg   (the agent as a transition system, drawn -- scripts/draw_models.py)
"""Session 17 -- reading a CBMC counterexample: session 11's agent, in C.

The model's choice of action, and the human's answer, are inputs CBMC may set to
anything (nondet_int()). The property is the one the course has used since session
11: never delete without approval. Without a gateway it fails, and CBMC's trace says
exactly which inputs make it fail. With a gateway compiled in (-DGATEWAY), it holds
for every run of up to three steps.

Expected: the assertions at the bottom hold.
"""
import re
from pathlib import Path

from cbmc_cli import run

C = Path(__file__).resolve().parent.parent / "c"

out = run("cbmc", C / "agent.c", "--unwind", 4, "--trace")
print("$ cbmc agent.c --unwind 4 --trace")
trace = [l.strip() for l in out.splitlines() if re.match(r"\s+(approved|step|action)=", l)]
for l in trace:
    print("   " + l.split(" (")[0])
print("   " + next(l for l in out.splitlines() if "assertion approved" in l).strip())
assert "assertion approved: FAILURE" in out and "VERIFICATION FAILED" in out
values = [l.split(" (")[0] for l in trace]
assert "action=2" in values and values.index("action=2") < len(values)
assert "approved=0" in values                     # it deleted while approved was 0

out = run("cbmc", C / "agent.c", "--unwind", 4, "-DGATEWAY")
print("\n$ cbmc agent.c --unwind 4 -DGATEWAY")
print("   " + next(l for l in out.splitlines() if "assertion approved" in l).strip())
print("   " + next(l for l in out.splitlines() if "VERIFICATION" in l).strip())
assert "assertion approved: SUCCESS" in out and "VERIFICATION SUCCESSFUL" in out
print("\n   The bound is 3 steps. Longer runs need an argument CBMC does not make by itself:")
print("   an invariant (Thursday), or a monitor that checks every step at run time (session 15).")
