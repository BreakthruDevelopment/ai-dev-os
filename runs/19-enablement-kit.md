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
| `apps.yaml` PR | not opened — `30-apps-infra#98` is three slices away (see Blocked) |
| Catalog status | `building` |

**Why this repo is the track's bottleneck:** it solely owns **Domain 3** of the Claude Certified Architect exam
(Claude Code configuration and workflows, 20%), carries exam scenarios 2, 4 and 5, and owns 11 of the 30 task
statements. No other app in the portfolio covers a single statement in Domain 3.

## Merged so far

| Slice | Issue | PR | Harness | Merged (Central) |
| --- | --- | --- | --- | --- |
| 19.1 Python scaffolding and CI | #1 | [#13](https://github.com/BreakthruDevelopment/19-enablement-kit/pull/13) | Claude Code | 11-21 |
| 19.2 Principals, read-only sandbox Proxy, frozen contract | #2 | [#16](https://github.com/BreakthruDevelopment/19-enablement-kit/pull/16) | Claude Code | 11-21 |
| 19.3 Sample Java EE codebase | #3 | [#15](https://github.com/BreakthruDevelopment/19-enablement-kit/pull/15) | Grok | 11-21 |
| 19.4 Scaffold Factory and `kit new` | #4 | [#18](https://github.com/BreakthruDevelopment/19-enablement-kit/pull/18) | Grok | 11-22 |
| 19.7 PR reviewer: passes and written criteria | #7 | [#17](https://github.com/BreakthruDevelopment/19-enablement-kit/pull/17) | Claude Code | 11-22 |
| 19.5 Session state, resumption, forking | #5 | [#19](https://github.com/BreakthruDevelopment/19-enablement-kit/pull/19) | Grok, fixed by Claude Code | **11-23** |
| 19.6 MCP client against app 18's frozen contract | #6 | [#20](https://github.com/BreakthruDevelopment/19-enablement-kit/pull/20) | Grok | **11-23** |

