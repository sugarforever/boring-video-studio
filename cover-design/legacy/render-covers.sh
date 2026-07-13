#!/usr/bin/env bash
# render-covers.sh — shoot EVERY cover-<ratio>.html in a dir to cover-<ratio>.png.
#
#   render-covers.sh [dir]        # dir defaults to .
#
# This is the fix for "the 4:3 cover got dropped": you author the cover HTML per
# ratio, then this loop renders the WHOLE set in one go — no ratio forgotten.
#
# The ratio→dimensions map lives in ratios.sh, shared with check-covers.sh, so a
# ratio can never be renderable but uncheckable. Add a ratio: drop a
# cover-<ratio>.html and add one line to dims_for() in ratios.sh.
set -euo pipefail

dir="${1:-.}"
here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=ratios.sh
source "$here/ratios.sh"
cd "$dir"

shopt -s nullglob
found=0
for f in cover-*.html; do
  r="$(ratio_of "$f")"
  d="$(dims_for "$r")"
  if [ -z "$d" ]; then
    echo "⚠ skip $f — unknown ratio '$r', add it to dims_for() in ratios.sh"
    continue
  fi
  found=1
  # shellcheck disable=SC2086
  bash "$here/render-cover.sh" "$f" "${f%.html}.png" $d
done
[ "$found" = 1 ] || { echo "✗ no cover-*.html found in $dir"; exit 1; }
echo "— all covers rendered —"
