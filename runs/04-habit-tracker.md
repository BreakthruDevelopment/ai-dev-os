# Run log — 04-habit-tracker

BreakthruSoftwareFactory run log ([`FACTORY.md`](../FACTORY.md)), **reconstructed on 2026-11-10** from GitHub and a
live health check; nothing was logged while the app was built. Times are US Central. "Unknown" means GitHub doesn't
show it.

| Field | Value |
| --- | --- |
| App | 4, Habit and Goal Tracker |
| Spec | [`specs/04-habit-tracker.md`](../specs/04-habit-tracker.md) (ai-dev-os #8, 2026-11-08) |
| Repo | https://github.com/BreakthruDevelopment/04-habit-tracker |
| Live cloud | Oracle Cloud (Always Free A1 VM, Phoenix) |
| URL | https://app4.breakthruventures.ai |
| `apps.yaml` PR | 30-apps-infra #45, merged 2026-11-08 9:35 PM |
| Image tag | `sha-c91ffc1` (30-apps-infra #47, merged 2026-11-08 10:56 PM (reminders fix)) |
| Live smoke | Unknown: no `scripts/smoke.sh` result is recorded. `/api/health` answered `ok` with `sha-c91ffc1` on 2026-11-10 at about 2:29 PM |
| Catalog status | `deployed` (not `done`: this log and a recorded live smoke were missing) |

## Gates

| Gate | Evidence |
| --- | --- |
| 1 Spec | Spec merged (ai-dev-os #8, 2026-11-08) |
| 2 Build | 10 merged PRs; CI and Publish image green on `main` at the deployed commit |
| 3 Review | 0 of 10 merged PRs carry a GitHub PR review or PR comment. Any review done only inside a harness session left no trace in GitHub |
| 4 Release | Deployed by 30-apps-infra #45, merged 2026-11-08 9:35 PM; health check passes; smoke result not recorded |
| 5 Close-out | This reconstructed log (2026-11-10). Launch drafts: unknown |

## Who did what

Merged PRs by branch prefix (harness): claude 10. Per-role timing is unknown.

## Definition of done

- [x] README filled
- [ ] Live smoke recorded after the latest deploy (health check only, 2026-11-10)
- [x] Run log (this file, reconstructed)
- [ ] `catalog.yaml` `status: done`

## What slipped or surprised us

- README: Filled, with live URL and demo script.
- Open bug #16 (8-week hit rate counts the in-progress week) has no harness label, so nobody will pick it up.
