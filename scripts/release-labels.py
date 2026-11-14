#!/usr/bin/env python3
"""Give an issue its planned harness label (the start signal) once every dependency is done.

    python3 scripts/release-labels.py --dry-run                       # what it would release, and why not the rest
    python3 scripts/release-labels.py                                 # every repo tagged 30-apps-30-days
    python3 scripts/release-labels.py --repo 14-real-estate --repo 30-apps-infra
    python3 scripts/release-labels.py --verbose                       # also list issues it doesn't manage
    python3 scripts/release-labels.py --self-test                     # parsing tests (CI)

Who runs it: Claude Code after every merge into an app repo or 30-apps-infra (`--repo` for the repos involved),
and the ops monitor nightly (all repos). Uses the gh CLI's own sign-in and REST only; no tokens of its own.
Needs Python 3.10+.

An open issue is released when it has a `Planned harness: <name>` line, no harness label (claude, codex, grok,
antigravity), a `## Dependencies` section whose references are all full issue URLs, and every one of them done:
an issue closed as completed (not "not planned" or a duplicate), or a merged PR.
Then it adds the planned label and comments once (a hidden marker). Safe to run again: it never touches an issue
that already has a harness label, and it skips (and reports):
  - an issue labelled `hold` (the runner adds it when a harness stops and asks for help);
  - an issue released before (by this script, or labelled at creation by open-issues.py) whose label has since been
    removed: a person or the runner took the start signal away, so add it back by hand when it's ready;
  - an issue with no Dependencies section, or with a bare `#12` / `repo#12` there (fix the body first);
Issues without a harness label and without a `Planned harness:` line (made before 2026-11-14, or not slices,
like the ops report) are left alone and only counted; `--verbose` lists them.
"""
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import issuelib
from issuelib import HARNESSES, HOLD_LABEL, OWNER, TOPIC

MARK = issuelib.RELEASE_MARK
MARK_RE = re.compile(r"<!-- release-labels:released harness=")
EXTRA_REPOS = ("30-apps-infra", "30-apps-template", "ai-dev-os")


def repos_from_catalog() -> list[str]:
    """Fallback when the org listing isn't allowed (repo-scoped sessions): the catalog's repos plus the shared
    ones, each checked for the topic with a repo-scoped call."""
    names = re.findall(r"^\s*repo:\s*([A-Za-z0-9._-]+)\s*$", (issuelib.ROOT / "catalog.yaml").read_text(), re.M)
    out = []
    for name in sorted(set(names) | set(EXTRA_REPOS)):
        try:
            r = issuelib.gh(f"repos/{OWNER}/{name}")
        except issuelib.GhError:
            continue  # not created yet, or not reachable from here
        if r.get("owner", {}).get("login") == OWNER and TOPIC in (r.get("topics") or []) and not r.get("archived"):
            out.append(name)
    return out


def decide(issue: dict, comments_fn, states: issuelib.StateCache) -> tuple[str, str]:
    """('release', harness), ('skip', reason), ('unmanaged', why) or ('none', '') if it already has a label."""
    labels = {lab["name"] for lab in issue.get("labels", [])}
    if labels & set(HARNESSES):
        return "none", ""
    body = issue.get("body") or ""
    planned = issuelib.planned_harness(body)
    if not planned:
        return "unmanaged", "no 'Planned harness:' line"
    if HOLD_LABEL in labels:
        return "skip", f"labelled `{HOLD_LABEL}`"
    problem = issuelib.intake_problem(body)
    if problem:
        return "skip", problem
    waiting = states.open_deps(body)
    if waiting:
        return "skip", "waiting on " + ", ".join(waiting)
    if any(MARK_RE.search(c.get("body") or "") for c in comments_fn()):
        return "skip", f"released before and its label was removed since; add `{planned}` by hand when it's ready"
    return "release", planned


