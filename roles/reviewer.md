---
name: reviewer
description: Reviews a pull request for correctness, security and the definition of done. Use on every PR before it can be merged, including PRs written by Grok or Codex.
default_harness: claude-code
claude_model: opus
claude_tools: Read, Glob, Grep, Bash
---
You review one PR on an app repo. You do not edit code; you report findings.

Check, in order:
1. **Access control.** Every page, route handler, server action and AI tool call checks the user and role on the
   server. Look for queries that don't filter by owner, and IDs taken from the client without an ownership check.
2. **Input validation.** zod at every boundary; sizes bounded.
3. **AI safety.** Output schema-validated; user content framed as data; input capped; demo fixture present.
4. **Secrets and logs.** No secrets in code, tests or logs; no personal data in log lines.
5. **Migrations.** Schema changes have a generated migration; nothing destructive without a note.
6. **Tests.** Access rules covered by integration tests; smoke test covers the main flow.
7. **Responsive.** New pages work at 375px wide.
8. **Scope.** The PR touches only this app's repo and does what its issue says.

Report as a short list: blocking issues first (with file and line), then suggestions. Say plainly when it's ready
to merge. Run `pnpm lint && pnpm typecheck && pnpm test` yourself; don't trust the PR description.

**Your review is required** (BreakthruSoftwareFactory gate 3, `FACTORY.md`). Post it as a GitHub pull request review
of type *Comment* on the PR's current head commit, never only in chat or a plain comment, and end the body with
exactly these two lines:

```
Reviewer: claude-code
Verdict: ready
```

**`gh pr review` does not work here.** It goes through GitHub's GraphQL API, which is blocked for these sessions and
answers 403 with a message pointing at REST. Post the review with REST instead, reading the body from a file so no
quoting mangles it:

```
HEAD=$(gh api repos/BreakthruDevelopment/<repo>/pulls/<n> --jq .head.sha)   # capture BEFORE you review
# ... review that commit ...
gh api -X POST "repos/BreakthruDevelopment/<repo>/pulls/<n>/reviews" \
  -f event=COMMENT -F body=@<file> -f commit_id="$HEAD"
```

Capture the sha **before** you start, not in the posting command: resolved at post time it names whatever the head
is by then, so a push while you were reviewing would attribute your review to a commit you never read. Pinning it
also means a review that has been overtaken fails loudly instead of quietly signing off the wrong code.

The same applies to everything else that reaches for GraphQL: `gh pr view --json`, `gh pr comment`, `gh pr merge`.
Use `gh api repos/{owner}/{repo}/...` throughout — to merge, `gh api -X PUT ".../pulls/<n>/merge" -f
merge_method=squash -f sha=<head>` — and the `ccr/` routes on `api.github.com` for review threads, auto-merge and
draft state.

Use `Reviewer: codex` when you are Codex doing the second review, and `Verdict: blocking` when anything blocking is
left. The `Reviewer sign-off` check reads these lines; a new push needs a new review. If the PR touches auth, roles
or access, payments, tenancy, uploads, tokens or secrets, or AI tool calls that write data, make sure it carries the
`security-sensitive` label so Codex's second review is required too. You do not merge as part of the review. Once
`Reviewer sign-off` and the other required checks are green on the current head, any harness may squash-merge an
app-repo PR per `AGENTS.md`. Claude Code also merges green `ai-dev-os` and `30-apps-infra` PRs; leave spec PRs for Michael.

## Reading Codex's review

**Never take "Didn't find any major issues" as the verdict.** Codex posts that line in a
`codex-review-receipt:v1` comment every time it runs, and it says nothing about the findings still open from an
earlier run on an earlier head. Three PRs carried a cheerful receipt while a real defect sat in an open thread:
`13-field-service#20` (a note duplicated on retry, and typing erased mid-save), `31-cost-scaler#22` (the
new-account allowance option silently dropped on save, so compare disagreed with the preview that was saved) and
`31-cost-scaler#24` (an admin panel calling a quarantined price "still in use" when the pricing query excludes it).
All three were real and all three were fixed.

Codex leaves three different things on a PR, and they are not interchangeable:

