#!/usr/bin/env python3
"""Generate Claude Code subagents (.claude/agents/*.md) from the harness-neutral roles in roles/.

roles/ is the single source of truth. Every harness reads the role files directly (Codex, Grok Build and
Antigravity via AGENTS.md); Claude Code needs them in its own subagent format, which this script produces.

    python3 scripts/sync-claude-agents.py          # write .claude/agents/
    python3 scripts/sync-claude-agents.py --check  # exit 1 if .claude/agents/ is out of date (used in CI)
"""
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
ROLES = ROOT / "roles"
OUT = ROOT / ".claude" / "agents"


def parse(path: pathlib.Path) -> tuple[dict[str, str], str]:
    match = re.match(r"^---\n(.*?)\n---\n(.*)$", path.read_text(), re.S)
    if not match:
        sys.exit(f"{path}: missing front matter")
    meta = dict(line.split(": ", 1) for line in match.group(1).splitlines() if ": " in line)
    for key in ("name", "description", "claude_model", "claude_tools"):
        if key not in meta:
            sys.exit(f"{path}: front matter needs '{key}'")
    return meta, match.group(2)


def render(meta: dict[str, str], body: str) -> str:
    return (
        "---\n"
        f"name: {meta['name']}\n"
        f"description: {meta['description']}\n"
        f"tools: {meta['claude_tools']}\n"
        f"model: {meta['claude_model']}\n"
        "---\n"
        "<!-- Generated from roles/" + meta["name"] + ".md by scripts/sync-claude-agents.py. Edit the role, not this file. -->\n\n"
        + body.lstrip("\n")
    )


def main() -> None:
    check = "--check" in sys.argv
    expected = {}
    for path in sorted(ROLES.glob("*.md")):
        meta, body = parse(path)
        expected[OUT / f"{meta['name']}.md"] = render(meta, body)

    stale = [p for p, text in expected.items() if not p.exists() or p.read_text() != text]
    extra = [p for p in OUT.glob("*.md") if p not in expected] if OUT.exists() else []

    if check:
        for p in stale + extra:
            print(f"out of date: {p.relative_to(ROOT)}")
        sys.exit(1 if stale or extra else 0)

    OUT.mkdir(parents=True, exist_ok=True)
    for p in extra:
        p.unlink()
    for p, text in expected.items():
        p.write_text(text)
    print(f"wrote {len(expected)} subagents to {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
