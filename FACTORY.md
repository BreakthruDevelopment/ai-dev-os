# BreakthruSoftwareFactory

**BreakthruSoftwareFactory** is the official name of the process this repo runs: the agent team, the five daily
gates and the definition of done that turn one `catalog.yaml` entry into one live, documented app. It is not a
separate repo or product; the factory *is* this playbook (`AGENTS.md`, `roles/`, `runbooks/`, `catalog.yaml`,
`specs/`, `runs/`) applied to the repos tagged `30-apps-30-days`.

It was named and hardened on 2026-11-10, after apps 1–12 and before apps 13–30
([retrospective](runs/retro-01-12.md)).

## Who does what

Michael Parrott (Breakthru Ventures) owns the factory. He merges spec PRs (gate 1, scope approval), enters secrets
and owns branch protection. On app repos, any harness may squash-merge a PR once CI and the required review are green
on the current head; Claude Code also merges green deploy (`30-apps-infra`) and playbook (`ai-dev-os`) PRs under
Michael's standing instruction. The full rule is in [`AGENTS.md`](AGENTS.md).

| Role (`roles/`) | Default harness | Notes |
| --- | --- | --- |
| Planner | Claude Code | Specs and issues |
| Full-stack builder | Grok Build, Codex or Antigravity, by issue | Claude Code for template changes and security-critical slices; Grok Bot as backup |
| AI builder | Claude Code | |
| UI builder | Grok Build | Grok Bot as backup |
| Reviewer | Claude Code on every PR; Codex second review on security-sensitive PRs | Required: see gate 3 |
| DevOps | Claude Code | Deploys through `30-apps-infra` |
| Docs writer | Grok Build or Antigravity | |
| Ops monitor | Claude Code, scheduled task at 5:37 AM Central | Posts to the `Ops report (nightly)` issue |

- **Grok Bot** holds no secrets and never merges. When Grok Build is out of usage, it builds issues Michael pastes
  in (as `ui-builder` or `fullstack-builder`) on `grok/<task>` branches, opening PRs that pass the same gates as
  everyone else's. It also drafts launch posts (X, LinkedIn) and a two-minute demo script from what Michael pastes
  in; Michael posts.
- **Antigravity replaced Jules** as of 2026-11-09.
- **Labels are the start signal:** `claude`, `codex`, `grok`, `antigravity`. Grok Build and Antigravity are CLIs on
  Michael's Mac, run by `scripts/run-harness.sh` ([runbook](runbooks/harnesses-on-mac.md)).
- **Usage limits:** relabel the issues to another harness that can take the role. Never buy credits.

## The five gates

Every app passes all five, in order. A gate is passed when its evidence is in GitHub, not when someone says so.

| # | Gate | What happens | Passed when |
| --- | --- | --- | --- |
| 1 | **Spec** | The planner writes `specs/NN-slug.md` (from `templates/spec.md`) and opens one issue per slice, each with a role in the title, a planned harness, `## Dependencies`, and a Codex second-review note where the slice is security-sensitive. | Michael has approved the scope (he merges the spec PR) and the issues exist. |
| 2 | **Build** | Issues get their harness label once dependencies merge. Each harness opens PRs from `<harness>/<task>` branches. | CI is green on the PR: lint, types, tests, build, smoke (`Lint, test, build, smoke`). |
| 3 | **Review** | Required. Claude Code (reviewer role) reviews every PR; Codex also reviews PRs labelled `security-sensitive`. Each posts a GitHub PR review ending in the reviewer marker (below). Once this gate and gate 2 are green on the current head, any harness may squash-merge an **app-repo** PR ([`AGENTS.md`](AGENTS.md)). | The `Reviewer sign-off` check is green on the head commit. **No merge without it.** |
| 4 | **Release** | DevOps adds or bumps the app in `30-apps-infra` `apps.yaml` (a PR Claude Code merges once its checks and plan are clean), the deploy runs, and DevOps runs `scripts/smoke.sh` against the live URL. | Live smoke passes at `https://appN.breakthruventures.ai` and `/api/health` answers. |
| 5 | **Close-out** | Run log written (`runs/NN-slug.md`), `catalog.yaml` status and `BRIEFING.md` "Where things stand" updated, README filled. Grok Bot drafts the X and LinkedIn posts and the two-minute demo script; Michael posts. | The definition of done below is met. |

