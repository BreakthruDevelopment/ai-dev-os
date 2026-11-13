# Project briefing

Read this first if you're an AI harness (or a person) joining the **30 apps in 30 days** build. It's the current
state of every decision; the rules themselves are in [`AGENTS.md`](AGENTS.md).

The process that builds the apps is called the **BreakthruSoftwareFactory**: this playbook, its eight roles, the five
daily gates (spec, build, review, release, close-out) and the definition of done, all in [`FACTORY.md`](FACTORY.md).

_Last updated: 2026-11-13 ("Where things stand" brought up to date: apps 1–12 live, apps 5, 7, 9 and 10 `done`,
apps 31 and 32 in the catalog, branch protection re-checked). Since 2026-11-12, agents may squash-merge app-repo PRs
once CI and review are green; Claude Code also merges green deploy and playbook PRs; spec PRs stay with Michael._

## What we're building and why

Michael Parrott (Breakthru Ventures) is building a GitHub portfolio to win clients and roles as a **forward
deployed engineer**. The plan: 30 small, production-shaped web apps in 30 days, each solving a problem clients
commonly pay for, each with one AI feature, each deployable to **AWS, Azure, Google Cloud and Oracle Cloud**.
The agent setup that builds them (this repo) is itself a portfolio piece: an AI operating system across vendors.

## Decisions in force

