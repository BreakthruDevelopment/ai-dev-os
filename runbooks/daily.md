# One app, one day

The BreakthruSoftwareFactory's day ([`FACTORY.md`](../FACTORY.md)): gate 1 spec (morning), gate 2 build and gate 3
review (through the day), gate 4 release (afternoon), gate 5 close-out (evening).

| When | Step | Who |
| --- | --- | --- |
| Start | Mark the app `create_repo: true` in `catalog.yaml`; the workflow creates and tags the repo (see below) | Claude Code |
| Morning | Spec + issues (role in title, planned harness in the spec) on the board | Claude Code (planner) |
| Through the day | Add an issue's harness label once its dependencies are merged (the start signal) | Claude Code |
| Through the day | Run `scripts/run-harness.sh grok` (and `antigravity`) on the Mac; see `runbooks/harnesses-on-mac.md` | Michael |
| Midday | Data/API PRs | Grok Build; Codex or Antigravity on the issues assigned to them |
| Midday | AI feature PR; template changes | Claude Code |
| Midday | UI pages PR | Grok Build |
| Afternoon | Review every PR as a marked PR review (`Reviewer: claude-code` / `Verdict: ready`); `Reviewer sign-off` and CI green before merge | Claude Code (reviewer); Codex second review on `security-sensitive` PRs |
| Afternoon | Add the app to `apps.yaml` for the day's cloud (PR), smoke test after deploy | Claude Code (devops) |
| Afternoon | AWS days only: run `deploy/aws.sh` in AWS CloudShell | Michael |
| Evening | README and demo script | Grok Build (or Antigravity) |
| Evening | Launch post drafts (X, LinkedIn) and a two-minute demo script from the README and live URL | Grok Bot, from what Michael pastes in |
| Evening | Review and merge; post the app (DNS records are created in Cloudflare by the deploy) | Michael |
| Evening | Close-out: run log in `runs/NN-slug.md`, `catalog.yaml` status, `BRIEFING.md` "Where things stand"; `done` only when the definition of done holds | Claude Code (devops) |
| Overnight | Queued issues → PRs | Codex and scheduled Claude Code tasks; Grok Build and Antigravity if the runner is left going |
| 5:37 AM Central | CI status, stalled work, app health, free-tier usage → `Ops report (nightly)` issue in `ai-dev-os` | Scheduled Claude Code task (ops monitor) |

## Creating the day's repo

Repos are created by the **Create app repos** workflow (`scripts/create-app-repos.py`), not by hand:

1. Open a PR in this repo that sets `create_repo: true` on the app in `catalog.yaml`. The PR's check prints what it
   would create; nothing happens yet.
2. Merge it. On `main`, the workflow creates `BreakthruDevelopment/<repo>` from `30-apps-template` (public), adds the
   topic `30-apps-30-days`, the harness labels (`claude`, `codex`, `grok`, `antigravity`) and a `protect-main` ruleset
   (pull request required, `Lint, test, build, smoke` from GitHub Actions must pass, no force pushes or deletion).
   At most 4 new repos per run; rerun the workflow for more.
3. Leave `create_repo: true` in place: reruns only fill in what's missing. A repo that exists **without** the topic is
   refused and never touched (unless GitHub says it was made from the template, i.e. a run that stopped half way),
   and so is a name that redirects to a renamed or transferred repo. Nothing is ever renamed, deleted or archived.
4. Optional: add the Build Tracker webhook (`TRACKER_URL=<tracker base URL> scripts/add-tracker-webhook.sh <repo>`,
   with GitHub CLI signed in as Michael). Without it the tracker still finds the app and marks it live once its
   health check answers; the webhook adds pushes, PRs and CI results to the app's page.

### One-time setup (Michael)

**Protect `main` in this repo first**, since whatever lands on `main` can create repos: **Settings → Rules → Rulesets
→ New branch ruleset**, name `protect-main`, Active, target the default branch, turn on **Restrict deletions**,
**Block force pushes**, **Require a pull request before merging** (0 approvals) and **Require status checks to pass**
with `check`. (Checked 2026-11-10: the ruleset exists but its status-check list is empty, so `check` isn't
enforced yet. See "Review gate: turning it on" below.)

**The token**, `REPO_CREATOR_TOKEN`, a fine-grained personal access token kept as an *environment* secret:

1. GitHub → your avatar → **Settings → Developer settings → Personal access tokens → Fine-grained tokens →
   Generate new token**.
