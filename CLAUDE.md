@AGENTS.md

## Claude Code specifics

- Use the subagents in `.claude/agents/` for each role; run them one at a time.
- Use Sonnet for building and Opus for planning and review (set per subagent).
- Read the app repo's own `AGENTS.md` before writing code there; it has the stack rules.
- Log each app's run in `runs/NN-slug.md`: what each role did, time taken, review findings, anything that slipped.
