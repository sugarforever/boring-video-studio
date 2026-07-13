#!/usr/bin/env bash
# check-deliverables.sh — verify a video episode folder has the COMPLETE deliverable
# set, so nothing (a render, a cover ratio, a platform copy) silently goes missing.
#
#   check-deliverables.sh <episode-dir> [short|long]   # format defaults to short
#
# Exits non-zero if anything required is missing — run it before you call the job done.
set -uo pipefail

dir="${1:?usage: check-deliverables.sh <episode-dir> [short|long]}"
fmt="${2:-short}"
cd "$dir"

ok=0; miss=0
chk() {   # <glob-or-path> <label>
  local p="$1" label="$2" hit=""
  for g in $p; do [ -e "$g" ] && { hit="$g"; break; }; done
  if [ -n "$hit" ]; then printf '  ✓ %-26s %s\n' "$label" "$hit"; ok=$((ok+1));
  else printf '  ✗ %-26s MISSING (%s)\n' "$label" "$p"; miss=$((miss+1)); fi
}

echo "deliverables · $(basename "$PWD") · format=$fmt"

echo "render:"
chk "renders/*.mp4"  "成片 mp4"
chk "renders/*.srt"  "字幕 srt"

echo "covers (all ratios — none optional):"
# Both formats ship the full ratio set; only the MAIN cover differs by format.
# Covers live in covers/; the bare path is tolerated for older episodes.
chk "covers/cover-3x4.png   cover-3x4.png"    "3:4 竖屏"
chk "covers/cover-9x16.png  cover-9x16.png"   "9:16 Shorts"
chk "covers/cover-16x9.png  cover-16x9.png"   "16:9 横版"
chk "covers/cover-16x10.png cover-16x10.png"  "16:10 B站横版"
chk "covers/cover-4x3.png   cover-4x3.png"    "4:3 横版"
echo "  ↳ 深度检查（尺寸 / 平台安全区 / 证据图）：cover-design 的 check-covers.sh"

echo "platform copy:"
chk "youtube.md"  "YouTube 文案"
chk "bilibili.md" "Bilibili 文案"

echo "—"
if [ "$miss" -eq 0 ]; then
  echo "✓ complete — $ok deliverables present"
  exit 0
else
  echo "✗ incomplete — $miss missing, $ok present"
  case "$fmt" in
    short) echo "  主封面应为 cover-3x4.png（移动端竖屏）" ;;
    long)  echo "  主封面应为 cover-16x9.png（横版）" ;;
  esac
  exit 1
fi
