#!/usr/bin/env bash
# check-covers.sh — verify a covers/ dir is complete, correctly sized, and safe
# against the two things that silently ruin a video cover:
#
#   1. a missing ratio            (you shipped 16:9 and forgot 4:3)
#   2. platform chrome eating it  (the duration pill sits on your subtitle;
#                                  the 主页 grid center-crops your title away)
#
#   check-covers.sh [covers-dir] [short|long]     # dir defaults to ., format to short
#
# Exits non-zero on any ✗. Warnings (⚠) don't fail the run but MUST be looked at.
#
# What this script cannot do is judge whether the cover is any good. It writes
# proof sheets to .cover-check/ — a 240px thumbnail (mobile grid size) and a 1:1
# center crop (主页 grid) per cover. READ THOSE IMAGES. A cover that survives the
# scripted checks and fails the 240px read is still a broken cover.
set -uo pipefail

dir="${1:-.}"
fmt="${2:-short}"
here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=ratios.sh
source "$here/ratios.sh"
cd "$dir"

ok=0; miss=0; warn=0
pass() { printf '  ✓ %-24s %s\n' "$1" "$2"; ok=$((ok+1)); }
fail() { printf '  ✗ %-24s %s\n' "$1" "$2"; miss=$((miss+1)); }
warm() { printf '  ⚠ %-24s %s\n' "$1" "$2"; warn=$((warn+1)); }

case "$fmt" in
  short) main=3x4  ;;
  long)  main=16x9 ;;
  *) echo "✗ format must be short|long, got '$fmt'"; exit 2 ;;
esac

have_py=0
python3 - <<'EOF' >/dev/null 2>&1 && have_py=1
from PIL import Image  # noqa
EOF

echo "covers · $(basename "$PWD") · format=$fmt · main=cover-$main.png"
rm -rf .cover-check && mkdir -p .cover-check

for r in "${REQUIRED_RATIOS[@]}"; do
  png="cover-$r.png"
  read -r W H <<<"$(dims_for "$r")"

  if [ ! -s "$png" ]; then
    fail "$r" "MISSING ($png)"
    continue
  fi

  if [ "$have_py" = 1 ]; then
    # size + pill-corner quietness + proof sheets, in one pass
    out="$(python3 "$here/_inspect.py" "$png" "$W" "$H" "$PILL_W" "$PILL_H" \
            "$(printf '%s\n' "${PILL_RATIOS[@]}" | grep -qx "$r" && echo 1 || echo 0)" \
            ".cover-check")" || { fail "$r" "inspect failed"; continue; }
    status="${out%%|*}"; msg="${out#*|}"
    case "$status" in
      ok)   pass "$r" "$msg" ;;
      warn) pass "$r" "${msg%%;;*}"; warm "$r pill zone" "${msg#*;;}" ;;
      *)    fail "$r" "$msg" ;;
    esac
  else
    pass "$r" "$png (present; install Pillow for size + safe-area checks)"
  fi
done

[ -s "cover-$main.png" ] || fail "main cover" "format=$fmt 要求 cover-$main.png"

echo "—"
if [ "$have_py" = 1 ]; then
  echo "proof sheets → .cover-check/  (Read each *-240.png and *-1x1.png before you call it done)"
else
  echo "⚠ python3 + Pillow not found — size, safe-area, and proof sheets were SKIPPED."
fi

if [ "$miss" -eq 0 ]; then
  echo "✓ complete — $ok covers, $warn warning(s)"
  exit 0
fi
echo "✗ incomplete — $miss missing/bad, $ok ok, $warn warning(s)"
exit 1
