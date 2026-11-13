# Run log — 05-budget-planner

BreakthruSoftwareFactory run log ([`FACTORY.md`](../FACTORY.md)), **written on 2026-11-13** from GitHub only (merged PRs, PR reviews, `30-apps-infra`, and the `Live smoke test` runs on the repo's `claude/live-smoke` branch). Times are US Central. "Unknown" means GitHub doesn't show it.

| Field | Value |
| --- | --- |
| App | 5, Personal Budget Planner |
| Spec | [`specs/05-budget-planner.md`](../specs/05-budget-planner.md) (ai-dev-os #11, 2026-11-09 3:55 PM) |
| Repo | https://github.com/BreakthruDevelopment/05-budget-planner |
| Live cloud | AWS (Lambda + API Gateway, us-east-2) |
| URL | https://app5.breakthruventures.ai |
| `apps.yaml` PR | 30-apps-infra #65 (2026-11-10 4:01 PM, `sha-31081ae`), #75 (2026-11-12 2:04 PM, `sha-50aa60b`); deploy issue 30-apps-infra #55 |
| Image tag | `sha-50aa60b` |
| Live smoke | **pass**, 2026-11-12 2:20 PM, [run 43299326910](https://github.com/BreakthruDevelopment/05-budget-planner/actions/runs/43299326910): `/api/health` reported `sha-50aa60b`, `"bank":"demo"`; `scripts/smoke.sh` ended `SMOKE PASS` |
| Catalog status | `done` |

## Gates

| Gate | Evidence |
| --- | --- |
| 1 Spec | Spec merged (ai-dev-os #11) |
| 2 Build | 9 merged PRs: claude 6, grok 2, codex 1. Jules's README PR #6 was closed unmerged |
| 3 Review | Marked `claude-code` / `ready` reviews on #14, #15 and #16, one round each. #7–#13 have no GitHub review. No Codex review on any PR. The review gate's caller workflow reached this repo on 2026-11-10 at 6:43 PM (#13); PRs merged before it carry no `Reviewer: claude-code` review in GitHub. |
| 4 Release | 30-apps-infra #65 (2026-11-10 4:01 PM, `sha-31081ae`), #75 (2026-11-12 2:04 PM, `sha-50aa60b`); live smoke pass ([run 43299326910](https://github.com/BreakthruDevelopment/05-budget-planner/actions/runs/43299326910)) |
| 5 Close-out | This log and the catalog status (ai-dev-os, branch `claude/factory-docs-tidy`). Launch drafts: unknown |

## Who did what

Roles from PR titles; harness from the branch prefix. Per-role timing is unknown.

| Role | Harness | PR | Notes |
| --- | --- | --- | --- |
| Full-stack builder | Codex | #8 | Budget data layer, idempotent demo bank sync |
| Full-stack builder | Claude Code | #15 | Plaid bank sync: built, off until Plaid keys are entered |
| AI builder | Claude Code | #9 | Categorization and cash-flow explanation |
| UI builder | Grok Build | #12 | Overview, transactions, budgets, accounts, admin |
| Docs writer | Claude Code | #14 | README |
| DevOps / template | Claude Code; Grok | #7, #11, #16; #13 | Self-hosted fonts, demo-identity hooks, review-gate caller and its permissions |
| Reviewer | Claude Code (+ Codex's GitHub reviews) | see gate 3 | Codex findings are counted above; whether each was fixed isn't recorded |
| DevOps (deploy) | Claude Code | 30-apps-infra, see header | `claude/` branches |

## AI evals (live model)

Live smoke step "AI categorize and cash-flow summary (cached on unchanged data, private per user)" passed. No separate eval recorded.

## Definition of done

- [x] README filled
- [x] Live smoke passed after the latest deploy
- [x] This run log
- [x] `catalog.yaml` `status: done` and `BRIEFING.md` updated

## What slipped or surprised us

- Plaid is built but the live app runs the demo bank until Michael enters `PLAID_CLIENT_ID`, `PLAID_SECRET` and `TOKEN_ENC_KEY`.
- Six of nine PRs merged before the review gate existed and left no review in GitHub.
- Launch drafts: unknown.
