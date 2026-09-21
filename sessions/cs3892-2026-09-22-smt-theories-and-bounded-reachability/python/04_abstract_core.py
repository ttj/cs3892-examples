"""Session 8, demo 4 -- the abstract boolean unsat core he offered in class.

Thursday's core example was the leave policy, which carries meaning with it.
He offered a version with no meaning at all, so the mechanism is visible:

    a, b, c, d       four independent booleans
    five assertions, of which only THREE are the reason for unsat

An unsat core is a subset of the assertions that is ALREADY unsatisfiable.
It is the solver telling you which of your assumptions to go and look at --
the other two are innocent bystanders and the core leaves them out.
"""

from z3 import Bool, Implies, Not, Solver, unsat

a, b, c, d = Bool("a"), Bool("b"), Bool("c"), Bool("d")

ASSERTIONS = {
    "A1": a,                       # a holds                     <-- in the core
    "A2": Implies(a, b),           # a forces b                  <-- in the core
    "A3": Not(b),                  # but b does not hold         <-- in the core
    "A4": Implies(c, d),           # nothing to do with it
    "A5": Implies(d, c),           # nothing to do with it
}


def core():
    s = Solver()
    s.set(unsat_core=True)
    for name, f in ASSERTIONS.items():
        s.assert_and_track(f, name)
    result = s.check()
    return result, sorted(str(x) for x in s.unsat_core()) if result == unsat else []


if __name__ == "__main__":
    result, names = core()
    print(f"  check-sat        : {result}")
    print(f"  unsat core       : {names}")
    print(f"  not in the core  : {sorted(set(ASSERTIONS) - set(names))}")

    assert result == unsat, "the five assertions must be jointly unsatisfiable"
    assert set(names) == {"A1", "A2", "A3"}, f"expected A1-A3, got {names}"
    print("\n  Five assertions in, three come back. A1-A3 are already")
    print("  unsatisfiable on their own: a holds, a forces b, b does not hold.")
    print("  A4 and A5 are perfectly consistent and simply not the reason.")
    print()
    print("  In a real query the assertions are your SPEC. The core is the")
    print("  answer to 'which requirements contradict each other?', which is")
    print("  a far more useful thing to be handed than the word `unsat`.")
