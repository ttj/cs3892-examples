"""Session 20 -- the whole Lean project builds, and every theorem rests on the standard axioms.

S20.lean imports TS, Add2, Switch, Names, and the SMV translations Counter and Mutex with their
proofs. The build must finish with no warning (no `sorry`), and `#print axioms` must list
nothing beyond propext and Quot.sound for every theorem but two: the proof that the counter's
third INVARSPEC is false (and the reachability lemma it uses) goes through `simp` lemmas that
use Classical.choice. HW4's checker allows that axiom too; `sorryAx` it never allows.

Expected: the assertions at the bottom hold.
"""
import os
import subprocess
from pathlib import Path

from lean_cli import LEAN_DIR, _checker, messages

lake = _checker().find_lake()
env = dict(os.environ, PATH=str(Path(lake).parent) + os.pathsep + os.environ.get("PATH", ""))
r = subprocess.run([lake, "build"], cwd=LEAN_DIR, env=env, capture_output=True, text=True,
                   timeout=1800)
out = (r.stdout + r.stderr).strip()
print(out)
assert r.returncode == 0, out
assert "Build completed successfully" in out and "sorry" not in out and "warning" not in out, out

names = ["inductive_invariant_holds", "P_not_inductive", "even_inductive", "P_holds",
         "x_le_N", "reach_k", "bound_tight", "nng2", "even_add2", "rw_back",
         "CounterTS_inv1", "CounterTS_inv2", "mutual_exclusion"]
classical = ["reach_on", "CounterTS_inv3_false"]
src = "import S20\n" + "".join(f"#print axioms S20.{n}\n" for n in names + classical)
rc, msgs = messages("S20/Axioms.lean", src)    # runs src as a temporary S20/_Axioms.lean
print()
for _, text in msgs:
    print(text)
assert rc == 0
for text in (t for _, t in msgs):
    assert "sorryAx" not in text, text
    assert "Classical.choice" not in text or text.split("'")[1].split(".")[-1] in classical, text
assert len(msgs) == len(names + classical)
print("\nlake build: no sorry, no warning; only the false-INVARSPEC proof uses Classical.choice")
