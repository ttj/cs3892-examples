# FIGURE: figures/agent_c.svg   (session 11's agent as a C program, drawn -- scripts/draw_models.py)
"""Session 18 -- inside CBMC: the four forms a C program takes on its way to a verdict.

The program is c/agent.c, session 11's agent written in C (session 17). Each step the model
picks an action -- 0 plan, 1 ask the human, 2 delete -- and CBMC may choose it freely; asking
sets `approved` from the human's answer, another free choice. The property: assert(approved)
before every delete. The shortcut (delete without asking) breaks it.

  1. goto-cc compiles C to a GOTO program: a control-flow graph in which loops and ifs are
     IF ... THEN GOTO, and assume/assert are instructions.  (goto-instrument --show-goto-functions)
  2. Symbolic execution unwinds the loop k times and gives every assignment a fresh name:
     static single assignment (SSA) equations.  (cbmc --show-vcc)
  3. The equations, the assumptions and the NEGATED property become one formula over 32-bit
     bit-vectors. CBMC can write it in SMT-LIB: each input is a declare-fun, each branch an
     ite, then (check-sat).  (cbmc --smt2 --outfile)
  4. A solver answers. We run Z3 on CBMC's own file: sat, and the model's values for the
     inputs ARE the counterexample. Replaying them through the C semantics breaks the
     assertion, as cbmc --trace reports.

Expected: the assertions at the bottom hold.
"""
import re
import tempfile
from pathlib import Path

import z3

from cbmc_cli import run

C = Path(__file__).resolve().parent.parent / "c"
AGENT = C / "agent.c"
work = Path(tempfile.mkdtemp())


def short(s):
    s = re.sub(r"main::\$tmp::return_value_nondet_int(\$0)?", lambda m: "answer_in" if m.group(1) else "action_in", s)
    s = re.sub(r"main::(?:\d+::)*(\w+)", r"\1", s)
    return s.replace("goto_symex::\\guard#", "g")


# The C column of the slide's table: each construct as it appears in agent.c.
src = AGENT.read_text()
assert all(c in src for c in ("action = nondet_int();", "assume(0 <= action && action <= 2)",
                              "if (action == 2)", "assert(approved);"))

# --- 1. the GOTO program --------------------------------------------------------------------
run("goto-cc", AGENT, "-o", work / "agent.gb")
goto = run("goto-instrument", "--show-goto-functions", work / "agent.gb")
body = goto[goto.index("main /* main */"):]
body = body[:body.index("END_FUNCTION")]
keep = [short(l.rstrip()) for l in body.splitlines()
        if re.search(r"\b(IF|GOTO|ASSUME|ASSERT|ASSIGN)\b", l) and "return_value" not in l.split(":=")[0]
        and "SET RETURN" not in l]
print("1. GOTO program for main (goto-instrument --show-goto-functions; names shortened)")
print("\n".join("   " + l.strip() for l in keep))
assert any(l.strip().startswith("1: IF ¬(step < 3) THEN GOTO 5") for l in keep)
assert any("ASSUME 0 ≤ action ∧ action ≤ 2" in l for l in keep) and any("action := action_in" in l for l in keep)
assert any("ASSERT approved ≠ 0" in l for l in keep) and any(l.strip() == "GOTO 1" for l in keep)

# --- 2. SSA equations ----------------------------------------------------------------------------
vcc = run("cbmc", AGENT, "--unwind", 4, "--property", "main.assertion.1", "--show-vcc")
body = vcc[vcc.index("VERIFICATION CONDITIONS"):]
eqs = []
for l in body.splitlines():
    l = re.sub(r"^\{-?\d+\}\s*", "", l).strip()
    if re.search(r"main::|guard#|nondet", l) and "CPROVER" not in l:
        l = re.sub(r"main::\$tmp::return_value_nondet_int(\$0)?!0@(\d)#\d+", lambda m: ("answer" if m.group(1) else "action") + "_in" + m.group(2), l)
        l = re.sub(r"main::(?:\d+::)*(\w+)!0@(\d)#(\d+)", r"\1@\2_\3", l)
        l = re.sub(r'nondet_symbol identifier="symex::(nondet\d+)"', r"\1", l)
        eqs.append(l.replace("goto_symex::\\guard#", "g").replace("nondet_symex::", ""))
print("\n2. SSA equations, first iteration (cbmc --unwind 4 --property main.assertion.1 --show-vcc)")
print("\n".join("   " + l for l in eqs[:8]))
print("   ... %d equations in all; step 1's delete branch: %s" % (len(eqs), next(e for e in eqs if e.startswith("g2 "))))
assert "approved@1_2 = 0" in eqs and "action_in1 = nondet0" in eqs and "action@1_2 = action_in1" in eqs
assert "action@1_2 ≥ 0 ∧ ¬(action@1_2 ≥ 3)" in eqs and "g2 ⇔ (action@1_2 = 2)" in eqs

