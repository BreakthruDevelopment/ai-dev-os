#!/usr/bin/env python3
"""Shared rules for the issue scripts: open-issues.py, release-labels.py, and (in bash) run-harness.sh.

An issue is ready for a harness only when its body has:
  - a `Planned harness: <name>` line, and
  - a `## Dependencies` section (it may say "None") whose references are all full issue URLs,
    https://github.com/BreakthruDevelopment/<repo>/issues/<n> (or /pull/<n>), and every one of them is closed.
A bare `#12` or `repo#12` there is refused: the runner can't check it (2026-11-14, FACTORY.md). A dependency
counts as done only when it was completed: an issue closed as completed (not "not planned" or a duplicate), or a
merged PR.

    python3 scripts/issuelib.py --self-test   # the parsing cases, also run through run-harness.sh's bash copy

Needs Python 3.10+ and the gh CLI (signed in); the self-test also needs bash, git and jq.
"""
import json
import pathlib
import re
import subprocess
import sys

OWNER = "BreakthruDevelopment"
TOPIC = "30-apps-30-days"
HARNESSES = ("claude", "codex", "grok", "antigravity")
HOLD_LABEL = "hold"  # "a person must look first": release-labels.py leaves such issues alone; the runner adds it
RELEASE_MARK = "<!-- release-labels:released harness={} -->"  # posted once an issue has had its start signal

# Foundation (wave 1) paths: only the foundation slice, which is security-sensitive, may create or edit them.
# Role and permission code lives in src/lib/auth/ (rbac.ts, permissions.ts) in the template; src/proxy.ts and
# src/middleware.ts sit in front of every request. Same list as WAVE1_RE in run-harness.sh.
#
# The second group is the Python track, whose foundation is a `core/` package plus the schema and the frozen
# contracts rather than Drizzle and Better Auth. Added 2026-11-21: the list was TypeScript-only, so `p2p/core/`
# and `kit/core/` were protected by their specs and the reviewer but by nothing mechanical, and the note in every
# generated issue told a Python-track builder to avoid paths its repo does not have. Each group is inert in the
# other's repos, so one list serves both.
#
# **`agent_container/core/` (app 17) is deliberately NOT here.** Its spec draws a distinction this guard cannot
# express: "Wave 1 owns them; later slices extend by adding files", and slice 17.5 is a `grok` slice, not
# security-sensitive, that is explicitly allowed to add `core/log.py`. The guard refuses on any path match and
# `git diff --name-only` lists additions, so listing it would refuse that push and strand the branch. App 17's
# `core/` stays protected by its spec and the reviewer. Apps 18 and 19 forbid their `core/` to be created *or*
# edited outside wave 1, so they are safe to list; a Python-track repo that wants the add-and-not-edit rule needs
# the guard to learn that distinction first.
WAVE1_PATHS = ("src/lib/db/", "drizzle/", "drizzle.config.ts", "src/lib/auth/", "src/lib/access.ts", "src/lib/access/",
               "src/proxy.ts", "src/middleware.ts",
               "p2p/core/", "kit/core/", "erp/", "contracts/")

ROOT = pathlib.Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts" / "run-harness.sh"
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


def dep_state(issue: dict) -> str:
    """"done" for a completed dependency, else why not. Same rule as DEP_STATE_JQ in run-harness.sh."""
    if issue.get("state") != "closed":
        return issue.get("state") or "unknown"
    if issue.get("pull_request"):
        return "done" if issue["pull_request"].get("merged_at") else "closed without merging"
    if issue.get("state_reason") in ("not_planned", "duplicate"):
        return f"closed as {issue['state_reason']}"
    return "done"


