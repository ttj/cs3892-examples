"""Session 15 -- a per-request authorization policy, and what a solver can say about it.

Cedar (AWS, open source) decides ONE request at a time. A policy is a `permit`
or a `forbid` over a principal, an action and a resource, with an optional
`when` condition over the request. The decision rule is three lines:

    1. if any forbid policy matches the request   -> Deny
    2. else if any permit policy matches          -> Allow
    3. otherwise                                  -> Deny      ("default deny")

There is no state and there are no loops, so a policy set is just a formula
over the fields of one request -- and a solver can answer questions about ALL
requests at once: can anything be allowed? are two versions equivalent?

THIS FILE IS A TOY. It models the decision rule in Z3 over a three-field
request. It is not Cedar: the real analyzer compiles full Cedar policies with a
compiler proved correct in Lean, and it uses the cvc5 solver.

The running example is the agent's delete tool. In Cedar-style syntax:

    permit (principal, action == Action::"delete", resource)
      when { context.input.files <= 100 };

    forbid (principal, action == Action::"delete", resource)
      when { principal.role == "agent" && context.input.files > 10 };

    permit (principal, action == Action::"view", resource);

Expected: the assertions at the bottom hold.
"""

from z3 import (And, BoolVal, Const, EnumSort, Int, Not, Or, Solver, sat, unsat)

Role, (AGENT, ADMIN) = EnumSort("Role", ["agent", "admin"])
Action, (VIEW, DELETE) = EnumSort("Action", ["view", "delete"])
Tier, (GOLD, PLATINUM, NONE) = EnumSort("Tier", ["Gold", "Platinum", "none"])

# One request. Nothing here refers to any EARLIER request: there is nowhere to
# write "after an approval".
role, action, files, tier = Const("role", Role), Const("action", Action), Int("files"), Const("tier", Tier)
WELL_FORMED = files >= 0


def decision(permits, forbids):
    """Cedar's rule: Allow iff some permit matches and no forbid does."""
    return And(Or(*permits) if permits else BoolVal(False),
               Not(Or(*forbids)) if forbids else BoolVal(True))


def some_request(formula):
    """A request satisfying `formula`, or None if there is none."""
    s = Solver()
    s.add(WELL_FORMED, formula)
    return s.model() if s.check() == sat else None


def always(formula):
    """Does `formula` hold for EVERY well-formed request?"""
    return some_request(Not(formula)) is None


def show(m):
    return "role=%s action=%s files=%s" % (m.eval(role, True), m.eval(action, True), m.eval(files, True))


PERMITS = [And(action == DELETE, files <= 100), action == VIEW]
FORBIDS = [And(action == DELETE, role == AGENT, files > 10)]
allow = decision(PERMITS, FORBIDS)

print("1. Default deny: with no policies at all, is any request allowed?")
assert some_request(decision([], [])) is None
print("   no -- nothing is allowed until a permit says so\n")

print("2. Forbid overrides permit.")
both = some_request(And(Or(*PERMITS), Or(*FORBIDS)))
assert both is not None
print("   a request that a permit AND a forbid both match:", show(both))
assert always(Not(And(allow, action == DELETE, role == AGENT, files > 10)))
print("   proved for every request: an agent never deletes more than 10 files\n")

print("3. A policy that can never allow anything (the solver finds the bug).")
#    permit (...) when { principal.tier == "Gold" && principal.tier == "Platinum" };
broken = decision([And(action == DELETE, tier == GOLD, tier == PLATINUM)], [])
assert some_request(broken) is None
print("   tier == Gold && tier == Platinum is unsatisfiable: the permit is dead\n")

print("4. Two versions of the delete permit: are they the same policy?")
v1 = decision([And(action == DELETE, files <= 100)], [])
v2 = decision([And(action == DELETE, files < 100)], [])
diff = some_request(v1 != v2)
assert diff is not None and diff.eval(files).as_long() == 100
print("   not equivalent -- they disagree on:", show(diff))
assert always(Or(Not(v2), v1)) and not always(Or(Not(v1), v2))
print("   v2 implies v1 (v2 is less permissive), and not the other way round\n")

print("5. What the formula cannot say.")
print("   'delete only AFTER a human approved' is about two events, in order.")
print("   A decision here is a function of one request; identical requests get")
print("   identical decisions, whatever happened before. See 02 and 04.")

s = Solver()
s.add(WELL_FORMED, allow, action == DELETE, role == AGENT)
assert s.check() == sat and s.model().eval(files).as_long() <= 10
s.add(files > 10)
assert s.check() == unsat
