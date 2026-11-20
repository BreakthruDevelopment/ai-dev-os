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
  bus; a run budget; a factory that builds an agent from a manifest; a command-line demo; a Lambda health
  endpoint.
- **Out:** multi-agent coordination (app 20), MCP serving (app 18), Claude Code configuration (app 19), retrieval,
  and evals beyond this library's own tests. Each is built on this library in its own repo.

## Public interface

| Class | Pattern | What it does | Exam |
| --- | --- | --- | --- |
| `AgentLoop` | Template Method | `run()` is fixed: call the model, branch on the stop reason, run tools, append results, check the budget. Subclasses override `before_model`, `after_tool` and `should_stop`, never the skeleton. | 1.1 |
| `ModelProvider` (ABC) | Strategy | `converse(request) -> ModelResponse`. `BedrockProvider` calls the Bedrock Converse API; `ReplayProvider` returns recorded replies. | 1.1 |
| `Tool` (ABC) | — | `name`, `description`, a typed input model, `run(args, ctx) -> ToolResult`. | 2.1 |
| `ToolResult` | — | Carries `is_error`, `error_category` (`transient`, `validation`, `permission`, `business`) and `is_retryable`, so the model can tell a retry from a dead end. | 2.2 |
| `Retrying`, `Cached`, `Redacting`, `Metered` | Decorator | Each wraps a `Tool` and is itself a `Tool`. They stack. | 1.5 |
| `InterceptorChain` | Chain of Responsibility | Ordered interceptors run before and after each tool call. Each handles or passes on. Normalizing formats and blocking a policy violation are interceptors, not prompt instructions. | 1.5 |
| `PermissionGate` | Proxy | Stands in front of a tool with a policy of `read`, `staged_write` or `deny`. A staged write returns a `StagedChange` instead of acting. | 1.4 |
| `StagedChange` | Command | A recorded write with `apply()` and a description a person reads before approving. | 1.4 |
| `EventBus` | Observer | Publishes `ModelCalled`, `ToolCalled`, `ToolFailed`, `BudgetExceeded`. Subscribers never change the loop's behavior. | 1.5 |
| `Budget` | — | Maximum turns, tokens and wall-clock time. An ordinary object created once per run and passed in, **not** a singleton. The loop stops with a stated reason when a limit is hit. | 1.1 |
| `AgentFactory` | Factory | Builds a configured agent from a YAML manifest: model, system prompt, tools, limits, permissions. | 2.3 |

Design rules the code must hold to, and that the tests must prove:

- **The loop ends on the stop reason, never on the text.** `end_turn` ends it; `tool_use` continues it;
  `max_tokens`, `stop_sequence` and guardrail stops are handled explicitly and named in the result. Parsing the
  reply for "done" is the anti-pattern this slice exists to avoid.
- **Composition over inheritance.** One level from an abstract base is the limit; behavior is added by wrapping.
- **Substitutability is tested.** Every `ModelProvider` and every decorator passes one shared contract test suite,
  so a provider swap is proven, not asserted.
- **A write needs a gate.** Constructing an agent with a write-capable tool that has no `PermissionGate` raises at
  construction time, not at run time.

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
| A write-capable tool with no gate | fail at construction |

## Threat model

| Risk | Control |
| --- | --- |
| Prompt injection through a tool result | Results fenced as data; the allowed tool list is fixed by the manifest |
| A write nobody approved | Writes only through `PermissionGate`; `staged_write` is the default; no gate is a construction error |
| Runaway cost | `Budget` on every run; replay is the default provider; Bedrock only with `--live` |
| Secrets or personal data in recorded replies | The recorder redacts through `Redacting`; fixtures reviewed before commit |
| AWS credentials in the repo | None stored. Local runs use the default credential chain; CI assumes a role through GitHub OIDC |

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
   Dependencies: 17.2.
4. **17.4 `[fullstack-builder] Decorators, interceptor chain, permission gate and staged changes`** · `claude` · **2nd: Codex**
   Dependencies: 17.2.
5. **17.5 `[fullstack-builder] Event bus, agent factory and manifest`** · `grok`
   Dependencies: 17.2.

### Wave 3

6. **17.6 `[fullstack-builder] Command-line demo and smoke test`** · `grok`
   `agent-container demo` on replay; `--live` on Bedrock. Dependencies: 17.3, 17.4, 17.5.

### Wave 4

7. **17.7 `[devops] Deploy app 17`** · `claude` · repo **`30-apps-infra`**
   A Lambda health endpoint running the replay demo, in the second AWS account, us-east-2, with access by IAM role
   through GitHub OIDC. Dependencies: 17.6.
8. **17.8 `[docs-writer] README`** · `antigravity`
   Includes the pattern map and the exam map, each with file and line. Dependencies: 17.7.
