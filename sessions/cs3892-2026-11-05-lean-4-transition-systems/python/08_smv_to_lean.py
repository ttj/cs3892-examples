# FIGURE: figures/modes_efsm.svg   (the two-mode counter; the mutex is figures/mutex.svg)
"""Session 20 -- from SMV to Lean, mechanically: smv2lean on the two-mode counter and the mutex.

scripts/smv2lean is the translator from github.com/ttj/leansmv. Each VAR becomes a field of a
`State` structure (an enum becomes an `inductive`; `boolean` becomes `Bool`; a range like
0..25 becomes `Nat`, and the range is DROPPED); `init` becomes the TS's `init`; each
`next(v) := case ... esac` becomes an if-then-else chain, one branch per case line; a free
input (press, move) becomes `∃ press' : Bool, ...`; and each INVARSPEC becomes a commented
theorem stub. This script regenerates both Lean files and checks they are the committed ones.

Needs the `lark` parser: pip install lark.

Expected: the assertions at the bottom hold.
"""
import sys
from pathlib import Path

from lean_cli import lean

HERE = Path(__file__).resolve().parent
SESSION = HERE.parent
sys.path.insert(0, str(SESSION.parent.parent / "scripts" / "smv2lean"))
from to_course import translate  # noqa: E402

for model, lean_file in [("counter.smv", "S20/Counter.lean"), ("mutex.smv", "S20/Mutex.lean")]:
    smv = SESSION / "smv" / model
    text = translate(smv, "S20")
    committed = (SESSION / "lean" / lean_file).read_text()
    assert text == committed, f"{lean_file} is not what smv2lean makes from {model}: regenerate it"
    body = text[text.index("structure"):text.index("-- INVARSPEC 1")].rstrip()
    print(f"--- {model} -> {lean_file} (the definitions; the stubs follow in the file) ---")
    print(body, "\n")
    rc, out = lean(lean_file)
    assert rc == 0 and out == "", out

c = (SESSION / "lean" / "S20/Counter.lean").read_text()
assert "  x : Nat\n" in c and "0..25" not in c.split("-/", 1)[1].split("-- INVARSPEC")[0]   # range dropped
assert "∃ press' : Bool," in c                                                     # free input
assert c.count("    else if ") == 4 and "(s.x < 10)" in c                          # DEFINE inlined
assert c.count("-- theorem CounterTS_inv") == 3                                    # one stub per INVARSPEC
m = (SESSION / "lean" / "S20/Mutex.lean").read_text()
assert "∃ move' : Nat," in m and "(s.b ≠ .critical)" in m
print("both files are exactly what smv2lean makes, and both build")
