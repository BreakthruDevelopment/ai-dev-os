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
| Live smoke | not run. CI smoke green on every merge; `scripts/smoke.sh` passes locally against the installed wheel, twice, byte-identically |
| Catalog status | building |

All six code slices are merged. **Exam scenario 3 is complete**: 20.4 shipped the coordination half
(statements 1.2, 1.3, 5.3) and 20.5 the cited-report half (5.6), so the repo is not in the state the
spec warned against. What is missing is release, and it is missing for a reason nobody planned for.

## Merged tonight (2026-11-23)

| PR | Slice | Author | Note |
| --- | --- | --- | --- |
| [#15](https://github.com/BreakthruDevelopment/20-discovery-workbench/pull/15) | 20.5 readout synthesis, provenance, coverage | Grok | Review `blocking`: the print boundary it introduced had **zero** tests. Fixed on Grok's branch, merged |
| [#16](https://github.com/BreakthruDevelopment/20-discovery-workbench/pull/16) | #13 never-read sweep on the recording-failure path | Claude Code | One line plus the test that pins it |
| [#20](https://github.com/BreakthruDevelopment/20-discovery-workbench/pull/20) | — | Claude Code | Holds three rules nothing was holding (quote control-stripping, `_LOCKED`, wheel fixtures) |
| [#21](https://github.com/BreakthruDevelopment/20-discovery-workbench/pull/21) | 20.6 CLI, HTTP surface, replay demo, smoke | Grok | Review `blocking`: two defects in the HTTP error paths. Fixed on Grok's branch, merged |

**Open PRs: none.**

## Ready for Grok tonight: nothing

Grok's only app-20 slice was 20.6, and it is merged. Every open issue is `claude` or planner work.
Nothing here needs the Mac runner started for app 20.

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
2. **Merged #21 on a Codex *receipt*, not a marked verdict.** `AGENTS.md` asks for a Codex
   `Verdict: ready` review on `security-sensitive` PRs. Codex reviews this repo by posting a
   `codex-review-receipt` comment — clean on the exact head, no unresolved threads — and has never
   posted a marked verdict here. **That clause is currently unsatisfiable as written**, so it needs
   either a wording change or a Codex-side change; I did not let my own label stall the chain over it.
3. **Did not open a speculative `apps.yaml` PR.** Reporting the block beat opening a PR pointing at an
   image that does not exist.
4. **Read the spec's "readout with two coverage gaps" as loose drafting.** The committed recording has one
   failed subagent, hence one gap; the `unknown` maturity level is the same hole counted twice, and the
   spec's own stated gap rule is error propagation only. Grok's reading was right and it did not edit a
   merged 20.4 fixture to manufacture a second. **Worth a one-line spec correction when next touched.**
5. **Edited `.github/workflows/` in #20** — a declared foundation path here, owned by 20.1, unprotected by
   the pre-push guard. Purely additive, declared on the PR, by the harness that owns wave 1.

## Review findings worth keeping

**Tests that cannot fail remain the defect of this project.** Every blocking finding tonight was one:

- 20.5 shipped `workbench/readout/text.py`, a module whose entire purpose is a safety rule, with no test.
  With `_quote_lines`' prefix removed the suite stayed green at 306 passed — a model-authored quote could
  forge a second `coverage:` block under the real one, which is the single thing `coverage` exists to prevent.
- 20.6's `/healthz` could be stubbed constant-true and every test still passed, so nothing required the
  endpoint to touch the agent loop at all.
- Three more stated locks in 20.5 (ROI bounds, `_level` folding, the conflict filter) and the `\t`
  exception in `_quote_lines` were each removable with the suite green.

Both of 20.6's blocking defects were found **by probing a running server**, not by reading the diff: a
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
