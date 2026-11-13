# Run log — 12-restaurant-ordering

BreakthruSoftwareFactory run log ([`FACTORY.md`](../FACTORY.md)), **written on 2026-11-13** from GitHub only (merged PRs, PR reviews, `30-apps-infra`, and the `Live smoke test` runs on the repo's `claude/live-smoke` branch). Times are US Central. "Unknown" means GitHub doesn't show it.

| Field | Value |
| --- | --- |
| App | 12, Restaurant Ordering |
| Spec | [`specs/12-restaurant-ordering.md`](../specs/12-restaurant-ordering.md) (ai-dev-os #14, 2026-11-09 10:16 PM) |
| Repo | https://github.com/BreakthruDevelopment/12-restaurant-ordering |
| Live cloud | Oracle Cloud (Always Free A1 VM, Phoenix) |
| URL | https://app12.breakthruventures.ai |
| `apps.yaml` PR | 30-apps-infra #74 (2026-11-11 1:08 PM, `sha-cbd6f0f`), #75 (2026-11-12 2:04 PM, `sha-6bd0d02`); deploy issue 30-apps-infra #64 |
| Image tag | `sha-6bd0d02` |
| Live smoke | **fail**, 2026-11-12 2:08 PM, [run 43297320344](https://github.com/BreakthruDevelopment/12-restaurant-ordering/actions/runs/43297320344): `/api/health` reported `sha-6bd0d02`; steps pass up to the menu assistant, then `SMOKE FAIL: the menu has no orderable dish` |
| Catalog status | `deployed` (not `done`: the README still has the template's title, and no full live smoke has passed: it stops at "no orderable dish" until the demo workspace is loaded (admin button) or `SMOKE_STAFF_EMAIL` / `SMOKE_STAFF_PASSWORD` are set.) |

## Gates

| Gate | Evidence |
| --- | --- |
| 1 Spec | Spec merged (ai-dev-os #14) |
| 2 Build | 8 merged PRs: claude 5, grok 3 |
| 3 Review | Codex reviewed #8 (1 review, 3 inline: 1 P1, 2 P2), #9 (3 reviews, 8 inline: 5 P1, 3 P2) and #11 (2 P2). Marked `claude-code` / `ready` reviews on #11, #12, #14 and #15. The review gate's caller workflow reached this repo on 2026-11-10 at 6:43 PM (#10); PRs merged before it carry no `Reviewer: claude-code` review in GitHub. |
| 4 Release | 30-apps-infra #74 (2026-11-11 1:08 PM, `sha-cbd6f0f`), #75 (2026-11-12 2:04 PM, `sha-6bd0d02`); live smoke fail ([run 43297320344](https://github.com/BreakthruDevelopment/12-restaurant-ordering/actions/runs/43297320344)) |
| 5 Close-out | This log and the catalog status (ai-dev-os, branch `claude/factory-docs-tidy`). Launch drafts: unknown |

## Who did what

Roles from PR titles; harness from the branch prefix. Per-role timing is unknown.

| Role | Harness | PR | Notes |
| --- | --- | --- | --- |
| Full-stack builder | Claude Code; Grok Build | #8; #11 | Menu, allergens, orders; real-time order status over SSE |
| AI builder | Claude Code | #9, #14 | Menu assistant with allergen router; general-question routing |
| UI builder | Grok Build | #12 | Menu, cart, checkout, tracker, kitchen board, menu editor, admin |
| Docs writer | none | — | README not written: issue 12 #5 is open with no harness label |
| DevOps / template | Claude Code; Grok | #7, #15; #10 | Demo-identity hooks, review gate |
| Reviewer | Claude Code (+ Codex's GitHub reviews) | see gate 3 | Codex findings are counted above; whether each was fixed isn't recorded |
| DevOps (deploy) | Claude Code | 30-apps-infra, see header | `claude/` branches |

## AI evals (live model)

Live smoke step "menu assistant: ... allergen question answered deterministically with the notice and no safety claim" passed. No separate eval recorded.

## Definition of done

- [ ] README filled (template title or placeholder still there)
- [ ] Live smoke passed after the latest deploy
- [x] This run log
- [ ] `catalog.yaml` `status: done` and `BRIEFING.md` updated (status is `deployed`)

## What slipped or surprised us

- Earlier live smokes on 2026-11-11 and 2026-11-12 failed with TLS errors on `app12` (`tlsv1 alert internal error`). The 2026-11-11 1:08 PM "success" only checked the image manifest, not the app.
- No full smoke has passed against the live URL at any tag.
- Launch drafts: unknown.
