# Run log — 18-procure-to-pay

BreakthruSoftwareFactory run log ([`FACTORY.md`](../FACTORY.md)). Link evidence; write "unknown" rather than guess.

| Field | Value |
| --- | --- |
| App | 18, Procure-to-pay workflow |
| Spec | `specs/18-procure-to-pay.md` |
| Repo | https://github.com/BreakthruDevelopment/18-procure-to-pay |
| Live cloud | aws, us-east-2 — **not deployed, and blocked on a decision**, see "Release" below |
| URL | `app18.breakthruventures.ai` — no DNS record; Terraform creates it on deploy |
| `apps.yaml` PR | **none, deliberately.** See `30-apps-infra#97` and "Release" |
| Image tag | **none: app 18 has no `publish` workflow**, so no GHCR image exists |
| Live smoke | n/a — nothing deployed |
| Catalog status | building |

**The build is done: slices 18.1–18.8 are all merged and `main` is green** (`e757f99`), plus the backlog slice
18.11 raised out of a review. What is left is the deploy, and the deploy is blocked on something bigger than a
missing line in `apps.yaml` — app 18 is a Python command-line app on infra built for Next.js containers.

## Open PRs

**None.** `#18` (18.7, batch) merged as `6a39d63`; `#19` (18.8, demo and smoke) merged as `e757f99`.

## Ready for Grok

**Nothing.** `#8` was Grok's last slice here and it merged overnight. `#9` (18.10, README) is `grok`'s but stays
unlabelled while it waits on the deploy.

## Release: blocked, and why

`30-apps-infra#97` (18.9, `claude`, security-sensitive) was labelled when `#8` merged, and I stopped rather than
open the `apps.yaml` PR. Four findings, [recorded in full on the issue](https://github.com/BreakthruDevelopment/30-apps-infra/issues/97):

1. **No image exists.** App 18's `main` has only `ci.yml` and `review-gate.yml`; a deployable app has `publish.yml`.
   `apps.yaml` needs an `image` and an immutable `sha-<commit>` tag that `deploy/aws.sh` copies from GHCR into ECR.
   `.github/workflows/` is one of app 18's wave-1 foundation paths, so adding it wants a `claude`
   security-sensitive foundation slice in the app repo.
2. **The image is a CLI; the stack expects an HTTP server.** `stacks/aws/main.tf:320-321` sets `AWS_LWA_PORT=3000`
   and a readiness path — the Lambda Web Adapter. App 18's Dockerfile ends `ENTRYPOINT ["p2p"]`. `health.py`'s
   `handler` is the right shape for a zip/handler Lambda, not for this stack's `package_type = "Image"` behind API
   Gateway.
3. **The deployer's health gate asks for `/api/health`** (`deploy/aws.sh:336`, `deploy/health.sh:13`); the spec and
   `scripts/smoke.sh` say `/health`. One has to move.
4. **The spec says the second AWS account**; `stacks/aws` is one stack, one provider, one shared RDS in the first.

**Why stopping was the right call rather than trying it:** `stacks/aws` is a single Terraform stack covering every
AWS app, applied whole from `main` every 10 minutes. An entry whose image is absent fails the image copy, and the
deployer sets `DEPLOY_STRICT_HEALTH=1`, so a speculative app 18 entry would put **apps 1, 5 and 9's deploys**
behind a failing run that retries three times and is then left alone.

Worth deciding once for the whole Python track: **app 17's deploy (17.7) was cut on 2026-11-22** as a library with
nothing to deploy. App 18 is not that — it has a real endpoint and the definition of done wants a live smoke — but
it is the second Python app that does not fit this infra, and 19 and 20 are coming.

## Who did what

| Role | Harness | PRs |
| --- | --- | --- |
| Planner | Claude Code | spec, issues `#1`–`#9` |
| Full-stack / AI builder | Claude Code (18.1, 18.2, 18.11), Grok Build (18.3–18.8) | `#10`, `#11`, `#16`; `#12`, `#13`, `#14`, `#17`, `#18`, `#19` |
| Reviewer | Claude Code on every PR; Codex second review on the security-sensitive ones | — |
| DevOps | Claude Code — **stopped**, see "Release" | — |
| Docs writer / Launch drafts | not started | — |

## Decisions taken 2026-11-23 (overnight Claude Code run)

1. **Fixed Grok's blocking defects on its own branches rather than handing the PRs back** — `#18`
   (`c74283b..4f3f9e8`) and `#19` (`2887b3f..1a68e7a`), both ordinary pushes. Grok Build runs only when Michael
   starts it and does not return to a failed PR, so a blocking verdict left alone strands the slice. Both reviews
   say plainly that the reviewer also wrote the fix.
2. **Neither PR labelled `security-sensitive`, and Codex's quota not spent on them.** The spec marks 18.1–18.6
   with an explicit sentence and omits one for 18.7 and 18.8, and both diffs match that reading: no new tool, no
   new write path, no schema change, no authorization surface. **Michael might have decided otherwise for 18.8**,
   which does add a new public surface in `GET /health` — though that surface gets its second review at 18.9,
   which is security-sensitive.
3. **Did not open the `apps.yaml` PR**, for the reasons under "Release". Opening one was the overnight brief's
   expectation; the facts did not support it.
4. **A wave-5 slice touched a wave-1 foundation path and I accepted it.** `#19` adds one line to
   `.github/workflows/ci.yml` wiring its own `scripts/smoke.sh` into the existing smoke step. It renames no job,
   adds no job, trigger, permission or secret, and a smoke script CI never runs is worse than the edit. Note the
   issue's own generated list of forbidden paths does not include `.github/workflows/` — only the spec prose does
   — so the builder followed its instructions as written. If we want that rule enforced where builders read it, it
   belongs in the issue template for this repo.
5. **Three non-blocking suggestions on each PR were recorded, not fixed**, to keep the diffs to the defect. All
   are shared with existing code rather than introduced by these slices.

## Review findings worth keeping

Two blocking defects overnight, both in Grok's slices, both of the kind this track keeps hitting.

**`#18` (18.7) — a budget cut on the last document crashed the run.** The loop carried the budget's reason
whenever a document failed with the budget exhausted, including when that document was the last one, leaving
`stopped_early` set with no `not_reached` document behind it — which `BatchSummary` refuses. The pydantic error was
neither a `P2PError` nor an `OSError`, so it escaped both CLI handlers: a traceback instead of the summary and no
`batch_run` row for the whole run, in the one slice whose job is to always add up. The validator was right and the
loop was wrong, so the loop changed.

**`#19` (18.8) — neither guard on `GET /health` could fail**, which is the recurring defect in its purest form.
`/health` is app 18's entire live surface and the only thing the post-deploy smoke asserts. Three mutations each
left lint, mypy and all 408 tests green: gutting `_round_trip` to `return`; flipping its failure branch to report
`ok`; and the real bug underneath — **app 17's replay errors are not `P2PError`** (`ReplayExhausted` descends from
`RuntimeError`), so a short or malformed recording escaped as an unhandled Lambda error instead of the documented
500 body the smoke reads. Separately, `scripts/smoke.sh --url` asserted only that a `"version"` key was *present*,
never its value, so a deploy still serving the previous image passed the only live check app 18 has. Both fixed;
the script now reads the value and takes `--version sha-<commit>`, which 18.9 should pass.

