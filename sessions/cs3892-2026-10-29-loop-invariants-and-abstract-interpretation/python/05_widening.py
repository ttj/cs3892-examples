# FIGURE: figures/count100.svg   (the loop, drawn -- scripts/draw_models.py)
"""Session 18 -- a loop needs a fixpoint, and widening makes it arrive.

    i := 0;  while (i < 100) i := i + 1

At the loop head the analysis joins "first arrival" with "after one more iteration"
until nothing changes -- session 16's Reach_{k+1} = Reach_k U Post(Reach_k), on
intervals. Plain join climbs [0,0], [0,1], ..., [0,100]: 101 rounds here, and for a loop
with no bound in the code it would never stop. Widening jumps any bound that moved to
infinity: [0,0], [0,1], then [0,+inf), and the fixpoint is reached. The price is
precision: after the loop, i >= 100 gives [100, +inf). One narrowing step (re-running
the loop body once from the widened head, with a plain join) gives back [0, 100] at
the head and exactly 100 after the loop.

Expected: the assertions at the bottom hold.
"""
from absint import Analysis, Intervals, show

loop = ("while", ("<", ("var", "i"), ("const", 100)), ("assign", "i", ("+", ("var", "i"), ("const", 1))))
init = {"i": (0, 0)}

plain_trace = []
plain = Analysis(Intervals(), trace=plain_trace)
exit_plain = plain.run(loop, init)
print("plain join:   loop head %s ... %s   (%d rounds)   after the loop: i = %s"
      % (plain_trace[0]["i"], plain_trace[-1]["i"], plain.iterations, show(exit_plain["i"])))

wide_trace = []
wide = Analysis(Intervals(), widen_after=1, trace=wide_trace)
exit_wide = wide.run(loop, init)
print("widening:     loop head %s   (%d rounds)   after the loop: i = %s"
      % (", ".join(t["i"] for t in wide_trace), wide.iterations, show(exit_wide["i"])))

# one narrowing step: from the widened head, run the body once and join with the entry
I = Intervals()
head_w = (0, float("inf"))
A = Analysis(I)
body_out = A.run(loop[2], A.branch(loop[1], {"i": head_w}, True))
head_n = {"i": I.join(init["i"], body_out["i"])}
exit_n = A.branch(loop[1], head_n, False)
print("narrowing:    loop head %s   after the loop: i = %s" % (show(head_n["i"]), show(exit_n["i"])))

assert plain.iterations == 101 and exit_plain["i"] == (100, 100)       # [0,0] .. [0,100]
assert wide.iterations <= 3 and exit_wide["i"] == (100, float("inf"))
assert head_n["i"] == (0, 100) and exit_n["i"] == (100, 100)
