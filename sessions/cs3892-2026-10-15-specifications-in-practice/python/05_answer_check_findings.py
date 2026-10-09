"""Session 15 -- checking an LLM's ANSWER against rules, with a solver.

Automated Reasoning checks (Amazon Bedrock Guardrails) work in two steps.

    1. TRANSLATE   language models turn the question and the answer into
                   PREMISES and CLAIMS over the policy's variables.
                   AWS: "Because this step uses LLMs, it may contain errors."
    2. VALIDATE    an SMT solver compares premises and claims with the RULES.
                   This step is sound -- if the translation was right.

The rules are written in a subset of SMT-LIB:  =>  and  or  not  =  >  <  >=  <=
over BOOL, INT, NUMBER and enumerated variables.

THIS FILE IS A TOY of step 2 only. The premises and claims below are written by
hand; no language model is called, and nothing here talks to AWS. The policy is
this session's running example -- when may the agent delete files?

    R = the rules     P = the premises     C = the claims

    IMPOSSIBLE    R and P cannot all hold           (checked FIRST -- see part 2)
    VALID         R and P entail C
    INVALID       R and P entail not C
    SATISFIABLE   neither: C may be true or false, depending on facts not given

(The logical reading of each finding is ours. The service has three more
findings, for when translation fails: TRANSLATION_AMBIGUOUS, TOO_COMPLEX,
NO_TRANSLATIONS.)

Expected: the assertions at the bottom hold.
"""

from z3 import And, Bool, Int, Not, Solver, parse_smt2_string, sat, unsat

DECLS = """
(declare-const approved Bool)        ; a human approved this delete
(declare-const fileCount Int)        ; how many files the delete names
(declare-const isProduction Bool)    ; the files are in the production folder
(declare-const deleteAllowed Bool)   ; the agent may carry out the delete
"""
RULES = {
    "r1": "(=> (not approved) (not deleteAllowed))",
    "r2": "(=> (> fileCount 100) (not deleteAllowed))",
    "r3": "(=> (and approved (<= fileCount 100) (not isProduction)) deleteAllowed)",
    "r4": "(>= fileCount 0)",          # a bare assertion: an axiom, true of every input
}
R = [parse_smt2_string(DECLS + "(assert %s)" % r)[0] for r in RULES.values()]
approved, fileCount = Bool("approved"), Int("fileCount")
isProduction, deleteAllowed = Bool("isProduction"), Bool("deleteAllowed")


def consistent(*fs):
    s = Solver()
    s.add(*fs)
    return s.model() if s.check() == sat else None


def classify(premises, claims):
    P, C = And(*premises), And(*claims)
    if consistent(*R, P) is None:
        return "IMPOSSIBLE", None
    true_case, false_case = consistent(*R, P, C), consistent(*R, P, Not(C))
    if false_case is None:
        return "VALID", None                      # no way for the claim to be false
    if true_case is None:
        return "INVALID", None                    # no way for the claim to be true
    return "SATISFIABLE", (true_case, false_case)


CASES = [
    ("I have approval to delete 20 files in the test folder. May the agent delete them?  -- Yes.",
     [approved, fileCount == 20, Not(isProduction)], [deleteAllowed], "VALID"),
    ("I have approval to delete 250 files in the test folder. May the agent?  -- Yes.",
     [approved, fileCount == 250, Not(isProduction)], [deleteAllowed], "INVALID"),
    ("I have approval to delete 20 files. May the agent delete them?  -- Yes.",
     [approved, fileCount == 20], [deleteAllowed], "SATISFIABLE"),
    ("I have approval to delete -5 files. May the agent delete them?  -- Yes.",
     [approved, fileCount == -5], [deleteAllowed], "IMPOSSIBLE"),
]

print("1. Four question-and-answer pairs, already translated by hand")
for text, premises, claims, want in CASES:
    got, scenarios = classify(premises, claims)
    print("   %-11s %s" % (got, text))
    if scenarios:
        _, f = scenarios
        P = And(*premises)
        assert consistent(*R, P, deleteAllowed, Not(isProduction)) is not None
        assert consistent(*R, P, Not(deleteAllowed), Not(isProduction)) is None
        print("               true in one scenario (the files are not in production);")
        print("               false in another, which needs isProduction = %s" % f.eval(isProduction, True))
    assert got == want, (got, want)

print("\n2. Why IMPOSSIBLE is checked first")
P = And(approved, fileCount == -5)
assert consistent(*R, P, deleteAllowed) is None and consistent(*R, P, Not(deleteAllowed)) is None
print("   with contradictory premises, 'the claim cannot be false' AND 'the claim")
print("   cannot be true' both hold: an inconsistent set entails everything.")

print("\n3. What VALID does not cover")
got, _ = classify([approved, fileCount == 20, Not(isProduction)], [deleteAllowed])
assert got == "VALID"
print("   'I FORGED the approval for these 20 test files. May the agent?  -- Yes.'")
print("   There is no variable for 'forged', so the translation drops it and the")
print("   verdict is VALID. The check covers the translated claims, nothing else.")

print("\n4. Two translations of 'up to 100 files' -- do they agree?")
t1, t2 = fileCount < 100, fileCount <= 100
diff = consistent(*R, t1 != t2)
assert diff is not None and diff.eval(fileCount).as_long() == 100
print("   no: they differ at fileCount = %s. The service runs several translators," % diff.eval(fileCount))
print("   compares them like this, and reports TRANSLATION_AMBIGUOUS when they disagree.")

s = Solver()
s.add(*R)
assert s.check() == sat                             # the rules themselves are consistent
s.add(approved, fileCount == 250, deleteAllowed)
assert s.check() == unsat
