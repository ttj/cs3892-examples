#!/usr/bin/env python3
"""Check that every link a student can click is one a student can open.

This exists because of a real failure: a homework README linked the handout in
a repository that was private. The link was fine for the instructor and a 404
for every student, and nothing noticed for two weeks.

It reads Markdown, notebooks, HTML and PDFs, and applies four rules:

  LOCAL    no `file:` link, and no link to localhost. (A PDF built from
           Markdown turns a relative link into file:///... on the build
           machine; it works there and nowhere else.)
  MISSING  a relative link must point at a file that exists.
  GITHUB   a link into a GitHub repository must be to a PUBLIC repository, and
           the file or folder it names must exist there. The check uses the
           GitHub API and reads the repository's visibility, so it gives the
           same answer whether or not the token running it could see a private
           repository. This is the rule that would have caught the handout.
  DEAD     (only with --external) any other URL must not be a 404 or 410.

    python3 scripts/check_links.py                 # this repository
    python3 scripts/check_links.py --external      # ...and every other host
    python3 scripts/check_links.py slides/*.html slides/dist/*.pdf
    python3 scripts/check_links.py --skip LINK-AUDIT.md .

The same file is used by the course's other two repositories, which fetch it
from here in CI. It needs only the standard library and `curl`.

A host that refuses automated requests (403, 429, a timeout) is reported as
"could not verify" and never fails the run; only a definite answer does.
"""
from __future__ import annotations

import argparse
import concurrent.futures as cf
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
import zlib

UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
      "Chrome/140.0.0.0 Safari/537.36")
TYPES = (".md", ".ipynb", ".html", ".htm", ".pdf")
SKIP_DIRS = {".git", ".github", "node_modules", "__pycache__", "build", ".venv", "venv"}

URL = re.compile(r"""https?://[^\s<>"'`\)\]\\]+""")
MD_LINK = re.compile(r"""!?\[[^\]]*\]\(\s*<?([^)\s>]+)>?(?:\s+"[^"]*")?\s*\)""")
HTML_ATTR = re.compile(r"""(?:href|src)\s*=\s*["']([^"']+)["']""", re.I)
PDF_URI = re.compile(rb"/URI\s*\((.*?)\)")
# First path segments on github.com that are pages of the site, not accounts.
GITHUB_PAGES = {"features", "orgs", "about", "pricing", "login", "join", "marketplace", "sponsors",
                "topics", "collections", "settings", "notifications", "apps", "search", "site",
                "enterprise", "security", "readme", "contact", "customer-stories", "team"}
REPO_PAGES = {"issues", "pull", "pulls", "releases", "actions", "wiki", "discussions", "commits",
              "commit", "tags", "branches", "projects", "security", "pulse", "graphs", "network",
              "compare", "archive", "invitations", "settings", "stargazers", "forks"}


# --- reading links out of files ------------------------------------------------
def clean(url: str) -> str:
    return url.rstrip(".,;:!?*_")


def is_template(url: str) -> bool:
    """A URL with a placeholder in it is not a link anyone clicks."""
    return any(c in url for c in "{}$<>") or url.endswith("...") or "…" in url


def links_in_text(text: str, markdown: bool) -> tuple[set[str], set[str]]:
    """(absolute URLs, relative targets) found in a piece of text."""
    urls, rel = set(), set()
    for raw in URL.findall(text):
        urls.add(clean(raw))
    targets = HTML_ATTR.findall(text)
    if markdown:
        targets += MD_LINK.findall(text)
    for t in targets:
        t = t.strip()
        if re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", t):
            if t.lower().startswith(("http://", "https://", "file:")):
                urls.add(clean(t))
        elif t and not t.startswith(("#", "//")):
            rel.add(t)
    return urls, rel


def links_in_pdf(path: str) -> set[str]:
    data = open(path, "rb").read()
    found = set(PDF_URI.findall(data))
    for m in re.finditer(rb"stream\r?\n(.*?)\r?\nendstream", data, re.S):
        try:
            found |= set(PDF_URI.findall(zlib.decompress(m.group(1))))
        except zlib.error:
            pass
    return {u.decode("latin1").replace("\\(", "(").replace("\\)", ")") for u in found}


