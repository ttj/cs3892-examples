"""Session 26 -- LLM proof search with Lean as the judge: two confident answers, two exact rejections.

Claude Haiku 4.5 was asked to prove 2 * sumTo n = n * (n + 1) in core Lean 4.33.0, no Mathlib
(llm/run.md). Round 1 used `mul_add` -- a Mathlib name, which the prompt ruled out -- and Lean says
exactly that. Round 2 got the task, its first answer and Lean's error, and dropped the rewrite for
`omega`; Lean says omega cannot prove the goal, and its message shows why: n * (n + 1) and
(n + 1) * (n + 1 + 1) are opaque atoms to a LINEAR arithmetic procedure. Two rounds, as HW4 Part 5
allows; the session stops there. The proof in lean/S26/Sum.lean (grind) is accepted, with Lean's
standard axioms. Lean decides, every time, whatever the model claims.

Expected: the assertions at the bottom hold.
"""
import re

from lean_cli import LEAN_DIR, messages, show

LLM = LEAN_DIR.parent / "llm"


def lean_file(reply):
    m = re.search(r"```(?:lean)?\n(.*?)```", reply, re.S)
    return m.group(1) if m else reply


verdicts = []
for rnd in (1, 2):
    src = lean_file((LLM / f"lean_response_round{rnd}.txt").read_text())
    rc, ms = messages(f"S26/Round{rnd}.lean", src)
    errs = [t for sev, t in ms if sev == "error"]
    print(f"round {rnd}: the model's proof")
    print("   " + src.strip().replace("\n", "\n   "))
    print(f"   Lean: {'accepted' if rc == 0 and not errs else 'REJECTED'}")
    for e in errs:
        print("   " + e.split("\n")[0])
    saved = (LLM / f"lean_check_round{rnd}.txt").read_text()
    assert errs and errs[0].split("\n")[0] in saved, (errs, saved)   # the same verdict as the saved run
    verdicts.append(errs[0])
assert "Unknown identifier `mul_add`" in verdicts[0]
assert "omega could not prove the goal" in verdicts[1] and "↑(n + 1) * ↑(n + 1 + 1)" in verdicts[1]

print("\na proof Lean accepts (lean/S26/Sum.lean):")
show("S26/Sum.lean", "sum")
rc, ms = messages("S26/Sum.lean")
print("Lean says:\n  " + "\n  ".join(t for _, t in ms))
assert rc == 0 and [t for _, t in ms] == ["'S26.two_sumTo' depends on axioms: [propext, Classical.choice, Quot.sound]"]
print("\ntwo rounds, two rejections, each naming the exact problem; the checker, not the model, decides")
