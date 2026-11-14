#!/usr/bin/env python3
"""Open an app's issues from its spec (or a JSON plan), in dependency order, without duplicates.

    python3 scripts/open-issues.py specs/NN-slug.md --dry-run   # print every issue body; nothing is created
    python3 scripts/open-issues.py specs/NN-slug.md             # create them (gh CLI sign-in, REST only)
    python3 scripts/open-issues.py plan.json                    # same, from a JSON plan (richer bodies)
    python3 scripts/open-issues.py specs/NN-slug.md --check     # parse and validate only (no GitHub calls)
    python3 scripts/open-issues.py --self-test                  # parsing tests, incl. templates/spec.md (CI)

Needs Python 3.10+ and the gh CLI (signed in).

Options: --repo NAME (app repo, if the spec's **Repo:** line is missing), --spec-ref REF (commit or branch the
spec links point at; default main).

Every issue gets a `Planned harness: <name>` line, a `## Dependencies` section of full issue URLs and a hidden
`<!-- open-issues id=NN.M -->` marker. Only an issue whose dependencies are all closed gets its harness label,
which is the start signal; on a first run that means the dependency-free issues, the foundation (wave 1).
An issue labelled at creation also gets release-labels.py's "released" comment, so if the runner or a person later
takes the label away, release-labels.py won't put it back. scripts/release-labels.py adds the rest as their
dependencies close (closed as completed, or a merged PR). An issue that already exists (same marker,
or same title in the same repo) is reused, never created twice or edited. `security-sensitive` is added at
creation; it isn't a start signal. Add the new issues to the project board by hand (Projects need GraphQL).

Spec format (templates/spec.md, "Issues"): `### Wave N` headings; under them one numbered item per slice,
    1. **NN.1 `[role] Title`** · `harness` · **2nd: Codex** · repo **`30-apps-infra`**
       What it covers (indented lines). Dependencies: none.
`2nd: Codex` (or `security-sensitive`) marks a security-sensitive slice; `repo` is optional (default: the app repo).
`Dependencies:` lists slice ids separated by commas: `NN.1, NN.3`, ranges `NN.1–NN.3` or `NN.1-3` (expanded), and
anything that isn't a slice id (`D4`, `Day 0 D4 (Michael)`) goes into the body as a plain dependency line. A token
that mixes an id with other text (`NN.1 (schema)`), or holds only digits and punctuation (`143`, or `14,3`, which
splits into `14` and `3`), is refused, so an id can't be lost.

A slice with such a non-issue prerequisite is opened with `hold` and without its harness label, whatever its issue
dependencies: no script can tell when `D4` is done. Claude removes `hold` once the step is done, and
release-labels.py then adds the label when the issue dependencies are done too.

JSON plan: {"repo": "NN-slug", "spec": "specs/NN-slug.md", "issues": [{"id": "NN.1", "title": "[role] Title",
"harness": "claude", "wave": 1, "security_sensitive": true, "deps": [], "repo": null, "body": "markdown",
"extra_deps": ["Day 0 D4 (Michael, not an issue): …"], "notes": ["…"]}]}. `body` replaces the "## Scope" text.

Rules checked before anything is created: ids unique, dependencies known and acyclic, harness known, wave 1 exists
and every wave 1 slice is `claude` and security-sensitive, no slice depends on a later wave, and every slice
outside wave 1 not planned for `claude` depends (directly or not) on a wave 1 slice.
"""
import json
import pathlib
import re
import subprocess
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import issuelib
from issuelib import HARNESSES, OWNER

