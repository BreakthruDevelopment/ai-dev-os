# Run log — NN-slug

BreakthruSoftwareFactory run log ([`FACTORY.md`](../FACTORY.md)). Link evidence; write "unknown" rather than guess.

| Field | Value |
| --- | --- |
| App | NN, name |
| Spec | `specs/NN-slug.md` (PR #) |
| Repo | https://github.com/BreakthruDevelopment/NN-slug |
| Live cloud | |
| URL | https://appN.breakthruventures.ai |
| `apps.yaml` PR | 30-apps-infra # |
| Image tag | sha-xxxxxxx |
| Live smoke | pass / fail, date and time (Central), link to the output |
| Catalog status | planned / building / deployed / done |

## Gates

| Gate | Evidence | Date (Central) |
| --- | --- | --- |
| 1 Spec: Michael approved scope | spec PR # | |
| 2 Build: PRs merged with CI green | PR #, #, # | |
| 3 Review: `Reviewer sign-off` green on every PR (Codex on security-sensitive) | review links | |
| 4 Release: Michael merged, deployed, live smoke | apps.yaml PR #, smoke output | |
| 5 Close-out: run log, catalog/briefing, launch drafts | catalog PR #; drafts given to Michael | |

## Who did what

| Role | Harness | PR | Notes |
| --- | --- | --- | --- |
| Planner | Claude Code | | |
| Full-stack builder | | | |
| AI builder | Claude Code | | |
| UI builder | Grok Build | | |
| Reviewer | Claude Code (+ Codex on security-sensitive) | | Findings: |
| DevOps | Claude Code | | |
| Docs writer | | | |
| Launch drafts | Grok Bot (no repo access; Michael posts) | — | |

## AI evals (live model)

| Case | Result |
| --- | --- |
| | |

## Definition of done

- [ ] README filled (no template title or "What this app does" placeholder; real live URL; demo script)
- [ ] Live smoke passed after the latest deploy
- [ ] This run log complete
- [ ] `catalog.yaml` `status: done` and `BRIEFING.md` updated

## What slipped or surprised us