# --- 3. the SMT-LIB formula CBMC writes ------------------------------------------------------------
smt = work / "agent.smt2"
run("cbmc", AGENT, "--unwind", 4, "--property", "main.assertion.1", "--smt2", "--outfile", smt)
text = smt.read_text()
lines = [l for l in text.splitlines() if l and not l.startswith(";")]
counts = {k: sum(1 for l in lines if l.startswith("(" + k)) for k in ("declare-fun", "define-fun", "assert")}
logic = next(l for l in lines if l.startswith("(set-logic"))
inputs = sorted({m for m in re.findall(r"\|nondet_symex::(nondet\d+)\|", text)}, key=lambda s: int(s[6:]))
pick = []
for pat in (r"\(declare-fun \|nondet_symex::nondet0\|", r"\(define-fun \|main::1::1::1::action!0@1#2\|",
            r"\(assert \(= \|goto_symex::&92;guard#2\|", r"bvsge \|main::1::1::1::action!0@1#2\| \(_ bv0 32\)\)",
            r"^\(check-sat\)"):
    pick.append(next(l for l in lines if re.search(pat, l)))


def smt_short(l):
    l = re.sub(r"\|main::(?:\d+::)*(\w+)!0@(\d)#(\d+)\|", r"\1@\2_\3", l)
    l = re.sub(r"\|main::\$tmp::return_value_nondet_int(\$0)?!0@(\d)#\d+\|", lambda m: ("answer" if m.group(1) else "action") + "_in" + m.group(2), l)
    return l.replace("|nondet_symex::", "").replace("|goto_symex::&92;guard#", "g").replace("|", "")


print("\n3. SMT-LIB, as CBMC writes it (cbmc ... --smt2 --outfile agent.smt2; names shortened)")
print("   %s   %d declare-fun, %d define-fun, %d assert, %d lines" % (logic, counts["declare-fun"],
      counts["define-fun"], counts["assert"], len(lines)))
print("\n".join("   " + smt_short(l)[:110] for l in pick))
print("   inputs (free variables): " + ", ".join(inputs))
picked = [smt_short(l) for l in pick]
assert "(declare-fun nondet0 () (_ BitVec 32))" in picked and "(assert (= g2 (= action@1_2 (_ bv2 32))))" in picked
assert any("(and (bvsge action@1_2 (_ bv0 32)) (not (bvsge action@1_2 (_ bv3 32))))" in l for l in picked)
assert logic == "(set-logic QF_AUFBV)" and "(_ BitVec 32)" in text and len(inputs) == 6

# the property and its negation: one check per unrolled delete, and "some check fails" asserted
props = [l for l in lines if l.startswith("(define-fun B") and "=>" in l and "approved" in l]
negated = next(l for l in lines if re.match(r"\(assert \(or \(not B\d+\)", l))
print("   the property, step 2's copy: " + smt_short(props[0])[:120])
print("   the negation:                " + negated + "   then (check-sat)")
assert len(props) == 2 and "(not (= approved@1_6 (_ bv0 32)))" in smt_short(props[0])
# B42, B43 are the assumes of steps 1 and 2: a copy of the check only counts on runs that meet them.
assert smt_short(props[0]) == ("(define-fun B52 () Bool (=> (and true B42 B43) (=> (and (not g3) g4) "
                               "(not (= approved@1_6 (_ bv0 32))))))")
assert negated == "(assert (or (not B51) (not B52) (not B53)))"

checks = [re.sub(r"^\{-?\d+\}\s*", "", l).strip() for l in body.splitlines() if l.strip().startswith("{1}")]
ssa_checks = [re.sub(r"goto_symex::\\guard#", "g", re.sub(r"main::(?:\d+::)*(\w+)!0@(\d)#(\d+)", r"\1@\2_\3", c)) for c in checks]
print("   SSA checks: " + " | ".join(ssa_checks[:2]))
assert len(checks) == 3 and "(¬g3 ∧ g4) ⇒ ¬(approved@1_6 = 0)" in ssa_checks

# --- 4. a solver answers ---------------------------------------------------------------------------
s = z3.Solver()
s.add(z3.parse_smt2_file(str(smt)))
verdict = s.check()
m = s.model()
val = {d.name().split("::")[1]: m[d].as_signed_long() for d in m.decls() if d.name().startswith("nondet_symex::")}
print("\n4. Z3 on CBMC's file: %s" % verdict)
print("   model: " + ", ".join("%s = %d" % (k, val[k]) for k in sorted(val, key=lambda s: int(s[6:]))))

# Replay the inputs through the C program: nondet0, nondet1 are step 1's action and answer, etc.
approved, broke = 0, None
for step in range(3):
    action, answer = val.get("nondet%d" % (2 * step), 0), val.get("nondet%d" % (2 * step + 1), 0)
    if action == 1:
        approved = 1 if answer > 0 else 0
    elif action == 2:
        if not approved:
            broke = (step + 1, action, approved)
            break
        approved = 0
print("   replayed: step %d, action = %d (delete) with approved = %d -> assert(approved) fails" % broke)
assert verdict == z3.sat and broke is not None and broke[1] == 2 and broke[2] == 0

trace = run("cbmc", AGENT, "--unwind", 4, "--trace")
assert "assertion approved: FAILURE" in trace
print("   cbmc --trace finds the same kind of run: a delete with approved = 0")
