"""Session 25 -- two verifiers on the same 25 queries: CROWN (incomplete) and an exact MILP (complete).

CROWN answers "verified" or "unknown"; the MILP answers "verified" or "falsified" (with an input).
Cross-tabulate them. Three cells are expected: both verify; CROWN unknown and the MILP verifies (an
incompleteness: CROWN's relaxation was too loose); CROWN unknown and the MILP falsifies (a real
counterexample). The fourth cell -- CROWN verified, MILP falsified -- must be EMPTY: a sound method
never verifies a false property, so an entry there means one of the two tools is wrong. The bounds
must also nest: CROWN's lower bound can never exceed the MILP's true minimum.

Expected: the assertions at the bottom hold.
"""
from collections import Counter

import milp
import toy
from queries import QUERIES

table = Counter()
for x0, eps in QUERIES:
    c = toy.crown(eps, x0)
    v, m, _ = milp.verify(x0, eps)
    assert abs(m - toy.exact(eps, x0)[0]) < 1e-6           # the MILP is exact
    assert c <= m + 1e-9, (x0, eps, c, m)                   # CROWN's bound is below the truth
    table[("verified" if c > 0 else "unknown", v)] += 1
print(f"{'':>22}  MILP verified   MILP falsified")
for cr in ("verified", "unknown"):
    print(f"  CROWN {cr:<14}  {table[(cr, 'verified')]:>13}   {table[(cr, 'falsified')]:>14}")
print(f"\n  {sum(table.values())} queries; CROWN verified + MILP falsified: {table[('verified', 'falsified')]}")
assert sum(table.values()) == 25
assert table[("verified", "falsified")] == 0
assert table[("unknown", "verified")] > 0 and table[("unknown", "falsified")] > 0
print("no unsound disagreement: CROWN never verifies what the MILP falsifies")