def read(path: str) -> tuple[set[str], set[str]]:
    ext = os.path.splitext(path)[1].lower()
    if ext == ".pdf":
        return links_in_pdf(path), set()
    text = open(path, encoding="utf-8", errors="replace").read()
    if ext == ".ipynb":
        try:
            cells = json.loads(text).get("cells", [])
        except json.JSONDecodeError:
            return set(), set()
        urls: set[str] = set()
        for c in cells:
            src = c.get("source", "")
            u, _ = links_in_text("".join(src) if isinstance(src, list) else src,
                                 markdown=c.get("cell_type") == "markdown")
            urls |= u                      # a notebook's relative links mean nothing in Colab
        return urls, set()
    return links_in_text(text, markdown=ext == ".md")


def files_under(paths: list[str], skip: set[str]) -> list[str]:
    out = []
    for p in paths:
        if os.path.isdir(p):
            for d, dirs, names in os.walk(p):
                dirs[:] = sorted(x for x in dirs if x not in SKIP_DIRS)
                out += [os.path.join(d, n) for n in sorted(names)]
        elif os.path.exists(p):
            out.append(p)
        else:
            print(f"no such path: {p}", file=sys.stderr)
    return [f for f in out if f.lower().endswith(TYPES) and os.path.basename(f) not in skip]


# --- GitHub ---------------------------------------------------------------------
def parse_github(url: str):
    """(owner, repo, ref, path) for a link into a repository; None otherwise.
    ref and path are None for a link to the repository itself."""
    u = urllib.parse.urlparse(url)
    host, parts = u.netloc.lower(), [urllib.parse.unquote(p) for p in u.path.split("/") if p]
    if host == "colab.research.google.com" and parts[:1] == ["github"]:
        host, parts = "github.com", parts[1:]
    if host == "raw.githubusercontent.com" and len(parts) >= 3:
        return parts[0], parts[1], parts[2], "/".join(parts[3:]) or None
    if host not in ("github.com", "www.github.com") or len(parts) < 2 or parts[0].lower() in GITHUB_PAGES:
        return None
    owner, repo = parts[0], re.sub(r"\.git$", "", parts[1])
    if len(parts) >= 4 and parts[2] in ("blob", "tree", "raw"):
        return owner, repo, parts[3], "/".join(parts[4:]) or None
    return owner, repo, None, None


def token() -> str:
    for name in ("GH_TOKEN", "GITHUB_TOKEN"):
        if os.environ.get(name):
            return os.environ[name]
    try:
        return subprocess.run(["gh", "auth", "token"], capture_output=True, text=True, timeout=10).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return ""


class GitHub:
    def __init__(self) -> None:
        self.token = token()
        self.cache: dict[str, tuple[int, object]] = {}

    def get(self, path: str) -> tuple[int, object]:
        if path not in self.cache:
            req = urllib.request.Request("https://api.github.com" + path, headers={
                "Accept": "application/vnd.github+json", "User-Agent": "cs3892-link-check"})
            if self.token:
                req.add_header("Authorization", "Bearer " + self.token)
            try:
                with urllib.request.urlopen(req, timeout=30) as r:
                    self.cache[path] = (r.status, json.loads(r.read() or b"null"))
            except urllib.error.HTTPError as e:
                self.cache[path] = (e.code, None)
            except (urllib.error.URLError, TimeoutError, OSError):
                self.cache[path] = (0, None)
        return self.cache[path]

    def verdict(self, owner: str, repo: str, ref, path, here: str, root: str) -> tuple[str, str]:
        """('ok' | 'fail' | 'unverified', reason)"""
        code, info = self.get(f"/repos/{owner}/{repo}")
        if code == 404:
            return "fail", "repository not found, or private: a student gets a 404"
        if code != 200 or not isinstance(info, dict):
            return "unverified", f"GitHub API answered {code or 'nothing'}"
        if info.get("private") or info.get("visibility") not in (None, "public"):
            return "fail", f"repository is {info.get('visibility', 'private')}: a student gets a 404"
        if path is None:
            return "ok", ""
        if f"{owner}/{repo}".lower() == here.lower() and ref in ("main", "master", "HEAD", info.get("default_branch")):
            return ("ok", "") if os.path.exists(os.path.join(root, path)) else \
                   ("fail", "no such file in this repository")
        code, _ = self.get(f"/repos/{owner}/{repo}/contents/{urllib.parse.quote(path)}?ref={urllib.parse.quote(ref)}")
        if code == 404:
            return "fail", f"no such path at `{ref}` in {owner}/{repo}"
        return ("ok", "") if code == 200 else ("unverified", f"GitHub API answered {code or 'nothing'}")


