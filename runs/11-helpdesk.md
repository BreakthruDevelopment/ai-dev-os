# Run log — 11-helpdesk

BreakthruSoftwareFactory run log ([`FACTORY.md`](../FACTORY.md)), **written on 2026-11-13** from GitHub only (merged PRs, PR reviews, `30-apps-infra`, and the `Live smoke test` runs on the repo's `claude/live-smoke` branch). Times are US Central. "Unknown" means GitHub doesn't show it.

| Field | Value |
| --- | --- |
| App | 11, Helpdesk Ticketing |
| Spec | [`specs/11-helpdesk.md`](../specs/11-helpdesk.md) (ai-dev-os #14, 2026-11-09 10:16 PM) |
| Repo | https://github.com/BreakthruDevelopment/11-helpdesk |
| Live cloud | Google Cloud (Cloud Run, us-central1) |
| URL | https://app11.breakthruventures.ai |
| `apps.yaml` PR | 30-apps-infra #76 (2026-11-12 6:08 PM, `sha-3fd1ca2`), custom domain #77 (9:36 PM; 2026-11-13 UTC); deploy issues 30-apps-infra #62, #63 |
| Image tag | `sha-3fd1ca2` |
| Live smoke | **pass**, 2026-11-12 11:18 PM (2026-11-13 05:18 UTC), [run 43371137256](https://github.com/BreakthruDevelopment/11-helpdesk/actions/runs/43371137256): `/api/health` reported `sha-3fd1ca2`; `scripts/smoke.sh` ended `SMOKE PASS` |
| Catalog status | `deployed` (not `done`: the README still has the template's "30 Apps Template" title, with no live URL or demo script.) |

## Gates

| Gate | Evidence |
| --- | --- |
| 1 Spec | Spec merged (ai-dev-os #14) |
| 2 Build | 9 merged PRs: claude 6, grok 3 |
| 3 Review | Codex reviewed #7 (8 reviews, 10 inline findings: 1 P1, 9 P2) and #11 (1 P2). Marked `claude-code` / `ready` reviews on #11, #12, #14, #15, #16 and #17. The review gate's caller workflow reached this repo on 2026-11-10 at 6:43 PM (#10); PRs merged before it carry no `Reviewer: claude-code` review in GitHub. |
| 4 Release | 30-apps-infra #76 (2026-11-12 6:08 PM, `sha-3fd1ca2`), custom domain #77 (9:36 PM; 2026-11-13 UTC); live smoke pass ([run 43371137256](https://github.com/BreakthruDevelopment/11-helpdesk/actions/runs/43371137256)) |
| 5 Close-out | This log and the catalog status (ai-dev-os, branch `claude/factory-docs-tidy`). Launch drafts: unknown |

## Who did what

Roles from PR titles; harness from the branch prefix. Per-role timing is unknown.

| Role | Harness | PR | Notes |
| --- | --- | --- | --- |
| Full-stack builder | Claude Code | #7, #12 | Tickets, access rules, outbox; SLA engine and knowledge base |
| AI builder | Claude Code | #14 | AI triage |
| UI builder | Grok Build | #11, #15 | Customer portal, public KB, inbox; agent desk, KB editor, admin |
| Docs writer | none | — | README not written: issue 11 #6 is open with no harness label |
| DevOps / template | Claude Code; Grok | #9, #16, #17; #10 | Demo-identity hooks, per-IP KB limit, review gate |
| Reviewer | Claude Code (+ Codex's GitHub reviews) | see gate 3 | Codex findings are counted above; whether each was fixed isn't recorded |
| DevOps (deploy) | Claude Code | 30-apps-infra, see header | `claude/` branches |

## AI evals (live model)

Live smoke checks that customers can't trigger or read triage or suggested replies. No eval of triage quality recorded.

## Definition of done

- [ ] README filled (template title or placeholder still there)
- [x] Live smoke passed after the latest deploy
- [x] This run log
- [ ] `catalog.yaml` `status: done` and `BRIEFING.md` updated (status is `deployed`)

## What slipped or surprised us

- Two live smokes failed before the pass: 10:20 PM (TLS EOF on the new domain) and 11:13 PM (sign-up failed).
- #15 failed CI on 2026-11-12 with an HTTP 429 on smoke sign-up (nightly ops report) before it was fixed and merged.
- Launch drafts: unknown.

## Update 2026-11-13

README filled (11-helpdesk#18, merged). With the passing live smoke on the deployed version and this run log, the definition of done is met; status set to `done`.
