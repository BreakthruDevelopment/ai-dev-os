# Day 0 for apps 5–8: template prep, order, Michael's steps, schedule

Specs: [05 Budget Planner](05-budget-planner.md) (AWS) · [06 Read-Later](06-read-later.md) (Azure) ·
[07 Appointment Booking](07-appointment-booking.md) (Google Cloud) · [08 Loan Portal](08-loan-portal.md) (Oracle).

Apps 5–8 are built as one batch over two days across four harnesses. Repos don't exist yet: **no issues are opened
until the Create app repos workflow has made them** (step M3); then the planner opens every issue below and in the
four specs, adds each to the board, and labels it.

## Who does what

| Harness | Label | Work in this batch |
| --- | --- | --- |
| Claude Code | `claude` | Planner; template prep T1–T5; T6 in `01-build-tracker`; ai-builder for apps 5 and 8; reviewer on **every** PR; devops (one `apps.yaml` PR per app); readies PRs for Michael's merge |
| Jules | `jules` | fullstack-builder for apps 6, 7, 8; ai-builder for apps 6 and 7; docs-writer for all four READMEs |
| Grok Build | `grok` | ui-builder for all four apps; an app's pages start once its first data/API PR is merged |
| Codex | `codex` | fullstack-builder for app 5; **second review** on security-sensitive PRs only: T1, T2, T4, 6.2, 7.5, 8.1, 8.2 (and 7.9, 8.7 if they're ever opened) |
| Grok Bot | — | No issues; keeps running the nightly ops report |

**Merges are Michael's** (AGENTS.md §1). 5.2 is written by Codex, so its second look is a dedicated crypto/logging
pass by the Claude reviewer instead of Codex reviewing its own code (**accepted by Michael**); the crypto primitive
itself (T4) is Claude-written and Codex-reviewed.

## Template prep (repo `30-apps-template`, all `claude`)

Merged **before** the repos are created, so all four apps start with them. Each is one PR.

- **T1 `[ai-builder] Tool-use loop in generate()`** · **2nd review: Codex** · needed by 7.5
  - `GenerateRequest` gains optional `tools: ToolDef[]`, `maxSteps` (default 4, max 6), `deadlineMs` (default 24,000)
    and `messages` (server-built history) as an alternative to `prompt`. Without `tools`, behaviour is unchanged.
  - `ToolDef<A, R> = { name; description; args: z.ZodType<A>; kind: "read" | "propose"; run(args, { signal }): Promise<R> }`.
    **The gateway never passes an actor:** handlers close over the acting user and call `assertCan()`/owner checks
    themselves, so authorization stays in app code and can't come from model arguments.
  - Loop: call the provider with the tool declarations (from `z.toJSONSchema`) → for each requested call (≤3 per
    step): name must be in this request's allow-list, args must parse, else an error result goes back to the model
    and counts as a step; run the handler with the remaining deadline; serialize the result to JSON capped at 2 KB and
    frame it as data. **Final answer** = a reserved `respond` tool whose args are the request's `schema`, forced on the
    last step (Gemini `functionCallingConfig.mode: "ANY"` restricted to `respond`; Anthropic `tool_choice`), then
    validated like today. Exhausting steps or the deadline → `AiError("…", "tool_loop")`, and the app shows its fallback.
  - **Gemini detail:** Gemini 3-generation models return a `thoughtSignature` on function-call parts and reject the
    next request (400) if it isn't sent back. The provider keeps the model's content parts verbatim in the turn's
    history, and returns parallel calls together followed by all responses.
  - **Demo mode:** `demoToolScripts[task]` (in `demo.ts`) is a function of a caller-supplied `demoContext`, returning
    steps `{call: {name, args}}` and a final `(results) => answer`; the real handlers run, so demos use real data.
  - Logs: task, steps, tool names, per-tool latency, outcome; never args, results or prompts.
  - Done when unit tests (stub provider) cover: unknown tool, bad args, a handler that throws, 4-step cap, deadline,
    `respond` forced on the last step, `thoughtSignature` round trip, demo script; `generate()` without tools is
    byte-for-byte the same request as before; `src/lib/ai/` stays self-contained so an app can copy it.
- **T2 `[fullstack-builder] Shared helpers every app has been porting`** · **2nd review: Codex**
  - Lift from apps 1, 3 and 4 into the template: `whenMigrated()` in `migrate-on-start.ts`; `owned.ts` (`ownedBy`);
    `rate_event` and `daily_usage` tables with `usage.ts` (`advisoryLock`, `reserveDaily`, sliding-window limit);
    `csrf.ts` (`requireSameOrigin`); `errors.ts` (`NotFoundError`, `ConflictError`, `TooManyRequestsError`,
    `PayloadTooLargeError`) mapped in `errorResponse`; `readJson(request, maxBytes)`; `magic.ts` (PDF, PNG, JPEG,
    WebP); app 1's `ip-guard.ts` (`isPublicIp`); `demo-identity.ts` and `demo-seed-config.ts` (seed refusal rules).
  - Done when each has its tests from the source app and the template smoke still passes.
- **T3 `[fullstack-builder] Background jobs pattern`** · needed by 6.2
  - `src/lib/jobs`: Postgres queue (`job` table shape from the app 6 spec, generic `kind`), `enqueue` (idempotent by
    key), `claim` (`for update skip locked`, lease), `complete`/`fail` with backoff, `startWorker({ handlers,
    intervalMs, concurrency })` from `instrumentation.ts` after `whenMigrated()`, `kick()` for `after()`, SIGTERM stop,
    `JOBS_WORKER=off` for tests.
  - README section **"Background work per cloud"**: Oracle (long-lived container, worker always on); Azure (worker runs
    only while visitors keep a replica up; nothing wakes it on a schedule, and the Build Tracker parks Azure apps); Google Cloud
    Run with `cpu_idle` and AWS Lambda (**no CPU after the response**: do the work inside the request with a budget,
    or use an external trigger). App 6 is the first user; app 21 (async queue) will reuse it.
  - Done when: lease-expiry reclaim, idempotent enqueue, two workers never run one job (concurrency test), backoff
    schedule, and the off switch are tested.
- **T4 `[fullstack-builder] Envelope encryption module`** · **2nd review: Codex** · needed by 5.2 (later 7.9, 8.7)
  - `src/lib/crypto/envelope.ts`: `encrypt(plaintext, aad)`, `decrypt(blob, aad)`, `rewrap(blob)`, AES-256-GCM with a
    random DEK per value wrapped by a KEK, versioned blob, key id, current + old key for rotation; keys from env as
    base64 32 bytes, validated (exact length); Node `crypto` only.
  - Done when tests cover round trip, wrong AAD fails, tampered tag/ciphertext/wrapped DEK fail, old-key decrypt and
    rewrap, short or malformed keys refused, and no function logs or throws with key or plaintext material.
- **T5 `[planner] Mark apps 5–8 create_repo: true`** · repo **`ai-dev-os`**
  - One-line-per-app PR to `catalog.yaml`; the PR check prints the plan. **Michael merges it after T1–T4 are merged and
    the token is set up**; the workflow creates all four (its cap is 4 per run).

**Parallel item, already in progress:**

- **T6 `[fullstack-builder] Build Tracker: Up/Down running state; Azure apps parked`** · `claude` · repo
  **`01-build-tracker`** · **must be merged and deployed before 6.5** (resolves R1)
  - Each app gets a running state, **Up** or **Down (parked)**. Azure apps default to Down and are **not
    health-checked at all**, so the tracker never wakes them; only real visitors do. An admin can set an app Up
    (health-checked as today) or press **Check now** for a single check.
  - Done when: the scheduled sync makes no request to a Down app (tested), Check now does exactly one, and app 2 shows
    Down by default after deploy.

## Order and dependencies

```
T2 ─┬─ T4 ─┐
    ├─ T3 ─┼─ (T1) ─ T5 (Michael merges) ─ repos exist ─ planner opens issues
    └──────┘
T6 (01-build-tracker, in parallel) ─────────────────── must be live before 6.5
App 5:  5.1 ─┬─ 5.2 (T4) ─┐
             ├─ 5.3 ──────┼─ 5.5 deploy ─ 5.6 docs
             └─ 5.4 UI ───┘            (Plaid keys: later, outside every issue; then `deploy`)
App 6:  6.1 ─┬─ 6.2 (T3) ─ 6.3 ─┐
             └─ 6.4 UI ─────────┴─ 6.5 deploy (after T6) ─ 6.6 docs
App 7:  7.1 ─ 7.2 ─┬─ 7.5 AI (T1) ─ 7.4 chat UI ─┐
             └─ 7.3 UI ─────────────────────────┴─ 7.6 deploy (domain null) ─ 7.7 domain ─ 7.10 docs
             (Google sync 7.8 → 7.9: later, not opened)
App 8:  8.1 ─┬─ 8.2 ─┐
             ├─ 8.3 ─┼─ 8.5 deploy ─ Michael reboots VM ─ 8.6 docs
             └─ 8.4 UI┘                 (8.7: later, not opened; only if Oracle is fixed)
```

If T1 isn't merged when the repos are created, 7.5 begins by copying `src/lib/ai/` from template `main` (it's
self-contained by T1's done-when); nothing else waits on T1.

## What needs Michael

| # | Step | When | Blocks |
| --- | --- | --- | --- |
| M1 | Merge this spec PR | Now | Issues link to the specs on `main` |
| M2 | Merge T1–T4 in `30-apps-template` as they go green | Day 1 morning | T5 |
| M3 | One time, if not done: `protect-main` ruleset on `ai-dev-os` and the `REPO_CREATOR_TOKEN` environment secret (`runbooks/daily.md`). Then merge **T5** (approve the `repo-creator` run if you set yourself as reviewer) | Day 1 late morning | Every app issue |
| M4 | **Plaid (app 5):** free Plaid account → sandbox `client_id` and sandbox secret; generate `TOKEN_ENC_KEY` with `openssl rand -base64 32`; store all three in CloudShell as `/30apps/budget-planner/PLAID_CLIENT_ID`, `…/PLAID_SECRET`, `…/TOKEN_ENC_KEY` with the README's silent `read -rsp` command; then `aws-autodeploy.sh` `bash -s -- deploy`. Never paste them into a chat | Later, whenever convenient; **app 5 ships on its demo bank** | No issue (Plaid switches on by itself) |
| M5 | **Google OAuth client (app 7): not in this batch.** Only if Google sync is wanted later: OAuth consent screen (External, Testing, add test users), Calendar API enabled, Web client with redirect `https://app7.breakthruventures.ai/api/auth/callback/google`; values into `30-apps-infra` `production` environment secrets | Later | 7.8, 7.9 (not opened) |
| M6 | **Reboot the VM** after 8.5 merges (OCI console → `apps-host` → Reboot) so Caddy loads app 8's site | Day 2 | App 8 live |
| M7 | Make each new GHCR package public after its first publish (`runbooks/daily.md`) | After each app's first merge to `main` | Every deploy |
| M8 | Review and merge app PRs; after 7.7, wait for the certificate and rerun the Terraform workflow on `main` | Throughout | — |
| M9 | Review and merge **T6** in `01-build-tracker` | Before 6.5 | 6.5 |

DNS needs nothing by hand: all four clouds create the Cloudflare records on apply when the token exists, as for apps 1–4.

## Decisions (Michael, 2026-11-09)

- **R1, Azure Container Apps grant: resolved by T6.** The problem: Azure apps run with min 0 replicas, so a woken
  replica is billed at the active rate until the 300 s cooldown ends, and the tracker's paired health checks twice an
  hour came to about 150,000 vCPU-s and 300,000 GiB-s a month per Azure app, against a subscription-wide grant of
  180,000 vCPU-s and 360,000 GiB-s. With T6, Azure apps are parked (Down) and never health-checked, so Azure usage
  follows real visits only. App 6's worker runs only while visitors keep it awake and doesn't rely on any ping.
- **Oracle:** no fix decided, so app 8 ships on the default: demo AI, documents in Postgres, a VM reboot for the new
  app. App 8's "If Oracle gets fixed" section stays as an optional later path (8.7 not opened).
- **Plaid:** app 5 ships on the demo bank; Plaid sandbox switches on later when Michael adds the keys (M4). No issue
  depends on the keys.
- **Calendar:** app 7 has ICS export and the private feed only; Google Calendar sync stays later, with no issue in
  these two days.
- **Reviews:** Claude does the crypto/logging review of 5.2 (Codex wrote it).
- **App 8 stays on Oracle only** (not also listed on Google Cloud).

## Two-day schedule

Harnesses don't talk to each other; this is the intended order on the board. Within Claude Code, roles run one at a
time. Jules runs several tasks at once, so its three fullstack tracks run in parallel.

| When | Claude Code | Jules | Grok Build | Codex | Michael |
| --- | --- | --- | --- | --- | --- |
| **Day 1 morning** | Open T1–T5 on the board; T2, T4, T3 (then T1); T6 in parallel | — | — | Review T2, T4 | M1, M2 |
| **Day 1 midday** | T5 PR; once repos exist, open the 26 app issues (7.8, 7.9, 8.7 aren't opened) | — | — | Review T1 | M3; M9 when T6 is ready |
| **Day 1 afternoon** | Review PRs as they open | 8.1, 6.1, 7.1 in parallel | — | 5.1 | Merge reviewed PRs |
| **Day 1 evening** | Reviews; 5.3 after 5.1 merges | — | 5.4 after 5.1 merges | Review 8.1 | Merge |
| **Overnight** | Scheduled task: 8.3 | 8.2, 6.2, 7.2 | 5.4 continues, 8.4 | 5.2 | — |
| **Day 2 morning** | Reviews of overnight PRs (crypto pass on 5.2) | 6.3; 7.5 after 7.2 | 6.4, 7.3 | Review 8.2, 6.2 | Merge |
| **Day 2 midday** | 5.5 (AWS), 8.5 (Oracle), 6.5 (Azure) | 7.5 continues | 8.4 finish; 7.4 after 7.5 | Review 7.5 | M6 reboot; M7 |
| **Day 2 afternoon** | 7.6 then 7.7; live smokes | 5.6, 6.6, 8.6 | 7.4 | — | Merge; M8 |
| **Day 2 evening** | Run logs `runs/05…08`; board tidy | 7.10 | Fixes from review | — | Merge, post apps |

## Usage-limit risks and the relabel rule

When a harness hits its limit, **Michael or the planner relabels its open issues** to another harness that has
headroom, following AGENTS.md §2 ("Can move to"); nobody buys credits. Where the load sits:

- **Claude Code (highest risk):** six template/catalog/tracker PRs (T1–T6), two AI features, five deploy PRs and a review of every
  PR (~35, on Opus). Reviews come first. Relief: 8.3 or 5.3 → `jules` (ai-builder may move to Jules); deploy PRs →
  any harness; docs are already on Jules.
- **Jules:** 12 issues, including three fullstack tracks at once. **Agreed rule: if Jules stalls (limit hit, or no
  PR on 7.1/7.2 by Day 1 evening), relabel 7.1 and 7.2 to `claude` or `codex`**, whichever has headroom. Other relief:
  docs → whoever has headroom; 6.3/7.5 → `claude`.
- **Grok Build:** five UI issues squeezed into about a day, because each waits for its app's data PR. Relief: one
  app's UI → `jules`.
- **Codex:** two builds plus seven second reviews. If Codex runs out, the Claude reviewer covers second reviews with
  the security checklist and says so in the PR; 5.2 can move to `claude`.
- If the batch slips, ship each app's core flow and move polish (extra evals, UI polish) to the next simpler app's
  day, per `runbooks/daily.md`.
