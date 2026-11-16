# Run log — 01-build-tracker

BreakthruSoftwareFactory run log ([`FACTORY.md`](../FACTORY.md)), **reconstructed on 2026-11-10** from GitHub and a
live health check; nothing was logged while the app was built. Times are US Central. "Unknown" means GitHub doesn't
show it.

| Field | Value |
| --- | --- |
| App | 1, Portfolio Build Tracker |
| Spec | [`specs/01-build-tracker.md`](../specs/01-build-tracker.md) (ai-dev-os #3, 2026-11-04) |
| Repo | https://github.com/BreakthruDevelopment/01-build-tracker |
| Live cloud | AWS (Lambda + API Gateway, us-east-2) |
| URL | https://app1.breakthruventures.ai |
| `apps.yaml` PR | 30-apps-infra #12, merged 2026-11-05 1:38 PM |
| Image tag | `sha-de78c18` (30-apps-infra #71) — what `apps.yaml` pins and what the site answers with. Was `sha-a4e6649` (#54, merged 2026-11-09 4:32 PM) when this log was first written |
| Live smoke | **Pass, 2026-11-16** ([run](https://github.com/BreakthruDevelopment/01-build-tracker/actions/runs/43926422042)): full `scripts/smoke.sh` against the live site. `/api/health` answered `ok` with `sha-de78c18`, matching the tag `apps.yaml` pins — read from a one-off workflow step, since the smoke itself never compares the tag (30-apps-template#37) |
| Catalog status | **`done`** (ai-dev-os #44) |

## Gates

| Gate | Evidence |
| --- | --- |
| 1 Spec | Spec merged (ai-dev-os #3, 2026-11-04) |
| 2 Build | 17 merged PRs; CI and Publish image green on `main` at the deployed commit |
| 3 Review | 0 of 17 merged PRs carry a GitHub PR review; 0 have PR comments. Any review done only inside a harness session left no trace in GitHub |
| 4 Release | Deployed by 30-apps-infra #12, merged 2026-11-05 1:38 PM; health check passes; no smoke result was recorded at the time (one was run 2026-11-16, below) |
| 5 Close-out | Log reconstructed 2026-11-10; close-out completed 2026-11-16 (ai-dev-os #44). Launch drafts: unknown |

## Who did what

Merged PRs by branch prefix (harness): claude 14, codex 2, grok 1. Per-role timing is unknown.

## Definition of done

- [x] README filled
- [x] Live smoke recorded after the latest deploy ([2026-11-16](https://github.com/BreakthruDevelopment/01-build-tracker/actions/runs/43926422042))
- [x] Run log (this file, reconstructed)
- [x] `catalog.yaml` `status: done`

## What slipped or surprised us

- README: Filled (problem, AI feature, demo script), but the header still says "going live with the Day 1 deploy"; Jules README PR #9 open since 2026-11-04, unmerged.
- Open: Jules README PR #9 needs a merge-or-close decision (Jules is read-only after 2026-11-11).
