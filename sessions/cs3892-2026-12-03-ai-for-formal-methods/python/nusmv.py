"""Find NuSMV (or fetch FBK's official build), run a model, and read its verdicts.

The same logic as the sessions 9-16 notebooks' NuSMV cell, as a module: NuSMV 2.7.1 first (it
needs glibc >= 2.38 and libedit), the static 2.6.0 build as the fallback. Both give the same
verdicts. A build counts as working only if it actually checks a model.
"""
import os
import re
import shutil
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
SMV = HERE.parent / "smv"
BUILDS = [("2.7.1", "https://nusmv.fbk.eu/distrib/2.7.1/NuSMV-2.7.1-linux64.tar.xz", "J"),
          ("2.6.0", "https://nusmv.fbk.eu/distrib/NuSMV-2.6.0-linux64.tar.gz", "z")]


def _works(exe):
    try:
        r = subprocess.run([exe, str(SMV / "counter.smv")], capture_output=True, text=True, timeout=60)
        return r.returncode == 0 and "NuSMV" in (r.stdout + r.stderr)
    except Exception:
        return False


def nusmv():
    found = [shutil.which("NuSMV")] + [str(Path.home() / ".local" / f"nusmv-{v}" / "bin" / "NuSMV")
                                       for v, _, _ in BUILDS]
    for exe in found:
        if exe and Path(exe).exists() and _works(exe):
            return exe
    if os.geteuid() == 0 and shutil.which("apt-get"):           # Colab runs as root
        subprocess.run("apt-get install -y -qq libedit2 >/dev/null 2>&1", shell=True)
    for ver, url, z in BUILDS:
        dest = Path.home() / ".local" / f"nusmv-{ver}"
        dest.mkdir(parents=True, exist_ok=True)
        subprocess.run(f"curl -sSL {url} | tar -x{z} -C {dest} --strip-components=1", shell=True, check=True)
        if _works(str(dest / "bin" / "NuSMV")):
            return str(dest / "bin" / "NuSMV")
    raise RuntimeError("could not install NuSMV")


def run(text):
    """Run NuSMV on a model given as text; return its output without the banner."""
    path = SMV / "_check.smv"
    path.write_text(text)
    try:
        r = subprocess.run([nusmv(), str(path)], capture_output=True, text=True, timeout=300)
    finally:
        path.unlink()
    return "\n".join(l for l in (r.stdout + r.stderr).splitlines() if not l.startswith("***")).strip()


def verdicts(out):
    """[(formula as NuSMV prints it, 'true' or 'false')] in output order."""
    return [(re.sub(r"\s+", " ", m.group(1)).strip(), m.group(2))
            for m in re.finditer(r"^-- specification\s+(.*?)\s+is (true|false)$", out, re.M)]
