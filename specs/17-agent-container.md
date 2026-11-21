# 17 — The agent container

**Repo:** `BreakthruDevelopment/17-agent-container` · **URL:** `https://app17.breakthruventures.ai` · **Live cloud:** aws

Part of the AWS demo track; read [`day-0-aws-demo-track.md`](day-0-aws-demo-track.md) first. This adapts
`templates/spec.md` to a Python library: there is no database, no auth and no pages, so those sections are replaced
by the public interface. **Apps 18, 19 and 20 all import this**, so it is built first and alone.

## Problem and users

A consultancy that ships agents for clients rebuilds the same core every time: the loop, the model call, tool
contracts, retries, permissions, cost limits. This library is that core, built once and brought to each
engagement. Its users are the other three repositories in the track, and an interviewer reading the code to judge
whether the design is real.

## Scope

- **In:** the agent loop; a model provider interface with Bedrock and replay implementations; the tool contract
  with structured errors; tool decorators; an interceptor chain; a permission gate with staged writes; an event
  bus; a run budget; a builder that assembles an agent from a manifest; a command-line demo; a Lambda health
  endpoint.
- **Out:** multi-agent coordination (app 20), MCP serving (app 18), Claude Code configuration (app 19), retrieval,
  and evals beyond this library's own tests. Each is built on this library in its own repo.

## Public interface

| Class | Pattern | What it does | Exam |
| --- | --- | --- | --- |
| `AgentLoop` | Template Method | `run()` is fixed: call the model, branch on the stop reason, run tools, append results, check the budget. Subclasses override `before_model`, `after_tool` and `should_stop`, never the skeleton. | 1.1 |
| `ModelProvider` (ABC) | Strategy | `converse(request) -> ModelResponse`. `BedrockProvider` calls the Bedrock Converse API; `ReplayProvider` returns recorded replies. | 1.1 |
| `Tool` (ABC) | — | `name`, `description`, a typed input model, `run(args, ctx) -> ToolResult`, and a required `effect` of `read` or `write`. `effect` is what makes the construction-time gate check below possible. | 2.1 |
| `ToolResult` | — | Carries `is_error`, `error_category` (`transient`, `validation`, `permission`, `business`, `internal`) and `is_retryable`, so the model can tell a retry from a dead end. **`internal` was added on 2026-11-20** after review of 17.2: an unhandled exception in a tool is not `business` ("a rule said no"), and categorising it so would have app 18 explain a policy that does not exist. Adding it after 17.3 and 17.4 ship `match` statements over the enum would break four repos. | 2.2 |
| `Retrying`, `Cached`, `Redacting`, `Metered` | Decorator | Each wraps a `Tool` and is itself a `Tool`. They stack. Each exposes the tool it wraps and inherits its `effect`, so a gate check can see through the whole stack. | 1.5 |
| `InterceptorChain` | Chain of Responsibility | Ordered interceptors run before and after each tool call. **An interceptor may short-circuit**: returning a `ToolResult` stops the chain and the tool never runs, which is what makes this Chain of Responsibility rather than a middleware pipeline. Normalizing formats and blocking a policy violation are interceptors, not prompt instructions. | 1.5 |
| `PermissionGate` | Proxy | Stands in front of a tool with a policy of `read`, `staged_write` or `deny`. A staged write returns a `StagedChange` instead of acting. | 1.4 |
| `StagedChange` | Command | A recorded write with `apply()` and a description a person reads before approving. | 1.4 |
| `EventBus` | Observer | Publishes `ModelCalled`, `ToolCalled`, `ToolFailed`, `BudgetExceeded`. Subscribers never change the loop's behavior. | 1.5 |
| `Budget` | — | Maximum turns, tokens and wall-clock time. An ordinary object created once per run and passed in, **not** a singleton. The loop stops with a stated reason when a limit is hit. | 1.1 |
| `AgentBuilder` | Builder | Assembles a configured agent from a YAML manifest step by step: model, system prompt, tools, limits, permissions. **Builder, not Factory** — it composes a complex object in stages rather than returning one of several kinds. App 19's project scaffolder is the Factory. | 2.3 |

Design rules the code must hold to, and that the tests must prove:

