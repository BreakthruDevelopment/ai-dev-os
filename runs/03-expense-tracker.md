# Run log — 03-expense-tracker

BreakthruSoftwareFactory run log ([`FACTORY.md`](../FACTORY.md)), **reconstructed on 2026-11-10** from GitHub and a
live health check; nothing was logged while the app was built. Times are US Central. "Unknown" means GitHub doesn't
show it.

| Field | Value |
| --- | --- |
| App | 3, Expense Tracker |
| Spec | [`specs/03-expense-tracker.md`](../specs/03-expense-tracker.md) (ai-dev-os #7, 2026-11-08) |
| Repo | https://github.com/BreakthruDevelopment/03-expense-tracker |
| Live cloud | Google Cloud (Cloud Run, us-central1) |
| URL | https://app3.breakthruventures.ai |
| `apps.yaml` PR | 30-apps-infra #39, merged 2026-11-08 10:17 AM; domain #41, 10:38 AM |
| Image tag | `sha-811aac4` (30-apps-infra #42, merged 2026-11-08 5:08 PM) |
| Live smoke | **Pass, 2026-11-16** ([run](https://github.com/BreakthruDevelopment/03-expense-tracker/actions/runs/43926456054)): full `scripts/smoke.sh` against the live site. The tag was not re-read on this run — the smoke never compares it (30-apps-template#37) — but this log's `sha-811aac4` health check still matches what `apps.yaml` pins, unchanged since 2026-11-08 |
| Catalog status | **`done`** (ai-dev-os #44) |

## Gates

| Gate | Evidence |
| --- | --- |
| 1 Spec | Spec merged (ai-dev-os #7, 2026-11-08) |
| 2 Build | 12 merged PRs; CI and Publish image green on `main` at the deployed commit |
| 3 Review | 0 of 12 merged PRs carry a GitHub PR review or PR comment. Any review done only inside a harness session left no trace in GitHub |
| 4 Release | Deployed by 30-apps-infra #39, merged 2026-11-08 10:17 AM; domain #41, 10:38 AM; health check passes; smoke result not recorded |
| 5 Close-out | This reconstructed log (2026-11-10). Launch drafts: unknown |

## Who did what

Merged PRs by branch prefix (harness): claude 12. Per-role timing is unknown.

## Definition of done

- [x] README filled
- [x] Live smoke recorded after the latest deploy ([2026-11-16](https://github.com/BreakthruDevelopment/03-expense-tracker/actions/runs/43926456054))
- [x] Run log (this file, reconstructed)
- [x] `catalog.yaml` `status: done`

## What slipped or surprised us

- README: Filled, with live URL and demo script.
- Migration retry needed after the first deploy (infra #40).