MARK = "<!-- open-issues id={} -->"
FOOTER = "\n---\n\U0001F916 Generated with [Claude Code](https://claude.com/claude-code)\n"
ID = r"(?:\d+|NN)\.\d+"
ITEM = re.compile(rf"^\s*\d+\.\s+\*\*(?P<id>{ID})\s+`(?P<title>\[[a-z-]+\][^`]*)`\*\*(?P<rest>.*)$")
WAVE = re.compile(r"^###\s+Wave\s+(\d+)\b", re.I)
WAVE1_NOTE = ("Wave 1 (foundation): this slice owns the schema, migrations, roles, access rules and auth config. "
              "Later slices don't change the foundation paths (`src/lib/db/`, `drizzle/`, `drizzle.config.ts`, `src/lib/auth/`, `src/lib/access.ts`, `src/proxy.ts`, `src/middleware.ts`).")
LATER_NOTE = ("Don't create or edit the foundation paths (`src/lib/db/`, `drizzle/`, `drizzle.config.ts`, `src/lib/auth/`, `src/lib/access.ts`, `src/proxy.ts`, `src/middleware.ts`) "
              "unless a security-sensitive `claude` slice is named as the owner: the foundation slice owns them. If the data layer this needs isn't on `main`, or it "
              "needs a schema change, stop and comment here. Never invent schema, migrations, roles or session code.")


class PlanError(ValueError):
    pass


def parse_spec(text: str) -> dict:
    """The spec's Issues section as a plan dict (see the docstring)."""
    lines = text.replace("\r", "").split("\n")
    repo = None
    m = re.search(rf"\*\*Repo:\*\*\s*`(?:{OWNER}/)?([A-Za-z0-9._-]+)`", text)
    if m:
        repo = m.group(1)
    start = next((i for i, ln in enumerate(lines) if re.match(r"^## Issues\b", ln)), None)
    if start is None:
        raise PlanError("no '## Issues' section")
    issues, wave, cur = [], None, None
    for ln in lines[start + 1:]:
        if re.match(r"^## ", ln):
            break
        if (w := WAVE.match(ln)):
            wave, cur = int(w.group(1)), None
            continue
        if (it := ITEM.match(ln)):
            if wave is None:
                raise PlanError(f"{it.group('id')} comes before any '### Wave N' heading")
            cur = {"id": it.group("id"), "title": it.group("title").strip(), "wave": wave, "_rest": it.group("rest"),
                   "_text": []}
            issues.append(cur)
            continue
        if cur is not None and ln.strip() and ln[:1] in " \t":
            cur["_text"].append(ln.strip())
        elif not ln.strip() or not ln.startswith((" ", "\t")):
            cur = None
    for it in issues:
        rest = it.pop("_rest")
        ticks = re.findall(r"`([^`]+)`", rest)
        harness = [t for t in ticks if t in HARNESSES]
        if not harness:
            raise PlanError(f"{it['id']}: no harness (`claude`, `codex`, `grok` or `antigravity`) after the title")
        it["harness"] = harness[0]
        it["security_sensitive"] = bool(re.search(r"2nd:\s*Codex|security-sensitive", rest, re.I))
        rm = re.search(r"\brepo\s+\**`([A-Za-z0-9._-]+)`", rest)
        it["repo"] = rm.group(1) if rm else None
        lead = rest.split("—", 1)[1].strip() if "—" in rest else ""
        text = " ".join(([lead] if lead else []) + it.pop("_text")).strip()
        dm = re.search(r"\bDependencies:\s*(.*)$", text, re.I)
        if not dm:
            raise PlanError(f"{it['id']}: end the slice with 'Dependencies: none.' or 'Dependencies: NN.1, NN.2.'")
        it["deps"], it["extra_deps"] = parse_deps(it["id"], dm.group(1))
        it["text"] = text[:dm.start()].strip()
    if not issues:
        raise PlanError("no slices under '## Issues' (numbered items under '### Wave N' headings)")
    return {"repo": repo, "issues": issues}


RANGE = re.compile(r"^(\d+|NN)\.(\d+)\s*[–-]\s*(?:(\d+|NN)\.)?(\d+)$")


