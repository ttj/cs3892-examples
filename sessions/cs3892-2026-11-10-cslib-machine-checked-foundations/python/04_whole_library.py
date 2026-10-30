"""Session 21 -- the project builds against Mathlib v4.33.0 + Cslib v4.33.0, with no sorry.

lakefile.toml pins Cslib at v4.33.0 (not `main`, which drags in a release-candidate toolchain).
The first build fetches Mathlib's cache (`lake exe cache get`) and compiles only the Cslib modules
S21 imports.

Expected: the assertions at the bottom hold.
"""
import os
import subprocess
from pathlib import Path

from lean_cli import LEAN_DIR, _checker

lake = _checker().find_lake()
env = dict(os.environ, PATH=str(Path(lake).parent) + os.pathsep + os.environ.get("PATH", ""))
for step in (["exe", "cache", "get"], ["build"]):
    r = subprocess.run([lake, *step], cwd=LEAN_DIR, env=env, capture_output=True, text=True,
                       timeout=3600)
    assert r.returncode == 0, (r.stdout + r.stderr)[-3000:]
out = (r.stdout + r.stderr).strip()
ours = [ln for ln in out.split("\n") if "S21" in ln and ("warning" in ln or "error" in ln)]
print("\n".join(out.split("\n")[-4:]))
assert "Build completed successfully" in out and not ours, ours
assert "rev = \"v4.33.0\"" in (LEAN_DIR / "lakefile.toml").read_text()
assert (LEAN_DIR / "lean-toolchain").read_text().strip() == "leanprover/lean4:v4.33.0"
print("\nlake build: Mathlib + Cslib v4.33.0, S21 builds with no sorry and no warning")
