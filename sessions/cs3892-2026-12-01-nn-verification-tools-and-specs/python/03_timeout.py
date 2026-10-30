"""Session 25 -- "timeout" and "unknown" prove nothing, and both depend on the budget.

The same query, three budgets. The MILP with a time limit of 0 seconds stops before it starts:
"timeout". Branch and bound with a budget of 2 boxes cannot finish: "unknown". Given time, both
reach the true answer. The network did not change -- only the budget -- so neither answer is
evidence about the network.

Expected: the assertions at the bottom hold.
"""
import numpy as np

import milp
import toy


def bab_budget(eps, x0, max_boxes):
    todo, used = [(x0 - eps, x0 + eps)], 0
    while todo:
        if used == max_boxes:
            return "unknown (budget spent)", used
        lo, hi = todo.pop()
        used += 1
        if toy.crown(None, lo=lo, hi=hi) > 0:
            continue
        mid = (lo + hi) / 2
        if toy.margin(mid) <= 0:
            return "falsified", used
        j = int(np.argmax(hi - lo))
        a, b = hi.copy(), lo.copy()
        a[j] = b[j] = mid[j]
        todo += [(lo, a), (b, hi)]
    return "verified", used


x0, eps = np.array([0.6, 0.5]), 0.16
print(f"query: x0 {x0.tolist()}, eps {eps}")
t0 = milp.verify(x0, eps, time_limit=0.0)[0]
t1 = milp.verify(x0, eps)
print(f"  MILP, 0 s           : {t0}")
print(f"  MILP, no limit      : {t1[0]} (min margin {t1[1]:+.2f})")
b2, b_all = bab_budget(eps, x0, 2), bab_budget(eps, x0, 10_000)
print(f"  BaB, 2 boxes        : {b2[0]}")
print(f"  BaB, unlimited      : {b_all[0]} after {b_all[1]} boxes")
assert t0 == "timeout" and t1[0] == "verified"
assert b2[0].startswith("unknown") and b_all[0] == "verified"
print("timeout and unknown are statements about the budget, not about the network")
