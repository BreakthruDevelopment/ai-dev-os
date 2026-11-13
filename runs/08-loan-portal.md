# Run log — 08-loan-portal

BreakthruSoftwareFactory run log ([`FACTORY.md`](../FACTORY.md)), **written on 2026-11-13** from GitHub only (merged PRs, PR reviews, `30-apps-infra`, and the `Live smoke test` runs on the repo's `claude/live-smoke` branch). Times are US Central. "Unknown" means GitHub doesn't show it.

| Field | Value |
| --- | --- |
| App | 8, Loan Application Portal |
| Spec | [`specs/08-loan-portal.md`](../specs/08-loan-portal.md) (ai-dev-os #11, 2026-11-09 3:55 PM) |
| Repo | https://github.com/BreakthruDevelopment/08-loan-portal |
| Live cloud | Oracle Cloud (Always Free A1 VM, Phoenix) |
| URL | https://app8.breakthruventures.ai |
| `apps.yaml` PR | 30-apps-infra #67 (2026-11-10 5:07 PM, `sha-86a1723`), #75 (2026-11-12 2:04 PM, `sha-713b6c3`); deploy issue 30-apps-infra #59 |
| Image tag | `sha-713b6c3` |
| Live smoke | **partial**, 2026-11-12 2:20 PM, [run 43299343101](https://github.com/BreakthruDevelopment/08-loan-portal/actions/runs/43299343101): `/api/health` reported `sha-713b6c3`; `/` and `/sign-in` render, `/dashboard` and `/admin` redirect (307). `scripts/smoke.sh` was not run |
| Catalog status | `deployed` (not `done`: `scripts/smoke.sh` has not passed against the live URL; the live check covers health and public pages only.) |

## Gates

| Gate | Evidence |
| --- | --- |
| 1 Spec | Spec merged (ai-dev-os #11) |
| 2 Build | 9 merged PRs: claude 7, grok 2. Jules's README PR #6 was closed unmerged |
| 3 Review | Codex reviewed #8 (2 reviews, 4 inline P2 findings; 2 more unmarked reviews from the shared account) and #11 (1 review, 1 P2). Marked `claude-code` / `ready` reviews on #13, #15 and #16. The review gate's caller workflow reached this repo on 2026-11-10 at 6:43 PM (#10); PRs merged before it carry no `Reviewer: claude-code` review in GitHub. |
| 4 Release | 30-apps-infra #67 (2026-11-10 5:07 PM, `sha-86a1723`), #75 (2026-11-12 2:04 PM, `sha-713b6c3`); live smoke partial ([run 43299343101](https://github.com/BreakthruDevelopment/08-loan-portal/actions/runs/43299343101)) |
| 5 Close-out | This log and the catalog status (ai-dev-os, branch `claude/factory-docs-tidy`). Launch drafts: unknown |

## Who did what

Roles from PR titles; harness from the branch prefix. Per-role timing is unknown.

| Role | Harness | PR | Notes |
| --- | --- | --- | --- |
| Full-stack builder | Grok Build; Claude Code | #8; #11 | Roles, state machine, audit log; document vault |
| AI builder | Claude Code | #9 | Risk rules and AI risk summary |
| UI builder | Claude Code | #12 | Applicant stepper, underwriter queue, admin and audit pages |
| Docs writer | Claude Code | #13 | README |
| DevOps / template | Claude Code; Grok | #7, #15, #16; #10 | Fonts, demo loader on the live host, review gate |
| Reviewer | Claude Code (+ Codex's GitHub reviews) | see gate 3 | Codex findings are counted above; whether each was fixed isn't recorded |
| DevOps (deploy) | Claude Code | 30-apps-infra, see header | `claude/` branches |

## AI evals (live model)

Not exercised by the live check. No eval recorded.

## Definition of done

- [x] README filled
- [ ] Live smoke passed after the latest deploy
- [x] This run log
- [ ] `catalog.yaml` `status: done` and `BRIEFING.md` updated (status is `deployed`)

## What slipped or surprised us

- Four live checks failed on 2026-11-10 between 6:15 and 6:41 PM with TLS errors on `app8` (`tlsv1 alert internal error`) before the first pass at 10:50 PM (run 42961816150).
- The full smoke still needs to run against the live site.
- Launch drafts: unknown.
