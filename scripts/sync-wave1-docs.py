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

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from issuelib import WAVE1_PATHS  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
BEGIN = "<!-- wave1:begin -->"
END = "<!-- wave1:end -->"

# Paths a spec protects that the guard cannot express. Hand-written; see the module docstring.
UNGUARDED = "app 17's `agent_container/core/`, where a later slice may add files but not edit them"

# BRIEFING.md is deliberately absent: its mention is inside a Markdown table cell, where a
# multi-line generated block would break the table, so it links to the generated copies instead.
DOCS = ("AGENTS.md", "FACTORY.md", "templates/spec.md", "runbooks/harnesses-on-mac.md")


def rendered() -> str:
    """One sentence naming the guarded set, then one naming what the guard cannot cover."""
    paths = ", ".join(f"`{p}`" for p in WAVE1_PATHS)
    return (
        f"The paths the pre-push guard enforces are {paths} — one list, `WAVE1_PATHS` in "
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


def main() -> int:
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
    if stale:
        print("out of date (run scripts/sync-wave1-docs.py): " + ", ".join(stale), file=sys.stderr)
    if missing or stale:
        return 1
    if check:
        print(f"wave1 doc regions ok ({len(DOCS)} files, {len(WAVE1_PATHS)} paths)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
