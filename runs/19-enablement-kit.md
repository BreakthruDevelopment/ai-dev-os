# Run log — 19-enablement-kit

BreakthruSoftwareFactory run log ([`FACTORY.md`](../FACTORY.md)). **In progress** — gates 4 and 5 are not reached,
so the full close-out table is filled when they are. Status below is as of **2026-11-23, early morning Central**.

| Field | Value |
| --- | --- |
| App | 19, Engineering enablement kit |
| Spec | [`specs/19-enablement-kit.md`](../specs/19-enablement-kit.md) |
| Repo | https://github.com/BreakthruDevelopment/19-enablement-kit |
| Live cloud | aws |
| URL | https://app19.breakthruventures.ai (not deployed yet) |
| `apps.yaml` PR | not opened — `30-apps-infra#98` is two slices away (see Blocked) |
| Catalog status | `building` |

**Why this repo is the track's bottleneck:** it solely owns **Domain 3** of the Claude Certified Architect exam
(Claude Code configuration and workflows, 20%), carries exam scenarios 2, 4 and 5, and owns 11 of the 30 task
statements. No other app in the portfolio covers a single statement in Domain 3.

## Merged so far

| Slice | Issue | PR | Harness | Merged |
| --- | --- | --- | --- | --- |
| 19.1 Python scaffolding and CI | #1 | [#13](https://github.com/BreakthruDevelopment/19-enablement-kit/pull/13) | Claude Code | 11-21 |
| 19.2 Principals, read-only sandbox Proxy, frozen contract | #2 | [#16](https://github.com/BreakthruDevelopment/19-enablement-kit/pull/16) | Claude Code | 11-22 |
| 19.3 Sample Java EE codebase | #3 | [#15](https://github.com/BreakthruDevelopment/19-enablement-kit/pull/15) | Grok | 11-22 |
| 19.4 Scaffold Factory and `kit new` | #4 | [#18](https://github.com/BreakthruDevelopment/19-enablement-kit/pull/18) | Grok | 11-22 |
| 19.7 PR reviewer: passes and written criteria | #7 | [#17](https://github.com/BreakthruDevelopment/19-enablement-kit/pull/17) | Claude Code | 11-22 |
| 19.5 Session state, resumption, forking | #5 | [#19](https://github.com/BreakthruDevelopment/19-enablement-kit/pull/19) | Grok, fixed by Claude Code | **11-23** |
| 19.6 MCP client against app 18's frozen contract | #6 | [#20](https://github.com/BreakthruDevelopment/19-enablement-kit/pull/20) | Grok | **11-23** |

`main` is green: 492 tests collected, `uv sync --locked` / `ruff` / `mypy --strict` / `pytest` / `uv build` all pass.

## Open PRs

| PR | Slice | Status |
| --- | --- | --- |
| [#21](https://github.com/BreakthruDevelopment/19-enablement-kit/pull/21) | 19.8 the scout and the migration brief | Opened by Claude Code, `security-sensitive`. CI green (584 passed, 1 skipped); `Reviewer sign-off` red pending the gate-3 review; `@codex review` requested |

Nothing else is open. Both Grok PRs that were open overnight are merged.

## Ready for Grok tonight

- **`19-enablement-kit#9` (19.9, plan mode vs direct execution, and iterative refinement)** — labelled `grok` by
  `release-labels.py` the moment #5 merged. Its dependencies (#5, #7) are both done. This is the one issue Grok
  can start on immediately.
- `#11` (19.11, HTTP surface and coverage map) releases to `grok` as soon as #8 and #9 close.
- `#14` (CI's `uv sync --frozen` does not validate the lock) is **Codex's**, not Grok's, and still open.

## Blocked, and why

- **`#11` → `30-apps-infra#98` → `#12` is the whole remaining critical path**, and it runs through Grok twice.
  `#11` waits on #8 (PR #21, in review) and #9 (unstarted). `#98` (deploy, `claude`) waits on #11. `#12` (README,
  `grok`) waits on #98. So **app 19 cannot deploy until Grok runs #9 and #11**, and Grok only runs when Michael
  starts `scripts/run-harness.sh grok` on his Mac.
- `#10` (19.10, headless reviewer in CI) is **not** blocked — `claude`, `security-sensitive`, dependency #7 merged.
  It is a leaf; nothing waits on it.
- Known gap left open **on purpose**: exam scenario 5 is "code reviews, test generation, and pull request
  feedback", and the reviewer judges tests but writes none. Closing it means a new write path in a repo whose
  entire security story is that only `kit new` writes. Not closed on an agent's authority.

## Decisions made today (2026-11-23)

1. **Fixed Grok's PR #19 rather than handing it back.** Review 2 left one blocking item — `_write`'s byte cap had
   no test, and deleting it kept the suite green. Claude Code wrote the test, pushed to Grok's branch (ordinary
   push, no force), re-requested both reviews, and merged on `Verdict: ready`. Grok does not return to a failed PR
   on its own, so the alternative was losing the slice.