`main` is green: 492 tests collected, 491 passed and 1 skipped (19.6's live-gateway test), with `uv sync --locked`
/ `ruff` / `mypy --strict` / `uv build` all passing. CI itself runs `uv sync --frozen`, which does not validate the
lock — that is `#14`, Codex's.

## Open PRs

| PR | Slice | Status |
| --- | --- | --- |
| [#21](https://github.com/BreakthruDevelopment/19-enablement-kit/pull/21) | 19.8 the scout and the migration brief | Claude Code, `security-sensitive`. CI green at head `b7544a8` (597 passed, 1 skipped). Three heads: gate 3 said **blocking** at `431463d`, **ready** at `f225e2f` after both findings were fixed, then two non-blocking suggestions closed at `b7544a8`. **Held, not merged** — see below |

Nothing else is open. Both Grok PRs that were open overnight are merged.

### Why #21 is held

Codex raised two new P2s **on `f225e2f`**, not on the current head: GitHub reports them against `b7544a8`
only because the lines did not move. Both are real (confirmed against the code at the current head), both are
tracked in **`19-enablement-kit#22`**, and both are left **unresolved on purpose**:

1. **A `build.gradle` seed yields no references at all.** `BUILD_NAMES` seeds it, but `.gradle` is not in
   `_KINDS`, so `kind_of()` returns `other` and neither extraction branch in `references()` runs. A Gradle-only
   project reads its build file and enqueues nothing.
2. **Build-file paths resolve against the sandbox root, not the build file's own directory.** A nested
   `module/build.xml` naming `src` misses `module/src/Thing.java`, and with a root-level `src/` present it reads
   that unrelated directory instead. `_seeds()` deliberately selects nested build files, so it is reachable by
   design. This one is a *misattribution*, which is worse than a miss.

**Codex has never run on `b7544a8`.** Its `codex-review-state:v1` marker still reads `commit_sha: f225e2f`, and
the `@codex review` re-requested at 08:07 was answered at 08:19 with *"To use Codex here, create an environment
for this repo"*. So the second review a `security-sensitive` PR needs may not be obtainable at all right now —
that is **Michael's to unblock**, and it is a second reason #21 is held, independent of the two findings. A
marker behind the head is the stale-marker case in [`roles/reviewer.md`](../roles/reviewer.md), cleared by
`@codex review` on the current head; here that request errors.

Neither finding is reachable from `sample/legacy-oms/` — a flat Ant tree — which is why 19.8's suite misses both. Fixing
either changes the exploration strategy and would mean regenerating the recorded demo brief and several evals,
with new fixtures for a nested and a Gradle project. **That is a slice, not a patch**, and resolving a thread
that has not been addressed would tell the gate something untrue: on a `security-sensitive` PR with no
`Reviewer: codex` review, the gate falls back to Codex's marker. So #21 needs a decision — fix #22 inside 19.8,
or take it as a follow-up and resolve the two threads as a known deferral — and then a fresh gate-3 review,
because `b7544a8` is newer than the `ready` review on `f225e2f`.

## Ready for Grok tonight

- **`19-enablement-kit#9` (19.9, plan mode vs direct execution, and iterative refinement)** — labelled `grok` by
  `release-labels.py` the moment #5 merged. Its dependencies (#5, #7) are both done. This is the one issue Grok
  can start on immediately.
- `#11` (19.11, HTTP surface and coverage map) releases to `grok` as soon as #8 and #9 close.
- `#14` (CI's `uv sync --frozen` does not validate the lock) is **Codex's**, not Grok's, and still open.

## Blocked, and why

- **`#11` → `30-apps-infra#98` → `#12` is the whole remaining critical path**, three slices from a deploy
  (`#8`, `#9`, `#11`), and it runs through Grok twice.
  `#11` waits on #8 (PR #21, in review) and #9 (unstarted). `#98` (deploy, `claude`) waits on #11. `#12` (README,
  `grok`) waits on #98. So **app 19 cannot deploy until Grok runs #9 and #11**, and Grok only runs when Michael
  starts `scripts/run-harness.sh grok` on his Mac.
- `#10` (19.10, headless reviewer in CI) is **not** blocked — `claude`, `security-sensitive`, dependency #7 merged.
  It is a leaf; nothing waits on it.
- Known gap left open **on purpose**: exam scenario 5 is "code reviews, test generation, and pull request
  feedback", and the reviewer judges tests but writes none. Closing it means a new write path in a repo whose
  entire security story is that only `kit new` writes. Not closed on an agent's authority.

## Decisions made today (2026-11-23)

1. **Fixed Grok's PR #19 rather than handing it back. Michael may have decided differently** — this is the
   furthest the run went on its own authority: Claude Code wrote code on another harness's branch, then reviewed
   and merged it, all as the same GitHub account. It is also **not the first time on this app** — #18 took three
   Claude Code fix commits and #20 one, in earlier sessions — so this is the established practice here rather
   than a one-off, which is the better reason for Michael to look at it. Review 2 left one blocking item — `_write`'s byte cap had no
   test, and deleting it kept the suite green. The test was written, pushed to Grok's branch (ordinary push, no
   force), both reviews re-requested, and the PR merged on `Verdict: ready`. Grok does not return to a failed PR
   on its own, so the alternative was losing the slice.
2. **Also deleted `test_an_oversized_file_is_refused`** in that push: its payload was `b"{" * (cap+1)`, not valid
   JSON, so the decoder refused it whatever the caps did and it could not fail. Its substance is covered by
   `test_corrupt_session_files_are_refused`.
3. **Merged #19 and #20 without `security-sensitive`.** Two consecutive reviews recommended the label for 19.5
   (first per-principal persistent state; a filesystem read path reimplemented outside `kit/core/`) — in fact
   three did, at `82dd5c0`, `7fcf70e` and `1681620`. The spec marks
   only 19.1, 19.2, 19.7, 19.8 and 19.10, and adding it would have turned the gate **red**, not green: Codex's
   marker is current at the head but reads `has_unresolved_findings: true` over a live P2 thread. **Michael may
   have decided differently** — see the carried findings below.
4. **The scout calls the model once; exploration order is deterministic code.** The spec says the scout "must
   choose what to read and say why"; this reads that as the kit choosing and recording rather than the model
   steering a loop, chosen so the recorded reply is meaningful and CI costs nothing. Flagged in PR #21 for review.
5. **Did not relabel #9 or #11 away from Grok.** `AGENTS.md` §3 leaves that to Michael or the planner.
6. **Did not resolve Codex's two new threads on PR #21, so the PR is held rather than merged.** Resolving them is
   what would turn the gate green, and that is exactly why it would have been the wrong move: the findings are
   real and unaddressed. Holding #21 costs little tonight, because `#11` needs `#9` from Grok regardless, so #8
   was never the only thing in the way. **Michael may have decided differently** — the alternative was to resolve
   both as accepted deferrals and merge.
7. **Fixed two non-blocking review suggestions rather than filing them** (the unpinned third log call site, and a
   docstring claiming an absolute the filter does not give). Both are the two defect shapes this repo keeps
   paying for, and each was a two-line change.

## Carried findings, not blocking

- `19-enablement-kit#19` → `kit/session/store.py:80`: `append` is read-modify-write, so two concurrent appends lose
  one turn. Real; judged a suggestion for a single-engineer CLI. Codex's thread is still open on the merged PR.
- `19-enablement-kit#20` → `kit/erp/stdio.py:216`: the gateway timeout applies to reads, not writes. Liveness only,
  on an opt-in `--live` path where `ci` is denied `CALL_GATEWAY`. Wants a follow-up issue.
- `kit/erp/client.py:103`: deleting `recording.check_against(contract)` leaves the suite green; `REPLAY_INVALID` is
  untested. Low risk (corrupting the transcript still fails six tests), but it is the "test that cannot fail" shape.

## First three steps tomorrow

1. **Decide `#22`, then land PR #21.** Either fix the two Gradle/nested-root findings inside 19.8, or accept them
   as a follow-up slice and resolve the two Codex threads as a known deferral. Then re-run the gate-3 review on
   the current head, request `@codex review` on that head — **check first whether Codex can run here at all**,
   since the last request returned "create an environment for this repo" — and merge, followed by
   `python3 scripts/release-labels.py --repo 19-enablement-kit`.
2. **Build `#10`** (19.10, headless reviewer in CI) — `claude`, `security-sensitive`, unblocked, and the last
   Claude-owned slice before the deploy chain. Not started this run: starting a build-plus-two-review-rounds
   cycle at the end of the window risks leaving a half-finished push, which is worse than not starting.
3. **Start Grok on `#9`**, then `#11` when it releases. Until those two land, `30-apps-infra#98` and `#12` cannot
   move and the app cannot go live. If Grok is out of usage, re-point #9 and #11 (Michael's or the planner's call).

## Tests that cannot fail: the running list

Counted strictly — a control whose test passes whether or not the control is there — these are the instances,
itemised so the count is checkable rather than asserted:

1. **#18**, review of `22854c0`: three tests that cannot fail, called out together.
2. **#17**, review of `5cbe53b`: `tests/test_review_evals.py:970`, the "further finding(s)" test.
3. **#17**, review of `837087a`: the same defect again, over `ReviewResult.omitted`.
4. **#19**, review of `82dd5c0`: `test_an_oversized_file_is_refused`, whose payload was not valid JSON, so the
   decoder refused it whatever the three byte caps did.
5. **#21**, review of `431463d`: the `_annotate_next()` ordering, where the fix **passed either way** across 584
   tests.

That is **seven** by instance (three of them inside item 1) or five by review. An eighth case is adjacent but
not the same thing: `kit/erp/client.py:103` in #20 is a control with *no* test rather than a test that cannot
fail, as are the eight #20's first review found, and they are listed under Carried findings. The distinction is
worth keeping — the first kind lies to you, the second merely says nothing — and the itemisation matters more
than the total, which is why an earlier draft of this log claiming a bare "six" was wrong to.

Every review on this repo now mutates each control it credits, and PR #21 was built that way: 34 mutations by the
builder (all killed but two equivalent mutants, and the run caught four weak tests the builder had written
itself), then eight reproduced independently by the reviewer, then six more on the logging fix. The reviewer also
found a *second* unreported survivor and one guard that was dead weight described as a bound — which is the
lesson worth keeping: **a comment claiming a bound is a comment someone later trusts as one.** That happened
twice in this slice, one commit apart (`MAX_SEARCHED_LINE`, raised at `431463d` and corrected in `f225e2f`;
then the log emitter's docstring, raised at `f225e2f` and corrected in `b7544a8`), so it is a habit rather than
a slip.

## Gates

| Gate | Evidence | Date (Central) |
| --- | --- | --- |
| 1 Spec: Michael approved scope | `specs/19-enablement-kit.md` merged (PR #60) | 11-21, 15:39 |
| 2 Build: PRs merged with CI green | #13, #15, #16, #17, #18, #19, #20 | 11-21 to 11-23 |
| 3 Review: `Reviewer sign-off` green on every merged PR | every merged PR carries a `Reviewer: claude-code` / `Verdict: ready` review on its merged head; Codex second-reviewed the `security-sensitive` ones | 11-21 to 11-23 |
| 4 Release | **not reached** — needs `#11`, then `30-apps-infra#98` | — |
| 5 Close-out | **not reached** — this log is the in-progress form; `catalog.yaml` moved to `building` with it | — |

## Who did what

| Role | Harness | PR | Notes |
| --- | --- | --- | --- |
| Planner | Claude Code | spec | 13 slices in 6 waves |
| Full-stack builder | Grok Build | #15, #18, #19, #20 | 19.3, 19.4, 19.5, 19.6. **#18, #19 and #20 each needed fix commits pushed by Claude Code** to clear a blocking review — three on #18, three on #19, one on #20. Only **#15** was Grok's work alone: one commit, `Verdict: ready` first time, no inline comments |
| Full-stack builder | Claude Code | #13, #16 | 19.1, 19.2 — wave 1, both `security-sensitive` |
| AI builder | Claude Code | #17, #21 | 19.7 merged; 19.8 open and held |
| Reviewer | Claude Code; Codex | every PR | Codex auto-reviews **every** PR in this repo, not only the `security-sensitive` ones — decision 3's argument depends on that. Findings in the table above and under Carried findings |
| DevOps | — | — | Not started: `30-apps-infra#98` is behind `#11` |
| Docs writer | — | — | `#12` is behind the deploy |

## What slipped or surprised us

- **Three of the four Grok PRs needed a second round, and for three different reasons.** #15 passed first time.
  #18's blocking round was a symlink-then-`..` defect in `_resolve_target`; #19's led with a FIFO hang; #20's was
  eight documented controls that could be deleted with `pytest` still green. Only the last of those is a
  *test that cannot fail* in the strict sense this log uses below — which is the point of keeping the
  distinction: the common thread is reviews that mutate what they credit, not one recurring bug.
- **The fix for a test-that-cannot-fail can itself be one.** PR #19's first fix commit argued all three
  enforcement points of the byte cap were "redundant", which is true of the two read-side comparisons and cannot
  be true of a write cap. The second round caught it.
- **Codex may not be able to run on this repo right now** — see "Why #21 is held". That is one of two things in
  app 19's way that no agent can clear; the other is Grok Build, which only runs when Michael starts the runner
  on his Mac, and `#9` and `#11` both wait on it.
- **The reviewer graded the run's own work and found real errors in this very log across three rounds** — a
  misattributed commit, a stale `catalog.yaml`, and then the one that matters: this section originally credited
  Claude Code fix commits to #19 and #20 and left out #18, which had three. That was the first error in the log
  running in the *flattering* direction rather than the self-critical one, and it understated decision 1. A
  self-reported run log is exactly where a run flatters itself, so it was worth three rounds.
- **A `ready` verdict can be granted over live findings nobody read.** The gate-3 `ready` on PR #21's `f225e2f`
  was posted at 08:19:30; Codex had raised its two new P2s on that same head at 08:10:12, nine minutes earlier.
  The review read the marker as covering the two *older* threads and called them addressed. So that sign-off was
  not merely overtaken by a later commit — it was given over two then-live findings that had not been examined.
  Reading the marker is not the same as reading the threads, and only the threads say what is open.