### Gate 3 in detail: the reviewer marker

The reviewer posts its findings as a pull request **review** (type *Comment*: every harness works as the same
GitHub account, and GitHub doesn't let an account approve its own PR). The review body ends with:

```
Reviewer: claude-code
Verdict: ready
```

Codex uses `Reviewer: codex`. `Verdict: blocking` means changes are needed. The
[`Review gate`](.github/workflows/review-gate.yml) workflow turns that into the `Reviewer sign-off` check:

- it needs the newest `claude-code` review to be on the PR's **current head commit** with `Verdict: ready`;
- if the PR is labelled `security-sensitive`, it needs the same from `codex`: either a review marked `Reviewer: codex` / `Verdict: ready`, or Codex's own GitHub review (comment `@codex review`) reporting no unresolved findings on the head commit, since Codex's app doesn't write the marker lines;
- a push after review fails the check until the reviewer reviews again.

This is a status check, not a human-approval count: required approvals stay at **0**. On app repos, a green
`Reviewer sign-off` plus green CI on the current head is what allows a harness to squash-merge; it is not a
substitute for those checks. Never bypass branch protection or use an admin merge. Because all agents share one
account, the marker guards against skipped reviews by mistake, not against that account. Michael's merge remains
the control for spec PRs; he can stop or reverse any other merge or deploy.

The planner marks a slice security-sensitive in the spec and issue (auth, roles and access, payments, tenancy, file
upload, tokens or secrets handling, AI tool use that writes data). The builder or reviewer adds the
`security-sensitive` label to the PR. `create-app-repos.py` creates the label (red, "Needs a Codex second review")
on every repo it creates or completes. For repos made before that, `python3 scripts/create-app-repos.py
--labels-only` adds it to apps 01–12 (one-off, by hand, with `REPO_CREATOR_TOKEN` set; it touches labels only).

After a marked review, the gate's `pull_request_review` run re-runs the PR's earlier `pull_request` run for the same
commit, so the required check turns green without anyone clicking re-run. App repos' caller workflow must grant
`actions: write` for that ([`runbooks/daily.md`](runbooks/daily.md#review-gate-turning-it-on)).

## Definition of done

An app is **done** only when all four hold, each with a link in its run log:

1. **Filled README.** The app repo's README follows `templates/app-readme.md`: the template's "What this app does"
   placeholder is gone, the live URL is real, and the demo script is there. No README still reads "30 Apps Template".
2. **Live smoke.** `scripts/smoke.sh` passed against the live URL after the latest deploy, and `/api/health`
   answers with the deployed image tag.
3. **Run log.** `runs/NN-slug.md` exists, from `templates/run-log.md`: who did what, review findings, deploy, smoke
   result, what slipped.
4. **Catalog status.** `catalog.yaml` says `status: done` for the app, and `BRIEFING.md` "Where things stand" agrees.

### Catalog status values

| Status | Meaning |
| --- | --- |
| `planned` | In the catalog; no repo or spec work yet |
| `building` | Repo exists and issues or PRs are in flight; not in `apps.yaml` yet |
| `deployed` | In `30-apps-infra` `apps.yaml` and answering `/api/health` at its domain; close-out not finished |
| `done` | Meets the definition of done above |

The `Check` workflow refuses an unknown status and refuses `done` without a run log.

## Branch protection, as it stands (checked 2026-11-13)

From the live rulesets (`gh api repos/BreakthruDevelopment/<repo>/rulesets` and `/rulesets/<id>`). Every ruleset
below is `protect-main`, active on the default branch: no deletion, no force push, PR required with 0 approvals,
plus the required checks listed.

| Repos | Required checks on `main` |
| --- | --- |
| `ai-dev-os` | `check` and `Reviewer sign-off` |
| `30-apps-infra` | `Validate aws`, `Validate azure`, `Validate gcp`, `Validate oci` |
| `05`–`12` app repos | `Lint, test, build, smoke` and `review / Reviewer sign-off` |
| `30-apps-template`, `01`–`04` app repos | **None yet**: no ruleset and no classic branch protection. Michael is importing a ruleset for them |

For the remaining repos, the recommended ruleset is in
[`runbooks/daily.md`](runbooks/daily.md#review-gate-turning-it-on).
