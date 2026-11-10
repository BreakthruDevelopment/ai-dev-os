# Retrospective: apps 1–12

Written 2026-11-10 (US Central) when the process was named the **BreakthruSoftwareFactory**
([`FACTORY.md`](../FACTORY.md)), before any work on apps 13–30. Everything here comes from GitHub (READMEs, CI runs,
PRs, issues, rulesets, `30-apps-infra` `apps.yaml`) and one live health check per deployed app at about 2:29 PM
Central on 2026-11-10. Where GitHub doesn't show something, it says unknown.

## Where the twelve apps are

| # | Repo | Cloud | In `apps.yaml` | `/api/health` 2026-11-10 | `main` CI | Merged / open PRs | Open issues | README | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 01-build-tracker | AWS | yes, `sha-a4e6649` | ok | green | 17 / 1 (Jules README #9) | 0 | Filled; header still says "going live" | deployed |
| 2 | 02-notes-kb | Azure | yes, `sha-6675f0b` | ok (after a cold-start timeout) | green | 14 / 0 | 0 | Filled | deployed |
| 3 | 03-expense-tracker | Google Cloud | yes, `sha-811aac4` | ok | green | 12 / 0 | 0 | Filled | deployed |
| 4 | 04-habit-tracker | Oracle | yes, `sha-c91ffc1` | ok | green | 10 / 0 | 1 (bug #16, unlabelled) | Filled | deployed |
| 5 | 05-budget-planner | AWS | no (infra #55 open) | no answer | green | 4 / 1 | 3 | Data/API section only; README issue #5 open | building |
| 6 | 06-read-later | Azure | no (infra #56 open) | no answer | green | 3 / 1 | 4 | **Template placeholder** | building |
| 7 | 07-appointment-booking | Google Cloud | no (infra #57, #58 open) | not checked | green | 4 / 0 | 3 | Partly filled; README issue #6 open | building |
| 8 | 08-loan-portal | Oracle | no (infra #59 open) | not checked | green | 3 / 0 | 3 | Partly filled; README issue #5 open | building |
| 9 | 09-invoicing | AWS | no (infra #60 open) | no answer | green | 5 / 0 | 3 | **Template placeholder** | building |
| 10 | 10-inventory | Azure | no (infra #61 open) | not checked | green | 4 / 0 | 3 | Section filled, template title/intro left | building |
| 11 | 11-helpdesk | Google Cloud | no (infra #62, #63 open) | not checked | green | 2 / 0 | 5 | Section filled, title still "30 Apps Template" | building |
| 12 | 12-restaurant-ordering | Oracle | no (infra #64 open) | not checked | green | 3 / 0 | 3 | Section filled, title still "30 Apps Template" | building |

"No answer" means `https://appN.breakthruventures.ai` didn't respond, as expected for an app that isn't deployed.
The template app is also in `apps.yaml` on all four clouds (`sha-99a8f86`).

## What went well

- **Four apps live on four clouds in five days** (deploy PRs merged 2026-11-05 to 2026-11-08), each answering its
  health check at its own `appN.breakthruventures.ai` with the image tag `apps.yaml` pins.
- **CI is green on `main` in all twelve app repos**, and every merge went through a PR.
- **Deploys became hands-off:** DNS records from Terraform (infra #15), AWS pull-model deployer Lambda (infra #52,
  #53), tracker sync from Cloud Scheduler (infra #48, #50).
- **Batch planning worked:** apps 5–8 and 9–12 were specced, created and issued in batches
  ([`day-0-apps-5-8.md`](../specs/day-0-apps-5-8.md), [`day-0-apps-9-12.md`](../specs/day-0-apps-9-12.md)) with
  dependency-gated labels.
- **The harness mix widened:** apps 1–4 were almost all Claude Code branches (for example 03 and 04: 12 and 10
  `claude/` PRs, none from other harnesses); apps 5–12 have `grok/` and `codex/` PRs and issues labelled for Grok Build.

## Known gaps (honest list)

1. **`runs/` was empty.** No run log was written for any app. Run logs for 1–4 are now reconstructed from GitHub
   ([`01`](01-build-tracker.md), [`02`](02-notes-kb.md), [`03`](03-expense-tracker.md), [`04`](04-habit-tracker.md));
   per-role timing and AI eval results are unknown.
2. **Review left little trace.** Across 81 merged PRs in apps 1–12, 6 carry a GitHub PR review (all in apps 7, 8,
   10, 11, 12) and 10 have any PR comment; some reviews were posted as plain comments (for example
   02-notes-kb #14). Apps 1, 3 and 4 have no review or comment on any merged PR. Nothing enforced the reviewer
   step, so it can't be shown to have happened.
3. **Branch protection is thinner than the runbook says.** `protect-main` as written requires a PR and the CI status
   check with **0 required approvals**. In practice:
   - `ai-dev-os`'s ruleset has "require status checks" on but **no checks listed**, so `check` isn't enforced;
   - `30-apps-template` and apps `01`–`04` have **no ruleset and no branch protection at all** (they predate
     `create-app-repos.py`);
   - apps `05`–`12` have the scripted `protect-main` (PR + `Lint, test, build, smoke`, 0 approvals);
   - `30-apps-infra` requires PRs and its four `Validate` checks.
4. **README debt:** app 06 and app 09 READMEs still have the template's unfilled "What this app does" placeholder
   (checked 2026-11-10). Apps 10, 11 and 12 replaced that section but still carry the template's title or intro;
   app 1's header still says it is going live with the Day 1 deploy. This is **close-out debt**, owned by each
   app's open README issue (06 #5, 09 #6, 10 #6, 11 #6, 12 #5); not fixed in the factory PR.
5. **Live smoke isn't recorded.** No `scripts/smoke.sh` output against a live URL is kept anywhere; only health
   checks (ops report and this pass) are evidenced.
6. **`BRIEFING.md` and `catalog.yaml` were stale:** the briefing said "Next: Day 1" and every app was `planned`.
7. **Loose ends:** 01 Jules README PR #9 open since 2026-11-04 (Jules goes read-only after 2026-11-11); 04 bug #16
   unlabelled; 05 #2 labelled `codex` but Codex has no environment for that repo (ops report, 2026-11-10); 06 #3
   (AI feature) unowned after a Jules error; the nightly ops report couldn't see repos 09–12 on 2026-11-10.
8. **Cadence:** 4 apps live by day 7 of the build (repos from 2026-11-04), against one a day. Apps 5–12 are in
   flight in parallel.

## What changes for apps 13–30

- The process has a name and five gates: spec, build, review, release, close-out ([`FACTORY.md`](../FACTORY.md)).
- **Review is a required check:** the `Reviewer sign-off` check (`.github/workflows/review-gate.yml`) passes only
  when Claude Code's marked review is on the head commit, plus Codex's on `security-sensitive` PRs. Turning it on
  as a *required* check is a ruleset change Michael makes ([`runbooks/daily.md`](../runbooks/daily.md#review-gate-turning-it-on)).
- **Definition of done:** filled README, live smoke, run log, catalog status. `catalog.yaml` gained `building`,
  `deployed` and `done`, and CI refuses `done` without a run log.
- **Run logs start at gate 1** ([`runs/README.md`](README.md)), not after the fact.
