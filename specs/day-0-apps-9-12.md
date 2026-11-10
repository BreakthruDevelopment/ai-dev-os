# Day 0 for apps 9–12: issues, order, Michael's steps, schedule

Specs: [09 Invoicing](09-invoicing.md) (AWS) · [10 Inventory Management](10-inventory.md) (Azure) ·
[11 Helpdesk Ticketing](11-helpdesk.md) (Google Cloud) · [12 Restaurant Ordering](12-restaurant-ordering.md) (Oracle).

**Target:** specs merged Wednesday 2026-11-11; repos created and issues opened by Thursday morning 2026-11-12; the four
apps live by Saturday 2026-11-14 (day 3 is buffer).

**No template prep this time.** Repos created from `30-apps-template` `main` now include the shared helpers,
envelope encryption, background jobs and self-hosted fonts, so no issue has a "port it first" step. **No issue depends
on the tool-use loop** (template PR #25, issue #20): all four AI features are single `generate()` calls with retrieval
or rules done in code. Envelope encryption isn't needed by any of the four (app 9's Stripe keys are env secrets, not
stored values).

## Harness split (as of 2026-11-09)

Jules has shut down; its label isn't used. Grok Bot has no repo access (it drafts launch posts; no issues).

| Harness | Label | Work in this batch |
| --- | --- | --- |
| Claude Code | `claude` | Planner; reviewer on **every** PR; ai-builder for all four apps; security-critical fullstack (9.2 payments, 10.1 tenancy, 11.1 roles and access); all five deploy PRs in `30-apps-infra` |
| Grok Build | `grok` | ui-builder for all four apps; fullstack 9.1, 11.2, 12.1; README 9.7 |
| Codex | `codex` | One fullstack issue (10.2, app 10 only); **second review** on 9.2, 10.1, 11.1, 12.1, 12.3 |
| Google Antigravity CLI (trial) | `antigravity` | Fullstack 9.3 (PDF) and 12.2 (SSE); READMEs 10.7, 11.8, 12.6. Branches `antigravity/<task>` |