def _split_top(text: str) -> list[str]:
    """Split on commas and semicolons outside parentheses ("and" is split by the caller)."""
    parts, depth, cur = [], 0, ""
    for ch in text:
        depth += ch == "("
        depth -= ch == ")" and depth > 0
        if ch in ",;" and depth == 0:
            parts.append(cur)
            cur = ""
        else:
            cur += ch
    return parts + [cur]


def parse_deps(sid: str, tail: str) -> tuple[list[str], list[str]]:
    """(slice ids, other dependency text) from what follows `Dependencies:`."""
    tail = tail.strip()
    if re.match(r"none\b", tail, re.I):
        return [], []
    ids, extra = [], []
    pieces = [x for raw in _split_top(tail.rstrip("."))
              for x in ([raw] if "(" in raw else re.split(r"\s+and\s+", raw))]
    for raw in pieces:
        tok = re.sub(r"^and\s+", "", raw.strip()).strip().rstrip(".").strip()
        if not tok:
            continue
        if re.fullmatch(ID, tok):
            ids.append(tok)
        elif (m := RANGE.match(tok)):
            major, lo, major2, hi = m.group(1), int(m.group(2)), m.group(3) or m.group(1), int(m.group(4))
            if major2 != major or hi <= lo:
                raise PlanError(f"{sid}: can't read the range '{tok}' (write e.g. 77.1–77.3)")
            ids += [f"{major}.{k}" for k in range(lo, hi + 1)]
        elif re.search(ID, tok):
            raise PlanError(f"{sid}: '{tok}' mixes a slice id with other text; list ids plainly (e.g. '14.1, 14.2')")
        elif re.fullmatch(r"[\d\s.,;:–-]+", tok):
            raise PlanError(f"{sid}: '{tok}' looks like a mistyped slice id; write ids as NN.M (e.g. '14.3')")
        else:
            extra.append(tok)
    if not ids and not extra:
        raise PlanError(f"{sid}: 'Dependencies:' lists nothing (write 'none' if there are none)")
    return list(dict.fromkeys(ids)), extra


def load_plan(path: str) -> dict:
    p = pathlib.Path(path)
    if p.suffix == ".json":
        plan = json.loads(p.read_text())
        for it in plan.get("issues", []):
            it.setdefault("deps", [])
            it.setdefault("security_sensitive", False)
    else:
        plan = parse_spec(p.read_text())
        plan.setdefault("spec", str(p.resolve().relative_to(issuelib.ROOT)) if p.resolve().is_relative_to(issuelib.ROOT)
                        else p.name)
    return plan


def validate(plan: dict) -> list[dict]:
    """Checks the wave rules; returns the issues in an order where dependencies come first."""
    items = plan.get("issues") or []
    by_id = {}
    for it in items:
        for key in ("id", "title", "harness", "wave"):
            if it.get(key) in (None, ""):
                raise PlanError(f"{it.get('id', '?')}: missing '{key}'")
        if it["id"] in by_id:
            raise PlanError(f"{it['id']}: duplicate id")
        if it["harness"] not in HARNESSES:
            raise PlanError(f"{it['id']}: unknown harness '{it['harness']}'")
        if not re.match(r"^\[[a-z-]+\] ", it["title"]):
            raise PlanError(f"{it['id']}: the title must start with the role, e.g. '[ui-builder] Dashboard page'")
        by_id[it["id"]] = it
    if not any(it["wave"] == 1 for it in items):
        raise PlanError("no wave 1 (foundation) slice")
    for it in items:
        for d in it["deps"]:
            if d not in by_id:
                raise PlanError(f"{it['id']}: unknown dependency {d}")
            if by_id[d]["wave"] > it["wave"]:
                raise PlanError(f"{it['id']} (wave {it['wave']}) depends on {d} in a later wave ({by_id[d]['wave']})")
        if it["wave"] == 1 and (it["harness"] != "claude" or not it["security_sensitive"]):
            raise PlanError(f"{it['id']}: wave 1 (foundation) slices are always `claude` and security-sensitive")
    order, done, pending = [], set(), list(items)
    while pending:
        ready = [it for it in pending if all(d in done for d in it["deps"])]
        if not ready:
            raise PlanError("dependency cycle among " + ", ".join(it["id"] for it in pending))
        for it in ready:
            order.append(it)
            done.add(it["id"])
            pending.remove(it)

    def reaches_wave1(i, seen=()):
        return any(by_id[d]["wave"] == 1 or (d not in seen and reaches_wave1(d, seen + (d,))) for d in by_id[i]["deps"])

    for it in items:
        if it["wave"] > 1 and it["harness"] != "claude" and not reaches_wave1(it["id"]):
            raise PlanError(f"{it['id']}: a {it['harness']} slice outside wave 1 must depend on the foundation (wave 1)")
    return order


