"""HW1 part 2 -- the timing harness. Run it, widen the range, report the wall.

The deliverable for part 2 is not "it got slow". It is a table plus one
sentence saying WHERE it stops finishing and why the encoding makes that
happen. This gives you the table.
"""

import time
from p2_nqueens import nqueens
from p2_pigeonhole import pigeonhole


def timed(build, label, sizes, budget_s=10.0):
    print(f"\n{label}")
    print(f"  {'size':>6}  {'result':>8}  {'seconds':>9}  clauses")
    for n in sizes:
        s = build(n)
        n_asserts = len(s.assertions())
        t0 = time.perf_counter()
        r = s.check()
        dt = time.perf_counter() - t0
        print(f"  {n:>6}  {str(r):>8}  {dt:>9.3f}  {n_asserts}")
        if dt > budget_s:
            print(f"  -- stopped: past the {budget_s:.0f}s budget. This is the wall.")
            break


if __name__ == "__main__":
    # Deliberately small so this finishes in CI. WIDEN THESE for your report.
    timed(nqueens, "n-queens (integer encoding)", range(4, 11))
    timed(lambda n: pigeonhole(n + 1, n), "pigeonhole n+1 into n (boolean encoding)",
          range(4, 9))
    print("\nFor the report: push each range until it stops finishing, and say "
          "which encoding hit the wall first and why.")
