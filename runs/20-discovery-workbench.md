# Run log — 20-discovery-workbench

BreakthruSoftwareFactory run log ([`FACTORY.md`](../FACTORY.md)). Link evidence; write "unknown" rather than guess.

| Field | Value |
| --- | --- |
| App | 20, Discovery workbench |
| Spec | `specs/20-discovery-workbench.md` |
| Repo | https://github.com/BreakthruDevelopment/20-discovery-workbench |
| Live cloud | aws — `apps.yaml` entry merged 2026-11-28 (`30-apps-infra#100`); the deployer Lambda pulls `main` every 10 minutes |
| URL | `https://app20.breakthruventures.ai` — DNS created by Terraform on deploy. **Not yet reached by anyone**, see "What is still open" |
| `apps.yaml` PR | [`30-apps-infra#100`](https://github.com/BreakthruDevelopment/30-apps-infra/pull/100), merged 2026-11-28 |
| Image tag | `sha-d5358ad` — 2-platform OCI index; the `linux/arm64` digest is byte-identical to the manifest the arm64 native build exported after passing the AArch64 adapter check |
| Live smoke | **still not run.** The 2026-11-28 session's egress proxy refuses `app20.breakthruventures.ai` (HTTP 403, host not allowed). CI smoke green on every merge; `scripts/smoke.sh --url` passes against a locally served instance |
| Catalog status | `building`, bumped from `planned` in #74 (not in this PR; `catalog.yaml` is untouched here). **Neither `building` nor `deployed` now fits**: `FACTORY.md` defines `building` as "not in `apps.yaml` yet", which is no longer true, and `deployed` as in `apps.yaml` **and** answering `/api/health`, which nobody has verified |

**Updated 2026-11-28.** Everything from here to "Release, 2026-11-28" was written on **2026-11-23** and is
kept as a record of what was known then. Several of its cells are now false — the DevOps and Docs-writer
rows, the reviewer's PR counts, "Open PRs: none", "Ready for Grok tonight: nothing" and "What is missing is
release". **Where the two disagree, the 2026-11-28 sections are current.** They are kept rather than edited
because the 2026-11-23 diagnosis was right and the gap it did not see is the more interesting half.

The release is no longer blocked: three more PRs closed the two gaps that made the
app undeployable, and the `apps.yaml` entry is merged. What remains is the README and a live smoke nobody
has been able to run. The "Blocked, and why" section below is kept as written on 2026-11-23, because its
diagnosis was right and the second gap it did not see is the more interesting half of the story.

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

**Open PRs: none** *(true on 2026-11-23; Grok opened five on 2026-11-24 — see 2026-11-28 below)*.

## Ready for Grok tonight: nothing *(2026-11-23; wrong by the next morning)*

Nothing here needs the Mac runner started for app 20 — but not because Grok's share was small.
**Grok built three of the six slices**: 20.3 (the synthetic discovery pack, #10), 20.5 (#15) and 20.6
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
| Reviewer | Claude Code on all 9 PRs; Codex on all four `security-sensitive` ones (#8, #9, #11, #21) | **11 blocking rounds** — 3 on #9, **6 on #11 (20.4, the most review-heavy slice of the app)**, 1 on #15, 1 on #21 — then `ready` on each merged head. Codex left suggestions on #9 and #11 (#11's became issue #12) and a clean marker on #8 and #21 |
| DevOps | Claude Code | **Blocked before any change.** Nothing written in `30-apps-infra` |
| Docs writer | Grok Build (planned) | #7, open, waiting on `infra#99` |
| Launch drafts | Grok Bot (Michael posts) | Not started: no live URL |

## What slipped, and what surprised us

- **A whole track with no publish workflow.** Six slices of a deployable app were planned, built and
  reviewed without anyone noticing there was no way to publish its image or make the container serve.
  That is a planning gap, not a build gap: no slice in the spec's Issues section owned it — 20.1 owns
  `.github/workflows/` but names only a Dockerfile, and 20.7 is the `apps.yaml` entry. Apps 17, 18 and 19
  are all in the same position. **It is worth asking of apps 21+ at spec time, not at deploy time.**
- **Review pushed back on the reviewer's own work, twice**, and both times it was right: #20's third
  assertion was conceded over-specified and rewritten to assert by content, and its first commit did not
  yet hold the `\t` exception it existed to hold — caught at `141c212` and held in the second commit, so
  it never merged unheld. Of #15's six non-blocking findings, three were filed as #17–#19 (eleven minutes
  after the merge, not before it), two were held in code in #20, and the sixth — the unbounded
  `coverage.gaps[]` count and the uncapped run-state block in `build_message` — was found still unfiled
  when this log was reviewed, and is now #25. **Non-blocking findings need filing in the same turn as the
  merge, or they are only remembered by whoever happens to re-read the review.**
- **Sabotage-verify after committing.** A `git checkout --` during a sabotage matrix wiped uncommitted
  fixes and cost a re-apply.
- The spec routes 20.5 to `claude`; issue #5 was opened and labelled `grok`. Harmless here — Grok built
  it well — but **spec and issue diverged and nothing noticed.**

## Review findings worth keeping

Of **2026-11-23's** three blocking findings (the table above counts all 11 the app took), one was a test
that cannot fail and the other two were live defects. Both kinds are worth keeping.

The test-gap one: 20.5 shipped `workbench/readout/text.py`, a module whose entire purpose is a safety
rule, with no test. With `_quote_lines`' prefix removed the suite stayed green at 306 passed — a
model-authored quote could forge a second `coverage:` block under the real one, which is the single thing
`coverage` exists to prevent.

Five further unheld rules were found and closed the same way, all **non-blocking** when found: 20.6's
`/healthz` could be stubbed `return True, "end_turn"` with every test still passing, so nothing required
the endpoint to touch the agent loop at all; and in 20.5 the ROI bounds check, `_level`'s folding to
`unknown`, the conflict filter and the deliberate `\t` exception in `_quote_lines` were each removable
with the suite green.

The two live ones, both in 20.6, were found **by probing a running server**, not by reading the diff: a
malformed request line got zero bytes and a stderr traceback, and the client's own method was echoed into
the response body and status line. Writing the fix surfaced a third route the review had not found
(`self.command` is `None`, not just `self.path`) and a fifth call site reachable with a *valid* version.
**Lesson for the next slice with a network surface: send it bad bytes.**

## Release, 2026-11-28: three PRs, and a mistake that changed a decision

| PR | Closes | What |
| --- | --- | --- |
| [#26](https://github.com/BreakthruDevelopment/20-discovery-workbench/pull/26) | #24 | `publish.yml`, byte-identical to the template's but for a comment. `CMD ["serve"]`, `EXPOSE`, `uv sync --locked`. `wb serve` binds every interface and reads `PORT`. Two CI steps that run the built container and curl it |
| [#30](https://github.com/BreakthruDevelopment/20-discovery-workbench/pull/30) | #29 | The second gap #24 did not see: the stack runs a `package_type="Image"` Lambda behind the Web Adapter at `AWS_LWA_PORT=3000`. Adapter, `ENV PORT=3000`, absolute `ENTRYPOINT`, in-build ELF architecture check |
| [#38](https://github.com/BreakthruDevelopment/20-discovery-workbench/pull/38) | #36 | `/api/health` as an alias of `/healthz`, after the health-gate mistake below |
| [`infra#100`](https://github.com/BreakthruDevelopment/30-apps-infra/pull/100) | `infra#99` | The `apps.yaml` entry, `tag: sha-d5358ad` |

**The planning gap went one layer deeper than #24 found.** #24 correctly said there was no way to publish
the image or make the container serve, and defined done as `docker run -p 8080:8080` answering. That is a
plain container runtime, and AWS here is not one: `stacks/aws/main.tf` deploys every app as a Lambda
behind the Web Adapter. So #26 shipped a publishable, serving image that **still could not have started**.
Worth saying plainly for apps 21+: *"it builds"*, *"it serves"* and *"it deploys"* are three different
claims, and this app had a test for only the first two.

### The mistake, recorded because Michael decided on it — and found by review, not by me

I told him app 20's missing `/api/health` route was harmless, because "a 404 does not fail that gate, only
a never-answers `000` does", and he reasonably chose to leave it and have me note it. That is true of
**`deploy/health.sh` — which never runs for AWS**; only `apply-azure` and `apply-gcp` call it. The AWS gate
is the inline block at `deploy/aws.sh:326-347`, which flags any non-200 and `exit 3`s under
`DEPLOY_STRICT_HEALTH=1`, set by `deployer.sh:139`.

And `exit 3` skips the `last_sha`/`last_hash` writes, so the "nothing AWS-relevant changed" short-circuit
would never match again: **every later commit to `main`, docs-only included, would re-deploy all five AWS
apps and report failure**, three attempts each, before giving up. "Leave it" was never an available
option. **Credit where it belongs: the review of [`infra#100`](https://github.com/BreakthruDevelopment/30-apps-infra/pull/100)
found this**, not I — #36 opens "Found while reviewing `30-apps-infra#100`", and #30's own review had
earlier accepted the deferral without challenging it. Michael was told before the fix went in, not after,
and the fix went app-side so `30-apps-infra` stayed untouched. Filed with a second defect review found and I had not — `health_deadline` is computed once
before the loop, so it is one shared budget and starves whichever apps sort last — as
[`infra#101`](https://github.com/BreakthruDevelopment/30-apps-infra/issues/101). That second one the review
flagged as "not in the PR body and not in Codex's finding" — it was nobody's prior knowledge.

### What review caught that the author did not

Eight review submissions across #26, #30 and #38, of which **exactly one was blocking** — the bare
`ENTRYPOINT` on #30 at `e31bd5a9`. The other two below were non-blocking findings that were then taken up,
which is the more common and more useful shape:

- **`ENTRYPOINT ["wb"]` was a bare name where AWS documents an absolute path.** `wb` is at
  `/opt/venv/bin/wb`, which is not on Lambda's default `PATH`. Whether it would have worked anyway is
  **not observable from outside** — it turns on whether Lambda's init resolves the command against the
  merged environment — which is exactly why it was worth blocking rather than arguing about. The PR's "byte-for-byte the template" argument did not reach it: the
  template's first word is `node`, at `/usr/local/bin/node`, already on that path. App 20 is the first
  image on this stack with an entry point outside `/usr/local/bin`, so there was no precedent either way.
- **A guard that could be commented out and still pass.** The new architecture-check test grepped the raw
  Dockerfile, so commenting the check out passed all eight tests *and* kept the build green. Comment lines
  are stripped first now. The same file already had the right idiom three tests above it (`test_the_build_validates_the_lock`).
- **`COPY --from` an external image can hand over a wrong-architecture binary**, and `ci.yml`'s `test -x`
  cannot see it: that job runs on amd64 while the deployed image is arm64. Now proved inside both platform
  builds by reading the adapter's ELF `e_machine`. A wrong-arch adapter now fails `publish.yml`'s arm64
  job, and because `merge` has `needs: build`, **no tag is created at all**.


### What the author caught, before review saw it

- **`int()` accepts any Unicode decimal digit**, so `PORT="٨٠٨٠"` (Arabic-Indic) parsed as 8080 and bound a
  port nothing asked for. The `isascii()` gate and its test shipped in #26 as authored; #26's review then
  confirmed the `٨٠٨٠` case is load-bearing by removing the gate and watching exactly that parameter fail.
  Recorded separately because the point of a sabotage matrix is that it catches its author.

### Two process notes worth keeping

- **`git checkout HEAD -- <file>` during a sabotage matrix reverts to `HEAD`**, which on a branch with no
  commit yet is the base — so it discards work in progress, not just the sabotage. It landed one commit carrying the `/api/health` tests, smoke check and CI step *without* the
  dispatch line they test. Three tests failed at once, including a `test_smoke.py` the author had not known
  existed, and it was fixed forward rather than force-pushed. **This is the second time this exact trap has
  cost this app a re-apply** — it is already recorded above from 2026-11-23. Commit before sabotaging.
- **Codex's receipt and its `codex-review-state` marker disagreed on the same head.** The receipt said
  "Didn't find any major issues" while the marker said `has_unresolved_findings: true` and the inline P1 was
  live and correct. The gate reads the marker; so should a human. Separately, Codex raised the same
  `.github/workflows/` wave-1 finding on two PRs and **withdrew it itself both times** once a real new
  commit gave it a fresh look — which is the right way to close a finding you disagree with. Resolving the
  thread by hand was refused by the session's permission classifier, correctly.

## Gates

| Gate | State |
| --- | --- |
| 1 spec | done — `specs/20-discovery-workbench.md`, issues #1-#7 |
| 2 build | done — all six code slices merged, plus #26, #30, #38 and seven defect PRs |
| 3 review | done on every merged PR; Codex on all seven `security-sensitive` ones |
| 4 release | **partial.** `apps.yaml` merged and the image published; **the live smoke has never run** |
| 5 close-out | **incomplete.** This log is current; the README is open; `catalog.yaml` is not `done` |

## Grok's PRs, which this run nearly missed

Grok opened **five** PRs on 2026-11-24 while this app was blocked, and the 2026-11-28 run did not re-check
for them after resuming — it had checked once on 2026-11-23, found none, and never looked again. They were
surfaced by the review of this very log, which is the only reason they are recorded here. **The standing
instruction is to check for other harnesses' PRs at the start of every run and after every slice; "once per
session" is not that**, and a session that spans five days makes the difference matter.

| PR | Issue | Outcome |
| --- | --- | --- |
| [#31](https://github.com/BreakthruDevelopment/20-discovery-workbench/pull/31) | #23 | merged 2026-11-28 07:59Z |
| [#32](https://github.com/BreakthruDevelopment/20-discovery-workbench/pull/32) | #27 | merged 2026-11-28 07:59Z |
| [#33](https://github.com/BreakthruDevelopment/20-discovery-workbench/pull/33) | #28 | merged 2026-11-28 08:00Z |
| [#34](https://github.com/BreakthruDevelopment/20-discovery-workbench/pull/34) | #28 | closed unmerged — same issue as #33, and it had become conflicted |
| [#35](https://github.com/BreakthruDevelopment/20-discovery-workbench/pull/35) | #7 | **open, draft** |

The first four were cleared at 07:59-08:00Z by another actor on the shared account, not by this run.
**#27 and #28 were issues this run filed** from #26's review, and Grok fixed both — so the filing worked as
intended, and only the not-looking-again did not.

[#35](https://github.com/BreakthruDevelopment/20-discovery-workbench/pull/35) is Grok's README, deliberately
kept a draft until the deploy was live, with every deploy-dependent line marked `TODO(deploy)` and no URL or
result invented — the right call. Its blocker is now closed, and it has a comment carrying the real values
for each placeholder (the `apps.yaml` entry, the runtime, "no new IAM", and the three routes). **It was left
as the author's draft rather than finished by this run**, because the one thing still missing is a live
result nobody can obtain yet.

## What is still open

1. **The live smoke has never run.** `scripts/smoke.sh --url https://app20.breakthruventures.ai`. The
   2026-11-28 session's egress proxy refuses that domain outright (HTTP 403), so its ten `000`s were the
   proxy and not the app. **Nobody has curled the arm64 artifact**; the first automatic deploy is the first
   time that exact manifest runs. Pair it with
   `aws lambda get-function --function-name 30apps-discovery-workbench --query 'Code.ImageUri'`, which turns
   "the smoke passed" into "this exact image answered" — worth doing because `/healthz` reports
   `workbench.__version__` rather than `APP_VERSION`, and `scripts/smoke.sh:19` greps that literal, so
   the smoke alone cannot say which image is live — which is what [#22](https://github.com/BreakthruDevelopment/20-discovery-workbench/issues/22) is for. It is better than it
   was: since `--url` now also checks `/api/health`, a pass positively rules out `sha-ee7f244` and earlier.
2. **[#7](https://github.com/BreakthruDevelopment/20-discovery-workbench/issues/7) — README.** Not a
   from-scratch job: **[#35](https://github.com/BreakthruDevelopment/20-discovery-workbench/pull/35) already
   exists** as Grok's draft and is written. Lifting the draft and filling its three `TODO(deploy)` lines is
   the work, and the last of those needs a live smoke result.
3. **`catalog.yaml` stays `building`** until the README and the live smoke are both done.

Backlog as of 2026-11-28, after Grok closed #23, #27 and #28:
[#17](https://github.com/BreakthruDevelopment/20-discovery-workbench/issues/17),
[#18](https://github.com/BreakthruDevelopment/20-discovery-workbench/issues/18),
[#22](https://github.com/BreakthruDevelopment/20-discovery-workbench/issues/22) and
[#25](https://github.com/BreakthruDevelopment/20-discovery-workbench/issues/25), all `claude` and all small.
**#22 is worth doing before the live smoke is trusted**: it is the one that makes the smoke able to say
which build answered.
[#12](https://github.com/BreakthruDevelopment/20-discovery-workbench/issues/12) and
[#19](https://github.com/BreakthruDevelopment/20-discovery-workbench/issues/19) touch `workbench/core/` and
are deliberately unlabelled for the planner to route. Not yet filed: `smoke.sh`'s new `/api/health` check is
not itself pinned by a test, and `/healthz` should report `APP_VERSION` — a generic win for every app.

## Beyond app 20: the whole Python track

Apps 17, 18 and 19 are all absent from `apps.yaml`, none has a publish workflow, and
`grep -c lambda-adapter Dockerfile` is **0** in each. Prep was filed as issues only — no code, branches or
clones touched — at [`17-agent-container#29`](https://github.com/BreakthruDevelopment/17-agent-container/issues/29),
[`18-procure-to-pay#22`](https://github.com/BreakthruDevelopment/18-procure-to-pay/issues/22) and
[`19-enablement-kit#28`](https://github.com/BreakthruDevelopment/19-enablement-kit/issues/28), each carrying
the copy-paste patch and the reasoning above.

**All three need a deployed surface designed, not just a Dockerfile edited** — app 20 was the only one of
the four that already had an HTTP server. App 17 ends `CMD ["demo"]` and its only subcommand is `demo`;
app 18 (`batch`, `demo`, `dispute`, `ingest`, `match`) and app 19 (`review`, `review-ci`, `session`) both
end `CMD ["--version"]` and neither has an HTTP server at all. App 18's only server is `p2p/mcp/server.py`,
an MCP **stdio** gateway, which the Web Adapter cannot front. So each of the three needs a `serve` command
and a health route written before its Dockerfile matters.

Worth asking at spec time for apps 21+ rather than at deploy time — the same lesson #24 drew, now with a
second instance behind it.
