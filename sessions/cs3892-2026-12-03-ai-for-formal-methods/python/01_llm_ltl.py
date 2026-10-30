# FIGURE: figures/counter.svg   (the running counter, drawn -- scripts/draw_models.py)
"""Session 26 -- autoformalization: an LLM turns four English requirements into LTL; NuSMV judges.

Claude Haiku 4.5 got the prompt in llm/ltl_prompt.txt (the running counter's NuSMV model and four
English requirements; see llm/run.md). Three checks, each catching something the previous misses:

  1. SYNTAX: the lines as written. Every one ends in a // comment, and NuSMV comments start with --,
     so NuSMV rejects the file.
  2. TRUTH on the system: with the comments removed, all four formulas hold on the counter -- and so
     do the four reference formulas. A model check cannot tell them apart.
  3. MEANING: is each the SAME property as the reference? On a free model (x takes any value at any
     step) LTLSPEC (llm <-> reference) holds exactly when the two agree on every run. R1-R3 agree.
     R4 does not: "reaches 10 only after it has been 5" was read as weak precedence, which a run
     that never reaches 5 (or 10) satisfies; the reference reads it as strong until, which that run
     violates. The English was ambiguous. NuSMV's counterexample is such a run.

Expected: the assertions at the bottom hold.
"""
import re

import nusmv

REPLY = (nusmv.HERE.parent / "llm" / "ltl_response.txt").read_text()
lines = [l.strip() for l in REPLY.splitlines() if l.strip().startswith("LTLSPEC")]
assert len(lines) == 4, lines
REFERENCE = ["G (x <= 10)", "G (x = 10 -> X x = 0)", "G F (x = 0)", "!(x = 10) U (x = 5)"]
counter = (nusmv.SMV / "counter.smv").read_text()
free = (nusmv.SMV / "free.smv").read_text()

print("1. The four lines as the model wrote them:")
for l in lines:
    print("   " + l)
out = nusmv.run(counter + "".join(f"  {l}\n" for l in lines))
err = [l for l in out.splitlines() if "syntax error" in l][0]
print("   NuSMV: " + re.sub(r"^file \S+: ", "", err))
assert "syntax error" in err and all("//" in l for l in lines)

llm = [re.sub(r"\s*//.*$", "", l)[len("LTLSPEC"):].strip().rstrip(";") for l in lines]
print("\n2. Comments removed; true on the running counter?")
v = nusmv.verdicts(nusmv.run(counter + "".join(f"  LTLSPEC {f}\n" for f in llm + REFERENCE)))
for (f, ok), name in zip(v, [f"R{i} llm" for i in range(1, 5)] + [f"R{i} ref" for i in range(1, 5)]):
    print(f"   {name}: {ok:5}  {f}")
assert [ok for _, ok in v] == ["true"] * 8

print("\n3. The same property as the reference? (LTLSPEC llm <-> ref, on the free model)")
out = nusmv.run(free + "".join(f"  LTLSPEC ({a}) <-> ({b})\n" for a, b in zip(llm, REFERENCE)))
v = nusmv.verdicts(out)
for i, (f, ok) in enumerate(v, 1):
    print(f"   R{i}: {'same' if ok == 'true' else 'DIFFERENT'}")
assert [ok for _, ok in v] == ["true", "true", "true", "false"]
trace = out.split("Trace Type: Counterexample", 1)[1]
xs = re.findall(r"x = (\d+)", trace)
vals = sorted({int(v) for v in xs})
print(f"   R4 counterexample: a lasso whose x values are {vals} -- never 5, never 10: the")
print("   model's formula accepts it, the reference rejects it")
assert "Loop starts here" in trace and vals and 5 not in vals and 10 not in vals
print("\nsyntax, truth and meaning are three different checks; only the third caught R4")
