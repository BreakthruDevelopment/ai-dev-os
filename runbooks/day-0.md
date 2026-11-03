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
- [ ] **Gemini API key** from Google AI Studio (free tier)
- [ ] **Codex:** in ChatGPT → Codex settings, connect GitHub; allow only repos tagged for this project
- [ ] **Grok:** install the Grok Build CLI; give Grok Bot read-mostly GitHub access, no merge rights

## Platform (Claude Code)

- [x] `30-apps-template`: Next.js, Postgres, roles, AI gateway, tests, CI, Dockerfile
- [x] `ai-dev-os`: rules, subagents, catalog, templates, runbooks
- [ ] Terraform modules for AWS, Azure, Google Cloud, Oracle Cloud (needs the accounts above)
- [ ] GitHub Actions → cloud trust via OIDC for each cloud (no stored cloud keys)
- [ ] Oracle A1 VM sized inside the Always Free limit, with Docker, Caddy and Postgres
- [ ] **Gate:** template app live on all four clouds, smoke test passing on each

## DNS (Michael, at Network Solutions)

DNS stays at Network Solutions. Each deploy prints one record to add; see `dns-network-solutions.md`.
