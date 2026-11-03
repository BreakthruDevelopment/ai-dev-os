# AI Dev OS: rules for every agent

This repo is the operating system for the **30 apps in 30 days** build: who does what, how work moves, and the
rules every AI tool follows. Claude Code, Grok Build, Grok Bot and Codex all read this file.

## 1. Repo safety (non-negotiable)

The BreakthruDevelopment org holds other, unrelated applications that must never change.

- Touch only repos with the GitHub topic `30-apps-30-days`. Anything else is read-only.
- Before creating a repo, list existing names. If the name is taken, **stop and ask**; never reuse or rename.
- Never force-push, delete, rename, transfer or archive a repo or branch.
- Never push to `main`. Work on `<tool>/<task>` branches (`claude/…`, `grok/…`, `codex/…`) and open a PR.
- Never commit or paste secrets. Keys go into GitHub Actions secrets or a cloud secret manager, entered by Michael.
- Merges to `main` are Michael's call.

## 2. GitHub is the single source of truth

Tools don't talk to each other directly. Work moves through:

| Thing | Where |
| --- | --- |
| What to build | `catalog.yaml` (this repo) and the app's spec at `specs/NN-slug.md` |
| Work items | GitHub issues on the app repo, labeled `claude`, `grok` or `codex` |
| Changes | Pull requests from tool branches |
| Status | PR checks, then the Build Tracker (app 20) |
| What happened | A run log per app in `runs/NN-slug.md` |

## 3. Who does what

| Work | Tool |
| --- | --- |
| Spec, data model, API contract, threat model | Claude Code — planner |
| API, database, server actions | Claude Code — full-stack builder |
| AI feature: prompts, tools, evals, demo fixtures | Claude Code — AI builder |
| Web pages and components, tests, Terraform for two clouds | Grok Build |
| Review of every PR; small issues (failing tests, dependency bumps, README polish) | Codex |
| Cross-review | Claude and Grok review each other's PRs |
| Nightly: CI status, free-tier usage, stalled PRs, status to the Build Tracker | Grok Bot |
| README and demo script | Whichever has headroom |

Claude Code's roles are subagents in `.claude/agents/`. Copy that folder into a working checkout to use them.

## 4. Daily flow

1. **Planner** writes `specs/NN-slug.md` from `templates/spec.md` and opens issues for each slice, labeled by tool.
2. **Builders** open PRs against the app repo. Grok takes UI issues; Claude takes data, API and AI issues.
3. **Reviewer** (Claude) plus Codex review each PR. CI must be green: lint, typecheck, tests, build, smoke.
4. **DevOps** deploys to the day's `live_cloud`, runs migrations as a one-off job, then the smoke test against the live URL.
5. **Docs** fills in the README from `templates/app-readme.md`.
6. **Michael** reviews and merges, adds the DNS record (see `runbooks/dns-network-solutions.md`), posts the app.

## 5. Usage limits

All three subscriptions have rolling limits. When a tool is capped, its open issues wait or are relabeled to
another tool; nobody buys extra credits. Roles run one after another, not in parallel, to stay inside Claude's
limits.