def labels_for(it: dict, deps_open: bool) -> list[str]:
    """Labels at creation. The harness label (start signal) only with no open dependency and no non-issue
    prerequisite; a non-issue prerequisite (`D4`) means `hold`, which Claude removes once the step is done."""
    held = bool(it.get("extra_deps"))
    return (([] if deps_open or held else [it["harness"]]) + (["security-sensitive"] if it["security_sensitive"] else [])
            + ([issuelib.HOLD_LABEL] if held else []))


def issue_body(it: dict, plan: dict, numbers: dict, spec_ref: str) -> str:
    """numbers: id -> (repo, number) for every dependency."""
    repo = it.get("repo") or plan["repo"]
    head = [f"**{it['id']}** · wave {it['wave']}" + (" (foundation)" if it["wave"] == 1 else ""),
            f"Planned harness: {it['harness']}"]
    if plan.get("spec"):
        head.append(f"**Spec:** [{plan['spec']}, Issues, {it['id']}]"
                    f"(https://github.com/{OWNER}/ai-dev-os/blob/{spec_ref}/{plan['spec']}#issues)")
    parts = ["\n".join(head)]
    parts.append(it["body"].strip() if it.get("body") else f"## Scope\n\n{(it.get('text') or it['title']).strip()}")
    deps = []
    for d in it["deps"]:
        drepo, dn = numbers[d]
        text = f"#{dn}" if drepo == repo else f"{drepo}#{dn}"
        deps.append(f"- Depends on [{text}](https://github.com/{OWNER}/{drepo}/issues/{dn}) ({d})")
    deps += [f"- {x}" for x in it.get("extra_deps", [])]
    parts.append("## Dependencies\n\n" + ("\n".join(deps) if deps else "None; can start now."))
    notes = []
    if it["security_sensitive"]:
        notes.append("Security-sensitive: Codex second review; label the PR `security-sensitive`.")
    notes.append(WAVE1_NOTE if it["wave"] == 1 else LATER_NOTE)
    notes += it.get("notes", [])
    parts.append("## Notes\n\n" + "\n".join(f"- {n}" for n in notes))
    parts.append("Follow the role file named in the title (`ai-dev-os/roles/`) and the app repo's `AGENTS.md`.\n\n"
                 + MARK.format(it["id"]))
    return "\n\n".join(parts) + "\n" + FOOTER


def existing_issues(repo: str) -> tuple[dict, dict]:
    """(marker id -> number, title -> number) for every issue in the repo, open or closed."""
    by_mark, by_title = {}, {}
    for i in issuelib.gh_pages(f"repos/{OWNER}/{repo}/issues?state=all"):
        if "pull_request" in i:
            continue
        if (m := re.search(r"<!-- open-issues id=(\S+) -->", i.get("body") or "")):
            by_mark.setdefault(m.group(1), i["number"])
        by_title.setdefault(i["title"], i["number"])
    return by_mark, by_title


