#!/usr/bin/env python3
"""Create the app repos that catalog.yaml marks with `create_repo: true`.

Run by .github/workflows/create-app-repos.yml on pushes to main (and by hand). For each marked app:

- The repo doesn't exist: create it, public, from the template repo; add the topic, the harness labels and a
  `protect-main` ruleset (pull request required, CI must pass, no force pushes or deletion).
- The repo exists with the topic: make sure the labels, topic and ruleset are there (adds only what's missing).
- The repo exists without the topic: REFUSE and touch nothing, unless GitHub says it was made from the template
  (a run that stopped between creating it and tagging it). It may be one of the account's other applications.
- The name redirects (a renamed or transferred repo) or GitHub answers with a different repo: REFUSE.

It never renames, deletes, transfers or archives a repo, never changes a repo it didn't create or that lacks the
topic, and never touches apps that aren't marked. At most 4 new repos per run; the rest wait for the next run. Names must match the catalog's own rules (NN-slug).

  --dry-run   validate the catalog and print the plan; no token needed and nothing is called
  --check     validate only (used by the Check workflow)

Needs REPO_CREATOR_TOKEN (fine-grained token in the repo-creator environment, see runbooks/daily.md).
"""

import json
import os
import re
import sys
import time
import urllib.error
import urllib.request

import yaml

API = "https://api.github.com"
LABELS = {  # harness labels the playbook uses (AGENTS.md section 3)
    "claude": ("6f42c1", "Work for Claude Code"),
    "grok": ("d93f0b", "Work for Grok Build"),
    "codex": ("0e8a16", "Work for Codex"),
    "jules": ("1d76db", "Work for Jules"),
}
REQUIRED_CHECKS = ["Lint, test, build, smoke"]  # the template's CI job, which runs on every pull request
MAX_CREATES_PER_RUN = 4  # new repos per run; apps stay marked, so only creations count


