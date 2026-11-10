# Grok Build and Antigravity on Michael's Mac

How two of the BreakthruSoftwareFactory's harnesses ([`FACTORY.md`](../FACTORY.md)) get their work: gate 2 (build).
Every PR they open still needs gate 3, the required `Reviewer sign-off`, and Michael's merge.

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

# 5. A shortcut, so the runner works from any folder and keeps the Mac awake
echo 'alias run-harness="caffeinate -i ~/30apps/ai-dev-os/scripts/run-harness.sh"' >> ~/.zshrc && exec zsh
```

**A local Postgres (required).** The script refuses to start without one, because without it every integration
test skips itself and a PR can pass locally and fail in CI (that happened on the first Grok run, 2026-11-09).
Pass `--no-db-ok` to run without it anyway; the PR then says the integration tests and smoke didn't run locally.

```bash
# Either Docker Desktop, with the same image CI uses:
docker run -d --name 30apps-pg --restart unless-stopped -p 5432:5432 \
  -e POSTGRES_USER=app -e POSTGRES_PASSWORD=app -e POSTGRES_DB=app pgvector/pgvector:pg17
brew install libpq && brew link --force libpq   # psql + pg_isready, so the script can make one database per app
# or Homebrew (CI runs Postgres 17 with pgvector; postgresql@16 also works for apps that don't use pgvector):
brew install postgresql@17 pgvector && brew services start postgresql@17
createuser -s app && psql -d postgres -c "alter user app password 'app'" && createdb -O app app

# Then, in ~/.zshrc (a local-only test database, not a secret), and open a new Terminal window:
export TEST_DATABASE_URL=postgres://app:app@localhost:5432/app
```

The script checks the database answers (`pg_isready`, else `psql`, else the port), then gives each app its own
database (`app_05_budget_planner`, …) so two runners on different apps don't run each other's migrations; without
`psql` they share `app`, which is fine for one runner at a time. The harness gets it as `TEST_DATABASE_URL` and
`DATABASE_URL`, and its prompt says the integration tests must run and pass locally before the PR, and that a PR
must never say tests passed when some were skipped.

**Antigravity permission rules (required).** A headless `agy` run can't ask you anything, so it refuses any
tool call you haven't allowed: file reads and edits as well as commands. The script runs `agy` in `accept-edits`
mode and refuses to start unless `~/.gemini/antigravity-cli/settings.json` allows `read_file`, `write_file` and
`edit_file` on `~/30apps/`. Open that file and merge in this block (keep any keys already there).
**Replace `/Users/YOUR_MAC_USER` with your real home folder**: agy matches paths literally, so `~` or `$HOME`
don't work. `echo "$HOME/30apps/"` prints the exact value.

```json
{
  "permissions": {
    "allow": [
      "read_file(/Users/YOUR_MAC_USER/30apps/)",
      "write_file(/Users/YOUR_MAC_USER/30apps/)",
      "edit_file(/Users/YOUR_MAC_USER/30apps/)",
      "command(pnpm)", "command(corepack)", "command(node)", "command(npx)",
      "command(git status)", "command(git diff)", "command(git log)", "command(git show)",
      "command(git add)", "command(git commit)", "command(git restore)", "command(git rm)", "command(git mv)",
      "command(git checkout)", "command(git branch)", "command(git rev-parse)", "command(git ls-files)",
      "command(gh issue view)",
      "command(pwd)", "command(ls)", "command(cat)", "command(head)", "command(tail)", "command(echo)",
      "command(test)", "command(grep)", "command(rg)", "command(find)", "command(wc)", "command(sed)",
      "command(sort)", "command(jq)", "command(mkdir)", "command(touch)", "command(cp)", "command(mv)",
      "command(sleep)", "command(curl)", "command(psql)", "command(pg_isready)",
      "command(nohup node .next/standalone/server.js)", "command(pkill -f .next/standalone/server.js)",
      "command(bash scripts/smoke.sh)"
    ],
    "deny": [
      "command(git push)", "command(git remote)", "command(git config)", "command(git checkout main)",
      "command(gh pr)", "command(gh api)", "command(gh repo)", "command(gh secret)", "command(gh auth)",
      "command(gh label)", "command(gh issue close)", "command(gh issue edit)",
      "command(sudo)", "command(rm -rf /)", "command(rm -rf ~)", "write_file(.git/)", "edit_file(.git/)"
    ]
  }
}
```

Or add just the three file rules with `jq` (built into macOS 15+):

```bash
f=~/.gemini/antigravity-cli/settings.json; d="$HOME/30apps/"
jq --arg d "$d" '.permissions.allow = ((.permissions.allow // []) + ["read_file(\($d))","write_file(\($d))","edit_file(\($d))"] | unique)' \
  "$f" > "$f.new" && mv "$f.new" "$f"