class StateCache:
    """Completion state of issues and PRs ("done" or why not), fetched once each."""

    def __init__(self):
        self._s: dict[tuple[str, int], str] = {}

    def state(self, repo: str, number: int) -> str:
        if (repo, number) not in self._s:
            try:
                self._s[(repo, number)] = dep_state(gh(f"repos/{OWNER}/{repo}/issues/{number}"))
            except GhError:
                self._s[(repo, number)] = "unknown"  # counts as not done: fail closed
        return self._s[(repo, number)]

    def open_deps(self, body: str) -> list[str]:
        return [f"{url} ({st})" for repo, n, url in dependency_urls(dependencies_section(body) or "")
                if (st := self.state(repo, n)) != "done"]


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
PATHS = (["src/lib/db/schema.ts", "src/lib/db/index.ts", "drizzle/0004_dispatch-board.sql", "drizzle/meta/_journal.json",
          "drizzle.config.ts", "src/lib/auth/rbac.ts", "src/lib/access.ts", "src/lib/access/rules.ts", "src/proxy.ts",
          "src/middleware.ts",
          "p2p/core/erp.py", "p2p/core/access.py", "kit/core/sandbox.py", "erp/schema.sql",
          "erp/seed/suppliers.csv", "contracts/p2p-erp.json"],
         ["src/lib/accessibility.ts", "src/app/board/page.tsx", "src/lib/dispatch.ts", "test/drizzle/x.ts",
          "src/proxy.test.ts", "drizzle.config.ts.bak", "src/lib/dbx.ts",
          "agent_container/core_utils.py", "agent_container/testing/contracts.py", "p2p/match/workflow.py",
          "kit/corex/y.py", "kit/scout/brief.py", "tests/p2p/core/test_erp.py", "contracts.py", "erp.sql",
          # App 17's core/ is excluded on purpose -- see the note on WAVE1_PATHS. 17.5 is a `grok` slice allowed
          # to add core/log.py, and this guard cannot tell adding from editing.
          "agent_container/core/loop.py", "agent_container/core/log.py"])
# (issue JSON, dep_state)
DEP_CASES = [
    ({"state": "open"}, "open"),
    ({"state": "closed", "state_reason": "completed"}, "done"),
    ({"state": "closed", "state_reason": None}, "done"),
    ({"state": "closed", "state_reason": "not_planned"}, "closed as not_planned"),
    ({"state": "closed", "state_reason": "duplicate"}, "closed as duplicate"),
    ({"state": "closed", "pull_request": {"merged_at": "2026-11-14T10:00:00Z"}}, "done"),
    ({"state": "closed", "pull_request": {"merged_at": None}}, "closed without merging"),
    ({"state": "open", "pull_request": {"merged_at": None}}, "open"),
]


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
    # The runner prints this list into the prompt it hands a harness, derived from WAVE1_RE by stripping the
    # regex. That stripping is a shell one-liner and silently mangles a grouped alternation such as
    # `(p2p|kit)/core/` or an end-anchored group, so compare it with the real list rather than trusting it.
    r = subprocess.run(["bash", str(ROOT / "scripts" / "run-harness.sh"), "--wave1-list"],
                       capture_output=True, text=True, check=True)
    listed = [x.strip() for x in r.stdout.strip().split(",") if x.strip()]
    if listed != list(WAVE1_PATHS):
        failures.append(f"run-harness.sh --wave1-list disagrees with WAVE1_PATHS: {listed}")
    for issue, want in DEP_CASES:
        got = dep_state(issue)
        r = subprocess.run(["bash", str(SCRIPT), "--dep-state"], input=json.dumps(issue),
                           capture_output=True, text=True)
        if got != want or r.stdout.strip() != want:
            failures.append(f"dep_state {issue}: python={got!r} bash={r.stdout.strip()!r} {r.stderr.strip()}")
    failures += _guard_tests()
    failures += _port_tests()
    r = subprocess.run(["bash", str(SCRIPT), "--quote"], capture_output=True, text=True, check=True,
                       input="ask @someone <!-- run-harness:claim h:1:2 --> ```\n~~~~\n" + "x" * 3000)
    q = r.stdout
    if "@" in q or "<!--" in q or "-->" in q or "```" in q or "~~~" in q or len(q.encode()) > 1600:  # capped at 1500 bytes before the replacements
        failures.append(f"quote_untrusted let something through: {q[:120]!r}")
    if failures:
        sys.exit("issuelib self-test FAILED:\n  " + "\n  ".join(failures))
    print(f"issuelib self-test ok ({len(CASES)} bodies, {len(DEP_CASES)} dependency states, the wave 1 paths, "
          "the pre-push guard, clone checks, quoting and per-repo ports, in Python and in run-harness.sh)")


