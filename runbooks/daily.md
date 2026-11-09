# One app, one day

| When | Step | Who |
| --- | --- | --- |
| Start | Mark the app `create_repo: true` in `catalog.yaml`; the workflow creates and tags the repo (see below) | Claude Code |
| Morning | Spec + issues (role in title, harness label) on the board | Claude Code (planner) |
| Midday | Data/API PR and AI feature PR | Claude Code, overflow to Jules |
| Midday | UI pages PR | Grok Build |
| Midday | Overflow builds; any infra change the app needs in `30-apps-infra` | Jules |
| Afternoon | Review every PR; CI green | Claude Code (reviewer) + Codex |
| Afternoon | Add the app to `apps.yaml` for the day's cloud (PR), smoke test after deploy | Claude Code (devops) |
| Afternoon | AWS days only: run `deploy/aws.sh` in AWS CloudShell | Michael |
| Evening | README and demo script | Docs (whoever has headroom) |
| Evening | Review and merge; add the DNS record; post the app | Michael |
| Overnight | Queued issues → PRs | Codex, Jules, scheduled Claude Code |
| Overnight | CI status, free-tier usage, stalled PRs → Build Tracker | Grok Bot (ops monitor) |

## Creating the day's repo

Repos are created by the **Create app repos** workflow (`scripts/create-app-repos.py`), not by hand:

1. Open a PR in this repo that sets `create_repo: true` on the app in `catalog.yaml`. The PR's check prints what it
   would create; nothing happens yet.
2. Merge it. On `main`, the workflow creates `BreakthruDevelopment/<repo>` from `30-apps-template` (public), adds the
   topic `30-apps-30-days`, the harness labels (`claude`, `grok`, `codex`, `jules`) and a `protect-main` ruleset
   (pull request required, `Lint, test, build, smoke` must pass, no force pushes or deletion).
3. Leave `create_repo: true` in place: rerunning only fills in anything missing. A repo that exists **without** the
   topic is refused and never touched, so the org's other applications are safe. Nothing is ever renamed, deleted
   or archived.

The Build Tracker finds new apps on its own (it reads this catalog and promotes an app once its health check
answers), so no webhook is needed.

### One-time setup: `REPO_CREATOR_TOKEN` (Michael)

A fine-grained personal access token, stored as an Actions secret in this repo:

1. GitHub → your avatar → **Settings → Developer settings → Personal access tokens → Fine-grained tokens →
   Generate new token**.
2. **Resource owner:** `BreakthruDevelopment`. **Expiration:** your choice (90 days is reasonable; the workflow
   says so when it stops working). **Repository access:** All repositories (it has to manage repos that don't
   exist yet).
3. **Repository permissions:** Administration **Read and write** (create repos, topics, rulesets), Contents
   **Read-only** (read the template), Issues **Read and write** (labels), Metadata **Read-only** (required).
   Nothing else.
4. If the org requires approval for fine-grained tokens, approve it under the org's **Settings → Personal access
   tokens → Pending requests**.
5. In this repo: **Settings → Environments → New environment**, name `repo-creator`. Under **Deployment branches and
   tags** choose **Selected branches and tags** and add the rule `main`. Then, in that environment, **Add environment
   secret**: name `REPO_CREATOR_TOKEN`, paste the token. (An environment secret limited to `main` can't be read by
   a branch or pull request, even one that edits the workflow; a plain repository secret could be.)

This is the most powerful secret in the project: it can administer every repo in the org. The workflow only acts
on catalog names, only from `main` (which is protected), and refuses repos without the topic, but the token
itself could do more, so keep it nowhere else and revoke it if it ever leaks.

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

## If an app slips

Ship the core flow that day and move polish to the next simpler app's day, so the one-a-day cadence holds.
When a harness hits its usage limit, relabel its open issues on the board to another harness rather than buying credits.