```

Rules are `action(target)`, prefix matches word by word; deny beats allow, so `write_file(.git/)` still protects
each clone's `.git` folder ([Antigravity permissions docs](https://antigravity.google/docs/permissions.md)). Why
the commands: the prompt has the agent read files, run `pnpm` checks, commit, and run smoke the way CI does
(`cp` the static files into `.next/standalone`, start `node .next/standalone/server.js`, poll `/api/health` with
`curl`, run `scripts/smoke.sh`, then `pkill` the server). `git switch` is left out on purpose (the agent must stay
on its branch), as are push, remote, config, `gh pr` and `gh api`. The rules apply to every `agy` session on the
Mac, not just the script's.

When agy refuses something, the run log and the issue comment name the refused call (the script runs agy with
`--output-format stream-json` and reads the tool events; if no event names it, it shows agy's own notice). Add it
to `allow` if it's safe, and rerun with `--retry-failed`.

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

Run these in a **plain Terminal window**, not inside a `grok` or `agy` session: a harness inside a harness mixes
their permissions and usage limits, so the script refuses unless you pass `--allow-nested`. They work from any
folder.

```bash
git -C ~/30apps/ai-dev-os pull --ff-only                                    # latest script
caffeinate -i ~/30apps/ai-dev-os/scripts/run-harness.sh grok --dry-run      # what it would pick up, and why not the rest
caffeinate -i ~/30apps/ai-dev-os/scripts/run-harness.sh grok                # every ready grok issue, one after another
caffeinate -i ~/30apps/ai-dev-os/scripts/run-harness.sh antigravity --once  # one antigravity issue, then stop
```

With the alias from setup step 5, that's `run-harness grok --dry-run`, `run-harness grok` and so on.
`caffeinate -i` keeps the Mac awake; leave the Terminal window open. Each run appends to
`~/30apps/logs/<harness>-<date>.log`.

Two runners at once (say `grok` in one window and `antigravity` in another) are fine. Each takes a lock per repo
(`~/30apps/.locks/<repo>.lock`) and claims each issue on GitHub before working it, so they never take the same
repo or issue.

Limit it to some repos with `REPOS="06-read-later 08-loan-portal" ~/30apps/ai-dev-os/scripts/run-harness.sh grok`.
Change the time limit per issue with `HARNESS_TIMEOUT_MIN=120` (default 90) and the CI wait with `CI_WAIT_MIN`
(default 20, `0` to skip).

| Option | What it does |
| --- | --- |
| `--once` | Stop after one issue |
| `--dry-run` | List what it would work, change nothing (no database or agy settings needed) |
| `--retry-failed` | Also take issues that failed in the last 6 hours |
| `--no-db-ok` | Run without a local Postgres; PRs say the integration tests and smoke didn't run locally |
| `--allow-nested` | Run even from inside a `grok` or `agy` session |

## How to stop

- **Now:** Ctrl-C. The current issue keeps its `in-progress` label and the clone keeps the branch; see below.
- **After the current issue:** `touch ~/30apps/STOP`. The script stops before the next issue and won't start again
  until you `rm ~/30apps/STOP`.

## What the script does

Before anything else it checks: not nested inside `grok`/`agy`, `gh` signed in, the harness CLI installed, for
Antigravity the file rules in `settings.json`, and `TEST_DATABASE_URL` set and answering (unless `--no-db-ok`).
Then, for each repo tagged `30-apps-30-days` whose name is `NN-slug`:

1. Lists open issues labelled with the harness. Skips any labelled `in-progress`, any with an open PR that closes it
   (`Closes #N` in the body or a `<harness>/N-…` branch), any whose title doesn't start with a known `[role]`, any
   this harness failed on in the last 6 hours (unless `--retry-failed`), and any whose `## Dependencies` list still
   has an open issue.