# Ports run-harness.sh derives from the repo name (cksum, 10000-19999). Pinned so a change to the derivation, or a
# machine whose cksum disagrees, shows up here instead of as two apps sharing a port on the Mac.
PORT_PINS = {"13-field-service": 14182, "14-real-estate": 16142, "15-event-ticketing": 15920, "31-cost-scaler": 10048}


def _port_tests() -> list[str]:
    """run-harness.sh's per-repo port: stable, in range, no two real repos share one, PORT overrides it, and a
    port that something already listens on is reported busy."""
    import os
    import socket
    out = []
    env = {k: v for k, v in os.environ.items() if k != "PORT"}

    def sh(*args, port=None):
        e = dict(env, **({"PORT": port} if port is not None else {}))
        return subprocess.run(["bash", str(SCRIPT), *args], capture_output=True, text=True, env=e)

    repos = re.findall(r"^\s+repo:\s*(\S+)", (ROOT / "catalog.yaml").read_text(), re.M)
    repos += ["30-apps-template", "ai-dev-os", "30-apps-infra"]
    if len(repos) < 35:
        out.append(f"port test found only {len(repos)} repo names")
    ports = {}
    for repo in repos:
        a, b = sh("--port-for", repo).stdout.strip(), sh("--port-for", repo).stdout.strip()
        if a != b or not a.isdigit() or not 10000 <= int(a) <= 19999:
            out.append(f"port for {repo}: {a!r} then {b!r}")
            continue
        ports.setdefault(a, []).append(repo)
        if sh("--resolve-port", repo).stdout.strip() != a:
            out.append(f"--resolve-port {repo} differs from --port-for")
    out += [f"port {p} shared by {rs}" for p, rs in ports.items() if len(rs) > 1]
    for repo, want in PORT_PINS.items():
        got = sh("--port-for", repo).stdout.strip()
        if got != str(want):
            out.append(f"port for {repo} is {got}, expected {want}")
    if sh("--resolve-port", "15-event-ticketing", port="12345").stdout.strip() != "12345":
        out.append("PORT in the environment wasn't respected")
    for bad in ("abc", "80", "0123", "70000", "-1", "3000 "):
        if sh("--resolve-port", "15-event-ticketing", port=bad).returncode == 0:
            out.append(f"PORT={bad!r} should have been refused")
    with socket.socket() as srv:
        srv.bind(("127.0.0.1", 0))
        srv.listen(1)
        busy = srv.getsockname()[1]
        if sh("--port-busy", str(busy)).returncode != 0:
            out.append(f"port {busy} has a listener but --port-busy said free")
    if sh("--port-busy", str(busy)).returncode != 1:  # listener closed: free again (nothing else binds it that fast)
        out.append(f"port {busy} has no listener but --port-busy said busy")
    return out


