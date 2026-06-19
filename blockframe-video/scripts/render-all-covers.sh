#!/usr/bin/env bash
# render-all-covers.sh — shoot EVERY cover-<ratio>.html in a dir to cover-<ratio>.png.
#
#   render-all-covers.sh [dir]        # dir defaults to .
#
# This is the fix for "the 4:3 cover got dropped": you author the cover HTML per
# ratio, then this loop renders the WHOLE set in one go — no ratio forgotten. The
# ratio→dimensions map below is the canonical BlockFrame cover sizing.
#
# Add a new ratio? Drop a cover-<name>.html and add one line to the case below.
set -euo pipefail

dir="${1:-.}"
here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$dir"

dims_for() {           # filename → "W H"
  case "$1" in
    cover-3x4.html)   echo "1080 1440" ;;   # 竖屏短视频主封面
    cover-9x16.html)  echo "1080 1920" ;;   # Shorts / 全屏竖屏
    cover-16x9.html)  echo "1920 1080" ;;   # 通用横版缩略图
    cover-16x10.html) echo "1920 1200" ;;   # B 站横版封面
    cover-4x3.html)   echo "1440 1080" ;;   # 横版 4:3
    cover-1x1.html)   echo "1080 1080" ;;   # 方图（可选）
    *)                echo "" ;;
  esac
}

shopt -s nullglob
found=0
for f in cover-*.html; do
  d="$(dims_for "$f")"
  if [ -z "$d" ]; then
    echo "⚠ skip $f — unknown ratio, add it to dims_for() in render-all-covers.sh"
    continue
  fi
  found=1
  bash "$here/render-cover.sh" "$f" "${f%.html}.png" $d
done
[ "$found" = 1 ] || { echo "✗ no cover-*.html found in $dir"; exit 1; }
echo "— all covers rendered —"
