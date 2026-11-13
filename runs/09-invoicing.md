# Run log — 09-invoicing

BreakthruSoftwareFactory run log ([`FACTORY.md`](../FACTORY.md)), **written on 2026-11-13** from GitHub only (merged PRs, PR reviews, `30-apps-infra`, and the `Live smoke test` runs on the repo's `claude/live-smoke` branch). Times are US Central. "Unknown" means GitHub doesn't show it.

| Field | Value |
| --- | --- |
| App | 9, Invoicing |
| Spec | [`specs/09-invoicing.md`](../specs/09-invoicing.md) (ai-dev-os #14, 2026-11-09 10:16 PM) |
| Repo | https://github.com/BreakthruDevelopment/09-invoicing |
| Live cloud | AWS (Lambda + API Gateway, us-east-2) |
| URL | https://app9.breakthruventures.ai |
| `apps.yaml` PR | 30-apps-infra #72 (2026-11-11 10:57 AM, `sha-4171700`); deploy issue 30-apps-infra #60 |
| Image tag | `sha-4171700` |
| Live smoke | **pass**, 2026-11-11 11:10 AM, [run 43065560993](https://github.com/BreakthruDevelopment/09-invoicing/actions/runs/43065560993): `/api/health` reported `sha-4171700`, `"payments":"demo"`; `scripts/smoke.sh` ended `SMOKE PASS` |
| Catalog status | `done` |

## Gates

| Gate | Evidence |
| --- | --- |
| 1 Spec | Spec merged (ai-dev-os #14) |
| 2 Build | 10 merged PRs: claude 7, grok 3 |
| 3 Review | Codex reviewed #11 (summary only, no inline findings), #14 (1 P2) and #15 (2 P2). Marked `claude-code` / `ready` reviews on #14, #15, #16 and #17. #7–#13 otherwise have no GitHub review. The review gate's caller workflow reached this repo on 2026-11-10 at 6:43 PM (#13); PRs merged before it carry no `Reviewer: claude-code` review in GitHub. |
| 4 Release | 30-apps-infra #72 (2026-11-11 10:57 AM, `sha-4171700`); live smoke pass ([run 43065560993](https://github.com/BreakthruDevelopment/09-invoicing/actions/runs/43065560993)) |
| 5 Close-out | This log and the catalog status (ai-dev-os, branch `claude/factory-docs-tidy`). Launch drafts: unknown |

## Who did what

Roles from PR titles; harness from the branch prefix. Per-role timing is unknown.

| Role | Harness | PR | Notes |
| --- | --- | --- | --- |
| Full-stack builder | Claude Code; Grok Build | #10, #11; #14 | Invoicing core, payments (demo + Stripe test mode); invoice PDF |
| AI builder | Claude Code | #7, #12 | Draft invoice lines from notes; add to invoice |
| UI builder | Grok Build | #15 | Invoice list and editor, clients, settings, public invoice, admin |
| Docs writer | Claude Code | #16 | README (merged after the deploy; README changes don't need a redeploy) |
| DevOps / template | Claude Code; Grok | #9, #17; #13 | Demo-identity hooks, review gate |
| Reviewer | Claude Code (+ Codex's GitHub reviews) | see gate 3 | Codex findings are counted above; whether each was fixed isn't recorded |
| DevOps (deploy) | Claude Code | 30-apps-infra, see header | `claude/` branches |

## AI evals (live model)

Live smoke step "draft from notes" and "add to invoice" passed (live model: lines vary, amounts not asserted). No separate eval recorded.

## Definition of done

- [x] README filled
- [x] Live smoke passed after the latest deploy
- [x] This run log
- [x] `catalog.yaml` `status: done` and `BRIEFING.md` updated

## What slipped or surprised us

- Payments run on the demo provider live; Stripe test mode is built but needs `STRIPE_SECRET_KEY` and `STRIPE_WEBHOOK_SECRET`.
- Launch drafts: unknown.
