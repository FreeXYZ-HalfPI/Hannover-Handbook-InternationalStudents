#!/usr/bin/env bash
# Check every external link in handbook/ and print: STATUS<TAB>FINAL_URL<TAB>URL<TAB>PAGES
# Status 000 = no connection. Some sites (make-it-in-germany.com, linkedin.com)
# block automated requests; open those in a browser.
set -euo pipefail
cd "$(dirname "$0")/.."

grep -rhoE '\]\(https?://[^) ]+\)' handbook | sed -E 's/^\]\((.*)\)$/\1/' | sort -u > /tmp/handbook-urls.$$

check() {
  local u="$1" out pages
  out=$(curl -s -o /dev/null -L --max-redirs 8 --max-time 25 \
    -A 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/156 Safari/537.36' \
    -H 'Accept-Language: en,de;q=0.8' -w '%{http_code}\t%{url_effective}' "$u" || true)
  pages=$(grep -rlF "]($u)" handbook | sed 's#handbook/##' | tr '\n' ' ')
  printf '%s\t%s\t%s\n' "$out" "$u" "$pages"
}
export -f check

xargs -P 12 -I{} bash -c 'check "$@"' _ {} < /tmp/handbook-urls.$$ | sort > link-report.tsv
rm -f /tmp/handbook-urls.$$
echo "Checked $(wc -l < link-report.tsv) links -> link-report.tsv"
awk -F'\t' '$1 != "200" { print }' link-report.tsv
