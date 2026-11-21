#!/usr/bin/env bash
# Run one script's --self-test and require its result line, not merely exit 0.
#
# A self-test that exits 0 having printed NOTHING is invisible to `test $? -eq 0`: reverting one word
# (`BaseException` -> `Exception`) plus an import-time SystemExit in another script once made an
# entire self-test vanish with CI green. So the line is required, whatever causes its absence.
#
# `|| rc=$?` rather than `; rc=$?`: GitHub Actions runs a `run:` block under `bash -e`, so a bare
# assignment that fails kills the script AT the assignment -- rc, the echo and the test never run, and
# a genuine failure shows a red step with an empty log. The status is the command substitution's
# either way, which `||` preserves.
#
# This lived inline in check.yml, duplicated byte-for-byte in two steps. One copy, called from both.
set -u

name=${1:?usage: ci-self-test.sh <script name without .py>}
root=$(cd "$(dirname "$0")/.." && pwd)

rc=0
out=$(python3 "$root/scripts/$name.py" --self-test) || rc=$?
printf '%s\n' "$out"
if [ "$rc" -ne 0 ]; then
  echo "::error::scripts/$name.py --self-test failed"
  exit "$rc"
fi
printf '%s' "$out" | grep -q 'self-test ok' || {
  echo "::error::scripts/$name.py --self-test exited 0 without its result line; it did not run to the end"
  exit 1
}
