# Run logs

Part of the **BreakthruSoftwareFactory** close-out (gate 5 in [`FACTORY.md`](../FACTORY.md)). One file per app,
`NN-slug.md`, started from [`templates/run-log.md`](../templates/run-log.md). A run log is one of the four parts of
the definition of done, and `catalog.yaml` can't say `status: done` without it (the `Check` workflow enforces this).

## The pattern

1. **Gate 1 (spec):** the planner creates `runs/NN-slug.md` from the template in the spec PR and fills in the
   header and the spec link.
2. **Gates 2–3 (build, review):** whoever opens a PR adds a row under "Who did what"; the reviewer adds its
   findings and the review link. One line each: no essays.
3. **Gate 4 (release):** devops fills in the cloud, URL, image tag, `apps.yaml` PR and the live smoke result.
4. **Gate 5 (close-out):** devops ticks the definition-of-done checklist, sets the catalog status, and notes what
   slipped. Grok Bot's drafts are noted as drafted (Michael posts them).

Write only what GitHub shows: link PRs and runs, say "unknown" rather than guess, and never paste secrets, tokens
or personal data. The AI Ops Console (app 30) reads these files to show what each agent did, what review caught,
and how the AI feature scored.

## Files

| File | What it is |
| --- | --- |
| [`retro-01-12.md`](retro-01-12.md) | Retrospective for apps 1–12, written when the factory was named (2026-11-10) |
| `01-build-tracker.md` … `04-habit-tracker.md` | Run logs reconstructed after the fact from GitHub for the four deployed apps |
| `05-budget-planner.md` … `12-restaurant-ordering.md` | Run logs written at close-out on 2026-11-13 from GitHub (PRs, reviews, deploys, live-smoke runs); apps 5, 7, 9 and 10 are `done` |