**Playbook:** the harness line-up and the runner for Grok Build and Antigravity are in `AGENTS.md` and
`scripts/run-harness.sh` (ai-dev-os #15); the repos were created with the `antigravity` label (#16).

**Start signal:** an issue is opened unlabeled if it has open dependencies; **its harness label is applied when every
dependency is merged** (by Michael or the planner). Harnesses only pick up labeled issues, and the runner also skips
any issue whose `## Dependencies` are still open, so nobody starts early.

## Issues as opened

Opened 2026-11-09 by the planner (REST), in dependency order; each body links its spec, lists the blocking issues
as full URLs under `## Dependencies` (what `scripts/run-harness.sh` checks), states its intended harness, and carries
the Codex second-review note where marked. Spec numbers are in the bodies, not the titles. **Labelled now (day-1
ready): 9.1, 9.4, 10.1, 10.5, 11.1, 12.1**; every other issue is unlabelled until its dependencies merge.
**Not on the project board:** its API is GraphQL-only, which planner sessions can't use (M3).
**2nd** = Codex second review (Claude reviews everything).

**`09-invoicing`**

| Spec | Issue | Title | Harness | Waits on | 2nd | Day 1 |
| --- | --- | --- | --- | --- | --- | --- |
| 9.1 | [#1](https://github.com/BreakthruDevelopment/09-invoicing/issues/1) | [fullstack-builder] Schema, clients, invoices, money rules, numbering, share links, demo seed | `grok` | — | | **ready** |
| 9.2 | [#3](https://github.com/BreakthruDevelopment/09-invoicing/issues/3) | [fullstack-builder] Payments: demo provider, Stripe test-mode Checkout, signed webhook | `claude` | 9.1 | Codex | |
| 9.3 | [#4](https://github.com/BreakthruDevelopment/09-invoicing/issues/4) | [fullstack-builder] Invoice PDF | `antigravity` | 9.1 | | |
| 9.4 | [#2](https://github.com/BreakthruDevelopment/09-invoicing/issues/2) | [ai-builder] Draft invoice lines from project notes | `claude` | — ("Add to invoice" wiring rebases on 9.1) | | **ready** |
| 9.5 | [#5](https://github.com/BreakthruDevelopment/09-invoicing/issues/5) | [ui-builder] Invoice list and editor, clients, settings, public invoice page, admin | `grok` | 9.1 (payment UI after 9.2) | | |
| 9.7 | [#6](https://github.com/BreakthruDevelopment/09-invoicing/issues/6) | [docs-writer] README for Invoicing | `grok` | 9.6 | | |

**`10-inventory`**

| Spec | Issue | Title | Harness | Waits on | 2nd | Day 1 |
| --- | --- | --- | --- | --- | --- | --- |
| 10.1 | [#1](https://github.com/BreakthruDevelopment/10-inventory/issues/1) | [fullstack-builder] Workspaces, memberships, invites and tenancy guard | `claude` | — | Codex | **ready** |
| 10.2 | [#2](https://github.com/BreakthruDevelopment/10-inventory/issues/2) | [fullstack-builder] Items, stock ledger with optimistic locking, lookup, CSV export | `codex` | 10.1 | Claude concurrency pass | |
| 10.3 | [#4](https://github.com/BreakthruDevelopment/10-inventory/issues/4) | [ai-builder] Forecast numbers and plain-language reorder explanation | `claude` | 10.2 | | |
| 10.4 | [#5](https://github.com/BreakthruDevelopment/10-inventory/issues/5) | [ui-builder] Workspaces, dashboard, items, forecast, team and admin pages | `grok` | 10.1 (stock screens after 10.2) | | |
| 10.5 | [#3](https://github.com/BreakthruDevelopment/10-inventory/issues/3) | [ui-builder] Barcode scanner component and scan screen | `grok` | — (wiring after 10.2) | | **ready** |
| 10.7 | [#6](https://github.com/BreakthruDevelopment/10-inventory/issues/6) | [docs-writer] README for Inventory Management | `antigravity` | 10.6 | | |

**`11-helpdesk`**

| Spec | Issue | Title | Harness | Waits on | 2nd | Day 1 |
| --- | --- | --- | --- | --- | --- | --- |
| 11.1 | [#1](https://github.com/BreakthruDevelopment/11-helpdesk/issues/1) | [fullstack-builder] Agent role, tickets, messages, notes, access rules, outbox | `claude` | — | Codex | **ready** |
| 11.2 | [#2](https://github.com/BreakthruDevelopment/11-helpdesk/issues/2) | [fullstack-builder] SLA engine, queue and knowledge base with full-text search | `grok` | 11.1 | | |
| 11.3 | [#3](https://github.com/BreakthruDevelopment/11-helpdesk/issues/3) | [ai-builder] Auto-triage and KB-grounded reply suggestions | `claude` | 11.1, 11.2 | | |
| 11.4 | [#4](https://github.com/BreakthruDevelopment/11-helpdesk/issues/4) | [ui-builder] Customer portal, public KB and inbox | `grok` | 11.1 (KB pages after 11.2) | | |
| 11.5 | [#5](https://github.com/BreakthruDevelopment/11-helpdesk/issues/5) | [ui-builder] Agent desk, KB editor and admin | `grok` | 11.1, 11.2 (AI panels after 11.3) | | |
| 11.8 | [#6](https://github.com/BreakthruDevelopment/11-helpdesk/issues/6) | [docs-writer] README for Helpdesk Ticketing | `antigravity` | 11.7 | | |

**`12-restaurant-ordering`**

| Spec | Issue | Title | Harness | Waits on | 2nd | Day 1 |
| --- | --- | --- | --- | --- | --- | --- |
| 12.1 | [#1](https://github.com/BreakthruDevelopment/12-restaurant-ordering/issues/1) | [fullstack-builder] Staff role, menu and allergen declarations, orders and allergy flow, demo seed | `grok` | — | Codex | **ready** |
| 12.2 | [#2](https://github.com/BreakthruDevelopment/12-restaurant-ordering/issues/2) | [fullstack-builder] Real-time order status over SSE with polling fallback | `antigravity` | 12.1 | | |
| 12.3 | [#3](https://github.com/BreakthruDevelopment/12-restaurant-ordering/issues/3) | [ai-builder] Menu assistant with allergen router and guardrails | `claude` | 12.1 | Codex | |
| 12.4 | [#4](https://github.com/BreakthruDevelopment/12-restaurant-ordering/issues/4) | [ui-builder] Menu, cart and checkout, order tracker, kitchen board, menu editor, admin | `grok` | 12.1 (live parts after 12.2) | | |
| 12.6 | [#5](https://github.com/BreakthruDevelopment/12-restaurant-ordering/issues/5) | [docs-writer] README for Restaurant Ordering | `antigravity` | 12.5 | | |

**`30-apps-infra`** (all `claude`)

| Spec | Issue | Title | Waits on |
| --- | --- | --- | --- |
| 9.6 | [#60](https://github.com/BreakthruDevelopment/30-apps-infra/issues/60) | [devops] Deploy app 9 to AWS | 9.1–9.5 |
| 10.6 | [#61](https://github.com/BreakthruDevelopment/30-apps-infra/issues/61) | [devops] Deploy app 10 to Azure | 10.1–10.5 |
| 11.6 | [#62](https://github.com/BreakthruDevelopment/30-apps-infra/issues/62) | [devops] Deploy app 11 to Google Cloud (default URL) | 11.1–11.5 |
| 11.7 | [#63](https://github.com/BreakthruDevelopment/30-apps-infra/issues/63) | [devops] Custom domain for app 11 | 11.6 live |
| 12.5 | [#64](https://github.com/BreakthruDevelopment/30-apps-infra/issues/64) | [devops] Deploy app 12 to Oracle Cloud | 12.1–12.4 |

**Totals: 28 issues** — `claude` 12 (7 app + 5 deploy), `grok` 10, `antigravity` 5, `codex` 1; Codex second reviews 5.
**Ready on day 1 (labeled at once): 9.1, 9.4, 10.1, 10.5, 11.1, 12.1** (`grok` 3, `claude` 3). Everything else is
labeled as its dependencies merge.

Security-critical work stays with Claude or gets a Codex second look: payments (9.2), tenancy (10.1), roles and the
customer/agent wall (11.1), roles and the allergy flow (12.1), allergen guardrails (12.3). 10.2 is Codex-written, so its
second look is a Claude concurrency pass instead of Codex reviewing its own code (same rule as 5.2).

## Order and dependencies

```
App 9:  9.1 ─┬─ 9.2 (Codex 2nd) ─┐
             ├─ 9.3 PDF ─────────┤
             └─ 9.5 UI ──────────┼─ 9.6 deploy ─ 9.7 docs        (Stripe keys: later, M4)
        9.4 AI (from day 1) ─────┘
App 10: 10.1 (Codex 2nd) ─┬─ 10.2 (Codex) ─ 10.3 AI ─┐
                          └─ 10.4 UI ────────────────┼─ 10.6 deploy ─ 10.7 docs
        10.5 scanner (from day 1) ───────────────────┘
App 11: 11.1 (Codex 2nd) ─┬─ 11.2 ─┬─ 11.3 AI ─┐
                          ├─ 11.4 ─┤           ├─ 11.6 deploy (domain null) ─ 11.7 domain ─ 11.8 docs
                          └────────┴─ 11.5 ────┘
App 12: 12.1 (Codex 2nd) ─┬─ 12.2 SSE ─┐
                          ├─ 12.3 AI (Codex 2nd) ─┼─ 12.5 deploy ─ Michael reboots VM ─ 12.6 docs
                          └─ 12.4 UI ──┘
```

## What needs Michael

| # | Step | When | Blocks |
| --- | --- | --- | --- |
| M1 | ~~Merge this spec PR~~ **Done** (#14) | Wednesday | Issues link to specs on `main` |
| M2 | **Done** (#16; repos created with the `antigravity` label). Merge the separate **create_repo PR** (planner opens it after M1: `create_repo: true` for apps 9–12, plus `antigravity` added to `LABELS` in `scripts/create-app-repos.py` so new repos get the label). Four repos = the per-run cap. Approve the `repo-creator` run if you're its reviewer | Wednesday evening | Every app issue |
| M3 | Add the 28 issues ([list](#issues-as-opened)) to the project board (its API is GraphQL-only, which planner sessions can't use) and add `antigravity` to the board's Harness field | Thursday morning | Board view only |
| M4 | **Stripe test mode (app 9), optional, after 9.6 is live.** Free Stripe account (no activation needed for test mode); create a **restricted test key** (`rk_test_…`, Checkout Sessions: write, nothing else) or use the `sk_test_` key; add a test-mode webhook endpoint `https://app9.breakthruventures.ai/api/stripe/webhook` for `checkout.session.completed` and copy its signing secret; store both in CloudShell as `/30apps/invoicing/STRIPE_SECRET_KEY` and `/30apps/invoicing/STRIPE_WEBHOOK_SECRET` with the README's silent `read -rsp` command, then `aws-autodeploy.sh` `bash -s -- deploy`. Never paste them into a chat | Whenever convenient; **app 9 ships on demo payments** | No issue |
| M5 | Try the scanner (10.5 PR preview or local) on an iPhone and an Android phone; reply on the PR | Day 2 | 10.5 done |
| M6 | **Reboot the Oracle VM** after 12.5 merges (OCI console → `apps-host` → Reboot) so Caddy loads app 12 | Day 3 | App 12 live |
| M7 | Make each new GHCR package public after its first publish (`runbooks/daily.md`) | After each app's first merge | Every deploy |
| M8 | After 11.7, wait for the certificate and rerun the Terraform workflow on `main` | Day 3 | App 11 on its domain |
| M9 | Review and merge PRs; apply labels as dependencies merge (or tell the planner to) | Throughout | — |
| M10 | Check the Build Tracker shows app 10 as **Down (parked)** after 10.6 | Day 3 | — |

**Open recommendation (not blocking): fix Oracle once via the serial console.** A root shell lets the VM agent update
itself, puts the Gemini key in `shared.env` and enables per-app secrets and the Caddy reload fix (#46). That one session
turns on live AI for apps 4, 8 and 12 (all already `ai: gemini`), removes the reboot per new Oracle app (16, 20, 24, 28)
and unblocks app 8's later 8.7. App 12 doesn't need it: its allergen answers never use a model.

## Three-day schedule

Within Claude Code, roles run one at a time; reviews come before builds.

| When | Claude Code | Grok Build | Codex | Antigravity | Michael |
| --- | --- | --- | --- | --- | --- |
| **Wed (day 0)** | This PR; then the create_repo PR | — | — | — | M1, M2 |
| **Day 1 morning (Thu)** | Open 28 issues, label the six ready ones; then 11.1 | 12.1, then 9.1 | — | — | M3 |
| **Day 1 afternoon** | 10.1; review 12.1 / 9.1 | 9.1 finish; 10.5 | Second review 11.1 | 9.3 and 12.2 once 9.1/12.1 merge | Merge |
| **Day 1 evening** | Reviews; label newly unblocked issues | 12.4 (after 12.1), 11.4 (after 11.1) | Second review 12.1, 10.1 | 12.2 continues | Merge |
| **Overnight** | Scheduled task: 9.2 | 11.2 | 10.2 | 9.3 | — |
| **Day 2 morning (Fri)** | Reviews (concurrency pass on 10.2); 12.3 | 9.5, 10.4 | Second review 9.2 | Fixes from review | Merge, M5 |
| **Day 2 afternoon** | 11.3 (after 11.2), 9.4 | 11.5, 12.4 finish | Second review 12.3 | — | Merge |
| **Day 2 evening** | 10.3 | 10.5 wiring, 9.5 finish | — | — | Merge |
| **Day 3 (Sat)** | 9.6, 12.5, 10.6, 11.6 → 11.7; live smokes; run logs `runs/09…12` | 9.7; fixes | — | 10.7, 11.8, 12.6 | M6, M7, M8, M10; merge, post apps |

## Usage-limit risks and the relabel rule

When a harness hits its limit, **Michael or the planner relabels its open issues** to a harness with headroom; nobody
buys credits. Only unstarted issues move; a PR in progress stays with its author.

- **Claude Code (highest):** 12 issues plus a review of all ~28 PRs, while apps 5–8 are still finishing. Reviews first.
  Relief, in order: 9.4 and 10.3 slip to day 3 (the apps work without AI drafts; demo fixtures cover the UI); 10.1 →
  `codex` if Codex has headroom (Claude then does its second look); deploy PRs are small and stay last.
- **Grok Build (most issues):** 10, in parallel tracks. Relief: 11.2 → `claude` or `antigravity`; 9.7 → `antigravity`;
  10.5 → `antigravity`. If Grok's UI work lags, apps ship with fewer polish passes, not fewer checks.
- **Codex (tightest):** one build and five second reviews. If it runs out, the Claude reviewer covers second reviews
  with the security checklist and says so in the PR; 10.2 → `claude` or `grok`.
- **Antigravity (trial):** if no PR on 9.3 or 12.2 within half a day of labeling, relabel 9.3 → `grok` and 12.2 →
  `claude`; READMEs → `grok`.
- **Shared with apps 5–8:** their open issues compete for the same harnesses, and the 12 issues labeled `jules` there
  have no harness until relabeled (open question for Michael). If the batches collide, finish 5–8 first.
- If the batch slips, ship each app's core flow (smoke green, AI on demo answers) and move polish to the next simpler
  app's day, per `runbooks/daily.md`.
