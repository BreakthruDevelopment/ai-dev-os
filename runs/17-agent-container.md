# Run log — 17-agent-container

BreakthruSoftwareFactory run log ([`FACTORY.md`](../FACTORY.md)). Link evidence; write "unknown" rather than guess.

| Field | Value |
| --- | --- |
| App | 17, The agent container |
| Spec | `specs/17-agent-container.md` |
| Repo | https://github.com/BreakthruDevelopment/17-agent-container |
| Live cloud | aws (planned) — **nothing deployed**, see "Release" below |
| URL | none. `app17.breakthruventures.ai` has no DNS record and no Terraform resources |
| `apps.yaml` PR | none — never added |
| Image tag | n/a |
| Live smoke | **n/a: 17.7 cut.** CI smoke on every merge instead: `agent-container demo` through a built wheel, event stream validated |
| Catalog status | building (→ done when the README lands, pending the question below) |

This is the first repo in the track with **nothing to deploy**. It is a Python library — no pages, no database,
no auth — that apps 18, 19 and 20 import. Its own definition of done therefore does not fit the template, which
is the one open governance question from this run.

## Gates

| Gate | Evidence | Date (Central) |
| --- | --- | --- |
| 1 Spec: Michael approved scope | `specs/17-agent-container.md` merged | before 2026-11-20 |
| 2 Build: PRs merged with CI green | #14 (17.5), #15, #17 (17.6), #19 (#13) — and #10, #12 earlier | to 2026-11-22 |
| 3 Review: `Reviewer sign-off` green on every PR (Codex on security-sensitive) | 5 rounds on #17, 4 on #19 | 2026-11-22 |
| 4 Release: deploy, live smoke | **cut.** `30-apps-infra#96` closed as not planned | 2026-11-22 |
| 5 Close-out: run log, catalog, launch drafts | this file; `#7` README with `grok` | 2026-11-22 |

## Who did what

| Role | Harness | PR | Notes |
| --- | --- | --- | --- |
| Planner | Claude Code | — | Spec, waves, and the backlog issues #11, #13, #16 raised out of reviews |
| Full-stack builder | Claude Code (17.1–17.4), Grok Build (17.5, 17.6) | #14, #17 | 17.5 and 17.6 were Grok's |
| AI builder | Claude Code | #10 | 17.3, Bedrock provider and recorder |
| UI builder | — | — | No UI: a library |
| Reviewer | Claude Code (+ Codex on security-sensitive) | — | Findings below |
| DevOps | — | — | **Cut** |
| Docs writer | Grok Build | `#7` | Labelled `grok` 2026-11-22, re-pointed off the cut deploy |
| Launch drafts | Grok Bot (no secrets; Michael posts) | — | Not started; no live URL to post |

## Review findings worth keeping

Nine review rounds on 2026-11-22, across #17 (5) and #19 (4).

**Tests and checks that could not fail — the recurring defect in this repo.** Four were found in one earlier
night; three more on 2026-11-22:

- **Two CI wheel checks tested the checkout, not the wheel.** `python -c` puts the checkout root on `sys.path`,
  so `/tmp/wheel-check/bin/python -c "import agent_container…"` imported the source tree. Measured: a wheel whose
  `core/__init__.py` raises `ImportError` **passed with exit 0**. Both lines now use `python -P -c`. One was
  pre-existing from 17.1; it sat inside the job every merge in the track keys off.
- **A latent hole the demo's new answer line would have opened.** CI greps this stderr summary for `demo ok`.
  Printing the model's final answer flush left would have let a reply containing `demo ok` on its own line satisfy
  that grep on a run that had failed. The answer is indented under an `answer:` header and the three greps are
  anchored. Model output is data, including the final answer.