def _guard_tests() -> list[str]:
    """run-harness.sh's pre-push guard on a scratch repo: it uses the recorded base even when the clone's
    origin/main is moved, sees quoted and non-ASCII names, and fails (non-zero) when it can't check."""
    import tempfile
    out = []
    with tempfile.TemporaryDirectory() as d:
        def git(*a):
            return subprocess.run(["git", "-C", d, "-c", "user.name=t", "-c", "user.email=t@t", *a],
                                  capture_output=True, text=True, check=True).stdout.strip()

        def guard(base, branch="grok/1-x"):
            r = subprocess.run(["bash", str(SCRIPT), "--foundation-changes", d, branch, base],
                               capture_output=True, text=True)
            return r.returncode, r.stdout.splitlines()

        git("init", "-q", "-b", "main")
        pathlib.Path(d, "src/app").mkdir(parents=True)
        pathlib.Path(d, "src/app/page.tsx").write_text("a\n")
        git("add", "-A")
        git("commit", "-qm", "init")
        base = git("rev-parse", "HEAD")
        git("update-ref", "refs/remotes/origin/main", base)
        git("switch", "-qc", "grok/1-x")
        pathlib.Path(d, "src/lib/db").mkdir(parents=True)
        pathlib.Path(d, "drizzle").mkdir()
        pathlib.Path(d, "src/lib/db/schema.ts").write_text("x\n")
        pathlib.Path(d, "drizzle/0009_café.sql").write_text("x\n")
        pathlib.Path(d, 'drizzle/0010_"quoted".sql').write_text("x\n")
        pathlib.Path(d, "src/app/page.tsx").write_text("b\n")
        git("add", "-A")
        git("commit", "-qm", "work")
        want = ['drizzle/0009_café.sql', 'drizzle/0010_"quoted".sql', "src/lib/db/schema.ts"]
        rc, got = guard(base)
        if rc != 0 or sorted(got) != want:
            out.append(f"guard on a clean run: rc={rc} {got}")
        # (a) the harness moves origin/main to its own tip: the recorded base still sees everything.
        git("update-ref", "refs/remotes/origin/main", git("rev-parse", "HEAD"))
        rc, got = guard(base)
        if rc != 0 or sorted(got) != want:
            out.append(f"guard after origin/main was moved: rc={rc} {got}")
        # A branch rebuilt on another history doesn't build on the base: status 3.
        git("switch", "-q", "--orphan", "grok/2-y")
        pathlib.Path(d, "README.md").write_text("y\n")
        git("add", "README.md")
        git("commit", "-qm", "orphan")
        rc, _ = guard(base, "grok/2-y")
        if rc != 3:
            out.append(f"guard on a branch that doesn't build on the base: rc={rc}, wanted 3")
        # (c) git can't diff (a base that isn't a commit): non-zero, never an empty "nothing changed".
        rc, got = guard("0" * 40)
        if rc == 0:
            out.append(f"guard with an unusable base returned 0 ({got})")

        def reason(branch, b=base):
            return subprocess.run(["bash", str(SCRIPT), "--guard", d, branch, b],
                                  capture_output=True, text=True).stdout.strip()

        # The runner refuses any foundation change outright (no label check), and passes a page-only branch.
        git("switch", "-q", "main")
        git("switch", "-qc", "grok/3-page")
        pathlib.Path(d, "src/app/page.tsx").write_text("c\n")
        git("commit", "-qam", "page")
        if reason("grok/3-page"):
            out.append(f"guard held a page-only branch: {reason('grok/3-page')!r}")
        r1 = reason("grok/1-x")
        if "foundation files" not in r1 or "src/lib/db/schema.ts" not in r1 or "café" not in r1:
            out.append(f"guard reason for foundation changes: {r1!r}")
        if "doesn't build on" not in reason("grok/2-y") or not reason("grok/1-x", "0" * 40):
            out.append("guard reasons for a foreign history or an unusable base")

        # The clone checks: origin must be the https URL, .git/config only allowed settings.
        def clone_problem():
            return subprocess.run(["bash", str(SCRIPT), "--check-clone", d, "99-x"],
                                  capture_output=True, text=True).stdout.strip()

        git("remote", "add", "origin", f"https://github.com/{OWNER}/99-x.git")
        git("config", "branch.main.remote", "origin")
        git("config", "branch.main.merge", "refs/heads/main")
        if clone_problem():
            out.append(f"clean clone refused: {clone_problem()!r}")
        for key, val in [("core.fsmonitor", "touch pwned"), ("include.path", "../evil"),
                         ("url.https://evil.example/.insteadOf", "https://github.com/"), ("filter.x.smudge", "sh")]:
            git("config", key, val)
            if "settings the runner doesn't allow" not in clone_problem():
                out.append(f"clone check missed {key}")
            git("config", "--unset-all", key)
        for url in [f"git@github.com:{OWNER}/99-x.git", f"https://evil.example/{OWNER}/99-x.git",
                    f"https://github.com/{OWNER}/99-x-other.git"]:
            git("remote", "set-url", "origin", url)
            if "not https://github.com/" not in clone_problem():
                out.append(f"clone check accepted origin {url}")

        # The script's own git ignores hooks a harness wrote.
        hook = pathlib.Path(d, ".git/hooks/post-checkout")
        hook.write_text(f"#!/bin/sh\ntouch '{d}/HOOK-RAN'\n")
        hook.chmod(0o755)
        subprocess.run(["bash", str(SCRIPT), "--git", "-C", d, "switch", "-q", "main"], capture_output=True)
        if pathlib.Path(d, "HOOK-RAN").exists():
            out.append("run-harness.sh's git ran a hook from .git/hooks")
    return out


if __name__ == "__main__":
    if sys.argv[1:] == ["--self-test"]:
        self_test()
    else:
        sys.exit(__doc__)
