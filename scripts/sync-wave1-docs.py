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
paths a spec protects that the guard cannot express. Today that is app 17's `agent_container/core/`, where
additions are allowed and edits are not.
"""

from __future__ import annotations

import importlib.util
import re
import subprocess
import sys
from collections.abc import Callable
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from issuelib import WAVE1_PATHS  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
BEGIN = "<!-- wave1:begin -->"
END = "<!-- wave1:end -->"

# What each guarded path is for, keyed BY PATH rather than written as a sentence.
#
# Three rounds of review went on prose that named some of these paths beside the generated list and drifted from
# it: a path dropped from WAVE1_PATHS left the sentence asserting something the list no longer said, and every
# check stayed green. Keying the note to the path removes the possibility instead of testing for it — the gloss
# is assembled from WAVE1_PATHS itself, so a path leaving the list takes its note with it, and `self_test` fails
# if a path has no note or a note has no path.
NOTES = {
    "src/lib/db/": "the Drizzle schema and its generated SQL",
    "drizzle/": "the committed migrations",
    "drizzle.config.ts": "how they are generated",
    "src/lib/auth/": "where role and permission code lives",
    "src/lib/access.ts": "the per-row access rules",
    "src/lib/access/": "the same, once they outgrow one file",
    "src/proxy.ts": "in front of every request",
    "src/middleware.ts": "likewise",
    "p2p/core/": "a Python-track repo's data layer and access rules",
    "kit/core/": "the same, in app 19",
    "erp/": "the simulated ERP's schema and seed",
    "contracts/": "a contract frozen from another app",
}

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


# The guarded list, recovered back out of the rendered paragraph. Round 10: every containment pin was
# one-directional -- `path in text` says the truth appears, never that nothing else does, so the list
# could be a SUPERSET of the truth with every check green. Appending one line to `paths` had all four
# documents enforcing `agent_container/core/` and, a sentence later, placing it outside the guard.
# Parsing it back means the comparison is a list equality in both directions, so an addition, a
# removal and a reordering each fail.
GUARDED_SEGMENT = re.compile(r"enforces, and what each is:\s*(.*?)\.\s*One list,", re.S)


def guarded_in(text: str) -> list[str] | None:
    """The paths the rendered paragraph claims are guarded, in order, or None if it cannot be read."""
    m = GUARDED_SEGMENT.search(text)
    if not m:
        return None
    return re.findall(r"`([^`]+)`\s*\(", m.group(1))


def path_like(text: str) -> list[str]:
    """Backticked tokens that name a file or directory. `claude` and `main` are not paths."""
    return [t for t in re.findall(r"`([^`]+)`", text) if "/" in t or "." in t]


def rendered() -> str:
    """The guarded set with each path's note, then what the guard cannot cover."""
    if missing := [p for p in WAVE1_PATHS if p not in NOTES]:
        # Named, not a KeyError traceback from inside the join: round 9 found the commit message
        # claiming this said which path was missing when it did not.
        raise SystemExit(f"no note in NOTES for: {', '.join(missing)} (scripts/sync-wave1-docs.py)")
    paths = "; ".join(f"`{p}` ({NOTES[p]})" for p in WAVE1_PATHS)
    return (
        f"The paths the pre-push guard enforces, and what each is: {paths}. One list, `WAVE1_PATHS` in "
        f"`scripts/issuelib.py`, mirrored by `WAVE1_RE` in `scripts/run-harness.sh`. A repo has only one of "
        f"these groups. A spec may protect more than the guard can express: today {UNGUARDED}. This paragraph "
        f"is generated by `scripts/sync-wave1-docs.py`; edit the list and the notes in those files, not here."
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


def stray_markers(listed: list[str] | None = None,
                  read: Callable[[str], str] | None = None) -> list[str]:
    """Markdown outside DOCS that carries a region nothing renders.

    `templates/spec.md` is in DOCS and carries a region, so every spec copied from it inherits one — and
    `specs/` is not rendered or checked, which would leave a marked, generated-looking, silently stale list in
    each new spec. Fail instead, and let whoever adds it decide: delete the region from that file, or add the
    file to DOCS.
    """
    reader = read if read is not None else (lambda rel: (ROOT / rel).read_text())
    out = []
    # One loop, used in production and under test. Round 8 injected a {path: text} mapping with an
    # early `return`, which meant `return []` placed just below that seam never ran the real loop and
    # stayed green -- round 7's gap, one line further down. Injecting the reader instead leaves the
    # loop body on the only path there is.
    for rel in listed if listed is not None else tracked_markdown():
        try:
            text = reader(rel)
        except (OSError, UnicodeDecodeError):
            continue
        if is_stray(rel, text):
            out.append(rel)
    return out


def classify(texts: dict[str, str] | None = None) -> tuple[list[str], list[str]]:
    """Which of DOCS carry no region, and which carry a stale one.

    `main` made this comparison inline, where `self_test` could not reach it: round 9 showed
    `stale.append(name)` -> `pass` passing every check while AGENTS.md kept a stale list.
    """
    missing, stale = [], []
    for name in DOCS:
        text = texts[name] if texts is not None else (ROOT / name).read_text()
        if BEGIN not in text:
            missing.append(name)
        elif apply(text) != text:
            stale.append(name)
    return missing, stale


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
    marked = f"a\n{BEGIN}\nb\n{END}"
    if stray_markers(listed=[DOCS[0]], read=lambda _: marked) != []:
        failures.append("stray_markers() flagged a document DOCS renders")
    # A positive case too: the negative one alone leaves `return []` passing, the same hole the
    # predicate and the walk each had, one function further in.
    if stray_markers(listed=["runs/01-x.md"], read=lambda _: marked) != ["runs/01-x.md"]:
        failures.append("stray_markers() missed a marked file outside DOCS")
    if stray_markers(listed=["runs/01-x.md"], read=lambda _: "nothing marked") != []:
        failures.append("stray_markers() flagged an unmarked file")
    # An unreadable file is skipped, not fatal: the walk may list a path that has since gone.
    def boom(_: str) -> str:
        raise OSError("gone")
    if stray_markers(listed=["runs/01-x.md"], read=boom) != []:
        failures.append("stray_markers() did not skip an unreadable file")
    # Notes and paths must correspond exactly, in both directions.
    for path in WAVE1_PATHS:
        if path not in NOTES:
            failures.append(f"{path!r} is in WAVE1_PATHS with no note in NOTES")
    for path in NOTES:
        if path not in WAVE1_PATHS:
            failures.append(f"NOTES describes {path!r}, which is not in WAVE1_PATHS")
    if not regions(f"{BEGIN}\nx\n{END}"):
        failures.append("regions() found none in a document that has one")
    # Two regions, so truncating to the first is not green. No document has two today; that is what
    # makes it worth pinning rather than what makes it safe.
    if len(regions(f"{BEGIN}\na\n{END}\nmid\n{BEGIN}\nb\n{END}")) != 2:
        failures.append("regions() did not find both regions in a document that has two")
    # rendered() itself -- the one function that writes all four documents, and the one round 9 found
    # with no assertion at all. `WAVE1_PATHS[:8]` was green while the documents claimed eight paths.
    text = rendered()
    for path in WAVE1_PATHS:
        if f"`{path}` ({NOTES[path]})" not in text:
            failures.append(f"rendered() omits {path!r} or its note")
    if UNGUARDED not in text:
        failures.append("rendered() omits the set the guard cannot express")
    # Equality, not membership: an extra path in the rendered list fails here.
    claimed = guarded_in(text)
    if claimed is None:
        failures.append("the rendered paragraph's guarded list can no longer be read back")
    elif claimed != list(WAVE1_PATHS):
        failures.append(f"the rendered paragraph claims {claimed}, not WAVE1_PATHS")
    # And the paragraph names no path outside the guard apart from the ones UNGUARDED accounts for.
    allowed = set(WAVE1_PATHS) | set(path_like(UNGUARDED)) | {
        "scripts/issuelib.py", "scripts/run-harness.sh", "scripts/sync-wave1-docs.py",
    }
    if stray_paths := sorted(set(path_like(text)) - allowed):
        failures.append(f"the rendered paragraph names paths nothing accounts for: {stray_paths}")
    # classify(), driven with text rather than the repo, so the comparison main() makes is exercised.
    fresh = f"before\n{BEGIN}\n{text}\n{END}\nafter"
    base = {name: fresh for name in DOCS}
    if classify(texts=base) != ([], []):
        failures.append("classify() flagged up-to-date documents")
    if classify(texts={**base, DOCS[0]: f"a\n{BEGIN}\nstale\n{END}"}) != ([], [DOCS[0]]):
        failures.append("classify() missed a stale region")
    if classify(texts={**base, DOCS[1]: "no region at all"}) != ([DOCS[1]], []):
        failures.append("classify() missed a document with no region")
    # The two derivations templates/spec.md asserts. Hard-coding either was green until round 9, and
    # open-issues.py carries a comment recording that this exact bug already happened once.
    runner = (ROOT / "scripts" / "run-harness.sh").read_text()
    # Inside the builder prompt, not anywhere in the file: a whole-file substring test passed while the
    # prompt carried the old hard-coded sentence and `$(wave1_list)` survived only in a comment --
    # exactly the mistake round 9 fixed one file over, repeated here.
    prompts = re.findall(r"^\s*cat <<\s*EOF\s*$(.*?)^EOF\s*$", runner, re.S | re.M)
    builder = [b for b in prompts if "You are the $3 agent" in b]
    if not builder:
        failures.append("could not find run-harness.sh's builder prompt heredoc")
    for block in builder:
        if "$(wave1_list)" not in block:
            failures.append("run-harness.sh's builder prompt no longer interpolates wave1_list")
        if hard := sorted(p for p in WAVE1_PATHS if f"`{p}`" in block or f" {p}," in block):
            failures.append(f"run-harness.sh's builder prompt hard-codes guarded paths: {hard}")
    # By value, not by name: grepping for "WAVE1_PATHS" matched the import line while `_FOUNDATION`
    # itself was hard-coded, which is how round 9's 4b stayed green through a round of fixes.
    spec_mod = importlib.util.spec_from_file_location("_oi", ROOT / "scripts" / "open-issues.py")
    if not spec_mod or not spec_mod.loader:
        # Never silently: skipping the check is itself the failure.
        failures.append("could not load open-issues.py to check its foundation note")
    else:
        oi = importlib.util.module_from_spec(spec_mod)
        try:
            spec_mod.loader.exec_module(oi)
        except BaseException as err:  # noqa: BLE001 - a broken import is itself the failure
            failures.append(f"could not import open-issues.py to check its foundation note: {err}")
        else:
            want = ", ".join(f"`{path}`" for path in WAVE1_PATHS)
            if getattr(oi, "_FOUNDATION", None) != want:
                failures.append("open-issues.py's _FOUNDATION is not derived from WAVE1_PATHS")
            for name in ("WAVE1_NOTE", "LATER_NOTE"):
                note = getattr(oi, name, "")
                if any(path not in note for path in WAVE1_PATHS):
                    failures.append(f"open-issues.py's {name} does not name every guarded path")
                # Both directions. Membership alone let `({_FOUNDATION}, `agent_container/core/`)`
                # through, which told slice 17.5's builder not to add the files its own slice owns.
                if extra := sorted(set(path_like(note)) - set(WAVE1_PATHS)):
                    failures.append(f"open-issues.py's {name} names paths outside the guard: {extra}")
    # The runner's own derivation, by value too.
    try:
        listed_out = subprocess.run(["bash", str(ROOT / "scripts" / "run-harness.sh"), "--wave1-list"],
                                    capture_output=True, text=True, check=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError) as err:
        failures.append(f"run-harness.sh --wave1-list did not run: {err}")
    else:
        if listed_out != ", ".join(WAVE1_PATHS):
            failures.append(f"run-harness.sh --wave1-list disagrees with WAVE1_PATHS: {listed_out}")
    # UNGUARDED cannot be derived, but it can be pinned: the path it names must be absent from the
    # guard (that is the whole point of it) and present in the spec it credits.
    if "agent_container/core/" in WAVE1_PATHS:
        failures.append("agent_container/core/ is in WAVE1_PATHS; the guard cannot express add-not-edit")
    spec = ROOT / "specs" / "17-agent-container.md"
    if "agent_container/core/" not in UNGUARDED:
        failures.append("UNGUARDED no longer names agent_container/core/")
    elif not spec.is_file():
        # Not `spec.is_file() and ...`: that skipped half the pin when the spec was renamed.
        failures.append("specs/17-agent-container.md is gone; UNGUARDED credits a spec that is not there")
    elif "agent_container/core/" not in spec.read_text():
        failures.append("specs/17-agent-container.md no longer protects agent_container/core/")
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
    missing, stale = classify()
    if not check:
        for name in stale:
            p = ROOT / name
            p.write_text(apply(p.read_text()))
            print(f"updated {name}")
        stale = []
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
