"""Session 24 -- the eps frontier, and branch and bound: what completeness costs.

Binary search on eps gives each method's largest provable radius: IBP 0.04, CROWN 0.125, the truth
0.2. An incomplete method's frontier is a LOWER bound on the true robust radius. Branch and bound
recovers the rest: CROWN the box; if it cannot verify, split the box in two and try each half. At
eps = 0.15 one split suffices (3 boxes); at 0.25 a box centre is a real counterexample. alpha-CROWN
optimises CROWN's lower slopes; on this toy it finds nothing better than CROWN (HW5 Part 4 shows
a network where it does).

Expected: the assertions at the bottom hold.
"""
import nnv

f_ibp, f_crown = nnv.frontier(nnv.ibp), nnv.frontier(nnv.crown)
f_true = nnv.frontier(lambda e: nnv.exact(e)[0])
print(f"largest eps proved:  IBP {f_ibp:.3f}   CROWN {f_crown:.3f}   true robust radius {f_true:.3f}")
assert abs(f_ibp - 0.04) < 1e-6 and abs(f_crown - 0.125) < 1e-6 and abs(f_true - 0.2) < 1e-6

print("\nbranch and bound (CROWN on each box, split the ones it cannot verify):")
for eps in (0.15, 0.25):
    verdict, boxes, cex = nnv.bab(eps)
    extra = f"   counterexample {cex.round(3).tolist()}, margin {nnv.margin(cex):+.2f}" if cex is not None else ""
    print(f"  eps {eps:.2f}: {verdict} after {boxes} box(es){extra}")
assert nnv.bab(0.15)[:2] == ("verified", 3)
v, _, cex = nnv.bab(0.25)
assert v == "falsified" and nnv.margin(cex) <= 0

a = nnv.lirpa("alpha-CROWN", 0.15)
print(f"\nalpha-CROWN at eps 0.15: {a:+.2f} (CROWN {nnv.crown(0.15):+.2f}) -- no gain on this network")
assert abs(a - nnv.crown(0.15)) < 1e-6
print("incomplete methods give a lower bound on the radius; splitting buys back the rest, at a cost")
