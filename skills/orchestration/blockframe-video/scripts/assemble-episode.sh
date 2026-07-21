#!/usr/bin/env bash
# assemble-episode.sh — 章节化增量流水线的「拼接」收口。
#
#   assemble-episode.sh --segs <dir|glob> --out <file> [options]
#
# 做两件事,别的不碰:
#   1. 把各段 clip **无重编码**拼接(ffmpeg concat demuxer)。前提:各段编码参数完全一致
#      (分辨率/fps/pix_fmt/编码器/音频编码)—— 由渲染阶段从 manifest.encode 读死保证。
#   2. 可选:把持久进度条作为**最后一道 overlay** 叠上(drawbox,宽度随 t/总时长 增长)。
#      与章节解耦:改某段时长,只需重跑这一道,不必重渲下游。
#
# 片头(cover-as-intro)与 loudnorm 是流水线既有的最终步骤,在本脚本产物之后照常跑
# (见 SKILL.md「增量重建」节)。本脚本刻意只管拼接 + 进度条,保持单一职责、可测。
#
# Options:
#   --segs <dir|glob>   段 clip 目录或 glob(默认按文件名排序);或用位置参数直接列文件
#   --out <file>        输出路径(必填)
#   --no-bar            不叠进度条(纯拼接,零重编码,最快)
#   --bar-color RRGGBB  进度条颜色(默认 0F0F0F 墨黑)
#   --crf N             叠进度条时的编码 crf(默认 16)
#   --preset P          x264 preset(默认 medium)
set -euo pipefail

segs_spec=""; out=""; bar=1; color="0F0F0F"; crf=16; preset="medium"; files=()
while [ $# -gt 0 ]; do
  case "$1" in
    --segs) segs_spec="$2"; shift 2;;
    --out) out="$2"; shift 2;;
    --no-bar) bar=0; shift;;
    --bar-color) color="$2"; shift 2;;
    --crf) crf="$2"; shift 2;;
    --preset) preset="$2"; shift 2;;
    -h|--help) sed -n '2,26p' "$0"; exit 0;;
    *) files+=("$1"); shift;;
  esac
done
[ -n "$out" ] || { echo "✗ --out 必填 (assemble-episode.sh --help)"; exit 1; }

# 收集段文件
if [ ${#files[@]} -eq 0 ]; then
  if [ -d "$segs_spec" ]; then
    while IFS= read -r f; do files+=("$f"); done < <(find "$segs_spec" -maxdepth 1 -name 'seg-*.mp4' | sort)
  elif [ -n "$segs_spec" ]; then
    for f in $segs_spec; do files+=("$f"); done
  fi
fi
[ ${#files[@]} -ge 1 ] || { echo "✗ 没找到段 clip(--segs <dir|glob> 或直接列文件)"; exit 1; }
echo "拼接 ${#files[@]} 段:"; printf '  %s\n' "${files[@]}"

workdir="$(dirname "$out")"; mkdir -p "$workdir"
listfile="$(mktemp "${TMPDIR:-/tmp}/segs.XXXXXX.txt")"
for f in "${files[@]}"; do
  af="$(cd "$(dirname "$f")" && pwd)/$(basename "$f")"
  printf "file '%s'\n" "$af" >> "$listfile"
done

# 1) 无重编码拼接
body="$(mktemp "${TMPDIR:-/tmp}/body.XXXXXX.mp4")"
ffmpeg -y -f concat -safe 0 -i "$listfile" -c copy -movflags +faststart "$body" 2>/dev/null
rm -f "$listfile"

if [ "$bar" = 0 ]; then
  mv "$body" "$out"; echo "✓ 拼接完成(无进度条,零重编码)→ $out"; exit 0
fi

# 2) 进度条 overlay(一道 encode)
read -r W H < <(ffprobe -v error -select_streams v -show_entries stream=width,height -of csv=p=0 "$body" | tr ',' ' ')
DUR="$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$body")"
# BlockFrame 风格:底部墨黑细条,宽度随时间增长 + 外框
mg=$(python3 -c "print(round($W*0.03))"); bw=$(python3 -c "print(round($W-2*$W*0.03))")
bh=$(python3 -c "print(max(6,round($H*0.009)))"); by=$(python3 -c "print(round($H*0.922))")
th=$(python3 -c "print(max(3,round($H*0.0037)))")
vf="drawbox=x=${mg}:y=${by}:w='(${bw})*min(1\,t/${DUR})':h=${bh}:color=0x${color}:t=fill,drawbox=x=${mg}:y=${by}:w=${bw}:h=${bh}:color=0x${color}:t=${th}"
ffmpeg -y -i "$body" -vf "$vf" -c:v libx264 -preset "$preset" -crf "$crf" -pix_fmt yuv420p -c:a copy -movflags +faststart "$out" 2>/dev/null
rm -f "$body"
echo "✓ 拼接 + 进度条 overlay 完成 → $out (${W}x${H}, ${DUR}s)"
