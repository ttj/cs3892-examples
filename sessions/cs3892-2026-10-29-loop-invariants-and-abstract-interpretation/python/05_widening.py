# FIGURE: figures/counter.svg   (the running counter, drawn -- scripts/draw_models.py)
"""Session 18 -- the running counter, analysed with intervals: plain join, widening, narrowing.

    x := 0;  while (*) { if (x < 10) x := x + 1 else x := 0 }

At the loop head the analysis joins "first arrival" with "after one more iteration" until
nothing changes -- session 16's Reach_{k+1} = Reach_k U Post(Reach_k), on intervals instead
of BDDs. Plain join climbs [0,0], [0,1], ..., [0,10] and stops: 11 rounds, the same count as
the BDD fixpoint, because the code itself caps x. (A loop whose bound is not in the code would
climb forever.) Widening jumps a bound that moved to infinity: [0,0], [0,1], then [0,+inf) --
fast, and it loses x <= 10. One narrowing step (re-run the body once from the widened head,
with a plain join) gives back [0, 10]: the invariant you wrote by hand in session 9, found by
the tool.

Expected: the assertions at the bottom hold.
"""
from absint import Analysis, Intervals, show

V, K = (lambda x: ("var", x)), (lambda n: ("const", n))
body = ("if", ("<", V("x"), K(10)), ("assign", "x", ("+", V("x"), K(1))), ("assign", "x", K(0)))
loop = ("while", ("nondet",), body)
init = {"x": (0, 0)}

plain_trace = []
plain = Analysis(Intervals(), trace=plain_trace)
head_plain = plain.run(loop, init)
print("plain join:   loop head %s ... %s   (%d rounds)   x is in %s"
      % (plain_trace[0]["x"], plain_trace[-1]["x"], plain.iterations, show(head_plain["x"])))

wide_trace = []
wide = Analysis(Intervals(), widen_after=1, trace=wide_trace)
head_wide = wide.run(loop, init)
print("widening:     loop head %s   (%d rounds)   x is in %s"
      % (", ".join(t["x"] for t in wide_trace), wide.iterations, show(head_wide["x"])))

I = Intervals()
A = Analysis(I)
after_body = A.run(body, {"x": head_wide["x"]})
head_narrow = {"x": I.join(init["x"], after_body["x"])}
print("narrowing:    one more pass from %s gives %s -- so x <= 10 on every run"
      % (show(head_wide["x"]), show(head_narrow["x"])))

assert plain.iterations == 11 and head_plain["x"] == (0, 10)          # Reach_0 .. Reach_10, as in session 16
assert wide.iterations <= 3 and head_wide["x"] == (0, float("inf"))   # widening lost the bound
assert head_narrow["x"] == (0, 10)                                    # narrowing got it back
