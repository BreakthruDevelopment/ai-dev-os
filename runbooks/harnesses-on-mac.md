# Grok Build and Antigravity on Michael's Mac

Grok Build (`grok`) and Google Antigravity (`agy`) are command-line agents that run on Michael's Mac. GitHub labels
don't start them; [`scripts/run-harness.sh`](../scripts/run-harness.sh) does. It finds the issues labelled for that
harness, works them one at a time in a local clone and opens a PR for each. Michael still merges everything.

A harness label is the **start signal**: Claude adds `grok` or `antigravity` to an issue only once the issues it
depends on are merged. The script double-checks: it skips an issue whose `## Dependencies` section still lists an
open issue.

## One-time setup

Run these in Terminal. Nothing here needs a secret pasted into a chat.

```bash
# 1. Tools: GitHub CLI, Node 22 + pnpm, and coreutils (gives `gtimeout`, so a stuck Grok run is stopped)
brew install gh node@22 coreutils
corepack enable                      # provides pnpm at the version each repo pins
gh auth login                        # GitHub.com → HTTPS → sign in as the account that owns BreakthruDevelopment
gh auth setup-git                    # git pushes use the gh sign-in

# 2. Grok Build (SuperGrok / X Premium+). Installs `grok` into ~/.grok/bin and adds it to PATH.
curl -fsSL https://x.ai/cli/install.sh | bash
exec zsh                             # reload PATH
grok --version
cd ~ && grok                         # first run opens the browser to sign in with your grok.com account; then /exit

# 3. Antigravity CLI (Google AI Pro). Installs `agy` into ~/.local/bin.
curl -fsSL https://antigravity.google/cli/install.sh | bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc && exec zsh
agy                                  # choose "1. Google OAuth", sign in in the browser, paste the code back,
                                     # accept the terms; then /exit

# 4. Working folder (the script creates it too) and a copy of the script
mkdir -p ~/30apps/logs
gh repo clone BreakthruDevelopment/ai-dev-os ~/30apps/ai-dev-os
```

**Antigravity permission rules (required).** A headless `agy` run can't ask you anything, so it refuses any
command you haven't allowed. The script runs `agy` in `accept-edits` mode (file edits in the repo are approved)
and refuses to start unless `~/.gemini/antigravity-cli/settings.json` has a `permissions` block. Open that file and
merge in this block (keep any keys already there):

```json
{
  "permissions": {
    "allow": [
      "command(pnpm)", "command(corepack)", "command(node)", "command(npx)",
      "command(git status)", "command(git diff)", "command(git log)", "command(git show)",
      "command(git add)", "command(git commit)", "command(git restore)", "command(git rm)", "command(git mv)",
      "command(git branch)", "command(git rev-parse)", "command(git ls-files)",
      "command(gh issue view)", "command(ls)", "command(cat)", "command(head)", "command(tail)",
      "command(grep)", "command(rg)", "command(find)", "command(wc)", "command(mkdir)",
      "command(curl)", "command(bash scripts/smoke.sh)", "command(psql)"
    ],
    "deny": [
      "command(git push)", "command(git remote)", "command(git config)", "command(git checkout main)",
      "command(gh pr)", "command(gh api)", "command(gh repo)", "command(gh secret)", "command(gh auth)",
      "command(gh label)", "command(gh issue close)", "command(gh issue edit)",
      "command(sudo)", "command(rm -rf /)", "command(rm -rf ~)", "write_file(.git/)"
    ]
  }
}
```

