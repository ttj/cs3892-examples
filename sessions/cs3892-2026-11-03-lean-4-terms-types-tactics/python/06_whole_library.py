"""Session 19 -- the whole Lean project builds, as `lake build` (or VS Code) builds it.

S19.lean imports Counter, CurryHoward, Tactics and Sets, and the build must finish with no
warning: no `sorry` anywhere in the library. Sorry.lean (meant to warn) and OmegaStops.lean
(meant to fail) are deliberately not imported; scripts 03 and 04 run them on their own.

Expected: the assertions at the bottom hold.
"""
import os
import subprocess
from pathlib import Path

from lean_cli import LEAN_DIR, _checker

lake = _checker().find_lake()
env = dict(os.environ, PATH=str(Path(lake).parent) + os.pathsep + os.environ.get("PATH", ""))
r = subprocess.run([lake, "build"], cwd=LEAN_DIR, env=env, capture_output=True, text=True,
                   timeout=1800)
out = (r.stdout + r.stderr).strip()
print(out)
assert r.returncode == 0, out
assert "Build completed successfully" in out and "sorry" not in out and "warning" not in out, out
imports = (LEAN_DIR / "S19.lean").read_text()
assert "import S19.Sorry" not in imports and "import S19.OmegaStops" not in imports
print("\nlake build: the library builds with no sorry and no warning")