2. Takes the repo's local lock, then clones it into `~/30apps/<repo>`, or fetches, checks out `main` and
   fast-forwards. **Refuses a repo whose working tree is dirty.**
3. Claims the issue: re-reads its labels, adds `in-progress`, comments "Started by <harness> on Michael's Mac" with a
   hidden claim marker (host, process id, time), then re-reads the comments. If another runner's claim came first,
   it deletes its own comment and moves on.
4. Saves the issue and the role file to `.harness/` (ignored by git), creates `<harness>/<N>-<slug>` and runs the
   harness headless with a standard prompt: read `AGENTS.md` and the role, do the issue, run `pnpm install`, `lint`,
   `typecheck`, `test` (integration tests included, which must pass) and `build`, then smoke, commit, and write the
   PR description to `.harness/pr-body.md`. **Pushing is switched off in the clone while the harness runs**, and
   it's told not to push or touch PRs. If it fails with no commits and its output ends with a network error (TLS,
   connection reset, timeout, 502/503/429, `UNAVAILABLE`), the branch is reset to `main` and it's retried twice,
   after 30 s and 120 s.
5. Checks the result: still on the work branch, at least one commit, nothing uncommitted, local `main` unchanged.
   Then it pushes only that branch (never `--force`) and opens a PR whose body starts with `Closes #N`, followed by
   the harness's summary and checks list. It removes `in-progress`, since the open PR now marks the issue as taken.
6. Waits up to 20 minutes for the PR's CI checks and comments the result on the issue (passed, failed with the
   failing check names, or still running), so a red PR shows up straight away.

**When a run ends without a PR**, the script comments on the issue once with the reason (for Antigravity, the
refused tool call) and:

- **No commits:** cleans up by itself. Any uncommitted changes are saved to `~/30apps/logs/<repo>-<N>-<time>.patch`,
  the local branch is deleted, the clone goes back to `main` and `in-progress` comes off. The issue is skipped for 6
  hours so it doesn't loop; fix the cause and rerun with `--retry-failed` to take it sooner.
- **Commits but no PR** (push or PR creation failed, or uncommitted changes on top of commits): keeps the branch
  and the label and says so. Push it and open the PR by hand, or delete the branch and remove the label to retry.
- **Local `main` changed:** keeps everything for you to inspect; nothing was pushed.

An empty local branch left over from an older run is deleted automatically the next time the issue comes up.

## What it won't do

- Push `main`, force-push, delete or rename branches or repos, merge PRs, or change settings, secrets or other
  repos. Only repos with the `30-apps-30-days` topic are touched.
- Run two issues at once in one window, or run anything on a schedule: you start it.
- Install a database, or put a key or token anywhere. The only environment it sets for the harness is
  `AI_PROVIDER=demo`, a dummy local `BETTER_AUTH_SECRET` (the same kind CI uses), `PORT=3000`, and the local test
  database as `TEST_DATABASE_URL`/`DATABASE_URL`.
- Post anything outside GitHub.

## The auto-approve trade-off

Unattended runs can't answer permission prompts, so each harness gets standing approval:

| Harness | Mode the script uses | What runs without asking | What's refused |
| --- | --- | --- | --- |
| Grok Build | `--always-approve` plus `--deny` rules | Everything, including any shell command | `git push`, `git remote`, `git config`, `gh pr`, `gh api`, `gh repo`, `gh secret`, `gh label`, `gh auth`, closing or editing issues, `sudo`, `rm -rf /…` and `~…`, reading `~/.ssh`, `~/.grok`, `~/.config/gh`, `~/.aws`, `~/.gemini` |
| Antigravity | `--mode accept-edits` plus the rules above | File reads and edits under `~/30apps/` and the allowed commands | Anything denied, and anything not allowed (headless mode can't ask) |

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
  [headless mode](https://antigravity.google/docs/cli/headless) (`stream-json` events, soft-denied tool calls),
  [permissions](https://antigravity.google/docs/permissions.md) (rules, modes).
- Jules: [changelog](https://jules.google/docs/changelog/) (read-only after 2026-11-11, shut down 2026-12-31).
