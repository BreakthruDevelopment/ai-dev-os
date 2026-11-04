# Day 0 setup

Setup before Day 1. **Done on 2026-11-04:** the template app is live and healthy on all four clouds. This page
records what was set up, so the same steps can be repeated or audited.

## Accounts (Michael)

Enter keys and passwords directly into the service or GitHub secrets, never into a chat with an AI tool.

- [x] GitHub: BreakthruDevelopment org; this project's repos created and tagged `30-apps-30-days`
- [x] **AWS** (`dev@breakthruventures.ai`): **Free plan**, kept that way so it can't bill (closes after 6 months).
      Its project guardrails allow only **us-east-2** and block GitHub sign-in; lifting them needs a paid plan, so
      AWS deploys run from CloudShell instead.
- [x] **Azure** (`dev@breakthruventures.ai`): free account; the $200 credit lasts 30 days. East US can't host
      Postgres for this subscription, so the database is in Central US.
- [x] **Google Cloud** (`mparrott567@gmail.com`): project `mindful-pillar-460605-h4`, region `us-central1`. The trial
      had ended, so it's a paid account kept inside always-free limits: budget `GoogleCloudCap` (alerts); a Cloud Run
      spend cap is recommended.
- [x] **Oracle Cloud** (`dev@breakthruventures.ai`): home region US West (Phoenix).
- [x] Codex, Grok Build, Grok Bot and Jules connected to GitHub
- [x] **Gemini API key:** free tier, from Google AI Studio in its own project `30-apps-gemini` (no billing, so it
      can't charge). Stored as the `GEMINI_API_KEY` secret in the infra repo's `production` environment (Azure,
      Google Cloud) and in AWS Parameter Store at `/30apps/gemini_api_key`. New-format keys start with `AQ.` and are
      53 characters. Oracle isn't wired yet, so Oracle apps give demo answers until before app 4.
- [x] **Budget alerts at $1** on AWS (`BreakthruAWS`; verify the recipient email), Azure (`BreakthruAzure`) and
      Google Cloud. Oracle needs none: the trial account can't charge unless upgraded.
- [x] **Project board:** [30 Apps in 30 Days](https://github.com/users/BreakthruDevelopment/projects/1): Status (Todo / In Progress / In review / Done) and a Harness field (`claude`, `grok`, `codex`, `jules`); Board and table views. BreakthruDevelopment is a personal account, so the board lives under it rather than an org.

## Platform (Claude Code)

- [x] `30-apps-template`: Next.js, Postgres, roles, AI gateway, tests, CI, Dockerfile. Multi-arch image published
      to GHCR; migrations run on startup (`MIGRATE_ON_START=true`).
- [x] `ai-dev-os`: rules, roles, subagents, catalog, templates, runbooks
- [x] `30-apps-infra`: one Terraform stack per cloud, driven by `apps.yaml`
- [x] Bootstrap scripts (`bootstrap/<cloud>.sh`, run once in each cloud's shell): state storage, plus a read-only
      plan identity and a deploy identity. Azure and Google Cloud trust GitHub through keyless OIDC; Oracle uses an
      API key stored as the `production` environment secret.
- [x] **Gate:** template app live on all four clouds, health check passing on each

| Cloud | Template app |
| --- | --- |
| AWS | https://v1uf5au310.execute-api.us-east-2.amazonaws.com |
| Azure | https://app-template.salmonpebble-b870873b.eastus.azurecontainerapps.io |
| Google Cloud | https://template-189497094271.us-central1.run.app |
| Oracle | https://template.141-148-159-122.sslip.io |

## Gotchas found on Day 0

- The org uses **immutable OIDC subject claims**, so GitHub presents
  `repo:BreakthruDevelopment@225800281/30-apps-infra@1445302771:…`. The bootstrap scripts trust both forms.
- **AWS CloudShell's home folder is 1 GB**; `deploy/aws.sh` keeps Terraform's files in `/tmp`.
- **Oracle Always Free Ampere capacity** sells out per availability domain; the workflow tries all three. If all
  are full, rerun the workflow later.
- Google Cloud's deploy identity can't grant IAM, so the database VM uses the Compute default service account.

Day 1 builds app 1, the Build Tracker, so it can run the rest of the month as mission control.
