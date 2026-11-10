# Project briefing

Read this first if you're an AI harness (or a person) joining the **30 apps in 30 days** build. It's the current
state of every decision; the rules themselves are in [`AGENTS.md`](AGENTS.md).

_Last updated: 2026-11-09 (harness line-up: Jules replaced by Antigravity, Grok Build and Antigravity run from Michael's Mac, ops monitor moved to a scheduled Claude Code task; DNS and AWS deploy lines refreshed)._

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
| Grok Bot | X (Grok) | Michael pastes in a live app's README and URL | Build-in-public drafts: an X post, a LinkedIn post and a two-minute demo script per app. No repo access, no secrets; Michael posts |

**Jules is gone.** Google turns it read-only after 2026-11-11 and shuts it down on 2026-12-31
([changelog](https://jules.google/docs/changelog/)); Google Antigravity replaces it. Its open issues were
reassigned on 2026-11-09 ([`specs/day-0-apps-5-8.md`](specs/day-0-apps-5-8.md#2026-11-09-reassignment)).

**Labels are the start signal.** Grok Build and Antigravity are CLIs on Michael's Mac, not GitHub apps, so a label
doesn't trigger them. Claude adds a harness label only once an issue's dependencies are merged; the runner script
then picks it up, works it in `~/30apps/<repo>` and opens a PR (it also skips anything whose dependencies are
still open). Setup and safety trade-offs: [`runbooks/harnesses-on-mac.md`](runbooks/harnesses-on-mac.md).

## How work moves

GitHub is the only shared memory. Harnesses never talk to each other.

1. The **planner** turns the day's catalog entry into `specs/NN-slug.md` and opens issues. Each issue names a role
   in its title (`[ui-builder] Dashboard page`) and carries one harness label.
2. Once its dependencies are merged, the issue gets its harness label. Each harness picks up only its own label,
   follows the named role file, and opens a PR from a `<harness>/<task>` branch.
3. CI (lint, types, tests, build, smoke test) must pass; Claude Code reviews every PR, Codex the security-sensitive ones.
4. **Michael merges.** Nothing reaches `main` any other way.
5. The day's app is deployed to its cloud, smoke-tested at its live URL; its DNS record is created by the deploy.
6. Overnight, Codex and scheduled Claude Code tasks work queued issues into PRs for Michael's morning review;
   Grok Build and Antigravity run whenever Michael starts the runner. The nightly ops report lands in the
   `Ops report (nightly)` issue.
7. When an app is live, Grok Bot drafts its launch posts and demo script from the README for Michael to post.

When a harness hits its usage limit, its issues are relabeled to another harness.

## Where things stand

- Done (Day 0): the app template, this repo, the four cloud accounts, `30-apps-infra`, and the template app live and
  passing its health check on all four clouds:
  - AWS: https://v1uf5au310.execute-api.us-east-2.amazonaws.com
  - Azure: https://app-template.salmonpebble-b870873b.eastus.azurecontainerapps.io
  - Google Cloud: https://template-189497094271.us-central1.run.app
  - Oracle: https://template.141-148-159-122.sslip.io
- Next: Day 1, app 1 (Build Tracker), live on AWS, with the first `appN.breakthruventures.ai` record (now created automatically in Cloudflare).

## Where to read more

| You need | Read |
| --- | --- |
| The rules | [`AGENTS.md`](AGENTS.md) |
| Your role's instructions | [`roles/<role>.md`](roles/) |
| What to build | [`catalog.yaml`](catalog.yaml), then `specs/NN-slug.md` |
| How code must be written in an app | That app repo's `AGENTS.md` |
| The day's routine | [`runbooks/daily.md`](runbooks/daily.md) |
| Running Grok Build and Antigravity | [`runbooks/harnesses-on-mac.md`](runbooks/harnesses-on-mac.md) |
| How deploys work | [`30-apps-infra` README](https://github.com/BreakthruDevelopment/30-apps-infra#how-deploys-work) |
