#!/usr/bin/env bash
# gen-cover.sh — 用 codex-cli (gpt-image) 出一张封面，落盘到指定路径并校验尺寸/比例。
#
#   gen-cover.sh <out.png> <W:H> <prompt-file|-> [min-width]
#
# 例：
#   gen-cover.sh covers/cover-16x9.png 16:9 /tmp/p-h.txt 1600
#   printf '%s' "$PROMPT" | gen-cover.sh blog-images/cover.png 3:2 - 1500
#
# 为什么要 wrapper：`codex exec` 会**报告**「已保存到 ./x.png」，而它并没有。
# 内置 image_gen 总是写到 $CODEX_HOME/generated_images/<thread_id>/*.png，且不可配置。
# 所以这里用 `--json` 从事件流读 thread_id，去那个目录取图 —— thread_id 是唯一真相。
#
# 铁律：**拿不到 thread_id 就硬失败，绝不「取全局最新 PNG」兜底。**
# 实测教训：兜底会抓到另一个并发 codex 进程刚生成的无关图片，而它是合法 PNG、
# 尺寸也可能接近 —— magic 与尺寸校验全过，脚本「成功」落盘一张彻头彻尾的错图。
set -uo pipefail

out="${1:?usage: gen-cover.sh <out.png> <W:H> <prompt-file|-> [min-width]}"
ratio="${2:?missing ratio, e.g. 16:9}"
pfile="${3:?missing prompt file or -}"
minw="${4:-0}"

command -v codex >/dev/null || { echo "✗ codex CLI 不在 PATH"; exit 1; }

prompt="$([ "$pfile" = "-" ] && cat || cat "$pfile")"
[ -n "$prompt" ] || { echo "✗ 空 prompt"; exit 1; }

GEN="${CODEX_HOME:-$HOME/.codex}/generated_images"

# 比例写进第一行 —— codex 没有 --size 参数，比例只能靠 prompt 文字，模型会听。
# 末尾钉一遍「出位图、别写 SVG」：实测模型偶尔会改去生成 SVG 代码。
full="Generate an image, aspect ratio ${ratio} (high resolution).

${prompt}

Output a raster image. Do not write SVG or any code."

echo "◆ codex 出图 · ${ratio} → ${out}"
ev="$(mktemp)"; err="$(mktemp)"

# `</dev/null` 不可省：非交互环境下 codex 会读 stdin 并永久阻塞
#   （"Reading additional input from stdin..."）。
# `--skip-git-repo-check` 不可省：cwd 不是受信任的 git 目录时 codex 直接拒跑
#   （"Not inside a trusted directory..."），从 /tmp 之类的地方调用就会中招。
# stderr 留着，失败时要给人看 —— 千万别 2>/dev/null 把真正的错误吞掉。
codex exec --json -s read-only --skip-git-repo-check "$full" </dev/null >"$ev" 2>"$err"
rc=$?

thread="$(grep -o '"thread_id"[[:space:]]*:[[:space:]]*"[^"]*"' "$ev" 2>/dev/null | head -1 | sed 's/.*"\([^"]*\)"$/\1/')"

if [ -z "$thread" ]; then
  echo "✗ 没读到 thread_id —— codex 没有正常出图。**不做兜底**：「取全局最新 PNG」"
  echo "  会抓到别的并发进程的图，而且能骗过 PNG magic 与尺寸校验。"
  echo "  ── codex exit=${rc}，stderr："
  sed 's/^/     /' "$err" | head -12
  echo "  常见原因：cwd 非 git 目录且未加 --skip-git-repo-check / 未登录 /"
  echo "            模型改去写 SVG / 涉及真实商标被拒 / 超时。"
  rm -f "$ev" "$err"; exit 1
fi
rm -f "$ev" "$err"

dir="$GEN/$thread"
[ -d "$dir" ] || { echo "✗ thread=$thread 但 $dir 不存在 —— 本次调用没有生成图片（模型可能改去写 SVG 或被拒）"; exit 1; }

src="$(find "$dir" -type f -name '*.png' 2>/dev/null | sort | tail -1)"
[ -n "${src:-}" ] && [ -f "$src" ] || { echo "✗ $dir 里没有 PNG —— 本次调用没有生成图片"; exit 1; }

# PNG 合法性校验。别用 `od -An -tx1`：macOS 与 GNU 输出格式不同，会把合法 PNG 误判成非法。
file -b "$src" | grep -q "^PNG image data" || { echo "✗ $src 不是合法 PNG"; exit 1; }

mkdir -p "$(dirname "$out")"
cp "$src" "$out"

# 真实像素校验（模型给最接近的整数尺寸，不是数学精确比例）
if command -v sips >/dev/null; then
  w=$(sips -g pixelWidth  "$out" 2>/dev/null | awk '/pixelWidth/{print $2}')
  h=$(sips -g pixelHeight "$out" 2>/dev/null | awk '/pixelHeight/{print $2}')
  echo "  ✓ ${out}  ${w}×${h}"
  if [ "$minw" -gt 0 ] && [ "${w:-0}" -lt "$minw" ]; then
    echo "  ⚠ 宽度 ${w} < 要求的 ${minw} —— 平台会嫌糊，重出或换比例"
  fi
  rw="${ratio%%:*}"; rh="${ratio##*:}"
  if command -v bc >/dev/null && [ -n "${w:-}" ] && [ -n "${h:-}" ] && [ "$rh" -ne 0 ]; then
    dev=$(echo "scale=4; want=$rw/$rh; got=$w/$h; d=(got-want)/want; if(d<0) d=-d; d" | bc 2>/dev/null)
    [ "$(echo "$dev > 0.03" | bc 2>/dev/null)" = "1" ] &&
      echo "  ⚠ 实际比例偏离目标 >3% —— 居中裁切到目标比例（别拉伸），或重出"
  fi
else
  echo "  ✓ ${out}（无 sips，未校验尺寸）"
fi

echo "  ⤷ 源：$src  (thread=$thread)"
echo "  ⚠ 必做：Read 这张图，逐字核对标题/副标题清晰无错。错了就改 prompt 重出，"
echo "     绝不在位图上盖字修字。关键文字还要避开右下时长徽标区、落在竖版 1:1 中心方框内。"