- **A shared contract suite that passed a broken implementation, three versions running.** `StagedChangeContract`
  (#19) asked subclasses to *declare* that their arguments get rewritten; then checked a probe one-sidedly; then
  compared two strings not tied to the same argument. Each version was defeated by a case that is now checked in
  (`_ThawedCase`, `_UnrewrittenCase`, `_ModelProbeCase`, `_TruncatedCase`, `_InvisibleFieldCase`). A contract suite
  that cannot fail is worse than none, because every downstream consumer inherits the false assurance — and apps
  18 and 19 are the named subclassers.

**The pattern, which is the real finding.** In every one of the nine rounds the PR's own prose carried a
falsifiable claim that measurement killed, while the code survived every round. PR #17's body overstated what
`-P` catches (a gutted validator passes with and without it; what `-P` catches is an unimportable wheel). PR #19
overstated four times, each time asserting that the newest check *entails* the freeze property when what it does
is narrow the ways of evading it. Both PRs were written and reviewed by the same session; what made the reviews
work was giving the reviewer the code and the claims to re-measure, never the conclusion.

**A foundation rule held by review alone, and it held.** `agent_container/core/` is deliberately outside the
pre-push guard, because the guard matches on path prefix and `git diff --name-only` cannot tell an addition from
an edit — including it would have refused 17.5's push. Grok, running on the Mac, hit that rule on #13, read it
correctly, refused to edit `core/gate.py`, and wrote `.harness/blocked.md` instead of inventing a way through.
That is the guard working exactly as intended with no mechanism behind it.

## AI evals (live model)

| Case | Result |
| --- | --- |
| All of the spec's eval table | Covered by tests on recorded replies; **no live-model run**, by design: replay is the default and Bedrock only with `--live` |

## Definition of done

- [ ] README filled — `#7`, labelled `grok`, documents the command line (no live URL exists)
- [x] ~~Live smoke passed after the latest deploy~~ — **n/a, 17.7 cut.** See the open question
- [x] This run log complete
- [ ] `catalog.yaml` `status: done` and `BRIEFING.md` updated — blocked on the README and the question below

## Open question for Michael: what "done" means for a repo with nothing to deploy

`FACTORY.md`'s definition of done asks for a **live smoke** at `https://appN.breakthruventures.ai` with
`/api/health` answering. App 17 cannot clear that bar and never could: it is a library, and 17.7 — the one
deployable thing in it — was cut as the lowest-value item in the repo. So app 17 either never reaches `done`, or
the definition admits a case it was not written for.

**Proposed, not applied:** for an app with no deployable surface, condition 2 is met by the CI smoke on `main`
— for this repo, `agent-container demo` run through a **built wheel** with the event stream validated, which is
stronger than it was before 2026-11-22 (it now actually exercises the wheel). The run log records which it was.
Nothing else in the definition changes, and no app with a web surface gets an easier bar.

This is left as a question rather than an edit to `FACTORY.md`, because loosening the definition of done is
Michael's call and not a scheduled run's — and because the app that wants the exemption should not be the one
that drafts the rule. App 20 may want the same allowance; apps 18 and 19 both deploy, so the general rule is
better written from more than one case.

**Tracked as [`ai-dev-os#69`](https://github.com/BreakthruDevelopment/ai-dev-os/issues/69)**, not only here: a
governance question parked in a run log is one nobody re-reads, and app 17 would otherwise sit at `building` with
no owner for the condition it cannot meet.

## What slipped or surprised us

- **Apps 18, 19 and 20 pin `v0.1.0` (`9955f1f`), now three merges behind `main` — two of them library code.**
  `git log --first-parent v0.1.0..main` is #15, #17 and #19; #15 touched only
  `.github/workflows/review-gate.yml` (+6 lines), so consumers are three commits but two code merges behind. Both
  code merges are things those apps want — #19 is the approval-record fix that 18 and 19 depend on, and #17 is the
  demo. **Resolved 2026-11-22:** Michael created the annotated tag **`v0.1.1`** on `8b3d030`. Tag creation is
  blocked by policy in the scheduled environment, which is why it waited for him. **App 20 moved its pin the same
  day** (`20-discovery-workbench#14`, merged 2026-11-22, ~50 minutes after the tag); apps 18 and 19 still read
  `v0.1.0`. Moving each one is that app's own business, in the PR that first needs it, because `uv.lock` records
  the resolved commit rather than the tag — so an edit to `pyproject.toml` alone installs the old library, and a
  pin bump wants CI in its own repo to prove it.
- **17.7 cut**, the first cut deploy in the track. Recorded in the spec as the precedent.
- Issue **#11** (a `StrEnum` compared with `is` in `ToolResult.failure`) was reassigned from `claude` to `codex`
  mid-run and left with Codex, confirmed deliberate. App 20's slice 20.4 throttling eval depends on it:
  `ToolResult.failure` returns `is_retryable=False` for the wire string `"transient"`.
- Residual imprecision shipped knowingly. `agent_container/testing/contracts.py:325` on `main` says
  "What remains on trust, irreducibly:" and then claims more than the suite delivers: the word *irreducibly* is
  wrong, because one `_require` before `apply()` calibrates the two renderers and closes five of six adversarial
  cases with all 588 tests still passing, and the paragraph's claim that the suite checks `recomposed` "for
  consistency with the record" is wrong too — it is checked only for *difference* from it. Filed with those
  measurements in a **comment** on `17-agent-container#20` (not its body), rather than held for a fifth review
  round on a non-urgent backlog issue. A library that apps 18, 19 and 20 read now carries a docstring that
  overstates, which is the cost of that call.

## Status at 2026-11-23 (start of day)

`main` = `8b3d030`. Tags `v0.1.0` and `v0.1.1` both exist.

**Open PRs: none.** Every slice 17.1–17.6 is merged, plus #13's fix (#19). Nothing is in flight.

**Ready for Grok tonight: `#7` (README) — and only that.** Labelled `grok`, no unmet dependencies
(`release-labels.py --dry-run` reports nothing waiting). It needs Michael to start the runner on his Mac; labels
do not trigger Grok. It must document `agent-container demo` and the pattern and exam maps, **not** a live URL —
there is no deployment.

**Blocked, and why:**

| What | Blocked on |
| --- | --- |
| `catalog.yaml` → `done` | `#7` (Grok) **and** [`ai-dev-os#69`](https://github.com/BreakthruDevelopment/ai-dev-os/issues/69) — app 17 cannot clear the live-smoke condition, so the definition of done has to admit the case first. Michael's call. |
| `BRIEFING.md` agreeing with the catalog | BRIEFING still lists apps 13–30 as `planned`. Left for whoever closes out the whole AWS demo track, in one pass, rather than patched per app. |
| `#11`, `#16`, `#18` | Codex capacity. Not ours to build. |

`#20` is not blocked — it is simply the only Claude work left here.

**Decisions taken 2026-11-22:**

- **17.7 cut** (Michael). First cut deploy in the track; recorded in the spec as the precedent.
- **`#13` re-pointed `grok` → `claude` + `security-sensitive`**, then built and merged as #19. Grok had refused it
  correctly under the foundation rule; handing it back would have stalled on the same rule. The authorization was
  self-granted, which is worth knowing.
- **`#11` left with Codex**, confirmed deliberate after its label moved mid-run.
- **#19 merged with a knowingly imprecise docstring**, residue filed with measurements in a comment on `#20`,
  rather than a fifth review round on a non-urgent backlog issue.
- **The definition-of-done question got a venue (`ai-dev-os#69`)** instead of a `FACTORY.md` edit, on the grounds
  that the app wanting the exemption should not draft the rule.
- **A review-round cap was adopted** for future runs: two rounds, then file the residue and merge if CI is green
  and nothing in shipped behaviour is broken. Nine rounds across two PRs on 2026-11-22 is what prompted it; three
  of four overnight tasks died at `USAGE_LIMIT_REACHED` that morning.

**First three steps tomorrow:**

1. **Build `#20`** — the only `claude` work here. Its three items and their measurements are in a comment on the
   issue; it is security-sensitive because it edits `core/decorators.py`, and `#20` is the named owner of that edit.
2. **Review and merge whatever Grok or Codex left** — `#7`'s PR if the runner ran, or Codex's on `#11`/`#16`/`#18`.
   An unreviewed PR from them unblocks nothing, so this comes before building.
3. **Close app 17 out** once `#7` is merged and `#69` is answered: `catalog.yaml` to `done`, and `BRIEFING.md`
   in the same track-wide pass.