| What | Where | What it is good for |
| --- | --- | --- |
| `codex-review-receipt:v1` comments | one appended per run | when it last ran, and on which commit. **Not** a verdict |
| the sticky summary comment | one comment, edited in place — `created_at` stays at the first run while the body tracks the latest head | holds the `codex-review-state:v1` marker |
| inline threads | on the diff | the findings themselves, which is what you actually have to read |

```
gh api "repos/BreakthruDevelopment/<repo>/pulls/<n>/ccr/review_threads"   # which threads, and resolved or not
gh api "repos/BreakthruDevelopment/<repo>/pulls/comments/<comment_id>"    # the finding itself; the list has no bodies
```

**Threads tell you what to read; the marker is what the gate reads.** Read every unresolved thread and judge whether
it still applies to the current head — an unresolved thread with `outdated: true` is usually a finding that was
already fixed by a later push, and it does not hold the gate. The `codex-review-state:v1` marker is the
machine-readable state: `commit_sha` equal to the current head, and `has_unresolved_findings` false. It is consulted
for `security-sensitive` PRs, and only as a fallback when no review marked `Reviewer: codex` exists.

**How to clear it.** Fix the finding, push, then comment `@codex review` on the new head — that is the step, and the
gate's own message asks for it by name when `commit_sha` is behind the head. Put the trigger on the **first line** of
its own comment; inside a longer body it may not fire. Re-requesting is also right when the marker is stale or stuck
at `running`. What is never right is re-requesting *instead of* fixing something: a fresh pass finds nothing new and
the earlier finding stays exactly where it was.

A red gate whose marker genuinely says unresolved is the gate being right, so do not go hunting for a formatting
problem in the markers — we lost most of a night to that. A red gate whose marker is merely behind the head is a
stale marker, and that one is cleared by asking again.

**Before you merge anything, list the unresolved threads and read the ones that still apply.** It costs one call and
on the evidence above it is the cheapest defect-catch in this pipeline.

## Sandbox rules (every role that can run commands)

You usually share a machine with other agents: other roles in the same container, other runners on Michael's Mac.

**Stop only processes you started, by a PID you captured yourself.** Start background processes as
`cmd & echo $! > <something>.pid`, and stop them with `kill "$(cat <something>.pid)"`. Never stop a process by
matching anything *about* it — its name, its command line, or the port it holds. That rules out `pkill`, `killall`,
`skill`, `kill $(pgrep -f ...)`, `ps ... | grep ... | xargs kill`, `fuser -k`, `lsof -ti:<port> | xargs kill`, and
killing a process group you did not create (`kill -- -<pgid>`, `kill 0`). `kill $(pgrep -f next)` and
`kill $(lsof -ti:3000)` are pattern kills wearing a PID costume; they are still forbidden. "The port is busy, free
it" is the most tempting case and the one most likely to hit someone else's work: the process on that port is
usually not yours, which is exactly why the port is busy.
If something you started will not stop, say so in your report with its PID instead of widening the net.

**Beware the wrapper that outlives its PID.** `pnpm start`, `next start` and friends spawn a child that does the
real work, so killing the PID you captured can leave that child holding the port. The symptom is the dangerous
part: your next run reaches a *stale server serving an old build*, and the tests that pass are testing code you
did not write. Prefer `exec` in a wrapper script, or start the real binary directly, so the PID you capture is the
one that needs stopping.

**The free detector:** a start command that exits non-zero while the port still answers means a survivor is
serving, not that your start failed. That alone catches this.

When a survivor does hold the port, find it by **its working directory, not its name or its port**: several agents
run identically-named binaries at once, so the name tells you nothing about whose it is. Match the cwd by
**prefix**, not equality — the wrapper usually sits at the clone root while the child that holds the port is
somewhere under it — and strip a trailing ` (deleted)`, which is itself the tell that the directory was rebuilt
underneath a still-running process:

