"""Session 11 -- temporal properties over agent LOGS: runtime monitoring.

A model checker judges every infinite run of a MODEL. A runtime monitor
judges the one FINITE log of what an agent actually did, so far. Same
formulas, a weaker question -- and three possible answers:

  VIOLATED      a bad prefix has happened; no continuation can repair it
  SATISFIED     a good prefix has happened; no continuation can undo it
  INCONCLUSIVE  the log so far can still go either way

What each kind of property can ever say on a finite log:

  G (del -> approved)     safety     VIOLATED or INCONCLUSIVE -- never SATISFIED:
                                     a later step could still break it.
  F report                liveness   SATISFIED or INCONCLUSIVE -- never VIOLATED:
                                     the report could still come. (A liveness
                                     property a good prefix settles.)
  G (ask -> F answered)   liveness   INCONCLUSIVE on EVERY finite log. Any log
                                     extends to one that answers every ask, and
                                     to one that never answers again.

Each log entry is the set of propositions true at that step: the agent of
03/04_agent_approval_*.smv, plus two log events the model does not have --
`answered` (a human replied) and `report` (the agent reported back).

Expected: the assertions at the bottom hold.
"""

VIOLATED, SATISFIED, INCONCLUSIVE = "VIOLATED", "SATISFIED", "INCONCLUSIVE"


def never_unapproved_delete(log):
    """G (del -> approved): stop at the first bad step."""
    for i, step in enumerate(log):
        if "del" in step and "approved" not in step:
            return VIOLATED, f"step {i}: delete with no approval"
    return INCONCLUSIVE, "no violation yet -- not a proof"


def eventually(log, p):
    """F p: stop at the first good step."""
    for i, step in enumerate(log):
        if p in step:
            return SATISFIED, f"step {i}: {p}"
    return INCONCLUSIVE, f"no {p} yet"


def every_ask_answered(log):
    """G (ask -> F answered): never decided. Report what is still owed."""
    owed = [i for i, step in enumerate(log)
            if "ask" in step and not any("answered" in later for later in log[i + 1:])]
    return INCONCLUSIVE, f"asks still unanswered at the end of the log: {owed}"


# Three logs. "answered" marks the step right after a human replied.
CLEAN   = [{"plan"}, {"ask"}, {"del", "approved", "answered"}, {"done"},
           {"plan"}, {"ask"}, {"abort", "answered"}, {"done"}, {"report"}]
SHORTCUT = [{"plan"}, {"del"}, {"done"}, {"report"}]
WAITING = [{"plan"}, {"ask"}]

PROPERTIES = [("G (del -> approved)", never_unapproved_delete),
              ("F report", lambda log: eventually(log, "report")),
              ("G (ask -> F answered)", every_ask_answered)]

results = {}
for name, log in [("CLEAN", CLEAN), ("SHORTCUT", SHORTCUT), ("WAITING", WAITING)]:
    print(f"{name}  ({len(log)} steps)")
    for prop, monitor in PROPERTIES:
        verdict, why = monitor(log)
        results[name, prop] = verdict
        print(f"  {prop:24} {verdict:13} {why}")
    print()

# The safety monitor refutes the shortcut, and cannot certify the clean log.
assert results["SHORTCUT", "G (del -> approved)"] == VIOLATED
assert results["CLEAN", "G (del -> approved)"] == INCONCLUSIVE
# The guarantee is settled by a good prefix -- and only by one.
assert results["CLEAN", "F report"] == SATISFIED
assert results["WAITING", "F report"] == INCONCLUSIVE
# The response property is never decided on a finite log, however it looks.
assert all(results[name, "G (ask -> F answered)"] == INCONCLUSIVE
           for name in ("CLEAN", "SHORTCUT", "WAITING"))
assert every_ask_answered(WAITING)[1].endswith("[1]")
print("ok -- on a finite log, safety can only fail, F report can only succeed, "
      "and a response property can do neither")
