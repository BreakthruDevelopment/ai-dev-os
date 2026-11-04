# Project briefing

Read this first if you're an AI harness (or a person) joining the **30 apps in 30 days** build. It's the current
state of every decision; the rules themselves are in [`AGENTS.md`](AGENTS.md).

_Last updated: 2026-11-03 (Day 0)._

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
| AI in the apps | Every model call goes through the template's `generate()` gateway. Default model: Gemini, paid from Google AI Pro's monthly Google Cloud credit. Recorded demo answers when the quota runs out. Claude is an optional config switch. |
| Clouds | Free tiers only. Each app is live on one cloud, rotating AWS → Azure → Google Cloud → Oracle by app number; the other three are proven with `terraform plan`. The Oracle Always Free VM is the permanent demo host. |
| Domains | `appN.breakthruventures.ai` for app N. DNS stays at Network Solutions; records are added by hand (`runbooks/dns-network-solutions.md`). |
| GitHub | Org `BreakthruDevelopment`. It also holds unrelated apps that must never be touched: only repos tagged `30-apps-30-days` are in scope. |
| Budget | Nothing beyond the existing subscriptions (Claude, X/Grok, ChatGPT Plus, Google AI Pro) and cloud free tiers. No extra credits, no paid services. |
| Order | App 1 is the **Build Tracker**, built first so it serves as mission control for the month. Full list in [`catalog.yaml`](catalog.yaml). |

**Dropped, don't bring back:** native mobile (Expo/React Native), app-store publishing, the Kylon platform,
calling the Claude API from the apps, paid DNS, and running many agents in parallel inside one Claude session.

## How the AI team is organized

- A **model** does the thinking (Claude, Grok, OpenAI's Codex models, Gemini).
- A **harness** wraps a model so it can act on code: Claude Code, Grok Build, Grok Bot, Codex, Jules.
- An **agent** is a role running inside a harness. The eight roles live in [`roles/`](roles/), written once and
  usable by any harness.

| Harness | Subscription | Gets work by | Usually does |
| --- | --- | --- | --- |
| Claude Code | Claude | Issues labeled `claude` | Planning, data/API, AI feature, review, deploys |
| Grok Build | X (Grok) | Issues labeled `grok` | UI pages and components; AWS and Azure Terraform |
| Jules | Google AI Pro | Issues labeled `jules` | Google Cloud and Oracle Terraform; overflow |
| Codex | ChatGPT Plus | Every PR (review) and issues labeled `codex` | Code review; small fixes |
| Grok Bot | X (Grok) | Its nightly schedule | Ops report: CI, stalled work, app health, free-tier usage |

## How work moves

GitHub is the only shared memory. Harnesses never talk to each other.

1. The **planner** turns the day's catalog entry into `specs/NN-slug.md` and opens issues. Each issue names a role
   in its title (`[ui-builder] Dashboard page`) and carries one harness label.
2. Each harness picks up only its own label, follows the named role file, and opens a PR from a
   `<harness>/<task>` branch.
3. CI (lint, types, tests, build, smoke test) must pass; Claude Code and Codex review.
4. **Michael merges.** Nothing reaches `main` any other way.
5. The day's app is deployed to its cloud, smoke-tested at its live URL, and Michael adds the DNS record.
6. Overnight, harnesses with capacity work queued issues into PRs for Michael's morning review.

When a harness hits its usage limit, its issues are relabeled to another harness.

## Where things stand

- Done: the app template (tested end to end) and this repo (rules, roles, catalog, runbooks).
- Waiting on Michael: cloud accounts, Google AI Pro + Jules, Codex and Grok connections to GitHub, the project board,
  and repo settings (topics, template flag, branch protection). See [`runbooks/day-0.md`](runbooks/day-0.md).
- Next: Terraform for the four clouds, then the template deployed live on all four. Day 1 starts after that.

## Where to read more

| You need | Read |
| --- | --- |
| The rules | [`AGENTS.md`](AGENTS.md) |
| Your role's instructions | [`roles/<role>.md`](roles/) |
| What to build | [`catalog.yaml`](catalog.yaml), then `specs/NN-slug.md` |
| How code must be written in an app | That app repo's `AGENTS.md` |
| The day's routine | [`runbooks/daily.md`](runbooks/daily.md) |