def load_catalog(path="catalog.yaml"):
    cat = yaml.safe_load(open(path))
    org, topic, template = cat["github_org"], cat["repo_topic"], cat["template_repo"]
    marked = []
    for a in cat["apps"]:
        flag = a.get("create_repo", False)
        if not isinstance(flag, bool):
            sys.exit(f"app {a['n']}: create_repo must be true or false")
        if not flag:
            continue
        name = a["repo"]
        if not re.fullmatch(rf"{a['n']:02d}-[a-z0-9]+(-[a-z0-9]+)*", name) or len(name) > 60:
            sys.exit(f"app {a['n']}: repo name {name!r} must be NN-slug in lowercase")
        if name == template:
            sys.exit("the template repo can't be an app")
        marked.append(a)
    return org, topic, template, marked


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    """A renamed or transferred repo answers its old name with a redirect to a different repo. Never follow it."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


_OPENER = urllib.request.build_opener(_NoRedirect)


class GitHub:
    def __init__(self, token):
        self.token = token

    def call(self, method, path, body=None):
        """Returns (status, json or None). A 3xx comes back as its status, never followed."""
        req = urllib.request.Request(
            API + path,
            method=method,
            data=None if body is None else json.dumps(body).encode(),
            headers={
                "Authorization": f"Bearer {self.token}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
                "User-Agent": "30apps-create-app-repos",
            },
        )
        try:
            with _OPENER.open(req, timeout=30) as r:
                data = r.read()
                return r.status, (json.loads(data) if data else None)
        except urllib.error.HTTPError as e:
            data = e.read()
            try:
                payload = json.loads(data) if data else None
            except ValueError:
                payload = None
            return e.code, payload
        except urllib.error.URLError as e:
            return 0, {"message": f"network error: {e.reason}"}


def why(payload):
    msg = (payload or {}).get("message") if isinstance(payload, dict) else None
    return f": {msg}" if msg else ""


def ensure_extras(gh, org, name, topic, created, from_template):
    """Topic, labels and ruleset. Adds what's missing; never removes or rewrites what's there."""
    status, data = gh.call("GET", f"/repos/{org}/{name}/topics")
    names = (data or {}).get("names", []) if status == 200 else []
    if topic not in names:
        # Only a repo this workflow created (now, or in a run that stopped before the topic) may be given the topic.
        if not (created or from_template):
            print(f"REFUSE {org}/{name}: exists without the topic {topic}; not touching it")
            return False
        for attempt in range(5):  # a just-generated repo can briefly refuse writes
            s, p = gh.call("PUT", f"/repos/{org}/{name}/topics", {"names": sorted(set(names) | {topic})})
            if s == 200:
                break
            time.sleep(3)
        if s != 200:
            print(f"ERROR {org}/{name}: setting the topic failed (HTTP {s}{why(p)})")
            return False
        print(f"  topic {topic}")

    ok = True
    s, existing = gh.call("GET", f"/repos/{org}/{name}/labels?per_page=100")
    if s != 200:
        print(f"ERROR {org}/{name}: listing labels failed (HTTP {s}{why(existing)})")
        return False
    have = {l["name"] for l in existing or []}
    for label, (color, desc) in LABELS.items():
        if label in have:
            continue
        s, p = gh.call("POST", f"/repos/{org}/{name}/labels", {"name": label, "color": color, "description": desc})
        if s == 201:
            print(f"  label {label}")
        else:
            print(f"ERROR {org}/{name}: label {label} failed (HTTP {s}{why(p)})")
            ok = False

    s, rulesets = gh.call("GET", f"/repos/{org}/{name}/rulesets")
    if s != 200:
        print(f"ERROR {org}/{name}: listing rulesets failed (HTTP {s}{why(rulesets)})")
        return False
    if not any(r.get("name") == "protect-main" for r in rulesets or []):
        s, _ = gh.call(
            "POST",
            f"/repos/{org}/{name}/rulesets",
            {
                "name": "protect-main",
                "target": "branch",
                "enforcement": "active",
                "conditions": {"ref_name": {"include": ["~DEFAULT_BRANCH"], "exclude": []}},
                "rules": [
                    {"type": "deletion"},
                    {"type": "non_fast_forward"},
                    {
                        "type": "pull_request",
                        "parameters": {
                            "required_approving_review_count": 0,
                            "dismiss_stale_reviews_on_push": False,
                            "require_code_owner_review": False,
                            "require_last_push_approval": False,
                            "required_review_thread_resolution": False,
                        },
                    },
                    {
                        "type": "required_status_checks",
                        "parameters": {
                            "strict_required_status_checks_policy": False,
                            # 15368 is GitHub Actions: a commit status posted by anything else doesn't count.
                            "required_status_checks": [{"context": c, "integration_id": 15368} for c in REQUIRED_CHECKS],
                        },
                    },
                ],
            },
        )
        if s == 201:
            print("  ruleset protect-main")
        else:
            print(f"ERROR {org}/{name}: ruleset protect-main failed (HTTP {s}{why(_)})")
            ok = False
    return ok


def main():
    dry = "--dry-run" in sys.argv
    check = "--check" in sys.argv
    org, topic, template, marked = load_catalog()
    if check:
        print(f"create_repo ok: {', '.join(a['repo'] for a in marked) or 'none marked'}")
        return 0
    if dry:
        for a in marked:
            print(f"would ensure {org}/{a['repo']} from {org}/{template} with topic {topic}")
        return 0

    token = os.environ.get("REPO_CREATOR_TOKEN", "")
    if not token:
        print("REPO_CREATOR_TOKEN isn't set; nothing done. See runbooks/daily.md, Creating the day's repo.")
        return 1 if marked else 0
    gh = GitHub(token)
    failed = False
    creations = 0
    for a in marked:
        name = a["repo"]
        status, repo = gh.call("GET", f"/repos/{org}/{name}")
        created = from_template = False
        if 300 <= status < 400:
            print(f"REFUSE {org}/{name}: the name redirects (renamed or transferred repo); not touching it")
            failed = True
            continue
        if status == 404:
            if creations >= MAX_CREATES_PER_RUN:
                print(f"LATER {org}/{name}: {MAX_CREATES_PER_RUN} repos created this run; rerun to continue")
                continue
            creations += 1
            s, _ = gh.call(
                "POST",
                f"/repos/{org}/{template}/generate",
                {
                    "owner": org,
                    "name": name,
                    "description": f"App {a['n']} of 30 apps in 30 days: {a['name']}",
                    "private": False,
                    "include_all_branches": False,
                },
            )
            if s != 201:
                print(f"ERROR {org}/{name}: creating from {template} failed (HTTP {s}{why(_)})")
                failed = True
                continue
            created = True
            print(f"CREATED {org}/{name} from {org}/{template}")
            for _ in range(60):  # the new repo's contents arrive asynchronously
                s, _ = gh.call("GET", f"/repos/{org}/{name}/commits?per_page=1")
                if s == 200:
                    break
                time.sleep(2)
            else:
                print(f"WARNING {org}/{name}: still generating after 2 minutes; continuing")
        elif status == 200:
            if (repo.get("full_name", "").lower() != f"{org}/{name}".lower()
                    or (repo.get("owner") or {}).get("login", "").lower() != org.lower()):
                print(f"REFUSE {org}/{name}: GitHub answered with {repo.get('full_name')}; not touching it")
                failed = True
                continue
            if repo.get("archived") or repo.get("fork"):
                print(f"SKIP {org}/{name}: archived or a fork")
                continue
            from_template = ((repo.get("template_repository") or {}).get("full_name", "").lower()
                             == f"{org}/{template}".lower())
            print(f"EXISTS {org}/{name}")
        else:
            print(f"ERROR {org}/{name}: lookup failed (HTTP {status})")
            failed = True
            continue
        if not ensure_extras(gh, org, name, topic, created, from_template):
            failed = True
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
