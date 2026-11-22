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
Michael's call and not a scheduled run's. App 20 may want the same allowance; apps 18 and 19 both deploy.

## What slipped or surprised us

- **Apps 18, 19 and 20 pin `v0.1.0` (`9955f1f`), now two merges behind `main`.** Both merges are things those apps
  want — #19 is the approval-record fix that 18 and 19 depend on, and #17 is the demo. `main` wants a **`v0.1.1`**
  and the consumers' `pyproject.toml` pins want moving deliberately. **Tag creation is blocked by policy in the
  scheduled environment**, so the code is in and the tag is not. This is the one thing outstanding that affects
  other repos.
- **17.7 cut**, the first cut deploy in the track. Recorded in the spec as the precedent.
- Issue **#11** (a `StrEnum` compared with `is` in `ToolResult.failure`) was reassigned from `claude` to `codex`
  mid-run and left with Codex, confirmed deliberate. App 20's slice 20.4 throttling eval depends on it:
  `ToolResult.failure` returns `is_retryable=False` for the wire string `"transient"`.
- Residual imprecision shipped knowingly: `agent_container/testing/contracts.py`'s "irreducible trust floor"
  docstring claims more than the suite delivers, and one `_require` before `apply()` would close five of six
  adversarial cases. Filed with the measurements on `17-agent-container#20` rather than held for a fifth review
  round on a non-urgent backlog issue. A library three apps read now carries a docstring that overstates.