def run(plan: dict, dry: bool, spec_ref: str) -> None:
    if not plan.get("repo"):
        raise PlanError("no app repo: add '**Repo:** `BreakthruDevelopment/NN-slug`' to the spec or pass --repo")
    order = validate(plan)
    repos = sorted({it.get("repo") or plan["repo"] for it in order})
    known = {}
    for r in repos:
        try:
            known[r] = existing_issues(r)
        except issuelib.GhError as e:
            if not dry:
                raise
            print(f"(dry run: can't list {r} issues, assuming none exist: {e})")
            known[r] = ({}, {})
    numbers, states, fake, fresh = {}, issuelib.StateCache(), 9000, set()  # fresh: made in this run, so open
    for it in order:
        repo = it.get("repo") or plan["repo"]
        by_mark, by_title = known[repo]
        n = by_mark.get(it["id"]) or by_title.get(it["title"])
        if n:
            numbers[it["id"]] = (repo, n)
            print(f"exists  {it['id']:<6} {repo}#{n}  {it['title']}")
            continue
        body = issue_body(it, plan, numbers, spec_ref)
        problem = issuelib.intake_problem(body)
        if problem:  # our own output must pass the runner's checks
            raise PlanError(f"{it['id']}: generated body fails the intake check: {problem}")
        # The start signal only when every dependency is done: on a first run, only dependency-free issues.
        open_deps = [d for d in it["deps"] if d in fresh or states.state(*numbers[d]) != "done"]
        labels = labels_for(it, bool(open_deps))
        fresh.add(it["id"])
        if dry:
            fake += 1
            numbers[it["id"]] = (repo, fake)
            print(f"\n--- would create {it['id']} in {repo} (as #{fake} here), labels {labels}: {it['title']}\n{body}")
            continue
        res = issuelib.gh(f"repos/{OWNER}/{repo}/issues", "POST", {"title": it["title"], "body": body, "labels": labels})
        numbers[it["id"]] = (repo, res["number"])
        by_mark[it["id"]] = res["number"]
        if it["harness"] in labels:  # labelled now: record the release, so a label taken away later stays away
            issuelib.gh(f"repos/{OWNER}/{repo}/issues/{res['number']}/comments", "POST", {"body": (
                f"Labelled `{it['harness']}` at creation: no open dependencies, so this is the start signal. "
                f"(`scripts/open-issues.py`)\n\n{issuelib.RELEASE_MARK.format(it['harness'])}")})
        print(f"created {it['id']:<6} {repo}#{res['number']}  labels {labels}  {res['html_url']}", flush=True)
    if not dry:
        print("Add the new issues to the project board. Labels for the rest come from scripts/release-labels.py.")


# --- Self-test --------------------------------------------------------------------------------------------------

SAMPLE = """# 99 — Sample

**Repo:** `BreakthruDevelopment/99-sample`

## Issues

Intro text that isn't a slice.

### Wave 1: foundation

1. **99.1 `[fullstack-builder] Roles, schema and access rules`** · `claude` · **2nd: Codex**
   Tables, migration, roles and `access.ts`. Dependencies: none.

### Wave 2

2. **99.2 `[fullstack-builder] Data functions and routes`** · `antigravity`
   On 99.1's schema. Dependencies: 99.1, Day 0 D3 (Michael, not an issue).
3. **99.3 `[ai-builder] Summaries`** · `claude` · **2nd: Codex** — prompt, schema, evals. Dependencies: 99.1.

### Wave 3

4. **99.4 `[ui-builder] Dashboard`** · `grok` — `/dashboard`. Dependencies: 99.2, 99.3.
5. **99.5 `[devops] Deploy app 99`** · `claude` · repo **`30-apps-infra`** — apps.yaml. Dependencies: 99.4.

**Count:** not a slice.

## Threat model
"""