**Grok's tests were otherwise good, and that is worth recording.** Nine injected defects across the two slices —
`already_advanced` counted as ok, the dotfile filter removed, the >25 refusal removed, `change_key` dropped,
abort-on-first-failure, a `batch_run` row recorded on a refusal, the demo honouring `P2P_DATABASE`, the escalation
scene dropped, redaction made a no-op — each made at least one test fail. And 18.8's demo genuinely derives its
outcomes from the seeded ERP rather than narrating its fixtures: recorded replies carry `confidence: 0.99` and the
demo prints `0.97`, recomputed in code; a flagged supplier's row comes back `ok` with no `change_key` because the
forcing rule blocked staging.

**`ci.yml`'s wheel-import hole is already closed in this repo** — `python -P -c` run from `/tmp`, plus a step that
builds an ERP database from the installed wheel. The overnight brief said it was still open; it is not.

One slice stopped and commented during the build, as the rules require: **18.6** needed a case-wide read the
wave-1 foundation does not expose and is forbidden to add, which became
[`#15`](https://github.com/BreakthruDevelopment/18-procure-to-pay/issues/15) (18.11) and was built as `#16`.

## First three steps tomorrow

1. **Decide how a Python CLI serves one endpoint on this infra** (`30-apps-infra#97`). Either the image gains the
   Lambda Web Adapter and a minimal server on port 3000 returning `health_payload()` — app 18 then fits the
   existing stack unchanged — or the stack grows a per-app handler and health-path option. The first touches only
   app 18; the second touches shared infra every other app depends on. This is Michael's call because it changes
   what the spec promised, and it decides 19 and 20 as well.
2. **Open the foundation slice that adds `publish.yml`** to app 18 (`claude`, security-sensitive, copied from the
   template so the tag is multi-arch), since nothing can deploy without an image.
3. **Then the `apps.yaml` entry, the live smoke with `--version sha-<commit>`, and close-out** — `#9` (README),
   catalog status, this log and `BRIEFING.md`.

## What slipped or surprised us

Grok built six of the nine merged PRs here, more than on any app so far, and the work was good. The cost is that
Grok cannot answer a review, so every blocking finding on its PRs is Claude's to fix or the slice waits for
Michael — that is now the shape of this app's critical path, not a one-off.

The real surprise is the deploy. The track's definition of done assumes a containerised web app, and app 18 is a
command-line tool with one health endpoint. Nobody checked that against `stacks/aws` when the spec was written, so
"add it to `apps.yaml`" was carried as settled work through planning, the spec and the overnight brief, and only
turned out to be a design decision when someone tried to do it at one in the morning.