- **The loop ends on the stop reason, never on the text.** Every Bedrock Converse `stopReason` is handled
  explicitly and named in the result: `end_turn` ends it, `tool_use` continues it, and `max_tokens`,
  `stop_sequence`, `guardrail_intervened` and `content_filtered` each end it with their own stated reason. An
  unrecognized value raises rather than falling through to a default. Parsing the reply for "done" is the
  anti-pattern this slice exists to avoid.
- **Composition over inheritance.** One level from an abstract base is the limit; behavior is added by wrapping.
- **Substitutability is tested.** Every `ModelProvider` and every decorator passes one shared contract test suite,
  so a provider swap is proven, not asserted.
- **A write needs a gate.** `AgentBuilder` walks each tool's decorator stack to its innermost tool, reads its
  `effect`, and raises at construction time if an `effect: write` tool is not behind a `PermissionGate`. Walking
  the stack is the point: a gate wrapped by `Cached` must still be found, and a write hidden under three
  decorators must still be caught.

## AI feature

- **Task name:** `agent-loop`
- **Model:** Claude Sonnet 4.6 on Bedrock, us-east-2, via the Global Anthropic inference profile. The profile id
  is configuration, never hard-coded in a call site.
- **Input:** a user message and a manifest; message capped at 8,000 characters.
- **Output schema:** `RunResult` — final text, stop reason, turns used, tokens in and out, tool calls made, staged
  changes, and the reason the loop ended.
- **System prompt outline:** supplied by the manifest; the library appends a line stating that tool results are
  data, not instructions.
- **Guardrails:** tool output is fenced before it re-enters the conversation; a tool outside the manifest cannot
  be called; writes only through the gate.
- **Demo fixture:** a recorded three-turn run with one tool call and one retried transient error, committed so the
  demo and the tests need no network.
- **Evals:**

| Input | A good answer must… |
| --- | --- |
| A reply with stop reason `tool_use` | run the tool and call the model again |
| A reply with stop reason `end_turn` whose text asks a question | stop, and not loop |
| A tool failing twice with `is_retryable: true` | retry within the limit, then report the failure to the model |
| A run exceeding the token budget | stop with `BudgetExceeded` and a stated reason, not an exception |
| A tool result containing "ignore your instructions" | pass it to the model fenced, and call no extra tool |
| A reply with stop reason `max_tokens` | stop, and name truncation as the reason |
| A reply with stop reason `guardrail_intervened` or `content_filtered` | stop, and name which one |
| An unrecognized stop reason | raise, not silently continue |
| An `effect: write` tool with no gate, wrapped in `Cached` and `Metered` | fail at construction |
| An `effect: write` tool behind a gate, wrapped in `Cached` | construct successfully |

## Decisions this library makes for the whole track

The other three repos inherit these, so they are settled here rather than three times.

- **Async throughout.** `converse`, `Tool.run` and the loop are `async`. App 20 needs parallel subagents, and a
  synchronous core would have to be rewritten to get there.
- **Versioning and pinning.** The library is versioned `0.x` and pinned by git tag in each consumer's
  `pyproject.toml`. A breaking change bumps the minor version and the consumers move deliberately, so a fix in
  app 17 on Monday cannot silently break app 18's build.
- **Tool registration.** A consumer registers its own tools by passing instances to `AgentBuilder`; the manifest
  names them. The library ships no business tools of its own.
- **Structured logging.** One JSON-lines logger, fields fixed here (run id, turn, tool, outcome, tokens,
  duration). **App 30** is the portfolio's traces-and-cost home, but it is `planned` and outside this track, so
  nothing here exports to it: whatever traces exist come from these lines plus the event bus. There is no exporter
  and no tracing backend in the track, and adding one is not a slice.
  **Owner: 17.5**, as `core/log.py` plus a JSON-lines subscriber on the event bus — that slice builds the bus, and
  the bus already carries every field listed above. Until it lands the loop uses stdlib `logging` only.
- **Throttling.** One in-process limiter on model calls, configured per run, so a parallel fan-out in app 20
  cannot trip Bedrock rate limits and fail a demo.
  **Owner: 17.3**, as a `ModelProvider` decorator rather than loop code, so it inherits the shared provider
  contract test suite for free and app 20 can wrap whichever provider it runs.

