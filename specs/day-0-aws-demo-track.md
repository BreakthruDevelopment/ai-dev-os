# Day 0: the AWS demo track (apps 17–20)

Approved by Michael on 2026-11-19. Four repositories, built by **Tuesday 2026-11-24**, for a Caylent interview on
**2026-12-01**. They are demonstrations, not SaaS apps.

## What they are

One mock engagement, told in four repositories. A fictional company runs procure-to-pay on WebLogic and Oracle SOA
Suite. Michael leads the engagement: discover where AI pays off, build the first workflow, enable their engineers.

| # | Repo | Stage | Exam scenarios |
| --- | --- | --- | --- |
| 17 | `17-agent-container` | The reusable core brought to every client | underpins all six |
| 18 | `18-procure-to-pay` | Build | 1 and 6 |
| 19 | `19-enablement-kit` | Enable the client's engineers | 2, 4 and 5 |
| 20 | `20-discovery-workbench` | Discover and scope | 3 |

### The six scenarios and their subjects

**Supplied by Michael on 2026-11-21**, and recorded here as the single source of truth: nothing this project held
before that date carried the subjects, only the numbers and the repo assignments above. The three app specs map
them to slices rather than restating them.

| # | Subject | Repo | Answered by |
| --- | --- | --- | --- |
| 1 | Customer support agent: resolving high-ambiguity requests (refunds, billing disputes, account issues) using backend MCP tools and escalating to human agents when needed | 18 | 18.6, the disputes desk, over 18.3's MCP gateway |
| 2 | Code generation with Claude Code: using slash commands, `.md` and configuration files, and deciding between plan mode and direct execution | 19 | 19.4 (the `CLAUDE.md` hierarchy, path rules, commands, skills) and 19.9 (plan mode versus direct execution) |
| 3 | Multi-agent research system: coordinating task decomposition across sub-agents and synthesizing well-sourced, cited reports | 20 | 20.4 (coordination) **and 20.5** (the cited readout) — both halves, not one |
| 4 | Developer productivity tools: navigating and understanding unfamiliar codebases efficiently using built-in tools (such as search/grep and targeted file reads) | 19 | 19.8, the scout, over 19.3's sample Java EE codebase |
| 5 | Continuous integration (CI/CD): running Claude Code in automated pipelines for code reviews, test generation, and pull request feedback | 19 | 19.7 (the review passes and written criteria) and 19.10 (headless in CI, posting pull-request feedback) |
| 6 | Structured data extraction: extracting accurate, validated JSON from unstructured documents while avoiding hallucinated or missing fields | 18 | 18.4, invoice extraction |

App 17 underpins all six: each runs on its loop, its provider and its gate.

Two places where the fit is less than exact, recorded now that the subjects are known:

- **Scenario 1 is the loosest fit on the track.** The exam says *customer* support; app 18 does *supplier*
  disputes. "Billing disputes" is in the scenario text, the desk runs over backend MCP tools, a credit memo stands
  in for a refund, a payment-status lookup for an account issue, and escalation to a human is statements 5.2 and
  5.5 — so everything the scenario exercises is present and only the counterparty differs. The substitution
  **stands**; each README says so in those words rather than implying the exam asked about suppliers.
- **Scenario 5 lacks "test generation."** The reviewer's fourth pass judges tests and coverage and writes none,
  and nothing else in app 19 generates tests. Code review and pull-request feedback are covered in full. Recorded
  as a stated gap rather than papered over: a README claiming the whole scenario would be wrong.

### The five domains and their weights

Also **supplied by Michael on 2026-11-21**, from studytech.ai and szymonpaluch.com. They are **his figures and
approximate** — the official guide is confidential, so treat them as planning weights, not as quotable fact.

| Domain | Weight | Statements | Owned by |
| --- | --- | --- | --- |
| Agentic Architecture & Orchestration (1.x) | 27% | 7 | 17 (1.1, 1.5), 18 (1.4, 1.6), 19 (1.7), 20 (1.2, 1.3) |
| Claude Code Configuration & Workflows (3.x) | 20% | 6 | **19 alone** (3.1–3.6) |
| Prompt Engineering & Structured Output (4.x) | 20% | 6 | 18 (4.2–4.5), 19 (4.1, 4.6) |
| Tool Design & MCP Integration (2.x) | 18% | 5 | 17 (2.2), 18 (2.1, 2.3, 2.4), 19 (2.5) |
| Context Management & Reliability (5.x) | 15% | 6 | 18 (5.1, 5.2, 5.5), 19 (5.4), 20 (5.3, 5.6) |

