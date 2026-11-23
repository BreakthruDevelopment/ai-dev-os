# Run log — 20-discovery-workbench

BreakthruSoftwareFactory run log ([`FACTORY.md`](../FACTORY.md)). Link evidence; write "unknown" rather than guess.

| Field | Value |
| --- | --- |
| App | 20, Discovery workbench |
| Spec | `specs/20-discovery-workbench.md` |
| Repo | https://github.com/BreakthruDevelopment/20-discovery-workbench |
| Live cloud | aws (planned) — **nothing deployed**, see "Blocked" |
| URL | none. `app20.breakthruventures.ai` has no DNS record |
| `apps.yaml` PR | none — deliberately not opened, see "Blocked" |
| Image tag | **none exists.** No publish workflow in this repo |
| Live smoke | not run. CI smoke green on every merge; `scripts/smoke.sh` passes locally against the installed wheel, three times, byte-identically |
| Catalog status | `building` (bumped from `planned` in this PR, now every code slice is merged) |

All six code slices are merged. **Both halves of exam scenario 3 are built**: 20.4 shipped the
coordination half (statements 1.2, 1.3, 5.3) and 20.5 the cited-report half (5.6), so the repo is not in
the state the spec warned against. Calling the scenario *done* is 20.8's job, which is to record both
halves rather than assert them, and 20.8 is open. What is missing is release, and it is missing for a
reason nobody planned for.

## Merged tonight (2026-11-23)

