# Day 0 setup

Two days of setup before Day 1. Day 1 starts only when the template app is live on all four clouds.

## Accounts (Michael)

Enter keys and passwords directly into the service or GitHub secrets, never into a chat with an AI tool.

- [x] GitHub: BreakthruDevelopment org; this project's repos created and attached
- [ ] Email: `dev@breakthruventures.ai` (or use an existing address) for the cloud accounts
- [ ] **AWS:** sign up on the **Free plan** (can't bill; closes after 6 months). Budget alert at $1.
- [ ] **Azure:** free account. The $200 credit expires 30 days after sign-up, so create it when ready to start. Budget alert at $1.
- [ ] **Google Cloud:** billing account + project `breakthru-30-apps`; region `us-central1`. Budget alert at $1.
- [ ] **Oracle Cloud:** sign up with a **US home region** (can't be changed). Create nothing yet.
- [ ] **Gemini API key** from Google AI Studio, billed to the Google Cloud project so Google AI Pro's $10/month credit covers the apps' AI calls
- [ ] **Codex:** in ChatGPT → Codex settings, connect GitHub; allow only repos tagged for this project
- [ ] **Grok:** install the Grok Build CLI; give Grok Bot read-mostly GitHub access, no merge rights
- [ ] **Google AI Pro:** subscribe (confirm the intro price and the renewal price), connect Jules to GitHub with access to this project's repos only
- [ ] **Project board:** one GitHub Project across all app repos, columns Todo / In progress / In review / Done, a Harness field (`claude`, `grok`, `codex`, `jules`)
- [ ] **Repo settings** (this session can't change them): merge template PR #1; add topic `30-apps-30-days` to both repos; mark `30-apps-template` as a template repository; protect `main` on both (require PR + passing checks)

## Platform (Claude Code)

- [x] `30-apps-template`: Next.js, Postgres, roles, AI gateway, tests, CI, Dockerfile
- [x] `ai-dev-os`: rules, roles, subagents, catalog, templates, runbooks
- [ ] Terraform modules for AWS, Azure, Google Cloud, Oracle Cloud (needs the accounts above)
- [ ] GitHub Actions → cloud trust via OIDC for each cloud (no stored cloud keys)
- [ ] Oracle A1 VM sized inside the Always Free limit, with Docker, Caddy and Postgres
- [ ] **Gate:** template app live on all four clouds, smoke test passing on each

Day 1 builds app 1, the Build Tracker, so it can run the rest of the month as mission control.

## DNS (Michael, at Network Solutions)

DNS stays at Network Solutions. Each deploy prints one record to add; see `dns-network-solutions.md`.