def this_repo(root: str) -> str:
    if os.environ.get("GITHUB_REPOSITORY"):
        return os.environ["GITHUB_REPOSITORY"]
    try:
        url = subprocess.run(["git", "-C", root, "remote", "get-url", "origin"],
                             capture_output=True, text=True, timeout=10).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return ""
    m = re.search(r"github\.com[:/]([^/]+)/([^/]+?)(?:\.git)?$", url)
    return f"{m.group(1)}/{m.group(2)}" if m else ""


# --- everything else ------------------------------------------------------------
def probe(url: str) -> tuple[str, str]:
    try:
        out = subprocess.run(["curl", "-sS", "-o", "/dev/null", "-w", "%{http_code}", "-L",
                              "--max-time", "40", "--retry", "1", "-A", UA, url],
                             capture_output=True, text=True, timeout=100)
        return url, out.stdout.strip()[-3:] or "000"
    except (OSError, subprocess.SubprocessError):
        return url, "000"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("paths", nargs="*", default=["."], help="files or folders to read (default: .)")
    ap.add_argument("--external", action="store_true", help="also request every non-GitHub URL")
    ap.add_argument("--report", action="store_true", help="print the findings but never fail")
    ap.add_argument("--skip", action="append", default=[], metavar="NAME",
                    help="a file name to leave out (repeatable)")
    ap.add_argument("--root", default=".", help="the repository root (default: .)")
    args = ap.parse_args()
    root = os.path.abspath(args.root)
    here = this_repo(root)

    cited: dict[str, set[str]] = {}
    fail: list[tuple[str, str, str]] = []            # (rule, target, reason)
    for f in files_under(args.paths, set(args.skip)):
        shown = os.path.relpath(f, root) if os.path.abspath(f).startswith(root) else f
        urls, rel = read(f)
        for u in urls:
            if not is_template(u):
                cited.setdefault(u, set()).add(shown)
        for t in sorted(rel):
            target = urllib.parse.unquote(t.split("#")[0].split("?")[0])
            if target and not is_template(t) and not os.path.exists(os.path.join(os.path.dirname(f), target)):
                fail.append(("MISSING", f"{shown} -> {t}", "no such file"))

    gh, github, other = GitHub(), [], []
    for u in sorted(cited):
        host = urllib.parse.urlparse(u).netloc.lower().split(":")[0]
        if u.lower().startswith("file:") or host in ("localhost", "127.0.0.1", "0.0.0.0", ""):
            fail.append(("LOCAL", u, "opens only on the machine that made it"))
        elif parse_github(u):
            github.append(u)
        elif host not in ("example.com", "www.example.com"):
            other.append(u)

    unverified: list[tuple[str, str]] = []
    for u in github:
        status, reason = gh.verdict(*parse_github(u), here=here, root=root)
        if status == "fail":
            fail.append(("GITHUB", u, reason))
        elif status == "unverified":
            unverified.append((u, reason))

    if args.external:
        with cf.ThreadPoolExecutor(max_workers=8) as pool:
            for u, code in pool.map(probe, other):
                if code in ("404", "410"):
                    fail.append(("DEAD", u, f"HTTP {code}"))
                elif not code.startswith("2"):
                    unverified.append((u, f"HTTP {code}" if code != "000" else "no answer"))

    n_files = len({f for fs in cited.values() for f in fs})
    print(f"{len(cited)} distinct links in {n_files} file(s)"
          f" · {len(github)} into GitHub repositories"
          f" · {len(other)} to other hosts ({'requested' if args.external else 'not requested; use --external'})")
    if unverified:
        print(f"\n  could not verify {len(unverified)} (not a failure):")
        for u, why in unverified:
            print(f"      {why:<24} {u[:110]}")
    for rule in ("LOCAL", "MISSING", "GITHUB", "DEAD"):
        rows = [(t, why) for r, t, why in fail if r == rule]
        if rows:
            print(f"\n  {rule} — {len(rows)}:")
            for t, why in rows:
                print(f"      {t[:120]}\n          {why}")
                for f in sorted(cited.get(t, ()))[:4]:
                    print(f"          in {f}")
    print()
    if fail and not args.report:
        print(f"FAILED — {len(fail)} link(s) a student cannot open")
        return 1
    print("PASSED — every link checked is one a student can open" if not fail
          else "reported only; not failing")
    return 0


if __name__ == "__main__":
    sys.exit(main())
