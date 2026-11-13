# Run log — 07-appointment-booking

BreakthruSoftwareFactory run log ([`FACTORY.md`](../FACTORY.md)), **written on 2026-11-13** from GitHub only (merged PRs, PR reviews, `30-apps-infra`, and the `Live smoke test` runs on the repo's `claude/live-smoke` branch). Times are US Central. "Unknown" means GitHub doesn't show it.

| Field | Value |
| --- | --- |
| App | 7, Appointment Booking |
| Spec | [`specs/07-appointment-booking.md`](../specs/07-appointment-booking.md) (ai-dev-os #11, 2026-11-09 3:55 PM) |
| Repo | https://github.com/BreakthruDevelopment/07-appointment-booking |
| Live cloud | Google Cloud (Cloud Run, us-central1) |
| URL | https://app7.breakthruventures.ai |
| `apps.yaml` PR | 30-apps-infra #69 (2026-11-10 6:47 PM), custom domain #70 (10:57 PM), #75 (2026-11-12 2:04 PM, `sha-0f8cdf3`); deploy issues 30-apps-infra #57, #58 |
| Image tag | `sha-0f8cdf3` |
| Live smoke | **pass**, 2026-11-12 2:20 PM, [run 43299333557](https://github.com/BreakthruDevelopment/07-appointment-booking/actions/runs/43299333557): `/api/health` reported `sha-0f8cdf3`; `scripts/smoke.sh` ended `SMOKE PASS` |
| Catalog status | `done` |

## Gates

| Gate | Evidence |
| --- | --- |
| 1 Spec | Spec merged (ai-dev-os #11) |
| 2 Build | 10 merged PRs: claude 8, grok 2. Jules's README PR #7 was closed unmerged |
| 3 Review | Codex reviewed #11 (5 reviews, 11 inline findings: 4 P1, 7 P2) and #14 (1 review, 1 P2). Marked `claude-code` / `ready` reviews on #15, #17 and #18. #8–#13 otherwise have no GitHub review. The review gate's caller workflow reached this repo on 2026-11-10 at 6:43 PM (#13); PRs merged before it carry no `Reviewer: claude-code` review in GitHub. |
| 4 Release | 30-apps-infra #69 (2026-11-10 6:47 PM), custom domain #70 (10:57 PM), #75 (2026-11-12 2:04 PM, `sha-0f8cdf3`); live smoke pass ([run 43299333557](https://github.com/BreakthruDevelopment/07-appointment-booking/actions/runs/43299333557)) |
| 5 Close-out | This log and the catalog status (ai-dev-os, branch `claude/factory-docs-tidy`). Launch drafts: unknown |

## Who did what

Roles from PR titles; harness from the branch prefix. Per-role timing is unknown.

| Role | Harness | PR | Notes |
| --- | --- | --- | --- |
| Full-stack builder | Grok Build; Claude Code | #9; #10 | Availability engine; bookings, cancellation, .ics feed |
| AI builder | Claude Code | #11 | Booking assistant on the tool loop |
| UI builder | Claude Code | #12, #14, #17 | Booking pages, chat panel, home page (UI slices went to Claude, not Grok) |
| Docs writer | Claude Code | #15 | README |
| DevOps / template | Claude Code; Grok | #8, #18; #13 | Fonts, review gate |
| Reviewer | Claude Code (+ Codex's GitHub reviews) | see gate 3 | Codex findings are counted above; whether each was fixed isn't recorded |
| DevOps (deploy) | Claude Code | 30-apps-infra, see header | `claude/` branches |

## AI evals (live model)

Live smoke covers the assistant's guards ("chat page: sign-in required, 404s, panel shell, owner note"). No separate eval recorded.

## Definition of done

- [x] README filled
- [x] Live smoke passed after the latest deploy
- [x] This run log
- [x] `catalog.yaml` `status: done` and `BRIEFING.md` updated

## What slipped or surprised us

- One live smoke failed (run 42967905581, 2026-11-10 11:46 PM: sign-up HTTP 403); the run three minutes later passed.
- Launch drafts: unknown.
