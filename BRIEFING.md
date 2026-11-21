# Project briefing

Read this first if you're an AI harness (or a person) joining the **30 apps in 30 days** build. It's the current
state of every decision; the rules themselves are in [`AGENTS.md`](AGENTS.md).

The process that builds the apps is called the **BreakthruSoftwareFactory**: this playbook, its eight roles, the five
daily gates (spec, build, review, release, close-out) and the definition of done, all in [`FACTORY.md`](FACTORY.md).

_Last updated: 2026-11-15 (apps 16-32 re-aimed at the AI Engineer Roadmap, app 33 added, models served from the
Mac mini: [`ROADMAP.md`](ROADMAP.md). Before that: waves, `Planned harness:` lines, label release and a fail-closed
Mac runner, after the app 13 incident below). Since 2026-11-12, agents may squash-merge app-repo PRs once CI and review are green; Claude
Code also merges green deploy and playbook PRs; spec PRs stay with Michael._

## What we're building and why

Michael Parrott (Breakthru Ventures) is building a GitHub portfolio to win clients and roles as a **forward
deployed engineer**. The plan: 30 small, production-shaped web apps in 30 days, each solving a problem clients
commonly pay for, each with one AI feature, each deployable to **AWS, Azure, Google Cloud and Oracle Cloud**.
The agent setup that builds them (this repo) is itself a portfolio piece: an AI operating system across vendors.

## Decisions in force