def self_test() -> None:
    fails = []

    def expect_error(label, plan, fragment):
        try:
            validate(plan)
            fails.append(f"{label}: no error")
        except PlanError as e:
            if fragment not in str(e):
                fails.append(f"{label}: {e}")

    plan = parse_spec(SAMPLE)
    got = [(i["id"], i["harness"], i["wave"], i["security_sensitive"], i["repo"], i["deps"]) for i in plan["issues"]]
    want = [("99.1", "claude", 1, True, None, []), ("99.2", "antigravity", 2, False, None, ["99.1"]),
            ("99.3", "claude", 2, True, None, ["99.1"]), ("99.4", "grok", 3, False, None, ["99.2", "99.3"]),
            ("99.5", "claude", 3, False, "30-apps-infra", ["99.4"])]
    if got != want or plan["repo"] != "99-sample" or plan["issues"][1]["extra_deps"] != ["Day 0 D3 (Michael, not an issue)"]:
        fails.append(f"parse_spec: {got} repo={plan['repo']}")
    if plan["issues"][2]["text"] != "prompt, schema, evals." or plan["issues"][0]["text"] != "Tables, migration, roles and `access.ts`.":
        fails.append(f"parse_spec text: {[i['text'] for i in plan['issues']]}")
    order = [i["id"] for i in validate(plan)]
    if order.index("99.1") > order.index("99.2") or order.index("99.4") > order.index("99.5"):
        fails.append(f"order: {order}")

    numbers = {"99.1": ("99-sample", 1), "99.2": ("99-sample", 2), "99.3": ("99-sample", 3), "99.4": ("99-sample", 4)}
    plan["spec"] = "specs/99-sample.md"
    b4 = issue_body(plan["issues"][3], plan, numbers, "main")
    b5 = issue_body(plan["issues"][4], plan, numbers, "main")
    b1 = issue_body(plan["issues"][0], plan, numbers, "main")
    if issuelib.intake_problem(b4, "grok") or issuelib.planned_harness(b4) != "grok":
        fails.append(f"body 99.4 fails intake: {issuelib.intake_problem(b4, 'grok')}")
    urls = [u for _, _, u in issuelib.dependency_urls(issuelib.dependencies_section(b4))]
    if urls != [f"https://github.com/{OWNER}/99-sample/issues/2", f"https://github.com/{OWNER}/99-sample/issues/3"]:
        fails.append(f"body 99.4 urls: {urls}")
    if "[99-sample#4](https://github.com/BreakthruDevelopment/99-sample/issues/4)" not in b5 or issuelib.intake_problem(b5):
        fails.append("body 99.5: cross-repo dependency link")
    if "None; can start now." not in b1 or MARK.format("99.1") not in b1 or issuelib.intake_problem(b1, "claude"):
        fails.append("body 99.1: dependency-free body")
    if issuelib.run_harness_verdict(b4, "grok") != (True, urls):
        fails.append(f"run-harness.sh disagrees on body 99.4: {issuelib.run_harness_verdict(b4, 'grok')}")

    def variant(**change):
        p = parse_spec(SAMPLE)
        for i in p["issues"]:
            i.update(change.get(i["id"], {}))
        return p

    expect_error("wave 1 not claude", variant(**{"99.1": {"harness": "grok"}}), "always `claude`")
    expect_error("wave 1 not security-sensitive", variant(**{"99.1": {"security_sensitive": False}}), "security-sensitive")
    expect_error("grok slice without the foundation", variant(**{"99.4": {"deps": []}}), "must depend on the foundation")
    expect_error("depends on a later wave", variant(**{"99.2": {"deps": ["99.4"]}}), "later wave")
    expect_error("cycle", variant(**{"99.4": {"deps": ["99.5"]}, "99.5": {"wave": 3}}), "cycle")
    expect_error("unknown dependency", variant(**{"99.2": {"deps": ["99.9"]}}), "unknown dependency")
    expect_error("no wave 1", variant(**{"99.1": {"wave": 2}}), "no wave 1")
    for bad, frag in [(SAMPLE.replace(" Dependencies: none.", ""), "end the slice with"),
                      (SAMPLE.replace("### Wave 1: foundation\n", ""), "before any '### Wave N'"),
                      (SAMPLE.replace("`antigravity`", "`jules`"), "no harness")]:
        try:
            parse_spec(bad)
            fails.append(f"parse_spec accepted a spec missing: {frag}")
        except PlanError as e:
            if frag not in str(e):
                fails.append(f"parse_spec error {e!r}, wanted {frag!r}")

    for tail, want in [("77.1–77.3, D4.", (["77.1", "77.2", "77.3"], ["D4"])),
                       ("77.1-3 and 77.5", (["77.1", "77.2", "77.3", "77.5"], [])),
                       ("NN.2, NN.1–NN.2.", (["NN.2", "NN.1"], [])),
                       ("none.", ([], [])),
                       ("14.1; Day 0 D4 (Michael, before this issue), D5", (["14.1"], ["Day 0 D4 (Michael, before this issue)", "D5"]))]:
        try:
            if parse_deps("t", tail) != want:
                fails.append(f"parse_deps({tail!r}) = {parse_deps('t', tail)}")
        except PlanError as e:
            fails.append(f"parse_deps({tail!r}): {e}")
    for tail in ["14.1 (schema)", "77.3–77.1", "77.1–78.2", "", "143", "14,3", "14.1, 7", "14.3.1"]:
        try:
            parse_deps("t", tail)
            fails.append(f"parse_deps accepted {tail!r}")
        except PlanError:
            pass
    lab = [labels_for(plan["issues"][0], False), labels_for(plan["issues"][1], False), labels_for(plan["issues"][3], True),
           labels_for(plan["issues"][3], False)]
    if lab != [["claude", "security-sensitive"], ["hold"], [], ["grok"]]:
        fails.append(f"labels_for: {lab}")
    b2 = issue_body(plan["issues"][1], plan, numbers, "main")
    if "- Day 0 D3 (Michael, not an issue)" not in b2 or issuelib.intake_problem(b2, "antigravity"):
        fails.append("body 99.2: extra dependency text")

    template = (issuelib.ROOT / "templates" / "spec.md").read_text()
    try:
        tplan = parse_spec(template)
        validate(tplan)
        if not any(i["wave"] == 1 for i in tplan["issues"]):
            fails.append("templates/spec.md: no wave 1")
    except PlanError as e:
        fails.append(f"templates/spec.md doesn't parse: {e}")
    if fails:
        sys.exit("open-issues self-test FAILED:\n  " + "\n  ".join(fails))
    print(f"open-issues self-test ok (sample spec, {len(tplan['issues'])} slices in templates/spec.md, 18 refusals, 5 dependency lists)")


def main(argv: list[str]) -> None:
    if argv == ["--self-test"]:
        self_test()
        return
    args, opts = [], {"--repo": None, "--spec-ref": "main"}
    flags = {"--dry-run": False, "--check": False}
    it = iter(argv)
    for a in it:
        if a in opts:
            opts[a] = next(it, None)
        elif a in flags:
            flags[a] = True
        elif a.startswith("-"):
            sys.exit(f"unknown option {a}\n\n{__doc__}")
        else:
            args.append(a)
    if len(args) != 1:
        sys.exit(__doc__)
    try:
        plan = load_plan(args[0])
        if opts["--repo"]:
            plan["repo"] = opts["--repo"]
        if flags["--check"]:
            order = validate(plan)
            print(f"{args[0]}: {len(order)} slices in {len({i['wave'] for i in order})} waves; rules hold")
            return
        run(plan, flags["--dry-run"], opts["--spec-ref"])
    except (PlanError, issuelib.GhError, subprocess.SubprocessError) as e:
        sys.exit(f"open-issues: {e}")


if __name__ == "__main__":
    main(sys.argv[1:])
