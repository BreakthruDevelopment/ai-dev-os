# Run log — 31-cost-scaler

BreakthruSoftwareFactory run log ([`FACTORY.md`](../FACTORY.md)), **written on 2026-11-17** from GitHub only: merged PRs and their reviews, `30-apps-infra` `apps.yaml` and its Terraform runs, and the app's own `Live smoke` workflow. Times are US Central. "Unknown" means GitHub doesn't show it.

| Field | Value |
| --- | --- |
| App | 31, Cloud Cost Scaler |
| Spec | [`specs/31-cost-scaler.md`](../specs/31-cost-scaler.md) (ai-dev-os #31, 2026-11-14; amended by #36, 2026-11-15) |
| Repo | https://github.com/BreakthruDevelopment/31-cost-scaler |
| Live cloud | Google Cloud (Cloud Run, us-central1, always-free; Postgres on the always-free e2-micro, private network only) |
| URL | https://cost-scaler-189497094271.us-central1.run.app — `app31.breakthruventures.ai` pending certificate |
| `apps.yaml` PR | 30-apps-infra #92 (deploy, `sha-9d23e20`), #95 (domain + `sha-b4659b3`) |
| Image tag | `sha-b4659b3` (deployed first as `sha-9d23e20`) |
| Live smoke | **fail**, 2026-11-17 7:02 AM, [run 44087811971](https://github.com/BreakthruDevelopment/31-cost-scaler/actions/runs/44087811971): `SMOKE FAIL: /footprint has no 'outgrows free tier at' line (is the footprint seeded?)`. Health, both page checks and the landing page passed first; nothing has populated the price or footprint tables yet |
| Catalog status | `deployed` (not `done`: the live smoke cannot pass until a price refresh has run — see below) |

## Gates

| Gate | Evidence | Date (Central) |
| --- | --- | --- |
| 1 Spec | ai-dev-os #31, amended by #36 | 11-14, 11-15 |
| 2 Build | 14 merged PRs, all `claude/` branches: #9, #10, #11, #13, #15, #16, #17, #20, #21, #22, #23, #24, #25, #26 | 11-14 to 11-17 |
| 3 Review | `Reviewer sign-off` green on every merged PR. Codex second-reviewed the six `security-sensitive` ones (#9, #10, #13, #15, #22, #24) | 11-14 to 11-17 |
| 4 Release | 30-apps-infra #92 → apply `4 added, 1 changed, 0 destroyed`, health `cost-scaler … -> HTTP 200`; #95 adds the domain mapping and the 16.4.6 tag. Live smoke **fail**, as above | 11-17 6:48–7:05 AM |
| 5 Close-out | This log; `catalog.yaml` `status: deployed`; `BRIEFING.md` updated. Launch drafts: not yet given to Grok Bot | 11-17 |

## Who did what

Roles from PR titles, harness from the branch prefix. **Every slice ran in Claude Code** — no Grok Build, Codex or Antigravity build work on this app.

| Role | Harness | PR | Notes |
| --- | --- | --- | --- |
| Planner | Claude Code | ai-dev-os #31, #36 | 12 slices; the multi-agent advisor was an amendment |
| Full-stack builder | Claude Code | #9, #10, #11, #16, #21, #23, #24 | Schema and access rules; price ingestion for four clouds; the pricing engine, free-tier credits and break-even; pooled-credit ordering; footprint honesty; the price table and admin screens |
| AI builder | Claude Code | #13, #15 | Scaling advisor on Google ADK with four tools and server-side number checks; then a coordinator with pricing and migration agents. Both engines ship as a chain inside one `runAgent()` call, with the engine that answered stored per answer as `checks.engine` |
| UI builder | Claude Code | #17, #20, #22 | Landing, footprint and app detail; `wrap-anywhere` in shared UI; the scenario builder, four-cloud results and compare |
| Reviewer | Claude Code (+ Codex on security-sensitive) | see gate 3 | Findings below |
| DevOps | Claude Code | 30-apps-infra #92, #95; app #34 | Both deploy PRs; added the app's first `live-smoke.yml` |
| Docs writer | Claude Code | #26 | README with every figure sourced to a named constant |
| Launch drafts | Grok Bot (no secrets; Michael posts) | — | Not yet drafted |

## What review caught

The admin quarantine panel is the story of this app. Its copy was **wrong three times** and each version was falsified by a case nobody had enumerated:

1. "Value still in use" — false: `upsertPrices` sets `status = 'quarantined'` and `listPricePoints` filters `status = 'active'`, so the kept price is excluded from pricing. The column had also been showing the *accepted* price under a "Rejected value" heading, measured 4–5× off.
2. "The component it priced is unpriced" — false for size-keyed rows, which snap up to the next listed size: measured exactly 2.0× on `vm.2vcpu-8gb`, with the cloud still reporting `complete: true`.
3. "One of two ways" — a 21-key sweep found rows that come out *too low*: `postgres.storage` at −58% with the cloud not comparable, `load_balancer.capacity` at −26% with the cloud still claiming complete and no note at all.

The fourth version stopped describing the behaviour and stated a bound instead, and a reviewer then failed to falsify it — proving the clearing condition exhaustive rather than merely finding no counterexample. **The lesson worth carrying: when copy makes a claim about system behaviour, exercise the claim rather than reading the code that supposedly backs it.** All three wrong versions read correct in the source.

Codex found the sharpest defect of all: **widening the bounds cannot clear a `jump_over_3x` quarantine**, because `inBounds` is tested first and `JUMP_FACTOR` is hard-coded — so a price that has genuinely moved can never clear, and the copy was telling admins to take an action that does nothing. Three Claude reviews had read that sentence without testing it.

Other review findings, in the order they mattered:

- **#22:** the new-account allowance option was silently dropped when saving, so compare disagreed with the preview the user had just saved.
- **#21:** pooled free-tier credit depended on declaration order; a user could lose $2.67 of credit purely because x86 drew first.
- **#24:** a green "No drift" badge appeared even when **no** stack file could be read.
- Merging #22 and #24 made the header six links wide, and `/admin` measured `scrollWidth` 447 against a 375 viewport — an overflow created by composition that neither PR's CI could catch, and which affected every signed-in visitor, not just admins.

## AI evals (live model)

| Case | Result |
| --- | --- |
| Advisor, live Gemini | Not run against the deployed app: the advisor needs the price table, which is empty until a refresh runs. `AI_PROVIDER` and the key are set by Terraform; `src/lib/ai/demo.ts` fixtures cover CI |

## Definition of done

- [x] README filled (#26; every figure sourced to a named constant, which a review spot-checked against the code)
- [ ] **Live smoke passed after the latest deploy** — fails on the empty footprint; see below
- [x] This run log complete
- [ ] `catalog.yaml` `status: done` and `BRIEFING.md` updated — set to `deployed` for now

## What slipped or surprised us

**The app deploys healthy and still cannot pass its own smoke.** Nothing populates the price and footprint tables at boot: `src/instrumentation.ts` runs migrations and stops, and the only caller of `runFootprintRefresh` is `POST /api/prices/refresh`. That route has two triggers — the Cloud Scheduler job, or an admin pressing "Refresh now" — and **no admin account can exist on a Google Cloud app** (`30-apps-infra#91`): the stack sets no `SEED_*` variables, the app has no first-user promotion, and the Postgres VM has no public IP to promote one by hand. So the scheduler job is the only path, and it next fires at 07:05 UTC. Tracked as `30-apps-infra#89`; `31-cost-scaler#27` corrects `smoke.sh`'s comment, which claims the deployed app imports the footprint itself.

**The deploy needed two PRs, not one.** Terraform creates a Cloud Run domain mapping before the service and the mapping's service must already exist, so a new Google Cloud app goes in with `domain: null` first. The certificate then takes 15 minutes to 24 hours, and `APP_URL` only moves off the run.app URL when a later run observes the mapping `Ready` — which needs a **manual rerun** of the Terraform workflow, since `terraform.yml` has no schedule.

**Every pull-request plan in this repo reads as destructive, and it is an artifact.** This app's deploy PRs planned two and then three destroys — the Build Tracker's scheduler job, the Cloud Scheduler API, and (on #95) app 31's own refresh job. All three are counts that fall to zero because a PR plan is not given the `production` secrets. #92's own numbers prove it: it planned `3 to add` and applied `4 added`, the extra being the refresh job the plan could not see. Confirmed against #87, which touched no Terraform at all and planned the identical destroys. The real risk this exposes is that **nothing but a human reading the plan stands between a genuinely destructive plan and an apply** (`30-apps-infra#93`).

**A first-apply race exists and did not bite.** The Cloud Run service has no `depends_on` for its database and no startup probe, while databases are created by a 60-second timer on the Postgres VM. The apply happened to modify the VM metadata (12s) before creating the service (22s), so the database was there in time. That was ordering luck, not design (`30-apps-infra#90`).

**Nine issues were filed off this app's reviews**, seven of them on 11-17: `#27`–`#33` in the app repo plus `30-apps-infra#89`–`#91`. The three worth reading first are `#30` (a quarantined size-keyed row doubles an estimate while reporting complete, and the obvious fix relocates the problem into the like-for-like panel), `#31` (no way to accept a moved price) and `#32` (a quarantined row whose SKU leaves the feed is permanent too, and looks identical to a live one).

**Two untracked Google Cloud free-tier limits** turned up during the deploy review: Artifact Registry's 0.5 GB, undocumented here, and Cloud Run's 180,000 always-free vCPU-seconds — against which this app's nightly refresh is roughly 30% worst case, the first long-running workload in the fleet (`30-apps-infra#94`).