| Area | Decision |
| --- | --- |
| Apps | Responsive web apps only (must work at 375px). No native mobile apps. |
| Stack | Next.js + TypeScript, Postgres via Drizzle, Better Auth with `user`/`admin` roles, Tailwind. One container image per app. **One exception:** app 33 is Python (FastAPI + Streamlit), deliberately, to cover the roadmap's Python half. |
| Starting point | Every app is created from [`30-apps-template`](https://github.com/BreakthruDevelopment/30-apps-template), which already has auth, roles, the AI gateway, tests, CI and a Dockerfile. |
| AI in the apps | Every model call goes through the template's `generate()` gateway. Default model: Gemini on the free tier (key in a no-billing AI Studio project; set `ai: gemini` in `apps.yaml`). A missing key falls back to demo answers. Recorded demo answers when the quota runs out. Claude is an optional config switch. Open-weights models are to run on **Michael's Mac mini** behind a free Cloudflare Tunnel, health-checked with a Gemini fallback so a sleeping mini never breaks a live demo - **not built yet**: `generate()` picks one provider, allows only gemini/anthropic/demo and falls back to fixtures, so this needs a template change (app 33's second slice). Until then the apps use Gemini. |
| Clouds | Free tiers only. Each app is live on one cloud, rotating AWS → Azure → Google Cloud → Oracle by app number (an app may opt out with a `rotation_reason` in `catalog.yaml`: app 33 is pinned to the Oracle Always Free VM because a Python service needs a long-running host); listing more clouds for it in `apps.yaml` deploys it there too. The Oracle Always Free VM is the permanent demo host. Details below. |
| Deploys | [`30-apps-infra`](https://github.com/BreakthruDevelopment/30-apps-infra): `apps.yaml` lists each app, its clouds and its exact image tag; changing it is how you deploy. Merging to `main` applies Azure, Google Cloud and Oracle from GitHub Actions. AWS deploys itself: a deployer Lambda inside the account pulls `main` every 10 minutes and applies it (`30-apps-infra` #52, #53); one command in AWS CloudShell is the fallback. Apps migrate their own database on startup. |
| Domains | `appN.breakthruventures.ai` for app N. DNS is hosted at Cloudflare (free plan); each app's records are created automatically by Terraform on deploy when the app has a `domain` in `apps.yaml` (`30-apps-infra` README, "Custom domains and DNS"). Other records stay hand-managed. |
| GitHub | Org `BreakthruDevelopment`. It also holds unrelated apps that must never be touched: only repos tagged `30-apps-30-days` are in scope. |
| Budget | Nothing beyond the existing subscriptions (Claude, X/Grok, ChatGPT Plus, Google AI Pro) and cloud free tiers. No extra credits, no paid services. |
| AWS demo track | **Apps 17-20 are an exception to the Stack, AI, Clouds and Budget rows** (Michael, 2026-11-19). Four Python repositories on Amazon Bedrock (Claude Sonnet 4.6, us-east-2) in a second AWS account, built for a Caylent interview on 2026-12-01: one shared agent container and three demos that cover the Claude Certified Architect exam's six scenarios. Build target 2026-11-24. Plan: [`specs/day-0-aws-demo-track.md`](specs/day-0-aws-demo-track.md). |
| Order | App 1 is the **Build Tracker**, built first so it serves as mission control for the month. Full list in [`catalog.yaml`](catalog.yaml). |
| Pace | 30-35 days total for the whole portfolio; the roadmap's W01-W16 are topic labels, not a schedule. Twenty-one apps remain against roughly 17-22 days, so it fits only if repeated work is built once and reused: retrieval/rerank/evals in app 33; HITL approvals, webhooks and agent tracing as optional template modules (new files only, so live apps are untouched). Parallelism is **across harnesses**, never many agents inside one Claude Code session (still on the dropped list): Claude Code runs foundations, reviews, merges, app 33 and template modules sequentially; Grok takes UI and docs; Codex takes non-security slices. Claude Code is the constraint, so moving work out of it buys more than making it faster. If it still doesn't fit, the answer is fewer apps or more days, not a thinner definition of done. |
| Roadmap coverage | Apps 16-33 are aimed so that together they prove every week of the **AI Engineer Roadmap** (W01-W16). Scored honestly in [`ROADMAP.md`](ROADMAP.md): **live** only when running in a deployed app, **built** when merged but not deployed, and the two are never conflated. Today: 0 live, 3 built, 10 partial, 3 gaps (a week is live only when every topic in it is; W02 is held back by OOP alone). Deploying app 31 flips all three **built** weeks to **live**, the largest single coverage gain available. |
| Local compute | The Mac mini is a component host, not a dependency: tunnelled, token-protected endpoints with a cloud fallback. In version 2 it also takes batch embeddings, eval sweeps, reranker inference and scheduled ingestion - work that is wasteful to rent. Nothing on a live URL may require it to be awake. |
| Waves | Every spec groups its issues into waves. Wave 1 is the foundation (schema, migrations, roles, access rules, auth config): always `claude` and `security-sensitive`, and the only slice that may change a foundation path. The guarded set and what lies outside it are in [`AGENTS.md`](AGENTS.md) and [`FACTORY.md`](FACTORY.md#waves-and-the-start-signal), generated from one list. Builders who find the data layer missing stop and comment; they never invent schema or auth ([`FACTORY.md`](FACTORY.md#waves-and-the-start-signal)). |
| Start signal | Issue bodies carry a `Planned harness:` line and full-URL `## Dependencies`. The harness label appears only when every dependency is done (closed as completed, or a merged PR): `scripts/open-issues.py` labels only dependency-free issues, and `scripts/release-labels.py` (Claude after each merge, the ops monitor nightly) releases the rest. The Mac runner skips any issue it can't check. |

### The four clouds as built

| Cloud | Region | App runs on | Database | Sign-in from GitHub |
| --- | --- | --- | --- | --- |
| AWS | us-east-2 only (account guardrail) | Lambda (Arm image) + API Gateway | Shared RDS db.t4g.micro, on Free plan credits | None: the guardrails block GitHub sign-in, so a deployer Lambda in the account pulls `main` and runs `deploy/aws.sh`; CloudShell is the fallback |
| Azure | Apps East US, database Central US | Container Apps, 0–1 replicas | Shared Flexible Server B1ms (free 12 months; East US isn't offered to this subscription) | Keyless OIDC |
| Google Cloud | us-central1 | Cloud Run, 0–1 instances | Postgres on the always-free e2-micro VM, no public IP | Keyless OIDC |
| Oracle | US West (Phoenix) | Docker + Caddy on the Always Free A1 VM (2 OCPU / 12 GB) | Postgres on the same VM | API key in the `production` environment secret |

Account notes: AWS stays on the **Free plan** (can't bill; closes after 6 months), so don't upgrade it to remove the
guardrails. The Google Cloud trial ended, so it's a paid account kept inside always-free limits, with budget alerts
(a Cloud Run spend cap is recommended). Google Cloud is under `mparrott567@gmail.com`; the others use `dev@breakthruventures.ai`.
The org uses immutable OIDC subject claims (`repo:BreakthruDevelopment@<id>/<repo>@<id>:…`); the bootstrap scripts
trust both forms. That applies to the original account only: the second AWS account used by the apps 17-20 demo
track has no identity provider available, so its CI uses an IAM user's key in repo secrets (see
`specs/day-0-aws-demo-track.md`).

**Dropped, don't bring back:** fine-tuning (no free tier covers it; we show prompting, decoding controls and evals
instead, and say so), native mobile (Expo/React Native), app-store publishing, the Kylon platform,
calling the Claude API from the apps, paid DNS, and running many agents in parallel inside one Claude session.

## How the AI team is organized

- A **model** does the thinking (Claude, Grok, OpenAI's Codex models, Gemini).
- A **harness** wraps a model so it can act on code: Claude Code, Codex, Grok Build, Grok Bot.
- An **agent** is a role running inside a harness. The eight roles live in [`roles/`](roles/), written once and
  usable by any harness.

| Harness | Subscription | Gets work by | Usually does |
| --- | --- | --- | --- |
| Claude Code | Claude | Issues labeled `claude`; scheduled tasks overnight | Planner, reviewer, AI builder, deploys, template changes; the nightly ops report (scheduled task, 5:37 AM Central, posted to the `Ops report (nightly)` issue in this repo) |
| Codex | ChatGPT Plus (tightest limits) | Issues labeled `codex` | Fullstack on selected issues; second review on security-sensitive PRs |
| Grok Build | X (SuperGrok) | Issues labeled `grok`, worked when Michael runs `scripts/run-harness.sh grok` on his Mac | UI pages, fullstack issues and READMEs; Michael wants it used more |
| ~~Antigravity~~ | Google AI Pro | **Retired 2026-11-20** without coming off trial; plan no new work to it | — |
| Grok Bot | X (Grok) | Michael pastes in an issue, or a live app's README and URL | Backup `ui-builder` / `fullstack-builder` when Grok Build is out of usage: works the pasted issue on a `grok/<task>` branch and opens a PR that goes through the same gates. Build-in-public drafts: an X post, a LinkedIn post and a two-minute demo script per app. No secrets, never merges; Michael posts |

**Jules is gone.** Google turns it read-only after 2026-11-11 and shuts it down on 2026-12-31
([changelog](https://jules.google/docs/changelog/)); Google Antigravity replaced it on 2026-11-09, and
Antigravity was itself retired on 2026-11-20 without coming off trial. Jules's open issues were reassigned on
2026-11-09 ([`specs/day-0-apps-5-8.md`](specs/day-0-apps-5-8.md#2026-11-09-reassignment)). **Three harnesses
plan new work: Claude Code, Codex and Grok Build.**

**Labels are the start signal.** Grok Build is a CLI on Michael's Mac, not a GitHub app, so a label
doesn't trigger them. An issue gets its harness label only once its dependencies are done (completed or merged)
(`scripts/release-labels.py`); the runner script then picks it up, works it in `~/30apps/<repo>` and opens a PR. It
fails closed: it skips anything whose dependencies are still open, any issue without a `## Dependencies` section of
full URLs or a matching `Planned harness:` line, and anything labelled `hold`, and it never pushes a branch that
changes foundation files. Setup and safety trade-offs: [`runbooks/harnesses-on-mac.md`](runbooks/harnesses-on-mac.md).

## How work moves

GitHub is the only shared memory. Harnesses never talk to each other. The steps below are the
BreakthruSoftwareFactory's five gates ([`FACTORY.md`](FACTORY.md)): spec (1), build (2–3), review (3), release (4–5)
and close-out (7).

1. The **planner** turns the day's catalog entry into `specs/NN-slug.md`, slices grouped in waves (wave 1 the
   foundation), and once it's merged opens the issues with `scripts/open-issues.py`. Each issue names a role in its
   title (`[ui-builder] Dashboard page`) and its owner in a `Planned harness:` line.
2. Once its dependencies are done (completed or merged), the issue gets its harness label (`scripts/release-labels.py`). Each harness picks up only its own label,
   follows the named role file, and opens a PR from a `<harness>/<task>` branch.
3. CI (lint, types, tests, build, smoke test) must pass. **Review is required:** Claude Code reviews every PR, Codex
   also reviews PRs labelled `security-sensitive`, and each posts a marked PR review that the `Reviewer sign-off`
   check reads. No merge without it. Once those checks are green on the current head, any harness may squash-merge
   an **app-repo** PR (see [`AGENTS.md`](AGENTS.md)).
4. **Claude Code also merges** green deploy PRs (`30-apps-infra`, such as `apps.yaml`) and playbook PRs
   (`ai-dev-os`). **These stay with Michael:** spec PRs (gate 1, scope approval), secrets and branch protection.
5. The day's app is deployed to its cloud, smoke-tested at its live URL; its DNS record is created by the deploy.
   Claude Code merges the `apps.yaml` PR once its checks are green and the plan holds no surprise.
6. Overnight, Codex and scheduled Claude Code tasks work queued issues into PRs, and may squash-merge app-repo PRs
   that go green; Grok Build runs whenever Michael starts the runner. The nightly ops report lands in
   the `Ops report (nightly)` issue.
7. Close-out: the run log (`runs/NN-slug.md`), `catalog.yaml` status and this briefing are updated, and Grok Bot
   drafts the launch posts and demo script from the README for Michael to post. An app is **done** only with a filled
   README, a live smoke, a run log and `status: done` in the catalog.

When a harness hits its usage limit, its issues are relabeled to another harness.

## Where things stand

_As of 2026-11-13, from GitHub: `30-apps-infra` `apps.yaml` (through #77), the rulesets, and the `Live smoke test`
runs on each app repo's `claude/live-smoke` branch, whose `/api/health` output shows the version each app is serving.
Per-app evidence is in [`runs/`](runs/); the 2026-11-10 gap list is in [`runs/retro-01-12.md`](runs/retro-01-12.md)._

- **Day 0 done** (2026-11-04): the app template, this repo, the four cloud accounts, `30-apps-infra`, and the
  template app live on all four clouds (still in `apps.yaml`, tag `sha-99a8f86`):
  - AWS: https://v1uf5au310.execute-api.us-east-2.amazonaws.com
  - Azure: https://app-template.salmonpebble-b870873b.eastus.azurecontainerapps.io
  - Google Cloud: https://template-189497094271.us-central1.run.app
  - Oracle: https://template.141-148-159-122.sslip.io
- **Apps 1–12 are live** (12 of 33), each at `appN.breakthruventures.ai` with the tag `apps.yaml` pins. Apps 1–4 each
  passed a full live smoke on 2026-11-16, run from the Actions tab against the deployed site, and all four are
  serving the tag `apps.yaml` pins. **The smoke itself does not establish that second half:** `scripts/smoke.sh`
  asserts only that `/api/health` returns `status: ok`, never compares the tag, and the run log does not keep the
  body. Apps 2–4 were confirmed by the tag already recorded in their run logs, which `apps.yaml` has not changed
  since 2026-11-08; app 1 had been redeployed since its last tag check, so its tag was read back deliberately
  (`sha-de78c18`). For apps 5–12 the tag was likewise read by hand at the time and nothing re-checks it.
  [`30-apps-template#37`](https://github.com/BreakthruDevelopment/30-apps-template/issues/37) tracks making the
  smoke assert the deployed tag so "pass after the latest deploy" means what it says without a manual step.

  | # | App | Cloud | Tag | Deploy PR (`30-apps-infra`) | Live smoke after latest deploy | Status |
  | --- | --- | --- | --- | --- | --- | --- |
  | 1 | Portfolio Build Tracker | AWS | `sha-de78c18` | #71 | pass, 2026-11-16 | **done** |
  | 2 | Notes and Knowledge Base | Azure | `sha-6675f0b` | #42 | pass, 2026-11-16 | **done** |
  | 3 | Expense Tracker | Google Cloud | `sha-811aac4` | #42, domain #41 | pass, 2026-11-16 | **done** |
  | 4 | Habit and Goal Tracker | Oracle | `sha-c91ffc1` | #45, #47 | pass, 2026-11-16 | **done** |
  | 5 | Personal Budget Planner | AWS | `sha-50aa60b` | #65, #75 | pass, 2026-11-12 | **done** |
  | 6 | Bookmark and Read-Later | Azure | `sha-51175dd` | #66 | pass, 2026-11-10 | deployed (README) |
  | 7 | Appointment Booking | Google Cloud | `sha-0f8cdf3` | #69, domain #70, #75 | pass, 2026-11-12 | **done** |
  | 8 | Loan Application Portal | Oracle | `sha-713b6c3` | #67, #75 | health and public pages only | deployed (smoke) |
  | 9 | Invoicing | AWS | `sha-4171700` | #72 | pass, 2026-11-11 | **done** |
  | 10 | Inventory Management | Azure | `sha-881d16a` | #73, #75 | pass, 2026-11-12 | **done** |
  | 11 | Helpdesk Ticketing | Google Cloud | `sha-3fd1ca2` | #76, domain #77 | pass, 2026-11-13 (UTC) | deployed (README) |
  | 12 | Restaurant Ordering | Oracle | `sha-6bd0d02` | #74, #75 | fail: no orderable dish | deployed (README, smoke) |

  Notes on what's live:
  - **App 5:** Plaid bank sync is built (05-budget-planner #15) but off until Michael enters Plaid keys; health
    reports `"bank":"demo"`.
  - **App 9:** payments run on the demo provider (health reports `"payments":"demo"`); Stripe test mode is built.
  - **App 11:** custom domain live since 2026-11-13 (UTC; `30-apps-infra` #77, 9:36 PM Central on 11-12).
  - **App 12:** the live smoke passes every step up to ordering, then stops at "the menu has no orderable dish"
    until the demo workspace is loaded (admin button) or staff smoke credentials are set.
  - **App 8:** the live check is health plus public pages (`/`, `/sign-in`, and `/dashboard` and `/admin`
    redirecting); `scripts/smoke.sh` hasn't been run against the live URL.
- **Done (4): apps 5, 7, 9, 10.** Filled README, `scripts/smoke.sh` passed live after the latest deploy, run log in
  [`runs/`](runs/). Apps 6, 11 and 12 still need their README (open `[docs-writer]` issues 06 #5, 11 #6, 12 #5: no
  harness label); app 8 needs a full live smoke; app 12 also needs a passing smoke. Apps 1–4 need a recorded live
  smoke (and app 1 a README fix; see the retro).
- **App 31 (Cloud Cost Scaler) is live on Google Cloud** (2026-11-17, `30-apps-infra` #92 then domain #95), serving
  `sha-b4659b3` at https://cost-scaler-189497094271.us-central1.run.app; `app31.breakthruventures.ai` is waiting on
  its certificate, after which the Terraform workflow needs a **manual rerun** to move `APP_URL` onto it. Fifteen
  PRs, all `claude/`. Status is `deployed`, not `done`: **its live smoke fails on an empty footprint**, and no
  smoke has yet run against the deployed `sha-b4659b3` at all. Nothing
  populates the price and footprint tables at boot, and the only trigger is `POST /api/prices/refresh` — fired by
  the `cost-scaler-refresh` Cloud Scheduler job (next 07:05 UTC), or by an admin, and **no admin can exist on a
  Google Cloud app** (`30-apps-infra#91`). Force-running that job six times should fill the tables in about a minute —
  the scheduler path has no rate limit where the admin one does — though that is read from the code and nobody has
  run it yet. Then dispatch the app's new `Live smoke` workflow (31 #34). Detail in
  [`runs/31-cost-scaler.md`](runs/31-cost-scaler.md); blockers in `30-apps-infra#89`–`#91`.
- **Catalog:** app 32 (Purchase Orders and Vendor Management, Oracle) is `planned` (ai-dev-os #23). Apps 13–30 are
  `planned` too; 13, 14 and 15 have repos and merged work in progress.
- **Agreed order:** BreakthruSoftwareFactory complete → app 31 → apps 13–30 → app 32 last (ai-dev-os #23).
  **Superseded for apps 17-20 on 2026-11-19:** those four are the AWS demo track, built first, by 2026-11-24.
  The build of apps 13-16 is paused for two weeks from 2026-11-19.
- **Template:** hardening for apps 13+ is merged (`30-apps-template` #32, 2026-11-13), so new repos start from it.
- **Branch protection:** `ai-dev-os` now requires `check` and `Reviewer sign-off`; apps 05–12 require
  `Lint, test, build, smoke` and `review / Reviewer sign-off`, and since 2026-11-14 so do `30-apps-template` and
  apps 01–04 (same `protect-main` ruleset). See [`FACTORY.md`](FACTORY.md#branch-protection-as-it-stands-checked-2026-11-13).
- **Factory complete (2026-11-14).** READMEs for 06, 11 and 12 are merged (06 and 11 now `done`). Open app
  close-out, not blocking: the app 12 demo workspace and a passing full live smoke, app 8's full live smoke (needs
  an admin-based smoke or an accepted exception), live smokes for 1–4. **Next: app 31 (Cloud Cost Scaler, Google
  Cloud, likely built on Google ADK for TypeScript), then 13–30, then 32.**
- **Incident, 2026-11-14: Grok built before app 13's data layer existed.** The issue-opening step labelled every
  app 13 issue at once, including Grok's UI issues whose dependency (13.1, data layer, `claude`) was still open.
  Their `## Dependencies` used bare `#1`, which the runner's check couldn't see (it read only full URLs), so the Mac
  runner started them. Grok invented its own schema, migrations, RBAC and session code in `13-field-service` PRs #9
  and #10 (each adding a different `drizzle/0004_*`) and started #6. Those PRs are held. **Michael suspended Grok
  and Antigravity until the data layers are complete.** Labels came off every issue with open dependencies, and
  dependency references were rewritten as full URLs. The fix is the waves, `Planned harness:` lines, label release
  and fail-closed runner in [`FACTORY.md`](FACTORY.md#waves-and-the-start-signal). Issues opened before it have no
  `Planned harness:` line, so the runner and `release-labels.py` leave them alone until one is added.

## Where to read more

| You need | Read |
| --- | --- |
| The rules | [`AGENTS.md`](AGENTS.md) |
| The BreakthruSoftwareFactory: gates, definition of done, required review | [`FACTORY.md`](FACTORY.md) |
| What happened on each app | [`runs/`](runs/), starting with [`retro-01-12.md`](runs/retro-01-12.md) |
| Your role's instructions | [`roles/<role>.md`](roles/) |
| What to build | [`catalog.yaml`](catalog.yaml), then `specs/NN-slug.md` |
| How code must be written in an app | That app repo's `AGENTS.md` |
| The day's routine | [`runbooks/daily.md`](runbooks/daily.md) |
| Running Grok Build | [`runbooks/harnesses-on-mac.md`](runbooks/harnesses-on-mac.md) |
| How deploys work | [`30-apps-infra` README](https://github.com/BreakthruDevelopment/30-apps-infra#how-deploys-work) |