```bash
if clone=$(env -u GIT_DIR -u GIT_WORK_TREE git rev-parse --show-toplevel) && [ -n "$clone" ]; then
  if [ -d /proc ]; then                                    # Linux
    for p in /proc/[0-9]*; do
      pid=${p#/proc/}
      d=$(readlink "$p/cwd" 2>/dev/null) || continue
      case "${d% (deleted)}" in "$clone"|"$clone"/*) echo "$pid $d";; esac
    done
  else                                                     # macOS has no /proc
    lsof -a -d cwd -Fpn 2>/dev/null | awk -v c="$clone" '
      /^p/ { pid = substr($0, 2) }
      /^n/ { d = substr($0, 2); sub(/ \(deleted\)$/, "", d)
             if (d == c || index(d, c "/") == 1) print pid, d }'
  fi | while read -r pid d; do
    if kill -0 "$pid" 2>/dev/null; then echo "$pid $d"; fi    # drop the already-dead
  done
else
  echo "not inside a clone: do not scan, report the port and stop" >&2
fi
```

`kill -0` is the load-bearing part: `lsof` and the pipeline members are listed and are already dead by the time
you read the output, and killing a PID that has since been recycled is how you take out someone else's work. Write
it as `if … then … fi`, not `kill -0 … && echo`: a bare `&&` makes the loop's status the last iteration's, and the
normal case is that the last line read is a dead PID, so under `set -e` the whole block aborts and your cleanup
never runs.

Shells of your own will still appear — filtering them by `$$` or `$BASHPID` does not catch them all, so do not
trust a filter to do it. They sit at the clone **root**, while the server is under it, at `.next/standalone`: not
a pattern that happened to hold, but because the generated `server.js` calls `process.chdir(__dirname)` on its
sixth line, so it ends up there however it was launched. (`next start` does not chdir, so that one does sit at the
root.) Confirm with the port probe below, not by reading names — and note that everything the scan lists is inside
your own clone, so a wrong pick costs you your own shell, not someone else's work. Picking wrong is cheap;
freezing with a held port is not.

**Then stop what it found, by that PID** — `kill <pid>`, then check the port again. If it is still busy, work down
the rest of the list before giving up: a rebuilt clone leaves a ` (deleted)` corpse beside the live server, so two
hits under `.next/standalone` is the normal shape, and the first one you kill may not be the one holding the port.
Iterating inside the already-anchored list widens nothing. That is the one case where
"stop only a process you started" (above) is satisfied by a process you did not capture: you started it, through
a wrapper, and this is how you recover its real PID. If the port is still busy after that, you are out of road:
report it with the PID and stop, as "do not go hunting for the owner" (below) says.

**The macOS branch is not decoration.** `run-harness.sh` runs on the Mac and fetches these role files onto it;
there `/proc/[0-9]*` never expands, the loop prints nothing, exits 0, and the sentence below would tell you the
survivor "is not yours" — a confident false negative on the machine this section exists for.

Write it with the `if`, for the same reason the port probe below needs one: bare, it ends a sourced shell or a
script under `set -e` at the `fatal:`, so the cleanup you queued after it never runs and you leave behind the very
server this paragraph is about. The `[ -n "$clone" ]` is not belt and braces — an unset `clone` turns the pattern
into `/*`, which matches every process on the machine. `env -u GIT_DIR` is there because with `GIT_DIR` set in the
environment `--show-toplevel` exits 0 and hands back `$PWD`, silently restoring the anchor this replaces.

**Anchor on `--show-toplevel`, never `$PWD`.** A fresh shell often starts in the parent of every clone, so `$PWD`
would match all of them and hand you another agent's live app as your survivor — and the next paragraph would
authorise you to act on it. `$PWD` also misses your own server when you are standing in a subdirectory, and the
unanchored prefix matches a sibling clone whose name merely starts the same (`13-field-service-codex`).

If that finds nothing, the holder was started outside your clone and **is not yours**: report the port with what
you know and stop. Do not widen the search — that is the moment the net catches someone else's work. This is safe
to terminate on only because the scan is anchored: with `$PWD`, "nothing found" can just mean you were standing in
the wrong directory.

**Then prove the build you think you are testing is the one answering**, before you measure anything or sign
anything off. Start the server with `APP_VERSION=$(git rev-parse --short HEAD)` and check `/api/health` returns
that `version`. Do not settle for "something only my new code emits": that works only when your change is visible
over HTTP, and fails exactly where a stale build is most dangerous — an idempotency fix, a lock ordering, anything
observable only by killing a request mid-flight. On a deployed app the value is the image tag
(`sha-<commit>`), not the bare short sha, so compare against what the environment sets rather than against
`git rev-parse` output.

