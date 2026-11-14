#!/usr/bin/env python3
"""Shared rules for the issue scripts: open-issues.py, release-labels.py, and (in bash) run-harness.sh.

An issue is ready for a harness only when its body has:
  - a `Planned harness: <name>` line, and
  - a `## Dependencies` section (it may say "None") whose references are all full issue URLs,
    https://github.com/BreakthruDevelopment/<repo>/issues/<n> (or /pull/<n>), and every one of them is closed.
A bare `#12` or `repo#12` there is refused: the runner can't check it (2026-11-14, FACTORY.md).

    python3 scripts/issuelib.py --self-test   # the parsing cases, also run through run-harness.sh's bash copy
"""
import json
import pathlib
import re
import subprocess
import sys

OWNER = "BreakthruDevelopment"
TOPIC = "30-apps-30-days"
HARNESSES = ("claude", "codex", "grok", "antigravity")
HOLD_LABEL = "hold"  # a person's "don't release this yet"; release-labels.py leaves such issues alone

# Foundation (wave 1) paths: only the foundation slice, which is security-sensitive, may create or edit them.
# Role and permission code lives in src/lib/auth/ (rbac.ts, permissions.ts) in the template.
WAVE1_PATHS = ("src/lib/db/schema.ts", "drizzle/", "src/lib/auth/", "src/lib/access.ts", "src/lib/access/")

ROOT = pathlib.Path(__file__).resolve().parent.parent
ISSUE_URL = re.compile(rf"https://github\.com/{OWNER}/([A-Za-z0-9._-]+)/(issues|pull)/([0-9]+)")
_LINK = re.compile(r"\[[^\]]*\]\((https?://[^)\s]+)\)")
_FOREIGN_URL = re.compile(r"https://github\.com/[^/\s]+/[^/\s]+/(?:issues|pull)/[0-9]+")
_BARE = re.compile(r"(?:[A-Za-z0-9._-]+/)?[A-Za-z0-9._-]*#[0-9]+")
_PLANNED = re.compile(r"^[ \t*_]*[Pp]lanned [Hh]arness[*_]*[ \t]*:[ \t*_`]*([A-Za-z-]+)", re.M)


def dependencies_section(body: str | None) -> str | None:
    """Text under `## Dependencies`, up to the next `## ` heading or a `---` line. None if there's no such heading."""
    out, inside, found = [], False, False
    for line in (body or "").replace("\r", "").split("\n"):
        if re.match(r"^##[ \t]", line):
            inside = bool(re.match(r"^##[ \t]+dependencies([^a-z0-9_]|$)", line.lower()))
            found = found or inside
            continue
        if inside and re.match(r"^---[ \t]*$", line):
            inside = False
            continue
        if inside:
            out.append(line)
    return "\n".join(out) if found else None


def dependency_urls(section: str) -> list[tuple[str, int, str]]:
    """(repo, number, url) for every full issue or PR URL in the section, sorted, without repeats."""
    seen = {}
    for m in ISSUE_URL.finditer(section or ""):
        seen[m.group(0)] = (m.group(1), int(m.group(3)), m.group(0))
    return [seen[k] for k in sorted(seen)]


def bare_refs(section: str) -> list[str]:
    """References the runner can't check: `#12`, `repo#12`, `owner/repo#12`, or issue URLs outside the org.
    `[#12](https://github.com/BreakthruDevelopment/repo/issues/12)` is fine: the link's target is a full URL."""
    s = _LINK.sub(lambda m: " " + m.group(1) + " ", section or "")
    s = ISSUE_URL.sub(" ", s)
    found = [f"{u} (outside {OWNER})" for u in _FOREIGN_URL.findall(s)]
    found += _BARE.findall(_FOREIGN_URL.sub(" ", s))
    return sorted(set(found))


def planned_harness(body: str | None) -> str | None:
    m = _PLANNED.search((body or "").replace("\r", ""))
    return m.group(1).lower() if m else None


