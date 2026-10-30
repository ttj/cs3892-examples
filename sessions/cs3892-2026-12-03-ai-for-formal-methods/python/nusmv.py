"""Find NuSMV (or fetch FBK's official build), run a model, and read its verdicts.

The same logic as the sessions 9-16 notebooks' NuSMV cell, as a module: NuSMV 2.7.1 first (it
needs glibc >= 2.38 and libedit), the static 2.6.0 build as the fallback. Both give the same
verdicts. A build counts as working only if it actually checks a model.
"""
import hashlib
import os
import re
import shutil
import subprocess
import tarfile
import tempfile
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
SMV = HERE.parent / "smv"
# Each archive is pinned by SHA-256 (taken when first downloaded, Oct 30 2026; FBK publishes no
# checksums). A download that does not match is refused and never unpacked or run, as HW4's
# check_hw4.py refuses an elan installer that does not match its pin.
BUILDS = [("2.7.1", "https://nusmv.fbk.eu/distrib/2.7.1/NuSMV-2.7.1-linux64.tar.xz",
           "894dc71f0997683f28d4dc3512e3a6b608e02b9700e5e813017931df2d11883c"),
          ("2.6.0", "https://nusmv.fbk.eu/distrib/NuSMV-2.6.0-linux64.tar.gz",
           "11b12e42bc04566c4ec1f7cc205fa8704382ac4d69e052154cbb59c9b7e8e08c")]


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
    for ver, url, sha in BUILDS:
        dest = Path.home() / ".local" / f"nusmv-{ver}"
        _install(url, sha, dest)
        if _works(str(dest / "bin" / "NuSMV")):
            return str(dest / "bin" / "NuSMV")
    raise RuntimeError("could not install NuSMV")


def _install(url, sha, dest):
    """Download to a temporary file, refuse on a SHA-256 mismatch, then unpack (top folder
    stripped, no absolute or '..' paths) into a fresh directory moved into place only at the end."""
    with tempfile.TemporaryDirectory() as tmp:
        archive = Path(tmp) / url.rsplit("/", 1)[1]
        with urllib.request.urlopen(url, timeout=120) as r, open(archive, "wb") as fh:
            shutil.copyfileobj(r, fh)
        got = hashlib.sha256(archive.read_bytes()).hexdigest()
        if got != sha:
            raise RuntimeError(f"REFUSING {url}: SHA-256 {got} is not the pinned {sha}")
        stage = Path(tmp) / "stage"
        with tarfile.open(archive) as tar:
            for m in tar.getmembers():
                parts = Path(m.name).parts[1:]
                if not parts or m.issym() or m.islnk() or ".." in parts or Path(m.name).is_absolute():
                    continue
                m.name = str(Path(*parts))
                tar.extract(m, stage)
        if dest.exists():
            shutil.rmtree(dest)
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(stage), str(dest))


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