The domain-to-prefix mapping was **checked against the statement subjects**, not assumed: Michael's list is
ordered by weight rather than by domain number, which is where an error would hide. Every 1.x statement is loop,
coordinator, handoff or decomposition; every 2.x is a tool or MCP concern; 3.x is entirely Claude Code
configuration and workflow; 4.x is prompting and structured output; 5.x is context, escalation, propagation and
calibration. The counts are 7 / 5 / 6 / 6 / 6 = 30, and the weights sum to 100.

**Weighted ownership**, spreading each domain's weight evenly over its statements and crediting the first repo
listed in the coverage table: **app 18 39.3%, app 19 36.6%, app 20 12.7%, app 17 11.3%** (per statement: 3.86 in
domain 1, 3.60 in domain 2, 3.33 in domains 3 and 4, 2.50 in domain 5; the four sum to 100.0). Two consequences:

- **Domain 3 is sole-sourced to app 19** — the only domain owned entirely by one repo. Trimming app 19 forfeits a
  fifth of the exam with nothing else able to carry it, which is why the cut order already protects its Domain 3
  coverage and why app 19 outranks app 20 for scarce `claude` capacity.
- **Exam weight is not demo value.** App 20's 20.6, 20.7 and 20.8 carry zero statements and zero scenarios, while
  20.4 carries 10.2% and 20.5 carries 2.5%. That does not make the first three cuttable: 20.6 is the only surface
  anything can be shown from, and 20.8 is the artifact that proves the coverage claim to a reader. The weights
  rank what the exam rewards, not what an interview sees.

Nothing here is SOA Suite, uses SOA Suite, or imitates it. These are modern agentic systems: Python, the Bedrock
Converse API, MCP, Claude Code and Amazon Bedrock. The Claude Agent SDK is deliberately **not** used: app 17
hand-builds its loop so the design is the thing on show rather than a framework's. (`ROADMAP.md`'s W07 row is
named "Agents SDK" after the week's topic, not after a dependency of this track.) The client's legacy stack is
backdrop — a simulated ERP behind an MCP gateway in app 18, and a sample Java EE codebase that app 19's scout
reads. The WebLogic parallels are how Michael explains the designs from his own experience, not something the
code implements.

## Why this shape

Three sources, in priority order:

1. **The Claude Certified Architect (Foundations) exam** — five domains, 30 task statements, six scenarios. All six
   scenarios are built as running systems, and the table below gives every task statement a home. Each README will
   carry its own slice of it with file and line references. The scenario subjects and the domain weights are above;
   as of 2026-11-21 they are recorded, not guessed.
2. **Caylent's postings** for Forward Deployed Engineer and Forward Deployed AI Lead. They repeat three things:
   turn ambiguity into scoped work, ship software that runs after you leave, and leave a reusable artifact behind.
   The four repositories are those three things plus the artifact. The AI Lead posting lists "Certified Claude
   Architect" as required, and registration is currently limited to partner-network employees — so demonstrating
   the body of knowledge is the available substitute for holding the certificate.
3. **Object-oriented design applied to agents**, from Joshua Morley's post. That mapping is one author's proposal,
   not an industry standard; the patterns themselves (Gang of Four) are. **Thirteen** patterns are used.
   Singleton and Visitor were dropped on 2026-11-19 because neither solved a real problem here, and an
   interviewer would be right to probe them.

## Exam coverage: all 30 task statements

Claimed homes, not yet built. A statement with two repos is owned by the first and exercised by the second.

