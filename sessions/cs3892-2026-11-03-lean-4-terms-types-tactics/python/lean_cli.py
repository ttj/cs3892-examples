"""Find Lean v4.33.0 (installing it if needed), run a Lean file, and read Lean's goals.

The install is HW4's: `homework/hw4-lean/check_hw4.py` pins the elan release and the Lean
binaries by SHA-256, and this module calls it rather than keeping a second set of pins. If
`lake` is already on the PATH or in ~/.elan/bin it is used as it is; otherwise elan goes into
~/.elan (no root) and Lean is fetched through it (about 575 MB, once).

    from lean_cli import lean, region, goals
    rc, out = lean("S19/Counter.lean")          # Lean's messages, as the slides show them
    print(region("S19/Counter.lean", "counter-def"))
    for line, state in goals("S19/CurryHoward.lean", "tactic-steps"):
        print(line, state)

`region` returns the text between `-- SLIDE: <name>` and `-- END` -- exactly what the slide
prints. `goals` re-runs that region with `trace_state` before every tactic line and returns
Lean's goal at each step, so a goal on a slide is Lean's own output, not a transcription.

Run as a script, it prints the Lean version it found.
"""
import importlib.util
import json
import re
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
LEAN_DIR = HERE.parent / "lean"                  # the Lake project: lean-toolchain pins v4.33.0
CHECKER = HERE.parents[2] / "homework" / "hw4-lean" / "check_hw4.py"


def _checker():
    spec = importlib.util.spec_from_file_location("check_hw4", CHECKER)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def lean_bin():
    """The `lean` beside HW4's `lake` (elan's proxy picks v4.33.0 from lean-toolchain)."""
    return str(Path(_checker().find_lake()).parent / "lean")


def _run(rel, source, *flags):
    path = LEAN_DIR / rel
    if source is not None:                       # an instrumented copy, beside the original
        path = path.with_name("_" + path.name)
        path.write_text(source)
    try:
        r = subprocess.run([lean_bin(), *flags, str(path.relative_to(LEAN_DIR))], cwd=LEAN_DIR,
                           capture_output=True, text=True, timeout=600)
    finally:
        if source is not None:
            path.unlink()
    return r


def lean(rel):
    """Run one Lean file from the project folder; return (exit code, Lean's messages)."""
    r = _run(rel, None)
    return r.returncode, (r.stdout + r.stderr).rstrip()


def messages(rel, source=None):
    """(exit code, [(severity, text)]) -- Lean's messages one by one, via `lean --json`."""
    r = _run(rel, source, "--json")
    msgs = [json.loads(ln) for ln in r.stdout.splitlines() if ln.startswith("{")]
    return r.returncode, [(m["severity"], m["data"].rstrip()) for m in msgs]


def region(rel, name):
    """The lines between `-- SLIDE: name` and the next `-- END`, as the slide prints them."""
    text = (LEAN_DIR / rel).read_text()
    m = re.search(rf"^-- SLIDE: {re.escape(name)}\n(.*?)^-- END$", text, re.S | re.M)
    assert m, f"no region {name!r} in {rel}"
    return m.group(1).rstrip("\n")


def goals(rel, name):
    """[(tactic line, Lean's goal just before it)] for every tactic line in the region.

    A `trace_state` goes in before each line of each `by` block (at that line's indentation),
    and before the tactic of a one-line `| case => tactic` alternative. The last entry is the
    goal after the final line: "no goals" when the proof is complete."""
    text = (LEAN_DIR / rel).read_text()
    body = region(rel, name)
    out, steps, inside = [], [], False
    for ln in body.split("\n"):
        code = ln.split("--")[0].rstrip()
        if inside and not ln.startswith(" "):        # a line at column 0 ends the proof
            inside = False
        if inside and code.strip():
            alt = re.match(r"(\s*\|[^=]*=>\s*)(.*)", code)
            if alt:                                   # | zero => decide
                out.append(ln.replace(alt.group(0), f"{alt.group(1)}trace_state; {alt.group(2)}", 1))
                steps.append(code.strip())
                continue
            bullet = re.match(r"(\s*)· (.*)", code)
            indent = bullet.group(1) if bullet else code[: len(code) - len(code.lstrip())]
            out.append(f"{indent}trace_state")
            steps.append(code.strip())
        out.append(ln)
        if code.endswith(":= by"):
            inside = True
    rc, msgs = messages(rel, text.replace(body, "\n".join(out)))
    assert rc == 0, msgs
    states = [t for sev, t in msgs if sev == "information" and ("⊢" in t or t == "no goals")]
    assert len(states) == len(steps), (len(states), len(steps), msgs)
    return list(zip(steps, states)) + [("", "no goals")]


def show(rel, name):
    """Print a region as the slide shows it, under a header naming its file."""
    print(f"--- {rel} · {name} " + "-" * max(0, 56 - len(rel) - len(name)))
    print(region(rel, name))
    print()


def show_goals(rel, name):
    """Print Lean's goal before each tactic line of a region, then after the last one."""
    for step, state in goals(rel, name):
        print(f"  {'after the last line' if not step else 'before  ' + step}")
        print("    " + state.replace("\n", "\n    "))
    print()


if __name__ == "__main__":
    v = subprocess.run([lean_bin(), "--version"], cwd=LEAN_DIR, capture_output=True,
                       text=True).stdout.strip()
    print(v)
    assert "version 4.33.0" in v, v
