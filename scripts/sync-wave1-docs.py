#!/usr/bin/env python3
"""Render the foundation-path list into the human-facing docs from `WAVE1_PATHS`.

Why this exists. The list lived in prose in nine places. `WAVE1_PATHS` (`issuelib.py`) and
`WAVE1_RE` (`run-harness.sh`) are coupled by a self-test and have never drifted; the prose copies
were coupled by nothing and drifted four rounds running, each time with a reviewer catching it
rather than CI. Adding a path to both matchers left every prose copy stale and the checks green.

So the prose is generated too. Each doc carries a marked region:

    <!-- wave1:begin --> ...generated... <!-- wave1:end -->

`--check` fails when a region is out of date, and `check.yml` runs it. The builder-facing copies
are handled differently and on purpose: the role files name no paths at all, the runner
interpolates `WAVE1_RE` into its prompt, and the issue note is derived in `open-issues.py`. This
script is only for the documents people read without a Python interpreter.

The deliberately-unguarded set is written by hand below, because no list can derive it: it is the
paths a spec protects that the guard cannot express. Today that is app 17's `core/`, where
additions are allowed and edits are not.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from issuelib import WAVE1_PATHS  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
BEGIN = "<!-- wave1:begin -->"
END = "<!-- wave1:end -->"

# Paths the gloss below refers to by name. Every one must be in WAVE1_PATHS, and `self_test` asserts it: the
# gloss is prose beside a generated list, so without that a path dropped from the list leaves the sentence
# asserting something the list no longer says.
GLOSS_AUTH = "src/lib/auth/"
GLOSS_FRONT = ("src/proxy.ts", "src/middleware.ts")

# Paths a spec protects that the guard cannot express. Hand-written; see the module docstring.
UNGUARDED = (
    "app 17's `agent_container/core/`, where a later slice may add files but not edit them. That distinction "
    "is why the path is outside the guard and must stay outside it: `wave1_files` matches on path prefix and "
    "`git diff --name-only` lists an addition exactly like an edit, so adding the path would refuse slice 17.5's "
    "push and strand its branch"
)

# BRIEFING.md is deliberately absent: its mention is inside a Markdown table cell, where a
# multi-line generated block would break the table, so it links to the generated copies instead.
DOCS = ("AGENTS.md", "FACTORY.md", "templates/spec.md", "runbooks/harnesses-on-mac.md")


def rendered() -> str:
    """One sentence naming the guarded set, then one naming what the guard cannot cover."""
    paths = ", ".join(f"`{p}`" for p in WAVE1_PATHS)
    front = " and ".join(f"`{p}`" for p in GLOSS_FRONT)
    return (
        f"The paths the pre-push guard enforces are {paths} — role and permission code lives in "
        f"`{GLOSS_AUTH}`, and {front} sit in front of every request on the Next.js template, while on the "
        f"Python track a repo's `core/` package holds its data layer and access rules, `erp/` its schema and "
        f"seed, and `contracts/` a contract frozen from another app. One list, `WAVE1_PATHS` in "
        f"`scripts/issuelib.py`, mirrored by `WAVE1_RE` in `scripts/run-harness.sh`. A spec may "
        f"protect more than the guard can express: today {UNGUARDED}. This paragraph is generated "
        f"by `scripts/sync-wave1-docs.py`; edit the list in `issuelib.py`, not here."
    )


def regions(text: str) -> list[tuple[int, int]]:
    out, at = [], 0
    while True:
        b = text.find(BEGIN, at)
        if b < 0:
            return out
        e = text.find(END, b)
        if e < 0:
            raise SystemExit(f"a {BEGIN} has no matching {END}")
        out.append((b, e + len(END)))
        at = e + len(END)


def apply(text: str) -> str:
    body = f"{BEGIN}\n{rendered()}\n{END}"
    for b, e in reversed(regions(text)):
        text = text[:b] + body + text[e:]
    return text


def is_stray(rel: str, text: str) -> bool:
    """Whether this file carries a region nothing renders. Split out so `self_test` can reach it."""
    return BEGIN in text and rel not in DOCS


def tracked_markdown() -> list[str]:
    """Every tracked `.md` path, relative to the repo root.

    Split out so `self_test` can assert the traversal returns something: pinning only the predicate left
    `return []` here passing, which is how round 6's gap moved one function outward.
    """
    try:
        return sorted(subprocess.run(["git", "-C", str(ROOT), "ls-files", "*.md"],
                                     capture_output=True, text=True, check=True).stdout.split())
    except (OSError, subprocess.CalledProcessError):
        # No git here. A walk instead, skipping dotted directories and node_modules -- not equivalent, since a
        # tracked file under a dotted directory is missed, so this is the degraded path and not a substitute.
        return sorted(p.relative_to(ROOT).as_posix() for p in ROOT.rglob("*.md")
                      if not any(part.startswith(".") or part == "node_modules"
                                 for part in p.relative_to(ROOT).parts[:-1]))


def stray_markers(listed: list[str] | None = None) -> list[str]:
    """Markdown outside DOCS that carries a region nothing renders.

    `templates/spec.md` is in DOCS and carries a region, so every spec copied from it inherits one — and
    `specs/` is not rendered or checked, which would leave a marked, generated-looking, silently stale list in
    each new spec. Fail instead, and let whoever adds it decide: delete the region from that file, or add the
    file to DOCS.
    """
    out = []
    for rel in sorted(listed if listed is not None else tracked_markdown()):
        f = ROOT / rel
        if f.is_file() and is_stray(rel, f.read_text()):
            out.append(rel)
    return out


def self_test() -> int:
    """Pin the mutations that otherwise pass vacuously -- one per guard, including the stray check."""
    failures = []
    if not is_stray("runs/01-x.md", f"a\n{BEGIN}\nb"):
        failures.append("is_stray() missed a region outside DOCS")
    if is_stray(DOCS[0], f"a\n{BEGIN}\nb"):
        failures.append("is_stray() flagged a document DOCS renders")
    if is_stray("runs/01-x.md", "no region here"):
        failures.append("is_stray() flagged a file with no region")
    # The traversal, not only the predicate: round 6 pinned `is_stray` and `return []` at the top of the walk
    # stayed green, so the gap moved one function outward. Injecting the list reaches it.
    listed = tracked_markdown()
    if not listed:
        failures.append("tracked_markdown() returned nothing")
    for required in ("AGENTS.md", "FACTORY.md"):
        if required not in listed:
            failures.append(f"tracked_markdown() missed {required}")
    if stray_markers(listed=[DOCS[0]]) != []:
        failures.append("stray_markers() flagged a document DOCS renders")
    # The gloss names paths in prose beside the generated list; they must still be in it.
    for named in (GLOSS_AUTH, *GLOSS_FRONT):
        if named not in WAVE1_PATHS:
            failures.append(f"the gloss names {named!r}, which is no longer in WAVE1_PATHS")
    if not regions(f"{BEGIN}\nx\n{END}"):
        failures.append("regions() found none in a document that has one")
    marked = f"a\n{BEGIN}\nstale\n{END}\nb"
    if apply(marked) == marked:
        failures.append("apply() left a stale region unchanged")
    if BEGIN not in apply(marked) or "stale" in apply(marked):
        failures.append("apply() did not replace the region body")
    if apply(apply(marked)) != apply(marked):
        failures.append("apply() is not idempotent")
    try:
        regions(f"{BEGIN}\nno end here")
    except SystemExit:
        pass
    else:
        failures.append("an unterminated region did not raise")
    if failures:
        print("sync-wave1-docs self-test FAILED:")
        for f in failures:
            print("  " + f)
        return 1
    print(f"sync-wave1-docs self-test ok ({len(DOCS)} docs, {len(WAVE1_PATHS)} paths)")
    return 0


def main() -> int:
    if "--self-test" in sys.argv:
        return self_test()
    check = "--check" in sys.argv
    stale, missing = [], []
    for name in DOCS:
        p = ROOT / name
        text = p.read_text()
        if BEGIN not in text:
            missing.append(name)
            continue
        want = apply(text)
        if want == text:
            continue
        if check:
            stale.append(name)
        else:
            p.write_text(want)
            print(f"updated {name}")
    if missing:
        print("no wave1 region in: " + ", ".join(missing), file=sys.stderr)
    if stray := stray_markers():
        print("a wave1 region in a file nothing renders: " + ", ".join(stray), file=sys.stderr)
        missing.extend(stray)
    if stale:
        print("out of date (run scripts/sync-wave1-docs.py): " + ", ".join(stale), file=sys.stderr)
    if missing or stale:
        return 1
    if check:
        print(f"wave1 doc regions ok ({len(DOCS)} files, {len(WAVE1_PATHS)} paths)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
