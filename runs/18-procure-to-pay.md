# Run log — 18-procure-to-pay

BreakthruSoftwareFactory run log ([`FACTORY.md`](../FACTORY.md)). Link evidence; write "unknown" rather than guess.

| Field | Value |
| --- | --- |
| App | 18, Procure-to-pay workflow |
| Spec | `specs/18-procure-to-pay.md` |
| Repo | https://github.com/BreakthruDevelopment/18-procure-to-pay |
| Live cloud | aws, us-east-2 (second account) — **not deployed yet** |
| URL | `app18.breakthruventures.ai` — no DNS record yet; Terraform creates it on deploy |
| `apps.yaml` PR | none yet; the deploy issue is `30-apps-infra#97` |
| Image tag | n/a |
| Live smoke | n/a — nothing deployed |
| Catalog status | building |

Seven of the ten slices are merged, plus the backlog slice 18.11 raised out of a review. The remaining chain — demo and smoke, then deploy, then README — is
**entirely behind one Grok slice**, `#8`.

## Open PRs

**None.** `#18` (18.7, batch run over a folder) was the last one open and merged at `6a39d63` on 2026-11-23.

## Ready for Grok tonight

| Issue | Slice | Note |
| --- | --- | --- |
| [`#8`](https://github.com/BreakthruDevelopment/18-procure-to-pay/issues/8) | 18.8, command-line demo, recorded replies, smoke | Labelled `grok` 2026-11-23 when `#7` merged. **The only runnable issue in this repo**, and the whole tail depends on it |

Grok Build is a CLI on Michael's Mac, so `#8` needs `scripts/run-harness.sh grok` started there; the label alone
starts nothing.

## Blocked, and why

| Item | Waiting on |
| --- | --- |
| `30-apps-infra#97` (18.9, deploy — `claude`, security-sensitive) | `#8`. It is a one-line `apps.yaml` entry and needs no credentials — AWS pulls `main` every 10 minutes — but there is no point deploying before there is a smoke test to run against `GET /health` |
| [`#9`](https://github.com/BreakthruDevelopment/18-procure-to-pay/issues/9) (18.10, README — `grok`) | `30-apps-infra#97`, so transitively on `#8` too |

Nothing is blocked on a missing contract, a credential, or app 17: the pinned `v0.1.0` tag has everything the
merged slices needed, and no slice has had to stop and comment.

## Who did what

| Role | Harness | PRs |
| --- | --- | --- |
| Planner | Claude Code | spec, and issues `#1`–`#9` |
| Full-stack / AI builder | Claude Code (18.1, 18.2, 18.11), Grok Build (18.3–18.7) | `#10`, `#11`, `#16`; `#12`, `#13`, `#14`, `#17`, `#18` |
| Reviewer | Claude Code on every PR; Codex second review on the security-sensitive ones | — |
| DevOps / Docs / Launch drafts | not started | — |

## Decisions taken 2026-11-23 (overnight Claude Code run)

1. **Fixed Grok's blocking defect on its own branch rather than handing `#18` back.** Grok Build runs only when
   Michael starts it and does not return to a failed PR, so a blocking verdict left alone would have stranded the
   slice. An ordinary push (`c74283b..4f3f9e8`), never a force-push. The review says plainly that the reviewer
   also wrote the fix.
2. **No `security-sensitive` label on `#18`, and Codex's quota not spent on it.** The spec marks 18.1–18.6 with an
   explicit sentence and deliberately omits one for 18.7, and the diff matches: no new tool, no new write path, no
   schema change, no `p2p/core/` change, no new authorization surface. The counter-argument is amplification — one
   command now stages twelve postings instead of one — but that is throughput on an already-reviewed path whose
   apply side still needs a second principal. **Michael might have decided this differently.**
3. **`#8` left with Grok rather than re-pointed to `claude`.** It is Grok's slice by the spec and the overnight
   brief is explicit that Claude only reviews, fixes and merges other harnesses' work. Re-pointing it is a
   planning call, not a 3am one — but it is the single thing standing between app 18 and a deploy.

## Review findings worth keeping

`#18` (18.7) — one blocking defect, found by the `reviewer` subagent and confirmed by two reproductions:

**A budget cut on the last document crashed the run.** The run loop carried the budget's reason whenever a
document failed with the budget exhausted, including when that document was the last one — leaving
`stopped_early` set with no `not_reached` document behind it, which `BatchSummary` refuses. The pydantic error was
neither a `P2PError` nor an `OSError`, so it escaped both CLI handlers: a traceback instead of the summary, and no
`batch_run` row for the whole run, in the one slice whose job is to always add up. The validator was right and the
loop was wrong, so the loop changed. Realistic trigger: the wall clock on a live 25-document run.

**The tests were not of the cannot-fail kind** — the standing defect in this track. Six injected defects
(`already_advanced` counted as ok, the dotfile filter removed, the >25 refusal removed, `change_key` dropped,
abort-on-first-failure, a `batch_run` row recorded on a refusal) each made at least one test fail, and the two new
regression tests were each confirmed to fail without the fix.

**`ci.yml`'s wheel-import hole is already closed** in this repo — `python -P -c` run from `/tmp`, plus a step that
builds an ERP database from the installed wheel. The overnight brief said it was still open; it is not.

Three suggestions were left on the PR and not taken, all shared with `p2p ingest` rather than introduced by 18.7:
an `except OSError` that misattributes a folder permission error to the database, a whole-file read before the
20,000-char cap, and a default budget that does not scale down with the folder.

## First three steps tomorrow

1. **Get `#8` moving** — it gates everything. Either Michael starts `scripts/run-harness.sh grok` on the Mac, or
   the slice is re-pointed to `claude`/`codex` as a planning decision. Nothing else in app 18 can progress first.
2. **Merge `#8`'s PR when it is green**, then open `30-apps-infra#97` — a one-line `apps.yaml` entry for aws /
   us-east-2. Read the Terraform plan before merging and stop for Michael if it would destroy anything beyond a
   known change. The app is live about ten minutes after that merge.
3. **Live smoke against `GET /health`**, then release labels so `#9` (README) opens for Grok, and close out:
   catalog status, this log, `BRIEFING.md`.

## What slipped or surprised us

Grok built five of the eight merged PRs here — more than on any app so far — and the work was good: 18.7 came
in with a 532-line test file that survived six mutations. The cost is that Grok cannot answer a review, so every
blocking finding on its PRs is Claude's to fix or the slice waits for Michael. That is now the shape of app 18's
critical path, not a one-off.