def intake_problem(body: str | None, harness: str | None = None) -> str | None:
    """Why an issue can't be released or started (None if it can, apart from open dependencies)."""
    section = dependencies_section(body)
    if section is None:
        return "no '## Dependencies' section (add one, even 'None')"
    refs = bare_refs(section)
    if refs:
        return "'## Dependencies' has references that aren't full issue URLs: " + ", ".join(refs)
    planned = planned_harness(body)
    if not planned:
        return "no 'Planned harness:' line"
    if planned not in HARNESSES:
        return f"unknown planned harness '{planned}'"
    if harness and planned != harness:
        return f"planned harness is '{planned}', not {harness}"
    return None


def wave1_files(paths) -> list[str]:
    return [p for p in paths if any(p == w or (w.endswith("/") and p.startswith(w)) for w in WAVE1_PATHS)]


# --- GitHub (REST through the gh CLI and its own sign-in; no tokens of our own) ------------------------------------

class GhError(RuntimeError):
    pass


def gh(path: str, method: str = "GET", payload=None):
    cmd = ["gh", "api", path, "-X", method, "-H", "Accept: application/vnd.github+json"]
    if payload is not None:
        cmd += ["--input", "-"]
    r = subprocess.run(cmd, input=json.dumps(payload) if payload is not None else None, capture_output=True, text=True)
    if r.returncode:
        raise GhError(f"gh api {method} {path}: {(r.stderr or r.stdout).strip()}")
    return json.loads(r.stdout) if r.stdout.strip() else None


def gh_pages(path: str) -> list:
    """Every item of a list endpoint, 100 per page."""
    sep = "&" if "?" in path else "?"
    items, page = [], 1
    while True:
        batch = gh(f"{path}{sep}per_page=100&page={page}") or []
        items += batch
        if len(batch) < 100:
            return items
        page += 1


def topic_repos() -> list[str]:
    return sorted(r["name"] for r in gh_pages(f"orgs/{OWNER}/repos?type=all")
                  if TOPIC in (r.get("topics") or []) and not r.get("archived"))


class StateCache:
    """Open/closed state of issues and PRs, fetched once each."""

    def __init__(self):
        self._s: dict[tuple[str, int], str] = {}

    def state(self, repo: str, number: int) -> str:
        if (repo, number) not in self._s:
            try:
                self._s[(repo, number)] = gh(f"repos/{OWNER}/{repo}/issues/{number}").get("state", "unknown")
            except GhError:
                self._s[(repo, number)] = "unknown"  # counts as not closed: fail closed
        return self._s[(repo, number)]

    def open_deps(self, body: str) -> list[str]:
        return [f"{url} ({st})" for repo, n, url in dependency_urls(dependencies_section(body) or "")
                if (st := self.state(repo, n)) != "closed"]


# --- Self-test --------------------------------------------------------------------------------------------------