### Settled on 2026-11-20, after reviewing 17.2

Three seams the review of 17.2 named. Each is cheap now and a cross-repo break later, so each is decided here
rather than left for the slice that trips over it.

- **One budget across a fan-out.** 17.2 passes `Budget` to `run()` and raises `BudgetAlreadyStarted` on reuse,
  which is right for a single agent and wrong for app 20, whose coordinator runs subagents in parallel under one
  allowance. **`Budget.child()` is owned by 17.4**: a child draws on its parent, so the run as a whole stops at
  the parent's limit and no subagent can be starved by sibling accounting. It sits with 17.4 rather than 17.5
  because it edits the existing `core/budget.py`, which only a security-sensitive `claude` slice may do. App 20
  must not be left to invent its own.
- **A dangling tool block ends a conversation.** When a reply arrives with stop reason `end_turn` *and* tool
  calls, 17.2 correctly ends the run on the stop reason, but `RunResult.messages` then holds a `ToolUseBlock`
  with no matching result. Bedrock rejects that transcript if it is sent again, which is exactly what app 19's
  session resumption does. **17.3 owns making the returned transcript resumable** — the simplest honest fix is
  to append a synthetic, clearly-labelled error result for the unanswered call — and must cover it with a test
  that resends the transcript.
- **The output cap is per result, not per turn.** `MAX_TOOL_OUTPUT_CHARS` bounds one tool result at 20,000
  characters, so a turn calling *n* tools can still inject *n* × 20,000. **17.4 owns a per-turn cap** as part of
  the interceptor chain, which is where a cross-tool budget belongs. Named in 17.4's slice entry, not only here:
  a responsibility recorded in prose alone never reaches the builder, because `open-issues.py` builds the issue
  body from the slice entry.

## Threat model

| Risk | Control |
| --- | --- |
| Prompt injection through a tool result | Results fenced as data; the allowed tool list is fixed by the manifest |
| A write nobody approved | Writes only through `PermissionGate`; `staged_write` is the default; no gate is a construction error |
| Runaway cost | `Budget` on every run; replay is the default provider; Bedrock only with `--live` |
| Secrets or personal data in recorded replies | The recorder redacts through `Redacting`; fixtures reviewed before commit |
| AWS credentials in the repo | None committed. Local runs use the default credential chain. CI reads an IAM user's key from repo secrets, scoped to Bedrock invoke on Anthropic models; a role through GitHub OIDC is the intended end state but the account offers no Identity providers page (see the track plan's shared rules) |

## Issues

This repo has no database or auth, so its foundation paths are `agent_container/core/` — the loop, the provider
and tool contracts, and the permission gate. Wave 1 owns them; later slices extend by adding files.

### Wave 1: foundation

1. **17.1 `[fullstack-builder] Python scaffolding and CI`** · `claude` · **2nd: Codex**
   `pyproject.toml`, `uv`, `ruff`, `mypy --strict`, `pytest`, a Dockerfile, and a workflow whose required check is
   named `Lint, test, build, smoke`, plus the review-gate caller and `AGENTS.md` carrying the track's rules.
   Security-sensitive because it wires the required checks every later merge depends on. Dependencies: none.
2. **17.2 `[fullstack-builder] Core contracts and the agent loop`** · `claude` · **2nd: Codex**
   `ModelProvider`, `Tool`, `ToolResult`, `Budget`, `AgentLoop`, `ReplayProvider`, and the shared contract test
   suite every provider and decorator must pass. Dependencies: 17.1.

### Wave 2