| Statement | Subject | Repo |
| --- | --- | --- |
| 1.1 | Agentic loops and stop reasons | 17 |
| 1.2 | Coordinator and subagents | 20 |
| 1.3 | Subagent invocation and context passing | 20 |
| 1.4 | Enforced workflows and handoffs | 18 (on 17's gate) |
| 1.5 | Hooks intercepting tool calls | 17, 18 |
| 1.6 | Task decomposition strategy | 18 (fixed), 20 (adaptive) |
| 1.7 | Session state, resumption, forking | 19 |
| 2.1 | Tool interface design | 18 (on 17's contract) |
| 2.2 | Structured MCP error responses | 17, 18 |
| 2.3 | Tool distribution and `tool_choice` | 18, 20 |
| 2.4 | MCP server integration | 18 (builds), 19 (connects) |
| 2.5 | Built-in tools | 19 |
| 3.1 | CLAUDE.md hierarchy | 19 |
| 3.2 | Custom commands and skills | 19 |
| 3.3 | Path-specific rules | 19 |
| 3.4 | Plan mode versus direct execution | 19 |
| 3.5 | Iterative refinement | 19 |
| 3.6 | CI/CD integration | 19 |
| 4.1 | Explicit criteria for precision | 19 |
| 4.2 | Few-shot prompting | 18 |
| 4.3 | Structured output via tool use | 18 |
| 4.4 | Validation, retry and feedback loops | 18 |
| 4.5 | Batch processing | 18 |
| 4.6 | Multi-instance and multi-pass review | 19 |
| 5.1 | Preserving context in long interactions | 18, 20 |
| 5.2 | Escalation and ambiguity resolution | 18 |
| 5.3 | Error propagation across agents | 20 |
| 5.4 | Context in large codebase exploration | 19 |
| 5.5 | Human review and confidence calibration | 18 |
| 5.6 | Provenance and uncertainty in synthesis | 20 |

By repo: **17** owns 3, **18** owns 12, **19** owns 11, **20** owns 4 — thirty in total, each owned once. Domain 3
is entirely app 19, which is why app 19 cannot be cut.

## Decisions taken

- **Scenario 1 is the supplier disputes desk** inside app 18, not a separate customer-support app. Same
  architecture — lookups, a credit, escalation on explicit criteria — inside the engagement's own story. This
  bullet records only the decision; the scenario's own subject, and the one way the substitution diverges from it,
  are in the scenario table above and are not restated here.
- **Slots 21–29 and 32 are untouched** and keep their existing catalog entries. Michael's original instruction
  covered 17–29 and 32; narrowing to four repositories left the rest unassigned, and that is a separate decision.
- **Bedrock is confirmed**: the second AWS account (project "Ctrl Shift Believe"), region **us-east-2**, model
  **Claude Sonnet 4.6** via the Global Anthropic inference profile. Claude Opus 5 is **not** available to that
  account (`AccessDeniedException`, verified in the console on 2026-11-19).

## The track's shared rules

These replace the Next.js stack rules for these four repos. Each repo's `AGENTS.md` carries them.

- **Python 3.12**, `uv`, `ruff`, `mypy --strict`, `pytest`. The required check keeps the name
  `Lint, test, build, smoke` so the review gate and the merge rules work unchanged.
- **Every model call goes through app 17's `ModelProvider`.** No demo calls Bedrock directly.
- **Every demo runs at zero cost on recorded replies** (`ReplayProvider`), which is what CI and a default demo
  use. `--live` switches to Bedrock. A demo must never need the network to be shown.
- **Writes are staged.** A tool that changes anything returns a staged change for a person to approve.
- **Tool results are data, never instructions.**
- **Each README maps its patterns and exam task statements to file and line**, so a reader can check the claim.
- **No AWS credential is ever committed.** As of 2026-11-20 CI authenticates with an IAM user's access key held
  in each repo's GitHub secrets, scoped to `bedrock:InvokeModel` and `bedrock:InvokeModelWithResponseStream` on
  Anthropic models and inference profiles. A role assumed through GitHub OIDC is the intended end state and is
  better — short-lived, nothing to rotate — but the account's IAM console offers no Identity providers page, so it
  is not available today. Moving to a role is a follow-up, not a precondition for this track. Any slice that needs
  more than Bedrock invoke gets its own policy, reviewed on its own PR.

## Build order

Five days. The order is by value: whatever is finished on Tuesday must be the part worth showing.

| Day | Work |
| --- | --- |
| Fri 20 | Python scaffolding and CI; app 17 end to end |
| Sat 21 – Sun 22 | Apps 18 and 19 |
| Mon 23 | App 20; deploys to AWS; live smoke |
| Tue 24 | READMEs, exam links, recorded replays, final smoke |

**Friday does not hold as written, and the review of this PR said so.** Six slices on day one with no Python
template in the factory at all, and 17.1 to 17.2 are strictly serial. The plan stands because the week has a week
of slack behind it: the interview is 2026-12-01, so Tuesday slipping to Wednesday costs nothing real.

**App 20's Wednesday set changed on 2026-11-21**, when the scenario subjects arrived: it is 20.1–20.6 with the
ROI model and `GET /` cut, and 20.7's deploy plus 20.8's README on Friday. The earlier proposal (20.1–20.4 by
Wednesday, 20.5–20.8 to Friday) would have shipped the coordination half of scenario 3 and dropped the
cited-report half it is named for. Details and the fallback are in
[`20-discovery-workbench.md`](20-discovery-workbench.md) under "Wednesday". Scarce `claude` capacity goes to apps
18 and 19 first; app 19 sole-sources Domain 3.

**Known risks, recorded now rather than discovered later:**

- Friday is a single point of failure: everything imports app 17, and nothing can be parallelised around it.
- There is no Python template in this factory. Building one — CI, container image, the four required checks, the
  review-gate caller — is normally its own day and is folded into slice 17.1.
- Review rounds dominate the schedule. Recent history: three rounds on one small fix (`14-real-estate#27`),
  fifteen on `15-event-ticketing#16`. At three rounds per slice across ~28 slices the week does not fit.
- ~~Two things are blocked on Michael~~ **Both cleared on 2026-11-20:** the four repos exist with the topic set,
  and AWS credentials are in each repo's secrets. Day one is unblocked.
- **Cut order, invoked Saturday night rather than Monday if apps 17 and 18 are not both moving:** app 20's ROI
  model, then app 17's Lambda health endpoint (slice 17.7 — the lowest-value item in app 17), then session
  forking, then batch processing, then app 19's scout. Never cut app 17, app 18 end to end, app 19's Domain 3
  coverage, or the recorded replays.
- **The cut order has two scenario costs that were invisible until 2026-11-21.** Neither item is in Domain 3,
  which is why both looked cheap: **cutting app 19's scout drops scenario 4 entirely** (19.8 is its whole answer,
  over 19.3's sample codebase, and carries 2.5 and 5.4), and **cutting session forking strands 19.9**, whose
  `kit plan` runs two continuations from one forked prefix — that is scenario 2's plan-mode clause, and 19.9
  depends on 19.5. Cut the ROI model and app 17's Lambda health endpoint first: those two carry no scenario at
  all. If the order has to reach further, batch processing (18.7, statement 4.5) is the next item that costs no
  scenario, since scenario 6 is answered by 18.4 alone.
- **Realistic target:** apps 17 and 18 end to end by Tuesday. Four polished repos with all 30 statements mapped to
  file and line is not.

## What only Michael can do

1. ~~Create the four repos~~ **Done 2026-11-20.** All four exist, public, `main`, topic `30-apps-30-days`.
   `scripts/create-app-repos.py` generates a new repo from the Next.js template, which is wrong for a Python
   repo, so these four were created by hand. That skipped two things the script also does: the harness labels
   and the `protect-main` ruleset. **Both were put right on 2026-11-20 at 12:51**, by marking the four
   `create_repo: true` so the script's existing-repo path ran `ensure_extras` against them — it skips creation
   (they exist and carry the topic) and adds only what is missing. All four now carry an active `protect-main`
   with the same four rule types and both required checks as apps 5-15, and repo 17 carries the full harness
   label set. Nothing here is outstanding.
   Two notes kept because they were got wrong first time: a missing label would not have blocked anything,
   since GitHub auto-creates one on first use, so pre-creating only fixes the colour; and the script's
   precedent is apps 5-15 **and app 31**, not apps 1-4, whose rulesets Michael added by hand on 2026-11-14
   (`FACTORY.md`). Changing a ruleset still stays with Michael; the script doing it on his merge is the
   established route, not an exception.
2. ~~Set up AWS access for CI~~ **Done 2026-11-20.** An IAM user with a least-privilege Bedrock policy
   (`bedrock:InvokeModel`, `bedrock:InvokeModelWithResponseStream` on Anthropic models and inference profiles);
   its keys are repository secrets in all four repos. OIDC was the better option but the account's IAM console
   offers no Identity providers page, so this is the fallback and should move to a role later.
3. **Merge this PR, and each app's spec.**

## Open questions

- **Slots 21–29 and 32** have no assignment. They remain their original business apps in the catalog.
- **Apps 30 and 33** are unaffected by this change, and both keep consumers. This track removes **two** callers
  from app 33, one from each of its lever rows: the old app 17, which was to use its embeddings and rerank, and
  the old app 19, a refusal and redaction eval suite that was to use its eval runner. App 33 still serves app 29
  (retrieval and rerank) and apps 22 and 25 (eval runner), and publishes to app 30. **None** are removed from
  app 30: it still receives traces from apps 26, 28 and 31, none of which this track retires.
  (`ROADMAP.md`'s "one caller, not two" is correct where it stands, because it is scoped to the embeddings and
  rerank service alone; app 33 as a whole lost a caller from the other row too.)
- **App 30's A2A broker has no named caller.** Correcting the record above exposed it: app 30 is described as the
  MCP server and A2A broker, but app 28 — the app previously named as its consumer here — calls **app 31** over
  A2A (`catalog.yaml`), and no other app is named as calling app 30's broker. Its trace-and-cost half has four
  consumers — apps 26, 28 and 31 for traces, app 33 for eval scores — and its A2A half has none. That is app 30's
  real open question, and it is older than this track.
- **The exam guide was read from a public mirror and paraphrased**, since the official guide is marked
  confidential. Task-statement wording should be checked against Anthropic Academy before any README quotes it.
