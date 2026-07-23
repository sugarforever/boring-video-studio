#!/usr/bin/env bash
# check-deliverables.sh — verify a video episode folder has the COMPLETE deliverable
# set, so nothing (a render, a cover ratio, a platform copy) silently goes missing.
#
#   check-deliverables.sh <episode-dir> [short|long] [full|finance]
#     format     defaults to short
#     cover-set  defaults to full (5 ratios); 'finance' drops 16:10 (finance-stock-video 只出 4 比例)
#
# Exits non-zero if anything required is missing — run it before you call the job done.
set -uo pipefail

dir="${1:?usage: check-deliverables.sh <episode-dir> [short|long] [full|finance]}"
fmt="${2:-short}"
cover_set="${3:-full}"
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

if [ "$cover_set" = finance ]; then
  echo "covers (finance · 4 ratios — 16:10 不出):"
else
  echo "covers (all ratios — none optional):"
fi
# Both formats ship the full ratio set; only the MAIN cover differs by format.
# Covers live in covers/; the bare path is tolerated for older episodes.
chk "covers/cover-3x4.png   cover-3x4.png"    "3:4 竖屏"
chk "covers/cover-9x16.png  cover-9x16.png"   "9:16 Shorts"
chk "covers/cover-16x9.png  cover-16x9.png"   "16:9 横版"
[ "$cover_set" = finance ] || \
  chk "covers/cover-16x10.png cover-16x10.png"  "16:10 B站横版"
chk "covers/cover-4x3.png   cover-4x3.png"    "4:3 横版"
echo "  ↳ 深度检查（尺寸 / 平台安全区 / 证据图）：cover-design 的 check-covers.sh"

echo "platform copy:"
chk "youtube.md"  "YouTube 文案"
chk "bilibili.md" "Bilibili 文案"

# 结构软校验（warn only，不计入 miss）—— 见 references/platform-copy.md
warn=0
softwarn() { printf '  ⚠ %-26s %s\n' "$1" "$2"; warn=$((warn+1)); }

# 字幕文件（章节时间就从这里来）：优先 audio/narration.srt，回退 renders/*.srt
srt=""
for c in audio/narration.srt renders/*.srt narration.srt; do
  [ -f "$c" ] && { srt="$c"; break; }
done

if [ -f youtube.md ] && grep -q '⏱ 章节' youtube.md; then
  first_ch=$(awk '/⏱ 章节/{f=1;next} f && match($0,/[0-9]+:[0-9][0-9]/){print substr($0,RSTART,RLENGTH);exit}' youtube.md)
  [ "$first_ch" != "0:00" ] \
    && softwarn "YouTube 章节" "首章应为 0:00（现为 ${first_ch:-无}）—— 结构错，见 platform-copy.md"

  # 章节时间大致对得上字幕 cue 吗（宽容差 5s，吸收片头偏移；低精度，只抓大漂移/漏重算）
  if [ -n "$srt" ]; then
    bad=$(awk -v tol=5 '
      FNR==NR {                                # pass 1: srt cue 起始秒
        if ($0 ~ /-->/) { ts=$1; gsub(/[,.].*/,"",ts); split(ts,a,":")
          if (a[3]!="") cue[++n]=a[1]*3600+a[2]*60+a[3] }
        next }
      /⏱ 章节/ { inch=1; next }                 # pass 2: youtube.md 章节
      inch && /^## / { inch=0 }
      inch && match($0,/[0-9]+:[0-9][0-9]/) {
        split(substr($0,RSTART,RLENGTH),c,":"); t=c[1]*60+c[2]
        if (t>0) { hit=0
          for (i=1;i<=n;i++) if (cue[i]>=t-tol && cue[i]<=t+tol) { hit=1; break }
          if (!hit) miss++ } }
      END { print miss+0 }
    ' "$srt" youtube.md)
    [ "${bad:-0}" -gt 0 ] \
      && softwarn "YouTube 章节" "$bad 个章节起始时间对不上字幕 cue（±5s）—— 起始时间应落在 $srt 的 cue 上，见 platform-copy.md"
  fi
fi
if [ -f bilibili.md ] && grep -q '⏱ 章节' bilibili.md; then
  softwarn "Bilibili 章节" "B 站描述通常不放章节时间戳（见平台差异表）"
fi

echo "—"
if [ "$miss" -eq 0 ]; then
  echo "✓ complete — $ok deliverables present${warn:+, $warn warning(s)}"
  exit 0
else
  echo "✗ incomplete — $miss missing, $ok present"
  case "$fmt" in
    short) echo "  主封面应为 cover-3x4.png（移动端竖屏）" ;;
    long)  echo "  主封面应为 cover-16x9.png（横版）" ;;
  esac
  exit 1
fi