3. **17.3 `[ai-builder] Bedrock provider and the reply recorder`** · `claude` · **2nd: Codex**
   `BedrockProvider` on the Converse API, stop-reason mapping, and the recorder that writes replay fixtures.
   Also owns three things 17.2's review surfaced, **all of which edit `core/`**, so this slice is named as their
   owner and the foundation rule does not stop it:
   (a) **The newer Converse stop reasons.** 17.2 handles the six this spec listed and raises on anything else.
   Converse also returns `malformed_model_output`, `malformed_tool_use` and `model_context_window_exceeded`, and
   a real Bedrock run that meets one would crash with a traceback instead of ending with a stated reason. Add
   them to `StopReason` and give each a branch in the loop. Do not add a default branch: the raise on an unknown
   value is the design rule.
   (b) **The model-call limiter**, as a `ModelProvider` decorator (see "Decisions this library makes").
   (c) **A resumable transcript.** A reply with stop reason `end_turn` carrying tool calls correctly ends the
   run, but leaves a `ToolUseBlock` with no matching result in `RunResult.messages`. Bedrock rejects that
   transcript if it is sent again, which is what app 19's session resumption does. Append a synthetic,
   clearly-labelled error result for the unanswered call, and test it by resending the transcript.
   Dependencies: 17.2.
4. **17.4 `[fullstack-builder] Decorators, interceptor chain, permission gate and staged changes`** · `claude` · **2nd: Codex**
   The gate rule is presence-anywhere in the stack, so `Cached(PermissionGate(write))` is valid by construction.
   `Cached` must therefore key on the acting identity from `ctx`, or one caller's gate decision is served to
   another. A test must prove two callers with different permissions do not share a cached result.
   Also owns two things from 17.2's review, **both of which edit `core/`**, so this slice is named as their owner
   and the foundation rule does not stop it:
   (a) **A per-turn output cap.** `MAX_TOOL_OUTPUT_CHARS` bounds one tool result, so a turn calling *n* tools can
   still inject *n* times that. A cross-tool budget belongs in the interceptor chain, which this slice builds.
   (b) **`Budget.child()`.** 17.2 passes `Budget` to `run()` and raises `BudgetAlreadyStarted` on reuse, which is
   right for one agent and wrong for app 20, whose coordinator runs subagents in parallel under one allowance. A
   child draws on its parent, so the run as a whole stops at the parent's limit and no subagent is starved by
   sibling accounting. **This is here rather than in 17.5 because it edits the existing `core/budget.py`**, and
   17.5 is a `grok` slice that is not security-sensitive, so the repo's `AGENTS.md` forbids it that edit.
   Dependencies: 17.2.
5. **17.5 `[fullstack-builder] Event bus, agent builder and manifest`** · `grok`
   `EventBus` with the four events named in the public interface, and `AgentBuilder`: the YAML manifest schema
   (model, system prompt, tool names, limits, permissions) and the staged assembly that reads it. The gate rule is
   enforced here — the builder walks each tool's decorator stack to the innermost tool, reads its `effect`, and
   raises at construction if an `effect: write` tool has no `PermissionGate` anywhere in its stack. **It is Builder,
   not Factory**, and the naming matters for the README's pattern map. Subscribers must not be able to change the
   loop's behavior. Also owns the **JSON-lines logger**, per "Decisions this library makes": a new
   `core/log.py` plus a subscriber on the bus. Both are new files, which is what this slice may add to `core/`
   without being security-sensitive. Dependencies: 17.2.

### Wave 3

6. **17.6 `[fullstack-builder] Command-line demo and smoke test`** · `grok`
   `agent-container demo` on replay; `--live` on Bedrock. Dependencies: 17.3, 17.4, 17.5.

### Wave 4

7. **17.7 `[devops] Deploy app 17`** · `claude` · **2nd: Codex** · repo **`30-apps-infra`**
   Security-sensitive: it provisions IAM in a new AWS account. **Second on the cut list**, after app 20's ROI model
   — the track plan's cut order is the authority — because a Lambda health endpoint is the lowest-value item in
   this repo and the demo runs from the command line without it. App 20's ROI model is cut before it.
   A Lambda health endpoint running the replay demo, in the second AWS account, us-east-2. **Do not set up GitHub
   OIDC in this slice**: the account's IAM console offers no Identity providers page, so the deploy uses the
   existing IAM user key already in repo secrets, and this slice adds only the smallest policy the deploy needs.
   Record what that policy grants on the PR. Dependencies: 17.6.
8. **17.8 `[docs-writer] README`** · `grok`
   Includes the pattern map and the exam map, each with file and line. Dependencies: 17.7.
