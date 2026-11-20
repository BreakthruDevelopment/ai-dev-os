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

Nothing here is SOA Suite, uses SOA Suite, or imitates it. These are modern agentic systems: Python, the Claude
Agent SDK, MCP, Claude Code and Amazon Bedrock. The client's legacy stack is backdrop — a simulated ERP behind an
MCP gateway in app 18, and a sample Java EE codebase that app 19's scout reads. The WebLogic parallels are how
Michael explains the designs from his own experience, not something the code implements.

## Why this shape

Three sources, in priority order:

1. **The Claude Certified Architect (Foundations) exam** — five domains, 30 task statements, six scenarios. All six
   scenarios are built as running systems, and every task statement has a home. The map is in Michael's study
   guide; each README will carry its own slice of it with file and line references.
2. **Caylent's postings** for Forward Deployed Engineer and Forward Deployed AI Lead. They repeat three things:
   turn ambiguity into scoped work, ship software that runs after you leave, and leave a reusable artifact behind.
   The four repositories are those three things plus the artifact. The AI Lead posting lists "Certified Claude
   Architect" as required, and registration is currently limited to partner-network employees — so demonstrating
   the body of knowledge is the available substitute for holding the certificate.
3. **Object-oriented design applied to agents**, from Joshua Morley's post. That mapping is one author's proposal,
   not an industry standard; the patterns themselves (Gang of Four) are. **Twelve** patterns are used. Singleton
   and Visitor were dropped on 2026-11-19 because neither solved a real problem here, and an interviewer would be
   right to probe them.

## Decisions taken

- **Scenario 1 is the supplier disputes desk** inside app 18, not a separate customer-support app. Same
  architecture — lookups, a credit, escalation on explicit criteria — inside the engagement's own story.
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
- **AWS access is by IAM role via GitHub OIDC**, not a long-lived key. No AWS credential is ever committed.

## Build order

Five days. The order is by value: whatever is finished on Tuesday must be the part worth showing.

| Day | Work |
| --- | --- |
| Fri 20 | Python scaffolding and CI; app 17 end to end |
| Sat 21 – Sun 22 | Apps 18 and 19 |
| Mon 23 | App 20; deploys to AWS; live smoke |
| Tue 24 | READMEs, exam links, recorded replays, final smoke |

**Known risks, recorded now rather than discovered later:**

- Friday is a single point of failure: everything imports app 17.
- There is no Python template in this factory. Building one is normally its own day and is folded into Friday.
- Review rounds dominate the schedule. Recent history: three rounds on one small fix (`14-real-estate#27`),
  fifteen on `15-event-ticketing#16`. At three rounds per slice across ~28 slices the week does not fit.
- **Cut order if Monday is behind:** app 20's ROI model, then session forking, then batch processing, then app
  19's scout. Never cut app 17, app 18 end to end, or the recorded replays.

## What only Michael can do

1. **Create the four repos** with the topic `30-apps-30-days`. `scripts/create-app-repos.py` builds from the
   Next.js template and `gh api /orgs/...` is blocked in Claude Code sessions, so this cannot be automated here.
2. **Set up GitHub OIDC to the new AWS account** and add the role ARN as a repository secret or variable.
3. **Merge this PR, and each app's spec.**

## Open questions

- **Slots 21–29 and 32** have no assignment. They remain their original business apps in the catalog.
- **Apps 30 and 33** are unaffected by this change but were aimed at the old slate: app 30's MCP and A2A broker
  was to be consumed by the old app 28, and app 33's embeddings service by the old apps 17 and 29. Neither has a
  consumer now.
- **The exam guide was read from a public mirror and paraphrased**, since the official guide is marked
  confidential. Task-statement wording should be checked against Anthropic Academy before any README quotes it.