| PR | Slice | Author | Note |
| --- | --- | --- | --- |
| [#15](https://github.com/BreakthruDevelopment/20-discovery-workbench/pull/15) | 20.5 readout synthesis, provenance, coverage | Grok | Review `blocking`: the print boundary it introduced had **zero** tests. Fixed on Grok's branch, merged |
| [#16](https://github.com/BreakthruDevelopment/20-discovery-workbench/pull/16) | #13 never-read sweep on the recording-failure path | Claude Code | `coordinator.py` +4/−3, plus the 54-line test that pins the difference |
| [#20](https://github.com/BreakthruDevelopment/20-discovery-workbench/pull/20) | — | Claude Code | Holds three rules nothing was holding (quote control-stripping, `_LOCKED`, wheel fixtures) |
| [#21](https://github.com/BreakthruDevelopment/20-discovery-workbench/pull/21) | 20.6 CLI, HTTP surface, replay demo, smoke | Grok | Review `blocking`: two defects in the HTTP error paths. Fixed on Grok's branch, merged |

**Open PRs: none.**

## Ready for Grok tonight: nothing

Nothing here needs the Mac runner started for app 20 — but not because Grok's share was small.
**Grok built three of the six slices**: 20.3 (the synthetic discovery pack, #3), 20.5 (#15) and 20.6
(#21). Its fourth, **20.8 the README (#7), is still open and still planned `grok`** — it carries no
label only because `infra#99` is open, so it will come to Grok once the deploy lands.

## Blocked, and why

**The deploy cannot be written.** [`30-apps-infra#99`](https://github.com/BreakthruDevelopment/30-apps-infra/issues/99)
is `claude`-labelled and its dependency closed, so I picked it up — and stopped:

1. **No image exists.** `apps.yaml` needs an immutable `sha-<commit>` tag from the app repo's publish
   workflow. This repo has only `ci.yml` and `review-gate.yml`. An entry naming a tag would deploy one
   that does not resolve.
2. **The image would not serve.** `Dockerfile` ends `ENTRYPOINT ["wb"]` / `CMD ["--version"]` — it prints
   a line and exits. `wb serve` also binds `127.0.0.1` and reads no `PORT`.

Filed as [#24](https://github.com/BreakthruDevelopment/20-discovery-workbench/issues/24) (`claude`), and
`infra#99` now carries a comment explaining it. **Beyond app 20:** `17-agent-container` and
`18-procure-to-pay` have no publish workflow either, while `30-apps-template` does. The whole Python
track is in this position and may deserve one shared decision rather than three copies — apps 18 and 19
were being worked by other runs tonight, so their repos were not touched.

[#7](https://github.com/BreakthruDevelopment/20-discovery-workbench/issues/7) (README) waits on `infra#99`, so it waits on #24.

## Decisions — flagged because Michael might have made them differently

1. **Labelled #21 `security-sensitive`, which the spec does not.** It opens the repo's first public
   unauthenticated network surface and both blocking findings were in it, found by probing rather than
   reading. The spec reserves Codex's reviews for 20.1/20.2/20.4/20.7.
2. **Merged #21 by the second of gate 3's two Codex routes** — which is sanctioned, and which an
   earlier draft of this log got wrong. [`FACTORY.md`](../FACTORY.md) states the requirement as a
   disjunction: a review marked `Reviewer: codex` / `Verdict: ready`, **or** Codex's own GitHub review
   reporting no unresolved findings on the head commit, "since Codex's app doesn't write the marker
   lines". `review-gate.yml` implements both, and the second fired: the `codex-review-state:v1` marker
   read `commit_sha: b90ff118`, `has_any_findings: false`, `has_unresolved_findings: false`, review
   threads empty, and `Reviewer sign-off` went green on the merged head. Nothing was waived.
   Two things are still worth Michael's eye: no review marked `Reviewer: codex` exists on **any** of the
   48 `security-sensitive` PRs across the 23 tagged repos, so route one has never once been used; and
   `AGENTS.md`'s one-line paraphrase names only route one, which is what misled this log — worth naming
   both routes there.
3. **Did not open a speculative `apps.yaml` PR.** Reporting the block beat opening a PR pointing at an
   image that does not exist.
4. **Read the spec's "readout with two coverage gaps" as loose drafting.** The committed recording has one
   failed subagent, hence one gap; the `unknown` maturity level is the same hole counted twice, and the
   spec's own stated gap rule is error propagation only. Grok's reading was right and it did not edit a
   merged 20.4 fixture to manufacture a second. **Worth a one-line spec correction when next touched.**
5. **Edited `.github/workflows/` in #20** — a declared foundation path here, owned by 20.1, unprotected by
   the pre-push guard. Purely additive, declared on the PR, by the harness that owns wave 1.

## Who did what

| Role | Harness | Evidence |
| --- | --- | --- |
| Planner | Claude Code | `specs/20-discovery-workbench.md`, issues #1–#7 |
| Full-stack builder | Claude Code (20.1, 20.2), Grok Build (20.3, 20.6) | #8, #9, #10, #21 |
| AI builder | Claude Code (20.4), Grok Build (20.5) | #11, #15 |
| UI builder | — | No UI: a Python CLI and two text endpoints |
| Reviewer | Claude Code on all 4 PRs (+ Codex on #21) | 2 blocking, then ready on each merged head |
| DevOps | Claude Code | **Blocked before any change.** Nothing written in `30-apps-infra` |
| Docs writer | Grok Build (planned) | #7, open, waiting on `infra#99` |
| Launch drafts | Grok Bot (Michael posts) | Not started: no live URL |

## What slipped, and what surprised us

- **A whole track with no publish workflow.** Six slices of a deployable app were planned, built and
  reviewed without anyone noticing there was no way to publish its image or make the container serve.
  That is a planning gap, not a build gap: no slice in the spec's Issues section owned it. Apps 17 and 18
  are in the same position. **It is worth asking of apps 21+ at spec time, not at deploy time.**
- **Review pushed back on the reviewer's own work, twice**, and both times it was right: #20's third
  assertion was conceded over-specified and rewritten to assert by content, and the same PR shipped
  without holding the `\t` exception it existed to hold until a second round caught it. Six of #15's
  non-blocking follow-ups were also dropped rather than filed, and only four were later written up.
- **Sabotage-verify after committing.** A `git checkout --` during a sabotage matrix wiped uncommitted
  fixes and cost a re-apply.
- The spec routes 20.5 to `claude`; issue #5 was opened and labelled `grok`. Harmless here — Grok built
  it well — but **spec and issue diverged and nothing noticed.**

## Review findings worth keeping

**One of the three blocking findings was a test that cannot fail; the other two were live defects.**
Both kinds are worth keeping.

The test-gap one: 20.5 shipped `workbench/readout/text.py`, a module whose entire purpose is a safety
rule, with no test. With `_quote_lines`' prefix removed the suite stayed green at 306 passed — a
model-authored quote could forge a second `coverage:` block under the real one, which is the single thing
`coverage` exists to prevent.

Four further unheld rules were found and closed the same way, all **non-blocking** when found: 20.6's
`/healthz` could be stubbed `return True, "end_turn"` with every test still passing, so nothing required
the endpoint to touch the agent loop at all; and in 20.5 the ROI bounds check, `_level`'s folding to
`unknown`, the conflict filter and the deliberate `\t` exception in `_quote_lines` were each removable
with the suite green.

The two live ones, both in 20.6, were found **by probing a running server**, not by reading the diff: a
malformed request line got zero bytes and a stderr traceback, and the client's own method was echoed into
the response body and status line. Writing the fix surfaced a third route the review had not found
(`self.command` is `None`, not just `self.path`) and a fifth call site reachable with a *valid* version.
**Lesson for the next slice with a network surface: send it bad bytes.**

One process note: sabotage-verify *after* committing. `git checkout --` during a sabotage matrix wiped
uncommitted fixes and cost a re-apply.

## First three steps tomorrow

1. **[#24](https://github.com/BreakthruDevelopment/20-discovery-workbench/issues/24) — publish workflow and a serving container.** Copy `30-apps-template`'s `publish.yml`; make the image serve by default, bind `0.0.0.0`, read `PORT`. Everything else waits on this.
2. **[`infra#99`](https://github.com/BreakthruDevelopment/30-apps-infra/issues/99) — the `apps.yaml` entry**, once a `sha-` tag exists: aws, `app20.breakthruventures.ai`, `ai: demo`. Fold in [#22](https://github.com/BreakthruDevelopment/20-discovery-workbench/issues/22) **as part of this slice, not after** — `--url` currently checks a version constant across every commit and greps the map without its line numbers, so a stale revision still serving passes with exit 0, which is the one failure a post-deploy smoke exists to catch.
3. **[#7](https://github.com/BreakthruDevelopment/20-discovery-workbench/issues/7) — README**, which unblocks when `infra#99` closes. Then `catalog.yaml` to `done`.

Backlog after that, all `claude` and all small: [#22](https://github.com/BreakthruDevelopment/20-discovery-workbench/issues/22), [#23](https://github.com/BreakthruDevelopment/20-discovery-workbench/issues/23), [#17](https://github.com/BreakthruDevelopment/20-discovery-workbench/issues/17), [#18](https://github.com/BreakthruDevelopment/20-discovery-workbench/issues/18). [#12](https://github.com/BreakthruDevelopment/20-discovery-workbench/issues/12) and [#19](https://github.com/BreakthruDevelopment/20-discovery-workbench/issues/19) touch `workbench/core/` and are deliberately unlabelled for the planner to route.
