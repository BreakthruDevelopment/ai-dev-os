# AI Dev OS

The operating system behind **30 apps in 30 days**, run as the **BreakthruSoftwareFactory**: a team of AI agents running in five harnesses from four vendors that plans, builds,
reviews and deploys one production-shaped web app a day to AWS, Azure, Google Cloud or Oracle Cloud, with a human
approving every release.

Built by [Breakthru Ventures](https://breakthruventures.ai) as a forward deployed engineering portfolio: common
client problems, an AI feature in each, deployed on whichever cloud the client runs.

## How it works

```
catalog.yaml ──► Planner (Claude) ──► spec + GitHub issues
                                         │
              ┌──────────────────────────┼──────────────────────────┐
              ▼                          ▼                          ▼
  Full-stack (Grok Build, Codex, Antigravity)   AI builder (Claude)   UI builder (Grok Build)
              └──────────────► pull requests ◄──────────────────────┘
                                         │
   Reviewer (Claude, required check) + Codex on security PRs · CI: lint, types, tests, build, smoke
                                         │
            Agents squash-merge app-repo PRs once CI and review are green
                                         │
         Claude Code merges the apps.yaml PR once checks and plan are clean
                                         │
                       DevOps (Claude): deploy to the day's cloud, smoke test live URL
                                         │
                 Grok Bot drafts launch posts and a demo script; Michael posts
                                         │
   Overnight: Codex, scheduled Claude Code work the queue · nightly ops report (scheduled Claude Code task)
```

GitHub is the only shared state. Harnesses never call each other: one Project board is the queue, each issue
names a role and gets a harness label once its dependencies are merged (Grok Build and Antigravity
pick theirs up via `scripts/run-harness.sh` on Michael's Mac), and every change arrives as a PR. Any harness may
squash-merge an app-repo PR once CI and the required review are green; Claude Code also
merges green deploy and playbook PRs; spec PRs stay with Michael ([`AGENTS.md`](AGENTS.md)).

**Model, harness, agent.** A model does the thinking; a harness (Claude Code, Codex, Grok Build, Antigravity, Grok Bot)
wraps it so it can act; an agent is a role running inside a harness. Roles live in `roles/` once and run in
whichever harness has capacity.

## What's here

| Path | What it is |
| --- | --- |
| `BRIEFING.md` | Start here: the project, every decision in force, what was dropped, and where things stand |
| `FACTORY.md` | The BreakthruSoftwareFactory: five gates, definition of done, required review, branch protection |
| `AGENTS.md` | Rules every harness follows: repo safety, the role-to-harness map, how work moves |
| `roles/` | The eight roles, harness-neutral: planner, full-stack, AI and UI builders, reviewer, devops, docs writer, ops monitor |
| `.claude/agents/` | Claude Code subagents generated from `roles/` (`scripts/sync-claude-agents.py`) |
| `catalog.yaml` | The 30 apps: repo name, subdomain, cloud, AI feature |
| `templates/` | Spec, README and run-log templates |
| `runbooks/` | Day 0 setup, running Grok Build and Antigravity on the Mac, the daily flow (DNS is created by the deploy at Cloudflare; the old Network Solutions runbook is kept, superseded) |
| `specs/`, `runs/` | One spec and one run log per app; `runs/retro-01-12.md` is the apps 1–12 retrospective |

The app template lives in [`30-apps-template`](https://github.com/BreakthruDevelopment/30-apps-template).

## Budget

Runs entirely on existing subscriptions (Claude, X/Grok, ChatGPT Plus, Google AI Pro) and each cloud's free tier. Apps' AI
features use Gemini, paid from Google AI Pro's monthly Cloud credit, with a recorded demo fallback.
