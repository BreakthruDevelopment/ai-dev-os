# AI Engineer Roadmap coverage

The widely-shared **AI Engineer Roadmap** (16 weeks, W01–W16, Python → agents → production) is a hiring-manager's
checklist. This file maps every week of it onto something in this portfolio that *runs in production and can be
demoed in under two minutes*, and names the gaps we are closing in apps 16–33.

**W01–W16 are topic labels, not our schedule.** Theirs is a 16-week syllabus for one person learning in sequence.
Ours is 30–35 days for the whole portfolio, because the work runs in parallel streams across four harnesses and the
learning already happened. We keep their numbering so a reader can match this file to the graphic they saw; we do
not inherit their calendar. Pace and streams are at the end of this file.

It exists so that a reviewer, a client or an interviewer can go from "do you know RAG evals / MCP / LangGraph /
multi-agent handoffs?" to a live URL, a file in a repo and a 90-second demo, without taking anyone's word for it.

**Rule for this file:** a week is only `covered` when the thing is *running in a deployed app*, not when it appears
in a slide. A week whose proof is "we wrote a README about it" is `gap`.

## The 16 weeks

| Wk | Roadmap topic | Proven by | Status |
| --- | --- | --- | --- |
| W01 | Python basics — variables, loops, functions, debug | **33-ai-service** (FastAPI + Streamlit, typed, tested) | gap → app 33 |
| W02 | Dev tools — OOP, Git & GitHub, tests, type hints | This repo (BreakthruSoftwareFactory: 8 roles, 5 gates, PR-only flow, CI) + **33-ai-service** (`mypy`, `pytest`) | covered |
| W03 | APIs & data — REST, FastAPI, SQL, async | **33-ai-service** REST API; every app's route handlers; Drizzle/Postgres across 32 apps; async jobs in **21-meeting-notes** | gap → app 33 (FastAPI half) |
| W04 | LLM basics — tokens, attention, prompts, decoding | **16-lms** "Why this answer" panel: token count, temperature/top-p, logprob-ranked alternates on a generated quiz item | gap → app 16 |
| W05 | LLM apps — context, tool calls, LangChain, caching | **27-donor-crm** (context assembly, prompt cache, cost per draft); tool calls proven in 28/31 | partial → app 27 |
| W06 | RAG — embeddings, vector DB, rerank, RAG evals | **29-knowledge-assistant** (multi-source, pgvector, cross-encoder rerank, labelled eval set, citations) and **17-job-board-ats** (resume↔job matching with the same stack) | partial → apps 17, 29 |
| W07 | AI agents — agent loop, tools, Agents SDK, tracing | **31-cost-scaler** (Google ADK `runAgent()`, 4 tools, traced) ✅ and **28-support-agent** (order lookup, refunds with approval) | covered (31) |
| W08 | MCP & A2A — MCP servers, tools, A2A protocol | **30-ai-ops-console**: an MCP server exposing portfolio tools, and an A2A endpoint where app 28's agent asks app 31's agent for a priced answer | gap → app 30 |
| W09 | LangGraph — state, routing, checkpoints, HITL | **20-task-manager**: LangGraph.js graph for bulk natural-language edits — routing, checkpointed state, human approval before anything destructive | gap → app 20 |
| W10 | Multi-agent — supervisor, handoffs, parallel tasks | **31-cost-scaler** (coordinator + pricing + migration agents, AgentTool) ✅; handoffs in **26-property-management** | covered (31) |
| W11 | Agent memory — long-term memory, queues, webhooks | **18-employee-onboarding** (long-term memory of an employee's state across weeks) + **21-meeting-notes** (queue, webhooks) | gap → apps 18, 21 |
| W12 | Evals & safety — evals, tracing, guardrails, LLMOps | **30-ai-ops-console** (traces, eval scores, guardrail hits, cost per app, across all 33) + **19-patient-intake** (refusal and redaction evals) + **25-fitness-coaching** (safety limits) | partial → apps 19, 30 |
| W13 | Deploy — Docker, CI/CD, cloud, vLLM | One container image per app, GitHub Actions, four clouds ✅; **vLLM on the Mac mini**, reached by the apps over a free Cloudflare Tunnel (see "Where the models run") | covered except serving → app 33 |
| W14 | Full-stack AI — Streamlit, auth, scaling, load tests | **33-ai-service** (Streamlit console) + **22-analytics-dashboard** (row-level security, query sandbox) + a load test against one live app | gap → app 33 |
| W15 | Capstone build — architecture, build, interview prep | **31-cost-scaler** is the capstone: four-cloud price ingestion, a priced scenario engine, a multi-agent advisor | covered |
| W16 | Ship & present — deploy, demo, portfolio ready | 33 live URLs, a README and a 2-minute demo script each, the Build Tracker (app 1) as the index | covered |

## What changes in apps 16–32

Thirteen of the seventeen remaining apps keep their client need and their cloud exactly as planned. What changes is
**which AI technique each one is built to prove**, so that the seventeen of them together cover every roadmap week
instead of building six variations on "summarize this text".

| App | Was | Becomes | Roadmap week |
| --- | --- | --- | --- |
| 16 LMS | Quiz generation from course material | Quiz generation **plus a decoding lab**: tokens, temperature/top-p, logprob-ranked alternates, cost per item | W04 |
| 17 Job Board & ATS | Resume parsing and candidate-job matching | The same, built as **retrieval with a rerank stage and a labelled eval set**; bias guardrails measured, not asserted | W06, W12 |
| 18 Employee Onboarding | Policy Q&A over the handbook | Policy Q&A **plus long-term memory**: the assistant remembers where each new hire is across weeks | W11 |
| 19 Patient Intake | Intake form to structured summary | The same, with a **refusal and redaction eval suite** that runs in CI | W12 |
| 20 Task Manager | NL task entry and auto-prioritizing | **A LangGraph.js graph**: routing, checkpointed state, human-in-the-loop before destructive bulk edits | W09 |
| 21 Meeting Notes | Transcript to action items | The same, as a **queue + webhook** pipeline with retries and a visible job state machine | W11, W03 |
| 22 Analytics Dashboard | Ask-your-data (text to SQL) | The same, with **query sandboxing, row-level security and a text-to-SQL eval set** | W03, W14 |
| 23 Marketplace | Listing moderation | Listing moderation **with outbound webhooks** to seller systems | W11 |
| 24 Community Forum | Toxicity moderation + summaries | The same (unchanged) | W12 |
| 25 Fitness Coaching | Workout plan generator | The same, as a **guardrail case study**: hard safety limits, refusals, red-team fixtures | W12 |
| 26 Property Management | Maintenance request triage | Triage **with an agent handoff**: triage agent → scheduling agent, supervisor pattern | W10 |
| 27 Donor CRM | Outreach drafts and segmenting | The same, as a **context and caching case study**: prompt cache, context budget, cost per draft | W05 |
| 28 Support Agent | Agent with tools, refunds with approval | The same, **on an Agents-SDK loop with tracing**, and it calls app 31 over **A2A** | W07, W08 |
| 29 Knowledge Assistant | Multi-source RAG with evals | The same, **made the reference RAG**: embeddings, vector DB, cross-encoder rerank, RAG evals, citations | W06 |
| 30 AI Ops Console | One view of the agent team | The same, **plus the MCP server and A2A broker** for the portfolio, and the LLMOps home: traces, evals, guardrail hits, cost | W08, W12 |
| 31 Cost Scaler | Multi-agent cloud advisor | Unchanged — already W07, W10, W15 | ✅ |
| 32 Purchase Orders | Quote/invoice extraction, 3-way match | The same, with **human-in-the-loop approval chains** as the HITL reference | W09 |

### One new app

**33-ai-service** — *AI Service (Python)*, Oracle Cloud.

The roadmap is a Python roadmap; this portfolio is TypeScript. One app closes that honestly rather than pretending:

- **FastAPI** service: REST, async, SQL (SQLAlchemy against the same Postgres), full type hints, `pytest` + `mypy` in CI.
- **The embeddings and rerank service** apps 17 and 29 call, so the Python is load-bearing, not a demo.
- **The eval harness**: RAG evals, refusal evals and text-to-SQL evals run here and publish to app 30.
- **Streamlit console** for eval runs and traces — the one non-Next.js UI in the portfolio, which is the point.
- **Open-weights serving**: the app talks to the **vLLM endpoint on the Mac mini** (below) and is the thing that makes
  it useful to the rest of the portfolio — it holds the provider config, the health check and the fallback.

Cost: zero. The service runs on the Oracle Always Free A1 VM already hosting the permanent demos, in the same Postgres.

## Where the models run

Three providers, in this order, all at zero marginal cost:

| Provider | Runs on | Used for | When it isn't there |
| --- | --- | --- | --- |
| **vLLM** (open weights) | **Michael's Mac mini**, reached over a free Cloudflare Tunnel at a subdomain of `breakthruventures.ai`, bearer-token protected | The W13 serving proof; bulk eval runs (thousands of calls that would burn the Gemini free quota) | Falls through to Gemini |
| **Gemini free tier** | Google AI Studio (no-billing project) | Every app's default `generate()` | Falls through to demo answers |
| **Demo fixtures** | In the repo | Quota exhausted, keys missing, CI | — |

Notes that belong in the app 33 README, not in a slide:

- **vLLM on Apple silicon is the CPU backend, built from source**: it runs, it is slow, and it does not use the GPU.
  What actually performs on an M-series mini is **MLX** (`mlx_lm.server`) or llama.cpp with Metal. So we run both:
  vLLM because it is the thing on the roadmap and the thing employers ask about, MLX as the fast path the demos use.
  Both expose the same OpenAI-compatible API, so `generate()` sees one provider; the README says plainly which served
  which number. We never claim a GPU vLLM deployment we don't have.
- **The mini is not always on.** Every call is health-checked with a short timeout and falls through to Gemini, so a
  sleeping mini degrades the answer, never the app. Eval runs that need the open-weights model queue instead of failing.
- **Nothing in a cloud free tier depends on the mini being reachable.** The live demos must survive Michael closing his
  laptop lid, being on a plane, or the tunnel being down.
- **Version 2:** the mini becomes a general component host for work that is wasteful to rent — batch embeddings, eval
  sweeps, reranker inference, scheduled ingestion. Same pattern each time: a tunnelled, token-protected endpoint with a
  cloud fallback, never a hard dependency.

## Demos, infographic and training material

Three artifacts, in this order:

1. **The coverage infographic** (first — see below). The 16-week spine with each week's node carrying the app that
   proves it and its live URL. It is simultaneously the portfolio index, the interview cheat sheet and the syllabus.
2. **Sixteen 90-second demo beats**, one per week, each recorded against a live URL: the clicks in order and what each
   one proves. App 1 (Build Tracker) links them all.
3. **A 16-part training series** written from the run logs in `runs/`: for each week, what the roadmap says, what we
   actually built, what broke, and the review finding that changed how we build. Written after the app ships, from
   what happened, not before it from what we hoped.

## Pace and parallel streams

Eighteen apps remain (16–33) inside a 30–35 day total. That is roughly one app a day, and the apps in this plan are
heavier than apps 1–12 were. One app a day only works if the expensive parts stop being rebuilt per app.

### The two levers

**1. Build each capability once, use it three or four times.** The re-aimed apps repeat five capabilities:

| Capability | Built once in | Reused by |
| --- | --- | --- |
| Retrieval + rerank + a RAG eval harness | **33-ai-service** | 17, 29 |
| Eval runner (refusal, text-to-SQL, red-team fixtures) | **33-ai-service** | 19, 22, 25 |
| HITL approval chain (a write blocked until a human signs) | **30-apps-template** (optional module) | 20, 32, 28 |
| Outbound webhooks (signed, replayable, with a job state machine) | **30-apps-template** (optional module) | 21, 23 |
| Agent loop with tracing, reporting to app 30 | **30-apps-template** (optional module) | 26, 28, 31 |

Template modules are **new files only**, never edits to existing ones, so the fifteen apps already live are
untouched until they choose to cherry-pick. This is the whole speed argument: if these five land early, the apps
that use them are thin app-specific layers. If they land late, we build each one four times and miss the window.

**2. Foundations run ahead of the stream, not inside it.** Wave 1 (schema, migrations, roles, access) is Claude-only
and security-sensitive, so every app funnels through one agent — it is the critical path, and when it is late every
other harness idles (the app 13 incident). So foundations are written **two or three apps ahead** of where the
builders are working, in a batch, while the current apps finish.

### The four streams

They never touch the same repo at the same time, which is what makes them safe to run at once:

| Stream | Harness | Carries |
| --- | --- | --- |
| **A — Foundation & review** | Claude Code | Wave-1 slices two or three apps ahead; every PR review; merges |
| **B — UI** | Grok Build / Grok Bot | Pages and components, once the app's data layer is on `main` |
| **C — Fullstack & docs** | Antigravity / Codex | Non-security slices, demo workspaces, READMEs |
| **D — Python** | Claude Code | 33-ai-service: shares no files with the Next.js apps, so it runs the whole time without ever colliding |

### Measuring it

Each run log records **hours from spec merge to live smoke**, split into working time and waiting time, and names
what the waiting was on (label release, review, a harness at its usage limit, something only Michael can do). The
nightly ops monitor reports the split. Optimize the largest waiting bucket, not the feeling of being busy.

The parallelism is itself portfolio material: app 30 shows concurrent runs across four harnesses, and app 1 shows
the streams. "Can you run several workstreams at once" is a question clients ask, and this answers it with a
dashboard instead of an anecdote.

## Honesty rules for all three

- A week is `covered` only when it runs in a deployed app. No slideware.
- No invented numbers anywhere: cost, latency and eval scores come from app 30 or the run logs, or they are left out.
- Where hardware forces a substitution (MLX instead of GPU vLLM; Gemini free tier instead of a fine-tune), the
  substitution is named in the artifact, not hidden.
- Fine-tuning (W04's deeper half) is **not** claimed anywhere: no free tier covers it. We show prompting, decoding
  controls and evals instead, and say so.