2. **Resource owner:** `BreakthruDevelopment`. **Expiration:** 90 days (the workflow fails with a 401 when it lapses;
   make a new one). **Repository access:** All repositories (it has to manage repos that don't exist yet).
3. **Repository permissions:** Administration **Read and write** (create repos, topics, rulesets), Contents
   **Read-only** (read the template), Issues **Read and write** (labels), Metadata **Read-only** (required).
   Nothing else.
4. In this repo: **Settings → Environments**, open `repo-creator` (it may already exist from the workflow's first
   run) or create it. Under **Deployment branches and tags** choose **Selected branches and tags** and add the
   branch rule `main`. Optionally add yourself under **Required reviewers**, so each run waits for your approval.
5. In that environment, **Add environment secret**: name `REPO_CREATOR_TOKEN`, paste the token. Not a repository
   secret: those can be read from any branch.

This is the most powerful secret in the project: it can administer every repo under BreakthruDevelopment. The
workflow only acts on catalog names, only from `main`, and refuses repos without the topic, but the token itself
could do more. Agents work as the same GitHub account, so these rules guard against mistakes rather than against
that account; keep the token nowhere else and revoke it if it ever leaks.

By hand, if the workflow can't run: **30-apps-template → Use this template → Create a new repository**, owner
`BreakthruDevelopment`, the catalog name, Public; then add the topic `30-apps-30-days`.

## Deploying the day's app

Deploys live in [`30-apps-infra`](https://github.com/BreakthruDevelopment/30-apps-infra). Once the app's image is
published (its `publish` workflow tags `sha-<7>`), add it to `apps.yaml`:

```yaml
  - name: build-tracker
    clouds: [aws]                 # the day's live_cloud; add more to run it elsewhere too
    image: ghcr.io/breakthrudevelopment/01-build-tracker
    tag: sha-1a2b3c4             # never "latest"
    domain: app1.breakthruventures.ai
    ai: gemini                   # or demo
```

- **Azure, Google Cloud, Oracle:** merging the PR deploys it. Oracle's VM picks it up within 2 minutes.
- **AWS:** after the merge, Michael runs in AWS CloudShell:
  `curl -fsSL https://raw.githubusercontent.com/BreakthruDevelopment/30-apps-infra/main/deploy/aws.sh | bash`
- The app migrates its own database on startup. Then run `BASE_URL=<url> scripts/smoke.sh` from the app repo.
- The app's GHCR package must be **public** (Package settings → Change visibility) so every cloud can pull it.

## Review gate: turning it on

Gate 3 is enforced by the `Reviewer sign-off` check from [`.github/workflows/review-gate.yml`](../.github/workflows/review-gate.yml).
The workflow reports on every PR in this repo as soon as it is on `main`; making it **required** is a ruleset change
only Michael makes. Required approvals stay at 0 and nothing removes Michael's ability to merge. No ruleset was
changed when this was added (2026-11-10).

**1. `ai-dev-os` (do this first).** Settings → Rules → Rulesets → `protect-main` → **Require status checks to pass**
→ add `check` and `Reviewer sign-off` (source: GitHub Actions). Leave **Require a pull request** at 0 approvals.
Optionally add **Repository admin** as a bypass actor ("for pull requests only") as an emergency override; since all
agents use the same account, they could bypass too, so only do it if you want the override.

**2. App repos (one at a time, only when you choose).** The playbook's `create-app-repos.py` puts the same
`protect-main` on every new app repo, but it only creates a ruleset that is missing and never edits one, and it
was **not** changed here. Requiring a check a repo doesn't run would block every merge there, so for each repo:

1. Add `.github/workflows/review-gate.yml` to the repo (better: once to `30-apps-template`, then to each existing
   app repo by PR):

   ```yaml
   name: Review gate
   on:
     pull_request:
       types: [opened, synchronize, reopened, labeled, unlabeled, ready_for_review]
     pull_request_review:
       types: [submitted, edited, dismissed]
   permissions:
     contents: read
     pull-requests: read
   jobs:
     review:
       uses: BreakthruDevelopment/ai-dev-os/.github/workflows/review-gate.yml@main
   ```

2. Create the `security-sensitive` label in the repo.
3. Once the check has reported on a PR, add `review / Reviewer sign-off` to that repo's `protect-main` required
   checks.
4. For apps 13–30: after the template has the caller workflow, add `"review / Reviewer sign-off"` to
   `REQUIRED_CHECKS` in `scripts/create-app-repos.py` (a PR here) so new repos get it from the start.

`30-apps-template` and apps 01–04 have **no** `protect-main` today (checked 2026-11-10); adding one there is
Michael's call, in Settings or by rerunning the scripted pattern by hand.

## If an app slips

Ship the core flow that day and move polish to the next simpler app's day, so the one-a-day cadence holds.
When a harness hits its usage limit, relabel its open issues on the board to another harness rather than buying credits.