| Area | Decision |
| --- | --- |
| Apps | Responsive web apps only (must work at 375px). No native mobile apps. |
| Stack | Next.js + TypeScript, Postgres via Drizzle, Better Auth with `user`/`admin` roles, Tailwind. One container image per app. |
| Starting point | Every app is created from [`30-apps-template`](https://github.com/BreakthruDevelopment/30-apps-template), which already has auth, roles, the AI gateway, tests, CI and a Dockerfile. |
| AI in the apps | Every model call goes through the template's `generate()` gateway. Default model: Gemini on the free tier (key in a no-billing AI Studio project; set `ai: gemini` in `apps.yaml`). A missing key falls back to demo answers. Recorded demo answers when the quota runs out. Claude is an optional config switch. |
| Clouds | Free tiers only. Each app is live on one cloud, rotating AWS → Azure → Google Cloud → Oracle by app number; listing more clouds for it in `apps.yaml` deploys it there too. The Oracle Always Free VM is the permanent demo host. Details below. |
| Deploys | [`30-apps-infra`](https://github.com/BreakthruDevelopment/30-apps-infra): `apps.yaml` lists each app, its clouds and its exact image tag; changing it is how you deploy. Merging to `main` applies Azure, Google Cloud and Oracle from GitHub Actions. AWS deploys itself: a deployer Lambda inside the account pulls `main` every 10 minutes and applies it (`30-apps-infra` #52, #53); one command in AWS CloudShell is the fallback. Apps migrate their own database on startup. |
| Domains | `appN.breakthruventures.ai` for app N. DNS is hosted at Cloudflare (free plan); each app's records are created automatically by Terraform on deploy when the app has a `domain` in `apps.yaml` (`30-apps-infra` README, "Custom domains and DNS"). Other records stay hand-managed. |
| GitHub | Org `BreakthruDevelopment`. It also holds unrelated apps that must never be touched: only repos tagged `30-apps-30-days` are in scope. |
| Budget | Nothing beyond the existing subscriptions (Claude, X/Grok, ChatGPT Plus, Google AI Pro) and cloud free tiers. No extra credits, no paid services. |
| Order | App 1 is the **Build Tracker**, built first so it serves as mission control for the month. Full list in [`catalog.yaml`](catalog.yaml). |

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
trust both forms.

**Dropped, don't bring back:** native mobile (Expo/React Native), app-store publishing, the Kylon platform,
calling the Claude API from the apps, paid DNS, and running many agents in parallel inside one Claude session.

## How the AI team is organized

- A **model** does the thinking (Claude, Grok, OpenAI's Codex models, Gemini).
- A **harness** wraps a model so it can act on code: Claude Code, Codex, Grok Build, Antigravity, Grok Bot.
- An **agent** is a role running inside a harness. The eight roles live in [`roles/`](roles/), written once and
  usable by any harness.

| Harness | Subscription | Gets work by | Usually does |
| --- | --- | --- | --- |
| Claude Code | Claude | Issues labeled `claude`; scheduled tasks overnight | Planner, reviewer, AI builder, deploys, template changes; the nightly ops report (scheduled task, 5:37 AM Central, posted to the `Ops report (nightly)` issue in this repo) |
| Codex | ChatGPT Plus (tightest limits) | Issues labeled `codex` | Fullstack on selected issues; second review on security-sensitive PRs |
| Grok Build | X (SuperGrok) | Issues labeled `grok`, worked when Michael runs `scripts/run-harness.sh grok` on his Mac | UI pages, fullstack issues and READMEs; Michael wants it used more |
| Antigravity | Google AI Pro | Issues labeled `antigravity`, worked when Michael runs `scripts/run-harness.sh antigravity` | Fullstack and docs, on trial |
| Grok Bot | X (Grok) | Michael pastes in an issue, or a live app's README and URL | Backup `ui-builder` / `fullstack-builder` when Grok Build is out of usage: works the pasted issue on a `grok/<task>` branch and opens a PR that goes through the same gates. Build-in-public drafts: an X post, a LinkedIn post and a two-minute demo script per app. No secrets, never merges; Michael posts |

**Jules is gone.** Google turns it read-only after 2026-11-11 and shuts it down on 2026-12-31
([changelog](https://jules.google/docs/changelog/)); Google Antigravity replaces it. Its open issues were
reassigned on 2026-11-09 ([`specs/day-0-apps-5-8.md`](specs/day-0-apps-5-8.md#2026-11-09-reassignment)).

**Labels are the start signal.** Grok Build and Antigravity are CLIs on Michael's Mac, not GitHub apps, so a label
doesn't trigger them. Claude adds a harness label only once an issue's dependencies are merged; the runner script
then picks it up, works it in `~/30apps/<repo>` and opens a PR (it also skips anything whose dependencies are
still open). Setup and safety trade-offs: [`runbooks/harnesses-on-mac.md`](runbooks/harnesses-on-mac.md).

## How work moves

GitHub is the only shared memory. Harnesses never talk to each other. The steps below are the
BreakthruSoftwareFactory's five gates ([`FACTORY.md`](FACTORY.md)): spec (1), build (2–3), review (3), release (4–5)
and close-out (7).

1. The **planner** turns the day's catalog entry into `specs/NN-slug.md` and opens issues. Each issue names a role
   in its title (`[ui-builder] Dashboard page`) and carries one harness label.
2. Once its dependencies are merged, the issue gets its harness label. Each harness picks up only its own label,
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
   that go green; Grok Build and Antigravity run whenever Michael starts the runner. The nightly ops report lands in
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
- **Apps 1–12 are live** (12 of 30), each at `appN.breakthruventures.ai` with the tag `apps.yaml` pins. For apps
  5–12 the latest live-smoke run's `/api/health` reported exactly that tag. App 4 also answered with its tag on
  2026-11-12 (logged inside app 8's live-smoke run). Apps 1–3 have no health check recorded on GitHub since
  2026-11-10.

  | # | App | Cloud | Tag | Deploy PR (`30-apps-infra`) | Live smoke after latest deploy | Status |
  | --- | --- | --- | --- | --- | --- | --- |
  | 1 | Portfolio Build Tracker | AWS | `sha-de78c18` | #71 | not recorded | deployed |
  | 2 | Notes and Knowledge Base | Azure | `sha-6675f0b` | #42 | not recorded | deployed |
  | 3 | Expense Tracker | Google Cloud | `sha-811aac4` | #42, domain #41 | not recorded | deployed |
  | 4 | Habit and Goal Tracker | Oracle | `sha-c91ffc1` | #45, #47 | health only | deployed |
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
- **Catalog:** apps 31 (Cloud Cost Scaler, Google Cloud) and 32 (Purchase Orders and Vendor Management, Oracle)
  were added as `planned` (ai-dev-os #23). Apps 13–30 are `planned` too: no repos yet.
- **Agreed order:** BreakthruSoftwareFactory complete → app 31 → apps 13–30 → app 32 last (ai-dev-os #23).
- **Template:** hardening for apps 13+ is merged (`30-apps-template` #32, 2026-11-13), so new repos start from it.
- **Branch protection:** `ai-dev-os` now requires `check` and `Reviewer sign-off`; apps 05–12 require
  `Lint, test, build, smoke` and `review / Reviewer sign-off`. `30-apps-template` and apps 01–04 have none yet;
  Michael is importing a ruleset. See [`FACTORY.md`](FACTORY.md#branch-protection-as-it-stands-checked-2026-11-13).
- **Next:** finish the factory: READMEs for 06, 11 and 12, the app 12 demo workspace and a passing smoke, a full
  live smoke for app 8, live smokes for 1–4, and the ruleset on the template and 01–04. Then app 31, then 13–30.

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
| Running Grok Build and Antigravity | [`runbooks/harnesses-on-mac.md`](runbooks/harnesses-on-mac.md) |
| How deploys work | [`30-apps-infra` README](https://github.com/BreakthruDevelopment/30-apps-infra#how-deploys-work) |
