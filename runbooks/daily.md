# One app, one day

| When | Step | Who |
| --- | --- | --- |
| Start | Create the app repo from the template (see below) and tag it | Michael |
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

`30-apps-template` is a GitHub template repository. Each morning:

1. On GitHub: **BreakthruDevelopment/30-apps-template → Use this template → Create a new repository**.
2. Owner `BreakthruDevelopment`, name from `catalog.yaml` (for example `07-appointment-booking`), Public.
3. Add the topic `30-apps-30-days` and turn on branch protection for `main` (require a PR and passing checks).

Or from a terminal with GitHub CLI signed in as Michael:

```bash
gh repo create BreakthruDevelopment/07-appointment-booking --public --template BreakthruDevelopment/30-apps-template
gh repo edit BreakthruDevelopment/07-appointment-booking --add-topic 30-apps-30-days
```

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
