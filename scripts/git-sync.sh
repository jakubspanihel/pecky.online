#!/bin/sh
# Fetch/push na GitHub s tokenem z .github-pat (token se nikdy nevypisuje).
#   scripts/git-sync.sh fetch   stáhne origin/main, vypíše HEAD..origin/main a origin/main..HEAD
#   scripts/git-sync.sh push    fetch + push main (bez force; při rozešlé historii skončí chybou) + fetch
set -eu
cd "$(dirname "$0")/.."
PAT=$(tr -d '\r\n' < .github-pat)
URL="https://x-access-token:${PAT}@github.com/jakubspanihel/pecky.online.git"
mask() { sed -e "s|${PAT}|***|g"; }

do_fetch() {
  git fetch "$URL" main:refs/remotes/origin/main --force 2>&1 | mask || true
}

report() {
  echo "--- na GitHubu a lokálně ne (HEAD..origin/main):"
  git log --oneline HEAD..origin/main
  echo "--- lokálně a na GitHubu ne (origin/main..HEAD):"
  git log --oneline origin/main..HEAD
}

case "${1:-}" in
  fetch)
    do_fetch
    report
    ;;
  push)
    do_fetch
    if [ -n "$(git log --oneline HEAD..origin/main)" ]; then
      echo "CHYBA: na GitHubu jsou commity, které lokálně nejsou — nepushuji. Nejdřív git merge origin/main."
      report
      exit 1
    fi
    git push "$URL" main 2>&1 | mask
    do_fetch
    report
    ;;
  *)
    echo "použití: scripts/git-sync.sh fetch|push" >&2
    exit 2
    ;;
esac
