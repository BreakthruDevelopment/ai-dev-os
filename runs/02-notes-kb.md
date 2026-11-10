# Run log — 02-notes-kb

BreakthruSoftwareFactory run log ([`FACTORY.md`](../FACTORY.md)), **reconstructed on 2026-11-10** from GitHub and a
live health check; nothing was logged while the app was built. Times are US Central. "Unknown" means GitHub doesn't
show it.

| Field | Value |
| --- | --- |
| App | 2, Notes and Knowledge Base |
| Spec | [`specs/02-notes-kb.md`](../specs/02-notes-kb.md) (ai-dev-os #5, 2026-11-07) |
| Repo | https://github.com/BreakthruDevelopment/02-notes-kb |
| Live cloud | Azure (Container Apps, East US) |
| URL | https://app2.breakthruventures.ai |
| `apps.yaml` PR | 30-apps-infra #26, merged 2026-11-07 8:23 PM; domain #31, 11:34 PM |
| Image tag | `sha-6675f0b` (30-apps-infra #42, merged 2026-11-08 5:08 PM (apps 1-3 admin-permissions fix)) |
| Live smoke | Unknown: no `scripts/smoke.sh` result is recorded. `/api/health` answered `ok` with `sha-6675f0b` on 2026-11-10 at about 2:29 PM |
| Catalog status | `deployed` (not `done`: this log and a recorded live smoke were missing) |

## Gates

| Gate | Evidence |
| --- | --- |
| 1 Spec | Spec merged (ai-dev-os #5, 2026-11-07) |
| 2 Build | 14 merged PRs; CI and Publish image green on `main` at the deployed commit |
| 3 Review | 0 of 14 merged PRs carry a GitHub PR review; 1 has a review posted as a plain comment (#14, "not ready to merge yet", three blocking fixes). Any review done only inside a harness session left no trace in GitHub |
| 4 Release | Deployed by 30-apps-infra #26, merged 2026-11-07 8:23 PM; domain #31, 11:34 PM; health check passes; smoke result not recorded |
| 5 Close-out | This reconstructed log (2026-11-10). Launch drafts: unknown |

## Who did what

Merged PRs by branch prefix (harness): claude 10, codex 2, grok 2. Per-role timing is unknown.

## Definition of done

- [x] README filled
- [ ] Live smoke recorded after the latest deploy (health check only, 2026-11-10)
- [x] Run log (this file, reconstructed)
- [ ] `catalog.yaml` `status: done`

## What slipped or surprised us

- README: Filled, with live URL and demo script.
- The first request in this pass timed out (scale-to-zero cold start); the retry answered.
