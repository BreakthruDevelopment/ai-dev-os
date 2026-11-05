#!/usr/bin/env bash
# Add (or update) the Build Tracker's GitHub webhook on app repos.
#
#   TRACKER_URL=https://<id>.execute-api.us-east-2.amazonaws.com scripts/add-tracker-webhook.sh 07-appointment-booking
#   TRACKER_URL=...                                              scripts/add-tracker-webhook.sh --all
#
# The webhook posts push, pull_request and workflow_run events (JSON) to $TRACKER_URL/api/webhooks/github,
# signed with the tracker's GITHUB_WEBHOOK_SECRET. Give the same value here in TRACKER_WEBHOOK_SECRET; if it
# isn't set, it is read silently from the terminal. It is never taken as an argument and never printed.
#
# Needs GitHub CLI signed in as someone who can admin the repos (Michael), and jq. Only repos carrying the
# topic 30-apps-30-days are touched. A repo that already has a hook pointing at the same URL is updated
# in place (so rerunning is safe and also rotates the secret); otherwise a hook is created.
# `--all` covers every repo listed in catalog.yaml that exists yet.
set -euo pipefail

ORG="BreakthruDevelopment"
TOPIC="30-apps-30-days"
EVENTS='["push","pull_request","workflow_run"]'
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

usage() {
  echo "Usage: TRACKER_URL=https://... $0 <repo> [<repo>...]" >&2
  echo "       TRACKER_URL=https://... $0 --all" >&2
  echo "Optional: TRACKER_WEBHOOK_SECRET (otherwise read silently; 16+ characters)" >&2
  exit 2
}

[ "$#" -ge 1 ] || usage

repos=()
if [ "$1" = "--all" ]; then
  [ "$#" -eq 1 ] || usage
  while IFS= read -r r; do repos+=("$r"); done < <(sed -n 's/^    repo: *\([^ #]*\).*/\1/p' "$HERE/../catalog.yaml")
  if [ "${#repos[@]}" -eq 0 ]; then echo "No repos found in catalog.yaml" >&2; exit 1; fi
else
  for a in "$@"; do
    case "$a" in -*) usage ;; esac
    repos+=("${a#"$ORG"/}")
  done
fi

if [ -z "${TRACKER_URL:-}" ]; then echo "TRACKER_URL is not set (the tracker's base URL)." >&2; exit 2; fi
base="${TRACKER_URL%/}"
case "$base" in
  https://*) ;;
  *) echo "TRACKER_URL must start with https://" >&2; exit 2 ;;
esac
url="$base/api/webhooks/github"

if [ -z "${TRACKER_WEBHOOK_SECRET:-}" ]; then
  if [ ! -t 0 ]; then echo "TRACKER_WEBHOOK_SECRET is not set and there is no terminal to ask on." >&2; exit 2; fi
  read -rsp "Webhook secret (the tracker's GITHUB_WEBHOOK_SECRET; input is hidden): " TRACKER_WEBHOOK_SECRET
  echo
fi
if [ "${#TRACKER_WEBHOOK_SECRET}" -lt 16 ]; then echo "The secret must be at least 16 characters." >&2; exit 2; fi
export TRACKER_WEBHOOK_SECRET  # jq reads it from the environment, so it never appears in a command line

# JSON body for GitHub. $1 = "create" adds the required hook name; updates leave it out.
body() {
  jq -n --arg url "$url" --argjson events "$EVENTS" --arg mode "$1" '
    {active: true, events: $events,
     config: {url: $url, content_type: "json", insecure_ssl: "0", secret: env.TRACKER_WEBHOOK_SECRET}}
    + (if $mode == "create" then {name: "web"} else {} end)'
}

failed=0
for repo in "${repos[@]}"; do
  case "$repo" in
    '' | *[!A-Za-z0-9._-]*) echo "skip   $repo: not a valid repo name"; failed=1; continue ;;
  esac
  full="$ORG/$repo"

  if ! gh api "repos/$full" --silent 2>/dev/null; then
    if [ "${1:-}" = "--all" ]; then echo "skip   $full: not created yet"; else echo "FAIL   $full: repo not found or not accessible"; failed=1; fi
    continue
  fi
  if ! gh api "repos/$full/topics" --jq '.names[]' 2>/dev/null | grep -qx "$TOPIC"; then
    echo "REFUSE $full: missing the topic $TOPIC"
    failed=1
    continue
  fi

  id="$(gh api --paginate "repos/$full/hooks" 2>/dev/null | jq -r --arg url "$url" '.[] | select(.config.url == $url) | .id' | head -n 1 || true)"
  if [ -n "$id" ]; then
    if body update | gh api -X PATCH "repos/$full/hooks/$id" --input - --jq .id >/dev/null; then
      echo "update $full: hook $id"
    else
      echo "FAIL   $full: could not update hook $id"; failed=1
    fi
  else
    if new="$(body create | gh api -X POST "repos/$full/hooks" --input - --jq .id)"; then
      echo "create $full: hook $new"
    else
      echo "FAIL   $full: could not create the hook"; failed=1
    fi
  fi
done

if [ "$failed" -ne 0 ]; then echo "Finished with problems." >&2; exit 1; fi
echo "Done. GitHub sends a ping on create; check it under each repo's Settings → Webhooks → Recent Deliveries."
