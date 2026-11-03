# AI Dev OS

The operating system behind **30 apps in 30 days**: a team of AI agents across three vendors that plans, builds,
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
   Full-stack builder (Claude)   AI builder (Claude)        UI + Terraform (Grok Build)
              └──────────────► pull requests ◄──────────────────────┘
                                         │
                     Reviewer (Claude) + Codex review · CI: lint, types, tests, build, smoke
                                         │
                       DevOps (Claude): deploy to the day's cloud, smoke test live URL
                                         │
                              Michael reviews and merges
                                         │
                     Grok Bot overnight: CI status, free-tier usage, stalled PRs
```

GitHub is the only shared state. Tools never call each other; they read specs and issues, open PRs, and review
each other's work.

## What's here

| Path | What it is |
| --- | --- |
| `AGENTS.md` | Rules every AI tool follows, including repo safety |
| `.claude/agents/` | Claude Code subagents: planner, full-stack builder, AI builder, reviewer, devops, docs writer |
| `catalog.yaml` | The 30 apps: repo name, subdomain, cloud, AI feature |
| `templates/` | Spec, README and run-log templates |
| `runbooks/` | Day 0 setup, the daily flow, DNS at Network Solutions |
| `specs/`, `runs/` | One spec and one run log per app |

The app template lives in [`30-apps-template`](https://github.com/BreakthruDevelopment/30-apps-template).

## Budget

Runs entirely on existing subscriptions (Claude, Grok, ChatGPT Plus) and each cloud's free tier. Apps' AI
features use a free model tier with a recorded demo fallback.
