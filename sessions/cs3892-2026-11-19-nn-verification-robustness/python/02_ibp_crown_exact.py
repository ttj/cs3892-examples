"""Session 24 -- three answers to one query: IBP, CROWN, and the exact minimum margin.

IBP pushes the input box through layer by layer and forgets that h1 and h2 move together, so it
loses even when every neuron is stable (eps = 0.05). CROWN replaces each unstable ReLU by lines
and keeps the margin as a LINEAR function of x, whose minimum over a box is exact. Both are SOUND:
a positive lower bound proves robustness. Neither is COMPLETE: a negative bound means "unknown",
not "not robust". The exact minimum (vertex enumeration, possible in 2-D) is the truth.
nnv.py's hand-written IBP and CROWN agree with auto_LiRPA's to 1e-9.

Expected: the assertions at the bottom hold.
"""
import nnv

print(f"{'eps':>5} {'IBP':>7} {'CROWN':>7} {'exact':>7}   worst input    verdicts (IBP / CROWN / exact)")
rows = {}
for eps in (0.05, 0.10, 0.15, 0.25):
    i, c, (e, worst) = nnv.ibp(eps), nnv.crown(eps), nnv.exact(eps)
    v = lambda b: "verified" if b > 0 else "unknown"
    verdict = (v(i), v(c), "verified" if e > 0 else "falsified")
    rows[eps] = verdict
    print(f"{eps:5.2f} {i:+7.2f} {c:+7.2f} {e:+7.2f}   {worst.round(2).tolist()}   {' / '.join(verdict)}")
    assert abs(nnv.lirpa("IBP", eps) - i) < 1e-9 and abs(nnv.lirpa("CROWN", eps) - c) < 1e-9
assert rows[0.05] == ("unknown", "verified", "verified")       # IBP loses, CROWN proves
assert rows[0.15] == ("unknown", "unknown", "verified")        # both incomplete; it IS robust
assert rows[0.25] == ("unknown", "unknown", "falsified")       # a real counterexample
print("\nhand-written IBP and CROWN = auto_LiRPA's; sound but incomplete; the exact answer decides")