def main(argv: list[str]) -> None:
    if argv == ["--self-test"]:
        self_test()
        return
    dry, verbose, repos, it = False, False, [], iter(argv)
    for a in it:
        if a == "--dry-run":
            dry = True
        elif a == "--verbose":
            verbose = True
        elif a == "--repo":
            repos.append(next(it, "") or sys.exit("--repo needs a name"))
        else:
            sys.exit(__doc__)
    try:
        if not repos:
            try:
                repos = issuelib.topic_repos()
            except issuelib.GhError:
                repos = repos_from_catalog()
        states, released, skipped, unmanaged = issuelib.StateCache(), 0, 0, 0
        for repo in repos:
            meta = issuelib.gh(f"repos/{OWNER}/{repo}")
            if TOPIC not in (meta.get("topics") or []) or meta.get("archived"):
                print(f"{repo}: not an active repo with the topic {TOPIC}; left alone")
                continue
            for issue in issuelib.gh_pages(f"repos/{OWNER}/{repo}/issues?state=open"):
                if "pull_request" in issue:
                    continue
                n = issue["number"]
                verdict, detail = decide(issue, lambda: issuelib.gh_pages(f"repos/{OWNER}/{repo}/issues/{n}/comments"),
                                         states)
                if verdict == "none":
                    continue
                if verdict == "unmanaged":
                    unmanaged += 1
                    if verbose:
                        print(f"ignore   {repo}#{n}: {detail}  ({issue['title']})")
                    continue
                if verdict == "skip":
                    skipped += 1
                    print(f"skip     {repo}#{n}: {detail}  ({issue['title']})")
                    continue
                released += 1
                if dry:
                    print(f"would add `{detail}` to {repo}#{n}  ({issue['title']})")
                    continue
                issuelib.gh(f"repos/{OWNER}/{repo}/issues/{n}/labels", "POST", {"labels": [detail]})
                issuelib.gh(f"repos/{OWNER}/{repo}/issues/{n}/comments", "POST", {"body": (
                    f"Every dependency is done (completed or merged), so the planned harness label `{detail}` was added: that's the start "
                    f"signal. (`scripts/release-labels.py`)\n\n{MARK.format(detail)}")})
                print(f"added `{detail}` to {repo}#{n}  ({issue['title']})", flush=True)
        print(f"{'dry run: would release' if dry else 'released'} {released}; skipped {skipped}; "
              f"{unmanaged} unlabelled issue(s) have no 'Planned harness:' line{'' if verbose else ' (--verbose lists them)'}; "
              f"repos: {' '.join(repos)}")
    except issuelib.GhError as e:
        sys.exit(f"release-labels: {e}")


# --- Self-test --------------------------------------------------------------------------------------------------

def self_test() -> None:
    U = f"https://github.com/{OWNER}/14-real-estate/issues"

    class FakeStates(issuelib.StateCache):
        def __init__(self, closed, other="open"):
            super().__init__()
            self._closed, self._other = closed, other

        def state(self, repo, number):
            return "done" if (repo, number) in self._closed else self._other

    deps = f"## Dependencies\n\n- Depends on [#1]({U}/1) (14.1)\n- Depends on [#4]({U}/4) (14.4)\n"
    body = f"**14.7** · wave 3\nPlanned harness: grok\n\n## Scope\n\nx\n\n{deps}\n---\nfooter"
    closed = FakeStates({("14-real-estate", 1), ("14-real-estate", 4)})
    half = FakeStates({("14-real-estate", 1)})
    not_planned = FakeStates({("14-real-estate", 1)}, "closed as not_planned")
    released = [{"body": "x\n\n" + MARK.format("grok")}]

    def issue(b=body, labels=()):
        return {"body": b, "labels": [{"name": x} for x in labels]}

    cases = [
        ("all closed", issue(), closed, [], ("release", "grok")),
        ("one open", issue(), half, [], ("skip", "waiting on")),
        ("one closed as not planned", issue(), not_planned, [], ("skip", "closed as not_planned")),
        ("already labelled", issue(labels=["grok"]), half, [], ("none", "")),
        ("claude-labelled", issue(labels=["claude", "security-sensitive"]), closed, [], ("none", "")),
        ("on hold", issue(labels=[HOLD_LABEL]), closed, [], ("skip", "labelled `hold`")),
        ("released before, label removed", issue(), closed, released, ("skip", "released before")),
        ("bare #1", issue(body.replace(f"[#1]({U}/1)", "#1")), closed, [], ("skip", "aren't full issue URLs")),
        ("no section", issue("Planned harness: grok\n\nDepends on #1"), closed, [], ("skip", "no '## Dependencies'")),
        ("no planned line", issue(body.replace("Planned harness: grok\n", "")), closed, [], ("unmanaged", "no 'Planned harness:'")),
        ("unknown harness", issue(body.replace("grok", "jules")), closed, [], ("skip", "unknown planned harness")),
        ("no dependencies", issue("Planned harness: antigravity\n## Dependencies\nNone; can start now.\n"), half, [],
         ("release", "antigravity")),
    ]
    fails = []
    for name, iss, states, comments, (verdict, frag) in cases:
        got = decide(iss, lambda c=comments: c, states)
        if got[0] != verdict or frag not in got[1]:
            fails.append(f"{name}: {got}")
    catalog = re.findall(r"^\s*repo:\s*([A-Za-z0-9._-]+)\s*$", (issuelib.ROOT / "catalog.yaml").read_text(), re.M)
    if len(catalog) < 30:
        fails.append(f"catalog.yaml repo names: found {len(catalog)}")
    if fails:
        sys.exit("release-labels self-test FAILED:\n  " + "\n  ".join(fails))
    print(f"release-labels self-test ok ({len(cases)} cases, {len(catalog)} catalog repos)")


if __name__ == "__main__":
    main(sys.argv[1:])
