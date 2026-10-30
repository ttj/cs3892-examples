"""Session 20 -- the whole Lean project builds, and every theorem rests on the standard axioms.

S20.lean imports TS, Add2 and Switch. The build must finish with no warning (no `sorry`), and
`#print axioms` must list nothing beyond propext and Quot.sound for any theorem: none of
today's proofs needs classical logic.

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
         "x_le_N", "reach_k", "bound_tight"]
src = "import S20\n" + "".join(f"#print axioms S20.{n}\n" for n in names)
rc, msgs = messages("S20/Axioms.lean", src)    # runs src as a temporary S20/_Axioms.lean
print()
for _, text in msgs:
    print(text)
assert rc == 0
for text in (t for _, t in msgs):
    assert "sorryAx" not in text and "Classical.choice" not in text, text
assert len(msgs) == len(names)
print("\nlake build: no sorry, no warning; no theorem needs more than propext and Quot.sound")
