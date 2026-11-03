# One app, one day

| When | Step | Who |
| --- | --- | --- |
| Start | Create the app repo from the template (see below) and tag it | Michael |
| Morning | Spec + issues from the catalog entry | Claude (planner) |
| Midday | Data/API PR and AI feature PR | Claude (builders) |
| Midday | UI pages PR, Terraform for two clouds | Grok Build |
| Afternoon | Review every PR; CI green | Claude (reviewer) + Codex |
| Afternoon | Deploy to the day's cloud, migrate, smoke test | Claude (devops) |
| Evening | README and demo script | Docs (whoever has headroom) |
| Evening | Review and merge; add the DNS record; post the app | Michael |
| Overnight | CI status, free-tier usage, stalled PRs → Build Tracker | Grok Bot |

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

## If an app slips

Ship the core flow that day and move polish to the next simpler app's day, so the one-a-day cadence holds.
When a tool hits its usage limit, relabel its open issues to another tool rather than buying credits.
