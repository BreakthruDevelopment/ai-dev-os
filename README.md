# AI Dev OS

The operating system behind **30 apps in 30 days**: a team of AI agents running in five harnesses from four vendors that plans, builds,
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
   Full-stack builder (Claude)   AI builder (Claude)   UI builder (Grok Build) · Terraform (Grok, Jules)
              └──────────────► pull requests ◄──────────────────────┘
                                         │
             Reviewer (Claude) + Codex review · Jules takes overflow · CI: lint, types, tests, build, smoke
                                         │
                       DevOps (Claude): deploy to the day's cloud, smoke test live URL
                                         │
                              Michael reviews and merges
                                         │
   Overnight: Codex, Jules, scheduled Claude Code work the queue · Grok Bot reports to the Build Tracker
```

GitHub is the only shared state. Harnesses never call each other: one Project board is the queue, each issue
names a role and carries a harness label, and every change arrives as a PR that Michael merges.

**Model, harness, agent.** A model does the thinking; a harness (Claude Code, Grok Build, Grok Bot, Codex, Jules)
wraps it so it can act; an agent is a role running inside a harness. Roles live in `roles/` once and run in
whichever harness has capacity.

## What's here

| Path | What it is |
| --- | --- |
| `AGENTS.md` | Rules every harness follows: repo safety, the role-to-harness map, how work moves |
| `roles/` | The eight roles, harness-neutral: planner, full-stack, AI and UI builders, reviewer, devops, docs writer, ops monitor |
| `.claude/agents/` | Claude Code subagents generated from `roles/` (`scripts/sync-claude-agents.py`) |
| `catalog.yaml` | The 30 apps: repo name, subdomain, cloud, AI feature |
| `templates/` | Spec, README and run-log templates |
| `runbooks/` | Day 0 setup, the daily flow, DNS at Network Solutions |
| `specs/`, `runs/` | One spec and one run log per app |

The app template lives in [`30-apps-template`](https://github.com/BreakthruDevelopment/30-apps-template).

## Budget

Runs entirely on existing subscriptions (Claude, X/Grok, ChatGPT Plus, Google AI Pro) and each cloud's free tier. Apps' AI
features use Gemini, paid from Google AI Pro's monthly Cloud credit, with a recorded demo fallback.
