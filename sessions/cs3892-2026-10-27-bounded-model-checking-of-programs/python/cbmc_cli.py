"""Find CBMC, or fetch the official release if this machine does not have it.

CBMC is free and open source (BSD-4-Clause, github.com/diffblue/cbmc). This module
uses, in order: $CBMC_BIN (a directory holding cbmc), a cbmc already on the PATH,
then the official 6.11.0 release package for Ubuntu 22.04, downloaded once into
~/.cache and checked by SHA-256. That one package runs on Colab and on any Linux
with glibc 2.34 or newer. The package is unpacked here in Python (a .deb is an `ar`
archive holding a gzipped tar), so this needs neither dpkg nor root.

    from cbmc_cli import tool, run
    print(run("cbmc", "--version"))

Run as a script, it prints the version it found.
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

VERSION = "6.11.0"
URL = (f"https://github.com/diffblue/cbmc/releases/download/cbmc-{VERSION}/"
       f"ubuntu-22.04-cbmc-{VERSION}-Linux.deb")
SHA256 = "de9fa1cc4cf51c493e708a1c7608b192ad4956717b684d9c4501e22fd22d88a0"
CACHE = Path.home() / ".cache" / "cs3892" / f"cbmc-{VERSION}"
TOOLS = ("cbmc", "goto-cc", "goto-instrument", "goto-analyzer")


def _ar_members(data):
    """Yield (name, bytes) for each member of an `ar` archive."""
    assert data[:8] == b"!<arch>\n", "not an ar archive"
    i = 8
    while i < len(data):
        header = data[i:i + 60]
        name = header[:16].decode().strip().rstrip("/")
        size = int(header[48:58].decode().strip())
        yield name, data[i + 60:i + 60 + size]
        i += 60 + size + (size % 2)


def _download():
    if platform.system() != "Linux" or platform.machine() not in ("x86_64", "AMD64"):
        return None
    print(f"  downloading CBMC {VERSION} (about 70 MB, once) ...")
    data = urllib.request.urlopen(URL, timeout=300).read()
    if hashlib.sha256(data).hexdigest() != SHA256:
        raise RuntimeError("the downloaded CBMC package does not match its SHA-256; not using it")
    payload = dict(_ar_members(data))["data.tar.gz"]
    CACHE.mkdir(parents=True, exist_ok=True)
    with tarfile.open(fileobj=io.BytesIO(payload), mode="r:gz") as t:
        for tool_name in TOOLS:
            member = t.getmember(f"./usr/bin/{tool_name}")
            out = CACHE / tool_name
            out.write_bytes(t.extractfile(member).read())
            out.chmod(0o755)
    return CACHE


def _works(directory):
    exe = Path(directory) / "cbmc"
    try:
        r = subprocess.run([str(exe), "--version"], capture_output=True, text=True, timeout=60)
        return r.returncode == 0 and r.stdout.strip().startswith(VERSION.split(".")[0])
    except OSError:
        return False


def bin_dir():
    """A directory holding working cbmc, goto-cc, goto-instrument and goto-analyzer."""
    on_path = shutil.which("cbmc")
    for d in (os.environ.get("CBMC_BIN"), on_path and str(Path(on_path).parent), str(CACHE)):
        if d and _works(d) and all((Path(d) / t).exists() for t in TOOLS):
            return Path(d)
    d = _download()
    if d and _works(d):
        return d
    raise RuntimeError("no CBMC: install it from https://github.com/diffblue/cbmc/releases")


def tool(name):
    return str(bin_dir() / name)


def run(name, *args, cwd=None):
    """Run one of the CBMC tools and return its combined output (it never raises on a
    failed verification: CBMC exits 10 for VERIFICATION FAILED, which is a result)."""
    r = subprocess.run([tool(name), *map(str, args)], capture_output=True, text=True, cwd=cwd)
    return r.stdout + r.stderr


if __name__ == "__main__":
    print("CBMC", run("cbmc", "--version").strip(), "in", bin_dir())