2. **Also deleted `test_an_oversized_file_is_refused`** in that push: its payload was `b"{" * (cap+1)`, not valid
   JSON, so the decoder refused it whatever the caps did and it could not fail. Its substance is covered by
   `test_corrupt_session_files_are_refused`.
3. **Merged #19 and #20 without `security-sensitive`.** Two consecutive reviews recommended the label for 19.5
   (first per-principal persistent state; a filesystem read path reimplemented outside `kit/core/`). The spec marks
   only 19.1, 19.2, 19.7, 19.8 and 19.10, and adding it would have turned the gate **red**, not green: Codex's
   marker is current at the head but reads `has_unresolved_findings: true` over a live P2 thread. **Michael may
   have decided differently** — see the carried findings below.
4. **The scout calls the model once; exploration order is deterministic code.** The spec says the scout "must
   choose what to read and say why"; this reads that as the kit choosing and recording rather than the model
   steering a loop, chosen so the recorded reply is meaningful and CI costs nothing. Flagged in PR #21 for review.
5. **Did not relabel #9 or #11 away from Grok.** `AGENTS.md` §3 leaves that to Michael or the planner.

## Carried findings, not blocking

- `19-enablement-kit#19` → `kit/session/store.py:80`: `append` is read-modify-write, so two concurrent appends lose
  one turn. Real; judged a suggestion for a single-engineer CLI. Codex's thread is still open on the merged PR.
- `19-enablement-kit#20` → `kit/erp/stdio.py:216`: the gateway timeout applies to reads, not writes. Liveness only,
  on an opt-in `--live` path where `ci` is denied `CALL_GATEWAY`. Wants a follow-up issue.
- `kit/erp/client.py:103`: deleting `recording.check_against(contract)` leaves the suite green; `REPLAY_INVALID` is
  untested. Low risk (corrupting the transcript still fails six tests), but it is the "test that cannot fail" shape.

## First three steps tomorrow

1. **Merge PR #21** (19.8, the scout) once the gate-3 review and Codex's second review are green on its head, then
   run `python3 scripts/release-labels.py --repo 19-enablement-kit`.
2. **Build `#10`** (19.10, headless reviewer in CI) — `claude`, `security-sensitive`, unblocked, and the last
   Claude-owned slice before the deploy chain.
3. **Start Grok on `#9`**, then `#11` when it releases. Until those two land, `30-apps-infra#98` and `#12` cannot
   move and the app cannot go live. If Grok is out of usage, re-point #9 and #11 (Michael's or the planner's call).

## Tests that cannot fail: the running count

This repo has now produced **six** controls that shipped with a test incapable of failing — four found in one
night, plus the two found this morning in Grok's PRs #19 and #20 (eleven controls between them). Every review on
this repo now mutates each control it credits, and PR #21 was built that way: 34 mutations, all killed but one
equivalent mutant, and the run caught four weak tests the builder had written itself.
