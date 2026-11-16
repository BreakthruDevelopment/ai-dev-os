# AI Engineer Roadmap coverage

The widely-shared **AI Engineer Roadmap** (16 weeks, W01–W16, Python → agents → production) is a hiring-manager's
checklist. This file maps every week of it onto something in this portfolio, and says honestly how far along each
one is.

**W01–W16 are topic labels, not our schedule.** Theirs is a 16-week syllabus for one person learning in sequence.
Ours is 30–35 days for the whole portfolio, because the work runs in parallel streams across four harnesses. We
keep their numbering so a reader can match this file to the graphic they saw; we do not inherit their calendar.
Pace is at the end.

## How a week is scored

| State | Means |
| --- | --- |
| **live** | Running in an app that is deployed and answering at its domain. The only state that proves anything to a stranger. |
| **built** | Merged to `main` and tested, but not deployed yet. Real code, no live URL. |
| **partial** | Some of the week's topics are live, others are not. The row says which. |
| **gap** | Not built. |

Nothing is scored on a plan, a slide or a README. **Today: 1 live, 3 built, 6 partial, 6 gaps.** Twelve apps are
deployed (`30-apps-infra/apps.yaml`); apps 13, 14, 15 and 31 are in build.

## The 16 weeks

| Wk | Roadmap topic | Where it stands | State |
| --- | --- | --- | --- |
| W01 | Python basics | Nothing in the portfolio is Python yet. **33-ai-service** is the answer. | gap |
| W02 | Dev tools — OOP, Git & GitHub, tests, type hints | Twelve deployed apps, each TypeScript strict with lint, typecheck, unit and integration tests, build and smoke in CI; the BreakthruSoftwareFactory itself (8 roles, 5 gates, PR-only, required review) | **live** |
| W03 | APIs & data — REST, FastAPI, SQL, async | REST handlers, Postgres/Drizzle and async jobs are live across twelve apps. **FastAPI** is the missing half → app 33. | partial |
| W04 | LLM basics — tokens, attention, prompts, decoding | Prompting is live in every app's AI feature. Tokens, decoding controls and logprobs → **16-lms** (on hold for the Oracle reboot). | partial |
| W05 | LLM apps — context, tool calls, LangChain, caching | Tool calls are built in app 31. Context budget, prompt cache and cost-per-draft → **27-donor-crm**. | gap |
| W06 | RAG — embeddings, vector DB, rerank, RAG evals | pgvector search is built in **14-real-estate** (not deployed). Rerank and a labelled eval set → **29-knowledge-assistant** and **17-job-board-ats**. | gap |
| W07 | AI agents — agent loop, tools, Agents SDK, tracing | **31-cost-scaler**: Google ADK `runAgent()` with four tools, merged and tested. Not deployed. | **built** |
| W08 | MCP & A2A — MCP servers, tools, A2A protocol | Nothing yet → **30-ai-ops-console** (MCP server + A2A broker), consumed by **28-support-agent**. | gap |
| W09 | LangGraph — state, routing, checkpoints, HITL | Nothing yet → **20-task-manager**; HITL approval chains also in **32-purchase-orders**. | gap |
| W10 | Multi-agent — supervisor, handoffs, parallel tasks | **31-cost-scaler**: coordinator plus pricing and migration agents via `AgentTool`, merged and tested. Not deployed. | **built** |
| W11 | Agent memory — long-term memory, queues, webhooks | Job queues with retries are live in several apps. Long-term memory → **18-employee-onboarding**; webhooks → **21** and **23**. | partial |
| W12 | Evals & safety — evals, tracing, guardrails, LLMOps | Guardrails and grounded-output checks are live (app 15's FAQ check survived seven adversarial rounds). Evals, tracing and LLMOps → **30**, **19**, **25**. | partial |
| W13 | Deploy — Docker, CI/CD, cloud, vLLM | One container image per app, GitHub Actions, four clouds: live. **vLLM** → the Mac mini (below). | partial |
| W14 | Full-stack AI — Streamlit, auth, scaling, load tests | Better Auth with roles is live in twelve apps. **Streamlit** → app 33; load tests → **22-analytics-dashboard**. | partial |
| W15 | Capstone — architecture, build, interview prep | **31-cost-scaler** is the capstone: four-cloud price ingestion, a BigInt-micros scenario engine, a multi-agent advisor. Merged, not deployed. | **built** |
| W16 | Ship & present — deploy, demo, portfolio ready | Twelve live URLs and the Build Tracker (app 1) as the index. READMEs and 2-minute demos are not complete across all twelve. | partial |

The three **built** rows all become **live** when app 31 deploys (`30-apps-infra` #79, #80). That single deploy is
the largest coverage change available to us right now, which is worth knowing when choosing what to do next.

## What changes in apps 16–32

Fifteen of the seventeen remaining catalog entries get a new `ai_feature`. **No app changes its client need or its
cloud.** What changes is which AI technique each one is built to prove, so that together they cover every week
instead of building six variations on "summarize this text".

| App | Becomes | Week |
| --- | --- | --- |
| 16 LMS | Quiz generation **plus a decoding lab**: tokens, temperature/top-p, logprob-ranked alternates, cost per item | W04 |
| 17 Job Board & ATS | Matching as **retrieval with a rerank stage and a labelled eval set**; bias measured, not asserted | W06, W12 |
| 18 Onboarding | Policy Q&A **plus long-term memory** across weeks | W11 |
| 19 Patient Intake | A **refusal and redaction eval suite** that runs in CI | W12 |
| 20 Task Manager | A **LangGraph.js graph**: routing, checkpointed state, HITL before destructive bulk edits | W09 |
| 21 Meeting Notes | A **queue + webhook** pipeline with retries and a visible job state machine | W11, W03 |
| 22 Analytics | Text-to-SQL **with an eval set**, sandboxing, row-level security, a load test | W03, W14 |
| 23 Marketplace | Moderation **with signed, replayable outbound webhooks** | W11 |
| 24 Community Forum | Unchanged | W12 |
| 25 Fitness | A **guardrail case study**: hard safety limits, refusals, red-team fixtures | W12 |
| 26 Property Mgmt | Triage **with an agent handoff** under a supervisor | W10 |
| 27 Donor CRM | A **context and caching case study**: context budget, prompt cache, cost per draft | W05 |
| 28 Support Agent | An **Agents-SDK loop with tracing**, calling app 31 over **A2A** | W07, W08 |
| 29 Knowledge Asst | **The reference RAG**: embeddings, vector DB, cross-encoder rerank, RAG evals, citations | W06 |
| 30 AI Ops Console | The **MCP server and A2A broker**, and the LLMOps home: traces, evals, guardrail hits, cost | W08, W12 |
| 31 Cost Scaler | Unchanged — already W07, W10, W15 | — |
| 32 Purchase Orders | Extraction and 3-way match, with **approval chains as the HITL reference** | W09 |

### One new app

**33-ai-service** — *AI Service (Python)*, Oracle Cloud.

The roadmap is a Python roadmap and this portfolio is TypeScript. One app closes that honestly:

- **FastAPI**: REST, async, SQLAlchemy on the same Postgres, full type hints, `pytest` and `mypy` in CI.
- **The embeddings and rerank service** apps 17 and 29 call, so the Python is load-bearing, not a demo.
- **The eval harness**: RAG, refusal and text-to-SQL evals run here and publish to app 30.
- **Streamlit console** for eval runs and traces — the one non-Next.js UI, which is the point.
- **The model provider** for the Mac mini endpoint below, including its health check and fallback.

It sits on the Oracle Always Free A1 VM because a Python service wants a long-running host, which is why its
catalog entry carries a `rotation_reason` instead of following the cloud rotation. **Its repo is created by hand**,
not by `scripts/create-app-repos.py`: that builds from the Next.js template, and the required
`Lint, test, build, smoke` check has no Python equivalent yet. That CI workflow is its first slice.

## Where the models run

| Provider | Runs on | Used for | When it isn't there |
| --- | --- | --- | --- |
| **Open weights** | **Michael's Mac mini**, over a free Cloudflare Tunnel at a subdomain of `breakthruventures.ai` | The W13 serving proof; bulk eval runs that would burn the Gemini free quota | Falls through to Gemini |
| **Gemini free tier** | Google AI Studio (no-billing project) | Every app's default `generate()` | Falls through to demo answers |
| **Demo fixtures** | In the repo | Quota exhausted, keys missing, CI | — |

**This does not work today, and the template is why.** `generate()` (`src/lib/ai/index.ts`) picks exactly one
provider, `src/lib/env.ts` allows only `gemini | anthropic | demo`, there is no base-URL setting and no health
check, and the existing fallback goes to demo fixtures rather than to a second live provider. Making the table
above true means **editing three existing template files** to add an OpenAI-compatible provider, a base URL and a
health check. That is app 33's second slice, and until it ships the table describes an intention, not a behaviour.
(The "new files only" rule below governs the *capability modules*; this provider change is a deliberate exception,
reviewed as a template change.)

Hardware notes that belong in app 33's README rather than a slide:

- **vLLM on Apple silicon** is the CPU backend, built from source, and does not use the GPU. There is now a
  `vllm-metal` plugin from the vLLM project doing Apple-silicon GPU inference with MLX underneath — try that
  first; if it works, one server replaces the two-server plan.
- Otherwise **MLX** (`mlx_lm.server`) is the fast path and vLLM-CPU is the roadmap proof. Both speak an
  OpenAI-compatible API, so `generate()` sees one provider, and the README says which served which number.
- **`mlx_lm.server` has no authentication** — no `--api-key` — and its own docs say it implements only basic
  security checks and is not recommended for production. The bearer token must therefore be enforced by
  Cloudflare Access in front of the tunnel, never by the model server.
- **The mini is not always on.** Nothing on a live URL may require it to be awake.
- **Version 2:** the mini takes work that is wasteful to rent — batch embeddings, eval sweeps, reranker inference,
  scheduled ingestion. Same pattern each time: tunnelled, token-protected, with a cloud fallback.

## Pace and parallel streams

**Twenty-one apps remain (13–33)** against 30–35 days total, of which roughly 17–22 are left. That is more than
one app a day, and three of them (30, 33, and finishing 31) are multi-day. **At the current shape it does not
fit.** It fits only if the repeated work stops being rebuilt per app — and if it still doesn't, the honest options
are fewer apps or more days, not a thinner definition of done.

### The lever: build each capability once

| Capability | Built once in | Reused by |
| --- | --- | --- |
| Retrieval + rerank + a RAG eval harness | **33-ai-service** | 17, 29 |
| Eval runner (refusal, text-to-SQL, red-team fixtures) | **33-ai-service** | 19, 22, 25 |
| HITL approval chain (a write blocked until a human signs) | **30-apps-template** (optional module) | 20, 32, 28 |
| Outbound webhooks (signed, replayable, with a job state machine) | **30-apps-template** (optional module) | 21, 23 |
| Agent loop with tracing, reporting to app 30 | **30-apps-template** (optional module) | 26, 28, 31 |

Template modules are **new files only**, never edits to existing ones, so the twelve live apps are untouched until
they choose to cherry-pick. Each module gets one adversarial review at the quality of app 15's FAQ check, so the
apps that reuse it inherit a control that has already survived that, instead of each re-earning it.

Wave 1 (schema, migrations, roles, access) is Claude-only and security-sensitive, so every app funnels through one
agent: it is the critical path, and when it is late every other harness idles. Foundations are therefore written
**two or three apps ahead** of where the builders are.

### The streams

Parallelism is **across harnesses**, not inside one Claude Code session — running many agents in parallel in one
session is on the "don't bring back" list, and roles inside Claude Code still run one after another.

| Stream | Harness | Carries |
| --- | --- | --- |
| **A** | Claude Code (sequential within itself) | Wave-1 foundations ahead of the builders, every PR review, merges, app 33, template modules |
| **B** | Grok Build / Grok Bot | Pages and components, once the app's data layer is on `main` |
| **C** | Antigravity / Codex | Non-security slices, demo workspaces, READMEs; Codex's second review on security-sensitive PRs |

Stream A is the constraint. Anything that moves work out of it — a slice Grok can take, a review Codex can do —
buys more than anything that makes Stream A faster.

### Measuring it

Each run log records **hours from spec merge to live smoke**, split into working and waiting time, naming what the
waiting was on (label release, review, a harness at its usage limit, something only Michael can do). The nightly
ops monitor reports the split. Optimize the largest waiting bucket.

## Demos, infographic and training material

1. **The coverage infographic** (first). The 16-week spine with each week's node carrying the app that proves it,
   its live URL and its state from the table above. Generated from `catalog.yaml` plus app 1's live health, so a
   week flips to **live** when the app actually answers at its domain — not when someone edits a slide.
2. **Sixteen 90-second demo beats**, one per week, each recorded against a live URL.
3. **A 16-part training series** written from the run logs in `runs/`: what the roadmap says, what we built, what
   broke, and the review finding that changed how we build. Written after the app ships, from what happened.

## Honesty rules for all three

- A week is **live** only when it runs in a deployed app. Merged is **built**, and the two are never conflated.
- No invented numbers: cost, latency and eval scores come from app 30 or the run logs, or they are left out.
- Where hardware forces a substitution (MLX instead of GPU vLLM), the substitution is named, not hidden.
- Fine-tuning is **not** claimed anywhere: no free tier covers it. We show prompting, decoding controls and evals.
- If a claim here and reality disagree, this file is what changes.
