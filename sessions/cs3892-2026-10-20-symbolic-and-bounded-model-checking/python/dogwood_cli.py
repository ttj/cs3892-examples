"""Find the `dogwood` command, fetching it if this machine does not have it.

Dogwood's reference interpreter is a Rust program. Compiling it takes about a
minute on a fast machine and several on Colab, so this course publishes an
unmodified Linux build of the v1.1 release (Apache-2.0; its LICENSE, NOTICE and
build notes are inside the archive). In order, this module uses:

  1. $DOGWOOD, if set;
  2. a `dogwood` already on the PATH;
  3. the course build, downloaded once into ~/.cache and checked by SHA-256;
  4. otherwise it compiles the release from source with cargo, if cargo exists.

Run as a script, it prints which one it found.
"""
import hashlib
import io
import os
import platform
import shutil
import subprocess
import tarfile
import urllib.request
from pathlib import Path

VERSION = "1.1.0"
ARCHIVE = f"dogwood-{VERSION}-x86_64-linux"
URL = f"https://github.com/ttj/cs3892-examples/releases/download/dogwood-v{VERSION}/{ARCHIVE}.tar.gz"
SHA256 = "205c585199770eb1033ed60e6a1df34613a80de6a9c1ad7ee7d201d07e2e96cd"
CACHE = Path.home() / ".cache" / "cs3892" / ARCHIVE


def _works(exe):
    try:
        r = subprocess.run([str(exe), "--version"], capture_output=True, text=True, timeout=30)
        return r.returncode == 0 and r.stdout.startswith("dogwood ")
    except OSError:
        return False


def _download():
    if platform.system() != "Linux" or platform.machine() not in ("x86_64", "AMD64"):
        return None
    try:
        data = urllib.request.urlopen(URL, timeout=60).read()
    except OSError as e:
        print(f"  (could not download the course build: {e})")
        return None
    if hashlib.sha256(data).hexdigest() != SHA256:
        raise RuntimeError("the downloaded dogwood archive does not match its SHA-256; not using it")
    CACHE.parent.mkdir(parents=True, exist_ok=True)
    with tarfile.open(fileobj=io.BytesIO(data), mode="r:gz") as t:
        for m in t.getmembers():                       # refuse anything outside the archive folder
            if not m.name.startswith(ARCHIVE + "/") and m.name != ARCHIVE:
                raise RuntimeError(f"unexpected path in archive: {m.name}")
        t.extractall(CACHE.parent, **({"filter": "data"} if hasattr(tarfile, "data_filter") else {}))
    exe = CACHE / "dogwood"
    exe.chmod(0o755)
    return exe


def _build():
    if not shutil.which("cargo"):
        return None
    print("  compiling dogwood v1.1 from source (a few minutes the first time) ...")
    root = CACHE.parent / f"dogwood-{VERSION}-cargo"
    subprocess.run(["cargo", "install", "--locked", "--quiet", "--root", str(root),
                    "--git", "https://github.com/dogwood-policy/dogwood", "--tag", "v1.1", "dogwood-cli"],
                   check=True)
    return root / "bin" / "dogwood"


def dogwood():
    """The path of a working `dogwood` executable."""
    for exe in (os.environ.get("DOGWOOD"), shutil.which("dogwood"), CACHE / "dogwood"):
        if exe and _works(exe):
            return str(exe)
    for get in (_download, _build):
        exe = get()
        if exe and _works(exe):
            return str(exe)
    raise RuntimeError("no dogwood: install Rust (https://rustup.rs), then\n"
                       "  cargo install --locked --git https://github.com/dogwood-policy/dogwood --tag v1.1 dogwood-cli")


if __name__ == "__main__":
    exe = dogwood()
    print(subprocess.run([exe, "--version"], capture_output=True, text=True).stdout.strip(), "at", exe)
