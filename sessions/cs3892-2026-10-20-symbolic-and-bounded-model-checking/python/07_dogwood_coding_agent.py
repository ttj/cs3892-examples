# FIGURE: figures/push_monitor.svg   (the monitor rule 2 needs, drawn -- scripts/draw_models.py)
"""Session 16 -- rules for a coding agent in Cedar and Dogwood, run by Dogwood's own interpreter.

Thursday's exercise listed five rules for a coding agent. A gateway can enforce three of them by
refusing calls, and Dogwood can write all three:

  1. never push to main                                  one request: plain Cedar
  2. before a push, the tests must have passed since     a bounded history: `since`
     the last edit
  3. at most three force-pushes an hour                  a bounded history: `count`

Rule 4 ("every pull request it opens is eventually reviewed") is liveness, and rule 5 ("it never
sends a secret it has read to the network") compares pairs of runs. No gateway can enforce
either by refusing calls.

Session 15's 02_history_monitor.py is a forty-line toy of the operator definitions. This file
runs the real `dogwood` CLI instead (v1.1, the reference interpreter, which its authors say is not
for production use) on the files in ../dogwood/:

  coding_agent_v1.dw    rule 2 as first written
  coding_agent.dw       rule 2 fixed
  trace_tests.log       one agent session: edits, test runs, pushes   (rules 1 and 2)
  trace_force.log       a burst of force-pushes                      (rule 3)

Part A replays the session against version 1, and one push gets through that should not.
Part B replays it against version 2. Part C replays the force-pushes. Part D shows what Dogwood
hands to Cedar: each temporal condition becomes one Boolean in the request's context, which a
monitor (the machine in the FIGURE) keeps up to date as events arrive.

Expected: the assertions at the end of each part hold.
"""
import re
import subprocess
from pathlib import Path

from dogwood_cli import dogwood

DIR = Path(__file__).resolve().parent.parent / "dogwood"
SCHEMA = DIR / "coding_agent.cedarschema"
DW = dogwood()
RULES = ["edit_and_test", "tests_passed_since_last_edit", "never_push_to_main",
         "at_most_three_force_pushes_an_hour"]          # the @id of each rule, in file order


def cli(*args):
    r = subprocess.run([DW, *map(str, args)], capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr
    return r.stdout


EVENT = re.compile(r'^@(\d+) .*?Repo::Action::"(\w+)"::(\w+)\(input: \{ ([^}]*) \}(?:, output: \{ ([^}]*) \})?')


def events(trace):
    """(time, action, kind, input, output) for each line of a trace file."""
    out = []
    for line in (DIR / trace).read_text().splitlines():
        t, action, kind, inp, outp = EVENT.match(line).groups()
        out.append((int(t), action, kind, inp, outp or ""))
    return out


def replay(policy, trace):
    """{time: (verdict, rule that decided it)} for every request in the trace."""
    got = {}
    for line in cli("replay", DIR / policy, "--policy-schema", SCHEMA, "--trace", DIR / trace).splitlines():
        m = re.match(r"@(\d+) \(time point \d+\): (ALLOW|DENY)(?:\s+\[rules: (\d+)\])?", line)
        if m:
            got[int(m[1])] = (m[2], RULES[int(m[3])] if m[3] else "no permit matched")
    return got


def table(trace, **runs):
    names = list(runs)
    print("   %-6s %-9s %-9s %-34s" % ("time", "action", "kind", "fields") + "".join("%-8s" % n for n in names))
    for t, action, kind, inp, outp in events(trace):
        fields = ", ".join(x for x in (inp, outp) if x)
        cells = "".join("%-8s" % (runs[n][t][0] if kind == "request" else "") for n in names)
        print("   @%-5d %-9s %-9s %-34s" % (t, action, kind, fields[:34]) + cells)
    print()


cli("validate", DIR / "coding_agent_v1.dw", "--policy-schema", SCHEMA)
cli("validate", DIR / "coding_agent.dw", "--policy-schema", SCHEMA)

# ------------------------------------------------------------------------------
print("A. Rule 2 as first written:  !Edit::response{} since within 24h RunTests::response{ passed: true }\n")
v1 = replay("coding_agent_v1.dw", "trace_tests.log")
v2 = replay("coding_agent.dw", "trace_tests.log")
table("trace_tests.log", v1=v1)
push = {t: v for t, v in v1.items() if t in (60, 240, 300, 420, 720)}
assert push == {60: ("DENY", "no permit matched"),            # edited, never tested
                240: ("DENY", "never_push_to_main"),          # tested, but to main: the forbid wins
                300: ("ALLOW", "tests_passed_since_last_edit"),
                420: ("DENY", "no permit matched"),           # an edit since the passing run
                720: ("ALLOW", "tests_passed_since_last_edit")}, push
print("   @720 is allowed, and the most recent test run (@660) FAILED. Nothing was edited since")
print("   the pass at @540, and that is all version 1 asks. It is true and too weak.\n")

# ------------------------------------------------------------------------------
print("B. Rule 2 fixed: no edit AND no failing run since the pass (two `since`s, as there is no `||`)\n")
table("trace_tests.log", v1=v1, v2=v2)
assert {t: v for t, v in v2.items() if v != v1[t]} == {720: ("DENY", "no permit matched")}
print("   The two versions differ at one request, @720.\n")

# ------------------------------------------------------------------------------
print("C. Rule 3: at most three force-pushes an hour, counting COMPLETED pushes (responses)\n")
force = replay("coding_agent.dw", "trace_force.log")
table("trace_force.log", verdict=force)
assert [force[t][0] for t in (100, 200, 300, 400, 3702, 3800)] == ["ALLOW"] * 3 + ["DENY", "ALLOW", "DENY"]
assert force[400][1] == "at_most_three_force_pushes_an_hour"
print("   @400: three completed force-pushes in the last hour, so the forbid wins over the permit.")
print("   @3702: the push completed at @101 is now 3601 s old, outside the window: two left, allowed.")
print("   @3800: @201, @301 and @3703 are all inside the hour again: refused.\n")

# ------------------------------------------------------------------------------
print("D. What Cedar receives. `dogwood lower` turns each temporal condition into a context field:\n")
lowered = cli("lower", DIR / "coding_agent.dw", "--policy-schema", SCHEMA, "--emit", "cedar-policies")
for line in lowered.splitlines():
    if line.startswith(("permit", "forbid")):
        print("   " + line)
assert "when { context.policy_1__temporal_0 }" in lowered
assert "(context.policy_3__temporal_0)" in lowered
print("\n   The Cedar policies keep no state. Dogwood computes those two Booleans from the history, and")
print("   for rule 2 one bit and one clock are enough to do it: that is the machine in the FIGURE.\n")
print("   `dogwood explain` reads the policy back in English, generated from the syntax tree with no")
print("   language model involved:\n")
english = cli("explain", DIR / "coding_agent.dw", "--policy-schema", SCHEMA)
print("\n".join("   " + l for l in english.splitlines() if l.strip()))
assert "no Edit response has occurred since then" in english