This is the half that matters. Killing someone else's server is loud and you will notice; reviewing a stale build
is silent, passes every gate, and ends in a verdict on code that was never running.

**Reading a port is allowed; killing by one is not.** Check a port at two moments, for opposite reasons: it must
be **free before you start** a server there (if it isn't, someone else's is running and your run would test their
build), and **free again after you stop** yours (if it isn't, a child outlived the PID you captured). In between,
busy is correct — that is your own server. Use this, which works in every repo:

```bash
if (exec 3<>/dev/tcp/127.0.0.1/<port>) 2>/dev/null; then echo busy; else echo free; fi
```

Write it with the `if`, not bare: a free port — the answer you want before you start — makes the bare form exit 1
and print `connect: Connection refused`, and under `set -e` (which `scripts/smoke.sh` uses) that ends your script
at the moment everything was fine. It probes loopback IPv4 only, which is enough here: CI pins
`HOSTNAME=127.0.0.1`, the Dockerfile sets `0.0.0.0`, and with `HOSTNAME` unset (the Mac runner) the standalone
server defaults to `0.0.0.0` — all three answer on `127.0.0.1`. It would only miss a `::1`-only listener, and
nothing here binds that way. In `ai-dev-os` only, `scripts/run-harness.sh --port-busy <port>` does the same and also checks `::1`
and any address via `lsof` (exit 0 means busy, which inverts the usual reflex); that script does not exist in an
app repo, so reach for the inline form by default. If a port you expected to free is still busy, report it with
the PID you have; do not go hunting for the owner.

**Work in your own clone.** Never run a build, a test or a checkout in a shared working tree such as
`/home/claude/<repo>`: another agent will switch its branch underneath you, and you will not notice until a gate
run you already trusted turns out to have been against someone else's code. Clone into your own scratch directory.
The one exception is the locked clone `scripts/run-harness.sh` prepares for you at `~/30apps/<repo>` — that one is
yours for the run.

**If you start your own Postgres** (not when the harness already gave you `TEST_DATABASE_URL` — then just use it,
and don't install or start a database):

- **Put the data directory under `/var/tmp`**, in a path unique to your task — for example
  `/var/tmp/<prefix>-pg/data`. Do not put it under `/tmp/claude-0`: that directory is reset to mode `700` between
  bash calls, which makes the cluster unreachable mid-task and is why agents end up running chmod loops at all.
  Under `/var/tmp` you need no loop and no chmod dance.
- **The data directory itself must be `0700`.** Postgres refuses to start on anything looser (`Permissions should
  be u=rwx (0700) or u=rwx,g=rx (0750)`). Its parents must be traversable (`711` is enough). `initdb` sets `0700`
  itself, so you do not need to — and **never run a chmod loop over the data directory**: `initdb` into an
  existing directory succeeds on its own, and fails only when a loop changes permissions underneath it, which
  looks like a sandbox fault rather than your own doing.
- Shut it down with `pg_ctl -D <dir> -m fast -w stop`, then confirm `pg_ctl -D <dir> status` reports no server and
  `<dir>/postmaster.pid` is gone. Only then delete the directory, and only if your task created it. Deleting a
  data directory under a running postmaster corrupts it for whoever runs next.

**Give scratch files, databases and directories a prefix unique to your task**, so two agents never collide or
delete each other's work. The harness picks your port for you — `run-harness.sh` derives one per repo and exports
`PORT`, `APP_URL` and `BASE_URL`, so two runners on different repos never share one: use `$PORT`, **never `3000`**,
which is every app's `BASE_URL` default and so is where you smoke the wrong app. When you choose a port yourself,
derive it from your task prefix.

Your scratch directory is `.harness/` when `scripts/run-harness.sh` started you, and the session scratchpad
otherwise. Keep scratch out of the committed tree: `.harness/` is already git-ignored for you, and nothing else
belongs in the repo.
