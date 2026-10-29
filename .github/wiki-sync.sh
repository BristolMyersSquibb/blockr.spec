#!/usr/bin/env bash
# Keeps the wiki of BristolMyersSquibb/blockr on one line of history with main
# here. The wiki mirrors main exactly, main only moves through the merge queue,
# and the queue merges a group only after `queue` has fast-forwarded the wiki
# to it, so main is always an ancestor of the wiki. Edits made on the wiki
# itself then sit on top of main, and come into main as a fast-forward.
#
# Usage: wiki-sync.sh queue|sync|reset, run in a clone of this repo whose HEAD
# is the commit to deploy, with WIKI and SPEC set to URLs that can push to the
# wiki and to this repo.
set -euo pipefail

fetch() {
  git fetch -q "$WIKI" master && wiki=$(git rev-parse FETCH_HEAD)
  git fetch -q "$SPEC" main && main=$(git rev-parse FETCH_HEAD)
}

ancestor() { git merge-base --is-ancestor "$1" "$2"; }

# The newest commit on the wiki that main lacks and that the merge queue made.
# The queue commits as GitHub, while an edit made on the wiki is committed by
# whoever made it.
leftover() {
  git log --format='%H %ce' "$main..$wiki" |
    awk '$2 == "noreply@github.com" { print $1; exit }'
}

# Fast-forwards main to the wiki, as long as all main lacks are edits made on
# the wiki.
bring_in() {
  if ! ancestor "$main" "$wiki"; then
    echo "::error::Main is not an ancestor of the wiki, so the two need reconciling by hand."
    return 1
  fi
  local left
  left=$(leftover)
  if [ -n "$left" ]; then
    echo "::error::The wiki holds $left from a merge queue run that never reached main. Check it, then run this workflow by hand with reset."
    return 1
  fi
  git push -q "$SPEC" "$wiki:refs/heads/main"
  echo "Brought the edits made on the wiki into main."
}

fetch
case ${1-} in
queue)
  # A plain push only goes through as a fast-forward, which makes it the check
  # that the wiki holds nothing this group lacks.
  git push -q "$WIKI" HEAD:refs/heads/master && exit 0
  echo "::error::The wiki has commits this merge group lacks, so the PR has to go through the queue again."
  fetch
  bring_in || true
  exit 1
  ;;
sync)
  left=$(leftover)
  if [ "$wiki" = "$main" ]; then
    echo "The wiki and main agree."
  elif ancestor "$wiki" "$main"; then
    git push -q "$WIKI" "$main:refs/heads/master"
    echo "Pushed main to the wiki."
  elif [ -n "$left" ] &&
    [ $(($(date +%s) - $(git log -1 --format=%ct "$left"))) -lt 1800 ]; then
    # The queue may still be merging a commit it pushed this recently.
    echo "The merge queue is still merging $left."
  else
    bring_in
  fi
  ;;
reset)
  # Drops a commit that a merge queue run pushed to the wiki and then never
  # merged, as long as nothing was added on top of it.
  left=$(leftover)
  if [ -z "$left" ] || [ "$left" != "$wiki" ] || ! ancestor "$main" "$wiki"; then
    echo "::error::The wiki holds more than a commit a merge queue run left on top of main, so reset it by hand."
    exit 1
  fi
  git push -q --force-with-lease="refs/heads/master:$wiki" "$WIKI" "$main:refs/heads/master"
  echo "Reset the wiki to main."
  ;;
*)
  echo "Usage: wiki-sync.sh queue|sync|reset" >&2
  exit 2
  ;;
esac
