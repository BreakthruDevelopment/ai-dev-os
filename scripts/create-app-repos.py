#!/usr/bin/env python3
"""Create the app repos that catalog.yaml marks with `create_repo: true`.

Run by .github/workflows/create-app-repos.yml on pushes to main (and by hand). For each marked app:

- The repo doesn't exist: create it, public, from the template repo; add the topic, the harness labels and a
  `protect-main` ruleset (pull request required, CI must pass, no force pushes or deletion).
- The repo exists with the topic: make sure the labels, topic and ruleset are there (adds only what's missing).
- The repo exists without the topic: REFUSE and touch nothing. It may be one of the org's other applications.

It never renames, deletes, transfers or archives a repo, never changes a repo it didn't create or that lacks the
topic, and never touches apps that aren't marked. Names must match the catalog's own rules (NN-slug).

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
MAX_CREATES_PER_RUN = 6


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
    if len(marked) > MAX_CREATES_PER_RUN:
        sys.exit(f"{len(marked)} apps marked create_repo; at most {MAX_CREATES_PER_RUN} per run")
    return org, topic, template, marked


class GitHub:
    def __init__(self, token):
        self.token = token

    def call(self, method, path, body=None, ok=(200, 201, 204)):
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
            with urllib.request.urlopen(req, timeout=30) as r:
                data = r.read()
                return r.status, (json.loads(data) if data else None)
        except urllib.error.HTTPError as e:
            data = e.read()
            try:
                payload = json.loads(data) if data else None
            except ValueError:
                payload = None
            if e.code in ok:
                return e.code, payload
            return e.code, payload


def ensure_extras(gh, org, name, topic, created):
    """Topic, labels and ruleset. Adds what's missing; never removes or rewrites what's there."""
    status, data = gh.call("GET", f"/repos/{org}/{name}/topics")
    names = (data or {}).get("names", []) if status == 200 else []
    if topic not in names:
        if not created:  # only a repo we just created may be given the topic
            print(f"REFUSE {org}/{name}: exists without the topic {topic}; not touching it")
            return False
        s, _ = gh.call("PUT", f"/repos/{org}/{name}/topics", {"names": sorted(set(names) | {topic})})
        if s != 200:
            print(f"ERROR {org}/{name}: setting the topic failed (HTTP {s})")
            return False
        print(f"  topic {topic}")

    s, existing = gh.call("GET", f"/repos/{org}/{name}/labels?per_page=100")
    have = {l["name"] for l in existing or []} if s == 200 else set()
    for label, (color, desc) in LABELS.items():
        if label in have:
            continue
        s, _ = gh.call("POST", f"/repos/{org}/{name}/labels", {"name": label, "color": color, "description": desc})
        print(f"  label {label}" if s == 201 else f"  WARNING label {label}: HTTP {s}")

    s, rulesets = gh.call("GET", f"/repos/{org}/{name}/rulesets")
    if s == 200 and not any(r.get("name") == "protect-main" for r in rulesets or []):
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
                            "required_status_checks": [{"context": c} for c in REQUIRED_CHECKS],
                        },
                    },
                ],
            },
        )
        print("  ruleset protect-main" if s == 201 else f"  WARNING ruleset protect-main: HTTP {s}")
    return True


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
    for a in marked:
        name = a["repo"]
        status, repo = gh.call("GET", f"/repos/{org}/{name}")
        created = False
        if status == 404:
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
                print(f"ERROR {org}/{name}: creating from {template} failed (HTTP {s})")
                failed = True
                continue
            created = True
            print(f"CREATED {org}/{name} from {org}/{template}")
            for _ in range(30):  # the new repo's contents arrive asynchronously
                s, _ = gh.call("GET", f"/repos/{org}/{name}/commits?per_page=1")
                if s == 200:
                    break
                time.sleep(2)
        elif status == 200:
            if repo.get("archived"):
                print(f"SKIP {org}/{name}: archived")
                continue
            print(f"EXISTS {org}/{name}")
        else:
            print(f"ERROR {org}/{name}: lookup failed (HTTP {status})")
            failed = True
            continue
        if not ensure_extras(gh, org, name, topic, created):
            failed = True
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