Rules are `action(target)`, prefix matches word by word; deny beats allow
([Antigravity permissions docs](https://antigravity.google/docs/permissions.md)). They apply to every `agy`
session on the Mac, not just the script's. If a run's PR says a command was refused, add it to `allow` and rerun.

**Optional: a local Postgres**, so harnesses can run the integration tests and the smoke test the way CI does.
Without it they skip both and say so in the PR; CI runs them on every PR either way.

```bash
# Either Docker Desktop, with the same image CI uses:
docker run -d --name 30apps-pg --restart unless-stopped -p 5432:5432 \
  -e POSTGRES_USER=app -e POSTGRES_PASSWORD=app -e POSTGRES_DB=app pgvector/pgvector:pg17
# or Homebrew (CI runs Postgres 17 with pgvector; postgresql@16 also works for apps that don't use pgvector):
brew install postgresql@17 pgvector && brew services start postgresql@17
createuser -s app && psql -d postgres -c "alter user app password 'app'" && createdb -O app app

# Then, in ~/.zshrc (a local-only test database, not a secret):
export TEST_DATABASE_URL=postgres://app:app@localhost:5432/app
```

**Check which repos protect `main`.** The script never pushes `main`, but the harness runs with broad approval
(below), so the server-side rule is the backstop:

```bash
for r in 01-build-tracker 02-notes-kb 03-expense-tracker 04-habit-tracker \
         05-budget-planner 06-read-later 07-appointment-booking 08-loan-portal; do
  printf '%-24s %s\n' "$r" "$(gh api repos/BreakthruDevelopment/$r/rulesets --jq '[.[].name] | join(",")')"
done
```

As of 2026-11-09: **05–08** (plus `ai-dev-os` and `30-apps-infra`) have the `protect-main` ruleset (PR and green CI
required, no force pushes or deletion). **01–04 and `30-apps-template` have no ruleset and no branch protection**,
so a harness that ignored its instructions could push to their `main`. Before pointing a harness at 01–04, add the
ruleset: either **Settings → Rules → Rulesets → New branch ruleset** (`protect-main`, Active, default branch,
Restrict deletions, Block force pushes, Require a pull request, Require status check `Lint, test, build, smoke`), or
mark those apps `create_repo: true` in `catalog.yaml`; the Create app repos workflow then adds only what's missing
(ruleset, labels) to repos that already carry the topic.

## Daily use

```bash
cd ~/30apps/ai-dev-os && git pull --ff-only     # latest script
scripts/run-harness.sh grok --dry-run           # what it would pick up, and why the rest are skipped
scripts/run-harness.sh grok                     # work every ready grok issue, one after another
scripts/run-harness.sh antigravity --once       # one antigravity issue, then stop
```

Leave the Terminal window open while it runs; the Mac must stay awake (`caffeinate -i scripts/run-harness.sh grok`
keeps it awake). Each run appends to `~/30apps/logs/<harness>-<date>.log`.

Limit it to some repos with `REPOS="06-read-later 08-loan-portal" scripts/run-harness.sh grok`. Change the time
limit per issue with `HARNESS_TIMEOUT_MIN=120` (default 90).

## How to stop

- **Now:** Ctrl-C. The current issue keeps its `in-progress` label and the clone keeps the branch; see below.
- **After the current issue:** `touch ~/30apps/STOP`. The script stops before the next issue and won't start again
  until you `rm ~/30apps/STOP`.

## What the script does

For each repo tagged `30-apps-30-days` whose name is `NN-slug`:

1. Lists open issues labelled with the harness. Skips any labelled `in-progress`, any with an open PR that closes it
   (`Closes #N` in the body or a `<harness>/N-…` branch), any whose title doesn't start with a known `[role]`, and
   any whose `## Dependencies` list still has an open issue.
2. Clones the repo into `~/30apps/<repo>`, or fetches, checks out `main` and fast-forwards. **Refuses a repo whose
   working tree is dirty.**
3. Creates `<harness>/<N>-<slug>`, labels the issue `in-progress` and comments "Started by <harness> on Michael's Mac"
   (the nightly ops monitor sees it as activity).
4. Saves the issue and the role file to `.harness/` (ignored by git) and runs the harness headless with a standard
   prompt: read `AGENTS.md` and the role, do the issue, run `pnpm install`, `lint`, `typecheck`, `test`, `build`
   (and smoke when `TEST_DATABASE_URL` is set), commit, and write the PR description to `.harness/pr-body.md`.
   **Pushing is switched off in the clone while the harness runs**, and it's told not to push or touch PRs.
5. Checks the result: still on the work branch, at least one commit, nothing uncommitted, local `main` unchanged.
   Then it pushes only that branch (never `--force`) and opens a PR whose body starts with `Closes #N`, followed by
   the harness's summary and checks list. It removes `in-progress`, since the open PR now marks the issue as taken.

If a run ends without a PR, the script comments on the issue with the reason and leaves `in-progress` on it, so
it isn't retried in a loop. To retry: look at `~/30apps/<repo>`, discard or keep the work, delete the local
branch (`git branch -D <branch>`), remove the label, and run again.

## What it won't do

- Push `main`, force-push, delete or rename branches or repos, merge PRs, or change settings, secrets or other
  repos. Only repos with the `30-apps-30-days` topic are touched.
- Run two issues at once, or run anything on a schedule: you start it.
- Install a database, or put a key or token anywhere. The only environment it sets for the harness is
  `AI_PROVIDER=demo` and a dummy local `BETTER_AUTH_SECRET`, the same kind CI uses.
- Post anything outside GitHub.

## The auto-approve trade-off

Unattended runs can't answer permission prompts, so each harness gets standing approval:

| Harness | Mode the script uses | What runs without asking | What's refused |
| --- | --- | --- | --- |
| Grok Build | `--always-approve` plus `--deny` rules | Everything, including any shell command | `git push`, `git remote`, `git config`, `gh pr`, `gh api`, `gh repo`, `gh secret`, `gh label`, `gh auth`, closing or editing issues, `sudo`, `rm -rf /…` and `~…`, reading `~/.ssh`, `~/.grok`, `~/.config/gh`, `~/.aws`, `~/.gemini` |
| Antigravity | `--mode accept-edits` plus the rules above | File edits in the repo and the allowed commands | Anything denied, and anything not allowed (headless mode can't ask) |

Grok's own docs recommend always-approve plus deny rules for unattended runs; deny always wins, even under
always-approve. The stricter Grok modes (`--permission-mode dontAsk` or `auto`) refuse `pnpm` and `git commit`
unless you pre-approve them, so a run stops half done. If you write an allow list in `~/.grok/config.toml`
(`[permission]` `allow = ["Bash(pnpm *)", "Bash(git add *)", "Bash(git commit *)", …]`), switch with
`GROK_PERMISSION="--permission-mode dontAsk" scripts/run-harness.sh grok`.

For Antigravity, `AGY_PERMISSION=--dangerously-skip-permissions` approves every tool call. The docs call that fit
for a throwaway run, and they don't say whether deny rules still apply under it. Use it only if the allow list keeps
getting in the way.

**What protects you either way.** Deny rules match command text; they're not a sandbox, and a model that writes a
script and runs it can get round them. A harness runs as you, with your GitHub sign-in, on your Mac. The real
backstops sit outside the model: the clone can't push while the harness runs, the script pushes only the work
branch, `main` on app repos 05+ needs a PR with green CI (add the ruleset to 01–04 before using them), and nothing
merges without you. Don't run the script from a folder that holds other projects, keep `~/30apps` for these clones
only, and read each PR's diff before merging.

## Sources

- Grok Build: [launch post](https://x.ai/news/grok-build-cli) (install, `-p` headless mode),
  [permissions](https://docs.x.ai/build/features/permissions),
  [permissions and safety guide](https://github.com/xai-org/grok-build/blob/main/crates/codegen/xai-grok-pager/docs/user-guide/22-permissions-and-safety.md) (`--permission-mode`, `--always-approve`,
  `--allow`/`--deny`), [community guide](https://www.codeagentswarm.com/en/guides/how-to-use-grok-build) (binary
  name, sign-in).
- Antigravity CLI: [hands-on codelab](https://codelabs.developers.google.com/antigravity-cli-hands-on) (install,
  sign-in, `-p`), [CLI reference](https://antigravity.google/docs/cli/reference/) (flags),
  [permissions](https://antigravity.google/docs/permissions.md) (rules, modes).
- Jules: [changelog](https://jules.google/docs/changelog/) (read-only after 2026-11-11, shut down 2026-12-31).
