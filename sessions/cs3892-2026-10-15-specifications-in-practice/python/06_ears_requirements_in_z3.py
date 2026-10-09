"""Session 15 -- requirements, before any code: can they all hold at once?

Spec-driven development (Kiro, GitHub Spec Kit) has the agent write a
specification first. Kiro writes acceptance criteria in EARS, a set of sentence
templates from Rolls-Royce (Mavin et al., 2009):

    The <system> shall <response>                      ubiquitous
    While <state>, the <system> shall <response>       state-driven
    When <trigger>, the <system> shall <response>      event-driven
    If <trigger>, then the <system> shall <response>   unwanted behaviour

Kiro's requirements analysis turns each sentence into an implication --
the When / While / If part is the antecedent, the "shall" part the consequent --
and asks an SMT solver two questions before design starts:

    CONFLICT       is there a situation in which no response satisfies them all?
    COMPLETENESS   is there a situation that no requirement says anything about?

THIS FILE IS A TOY of that analysis, on the five requirements Kiro's own post
uses (kiro.dev/blog/deep-spec-analysis, May 2026), then on this session's agent.
Here a "situation" is a truth assignment to the trigger and state variables;
the "responses" are what the system does. The formalization below is ours.

Expected: the assertions at the bottom hold -- including the two conflicting
sets and the gap that the Kiro post reports.
"""

from itertools import combinations, product

from z3 import And, Bool, BoolVal, Implies, Not, Solver, sat


def analyse(inputs, rules):
    """rules: {name: (antecedent, consequent)}. Returns (conflicts, gaps):
    conflicts -- {minimal set of rule names: the smallest situation in which they clash};
    gaps      -- situations in which no CONDITIONAL rule's antecedent holds.
    A situation is written as the list of inputs that are true in it."""
    situations = sorted(product([False, True], repeat=len(inputs)), key=lambda bits: (sum(bits), bits[::-1]))

    def formula(bits):
        return And(*[v if b else Not(v) for v, b in zip(inputs, bits)])

    def describe(bits):
        return ", ".join(str(v) for v, b in zip(inputs, bits) if b) or "nothing at all"

    def holds(*fs):
        s = Solver()
        s.add(*fs)
        return s.check() == sat

    conflicts = {}
    for k in range(1, len(rules) + 1):                    # smallest sets first, so they are minimal
        for names in combinations(sorted(rules), k):
            if any(set(c) <= set(names) for c in conflicts):
                continue
            for bits in situations:
                if not holds(formula(bits), *[Implies(*rules[n]) for n in names]):
                    conflicts[names] = describe(bits)
                    break
    gaps = [describe(bits) for bits in situations
            if not any(ante is not TRUE and holds(formula(bits), ante) for ante, _ in rules.values())]
    return conflicts, gaps


TRUE = BoolVal(True)

# --- 1. The five requirements in the Kiro post ---------------------------------
#  (condensed from the post; see it for the full sentences)
#  R1. WHEN an order is submitted AND inventory is available  -> fulfill it
#  R2. WHEN an order is submitted AND inventory is not available -> backorder it
#  R3. THE Order System SHALL NOT backorder any order
#  R4. WHEN an order is canceled -> refund its payments
#  R5. WHILE an order is canceled-and-refunded -> do NOT fulfill it
submitted, inventory, canceled, refunded_state = (Bool("order_submitted"), Bool("inventory_available"),
                                                  Bool("order_canceled"), Bool("canceled_and_refunded"))
fulfill, backorder, refund = Bool("fulfill"), Bool("backorder"), Bool("refund")
ORDER = {
    "R1": (And(submitted, inventory), fulfill),
    "R2": (And(submitted, Not(inventory)), backorder),
    "R3": (TRUE, Not(backorder)),
    "R4": (canceled, refund),
    "R5": (refunded_state, Not(fulfill)),
}
conflicts, gaps = analyse([submitted, inventory, canceled, refunded_state], ORDER)
print("1. The Order System (five EARS requirements from the Kiro post)")
for names, where in conflicts.items():
    print("   CONFLICT  {%s}   when the true inputs are: %s" % (", ".join(names), where))
for g in gaps:
    print("   GAP       no conditional requirement applies when the true inputs are: %s" % g)
assert conflicts == {("R2", "R3"): "order_submitted",
                     ("R1", "R5"): "order_submitted, inventory_available, canceled_and_refunded"}, conflicts
assert gaps == ["nothing at all", "inventory_available"], gaps        # not submitted, not canceled, not refunded
print("   -> the same two sets, and the same gap, that the post reports\n")

# --- 2. This session's agent ----------------------------------------------------
#  A1. WHEN a delete is requested AND an approval is in force,
#      THE Gateway SHALL allow the delete.
#  A2. WHEN a delete is requested AND it names more than 100 files,
#      THE Gateway SHALL deny the delete.
#  A3. THE Gateway SHALL NOT both allow and deny a request.
requested, approved, big = Bool("delete_requested"), Bool("approval_in_force"), Bool("more_than_100_files")
allow, deny = Bool("allow"), Bool("deny")
AGENT = {
    "A1": (And(requested, approved), allow),
    "A2": (And(requested, big), deny),
    "A3": (TRUE, Not(And(allow, deny))),
}
conflicts, gaps = analyse([requested, approved, big], AGENT)
print("2. The gateway for the agent's delete tool")
for names, where in conflicts.items():
    print("   CONFLICT  {%s}   when the true inputs are: %s" % (", ".join(names), where))
unanswered = [g for g in gaps if g.startswith("delete_requested")]
for g in unanswered:
    print("   GAP       nothing is said when the true inputs are: %s" % g)
assert conflicts == {("A1", "A2", "A3"): "delete_requested, approval_in_force, more_than_100_files"}
assert unanswered == ["delete_requested"], gaps
print("   -> an approved delete of 101 files must be allowed AND denied;")
print("      an unapproved small delete is not mentioned at all.")
print("      Cedar settles both by convention: forbid overrides permit, and default deny.\n")

# --- 3. And the logic these sentences leave open --------------------------------
print("3. 'WHEN approval is granted, THE Agent SHALL carry out the delete.'")
print("   In the next step, or eventually?  G (yes -> X del)  or  G (yes -> F del)")
print("   The template does not say. An implication over one situation, as above,")
print("   cannot say it either: that needs a temporal logic.")