U = f"https://github.com/{OWNER}"
# (name, body, ready-for-grok?, dependency URLs)
CASES = [
    ("full-url links, mk1415 style",
     f"**14.8**\nPlanned harness: grok\n\n## Dependencies\n\n- Depends on [#1]({U}/14-real-estate/issues/1) (14.1)\n"
     f"- Depends on [30-apps-infra#79]({U}/30-apps-infra/issues/79) (14.11)\n\n## Notes\n\n- see #5\n\n---\nfooter #9\n",
     True, [f"{U}/14-real-estate/issues/1", f"{U}/30-apps-infra/issues/79"]),
    ("bare #N (the 2026-11-14 bodies)",
     "Planned harness: grok\n\n## Dependencies\n\n- #1 (13.1)\n- #2\n", False, []),
    ("repo#N without a URL",
     f"Planned harness: grok\n## Dependencies\n- 31-cost-scaler#1–#7\n- [#1]({U}/13-field-service/issues/1)\n",
     False, [f"{U}/13-field-service/issues/1"]),
    ("owner/repo#N without a URL",
     "Planned harness: grok\n## Dependencies\n- BreakthruDevelopment/13-field-service#1\n", False, []),
    ("link text #N pointing at a spec, not an issue",
     f"Planned harness: grok\n## Dependencies\n- [#3]({U}/ai-dev-os/blob/main/specs/13.md#3)\n", False, []),
    ("issue URL outside the org",
     "Planned harness: grok\n## Dependencies\n- https://github.com/someone/else/issues/4\n", False, []),
    ("no Dependencies section", "Planned harness: grok\n\n## Scope\n\nDo it. Depends on #1.\n", False, []),
    ("Dependencies: None", "Planned harness: grok\n\n## Dependencies\n\nNone; can start now.\n", True, []),
    ("no Planned harness line", f"## Dependencies\n\n- {U}/14-real-estate/issues/1\n", False,
     [f"{U}/14-real-estate/issues/1"]),
    ("planned for another harness",
     "**Planned harness:** `antigravity`\n## Dependencies\nNone\n", False, []),
    ("bold planned harness, PR URL, CRLF, ### subheading stays inside",
     f"**Planned harness:** grok\r\n## Dependencies\r\n### Code\r\n- {U}/13-field-service/pull/12 and "
     f"{U}/13-field-service/issues/3#issuecomment-99\r\n## Notes\r\n- #4\r\n",
     True, [f"{U}/13-field-service/issues/3", f"{U}/13-field-service/pull/12"]),
    ("Dependencies heading in another case, section ends at ---",
     f"Planned harness: grok\n## dependencies\n- {U}/x/issues/2\n---\n- #77\n", True, [f"{U}/x/issues/2"]),
]
PATHS = (["src/lib/db/schema.ts", "drizzle/0004_dispatch-board.sql", "drizzle/meta/_journal.json",
          "src/lib/auth/rbac.ts", "src/lib/access.ts", "src/lib/access/rules.ts"],
         ["src/lib/db/index.ts", "src/lib/accessibility.ts", "src/app/board/page.tsx", "src/lib/dispatch.ts",
          "drizzle.config.ts", "test/drizzle/x.ts"])


def run_harness_verdict(body: str, harness: str = "grok") -> tuple[bool, list[str]]:
    """The same check through scripts/run-harness.sh's bash functions."""
    r = subprocess.run(["bash", str(ROOT / "scripts" / "run-harness.sh"), "--check-body", harness],
                       input=body, capture_output=True, text=True, check=True)
    lines = r.stdout.splitlines()
    return lines[0] == "ok", [ln for ln in lines[1:] if ln]


def self_test() -> None:
    failures = []
    for name, body, ready, urls in CASES:
        problem = intake_problem(body, "grok")
        got_urls = [u for _, _, u in dependency_urls(dependencies_section(body) or "")]
        if (problem is None) != ready or got_urls != sorted(urls):
            failures.append(f"python, {name}: problem={problem!r} urls={got_urls}")
        bash_ready, bash_urls = run_harness_verdict(body)
        if bash_ready != ready or bash_urls != sorted(urls):
            failures.append(f"run-harness.sh, {name}: ready={bash_ready} urls={bash_urls}")
    hits, misses = PATHS
    if wave1_files(hits + misses) != hits:
        failures.append(f"python wave1_files: {wave1_files(hits + misses)}")
    r = subprocess.run(["bash", str(ROOT / "scripts" / "run-harness.sh"), "--wave1-files"],
                       input="\n".join(hits + misses) + "\n", capture_output=True, text=True, check=True)
    if r.stdout.split() != hits:
        failures.append(f"run-harness.sh --wave1-files: {r.stdout.split()}")
    if failures:
        sys.exit("issuelib self-test FAILED:\n  " + "\n  ".join(failures))
    print(f"issuelib self-test ok ({len(CASES)} bodies and the wave 1 paths, in Python and in run-harness.sh)")


if __name__ == "__main__":
    if sys.argv[1:] == ["--self-test"]:
        self_test()
    else:
        sys.exit(__doc__)
