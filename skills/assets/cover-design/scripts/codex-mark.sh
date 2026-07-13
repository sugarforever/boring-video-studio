#!/usr/bin/env bash
# codex-mark.sh — generate ONE bespoke mark (glyph / mascot) via codex-cli's
# built-in image_gen, and land it where you asked, verified.
#
#   codex-mark.sh --out marks/nanoclaw.png --prompt-file prompts/nanoclaw.md [--transparent]
#   codex-mark.sh --out marks/x.png --prompt "a monoline crab holding a wrench" [--timeout 420]
#
# WHY THIS EXISTS
# ---------------
# `codex exec` will happily report "saved to ./mark.png" when it did no such
# thing. The built-in image_gen tool ALWAYS writes to
#     $CODEX_HOME/generated_images/<thread_id>/*.png
# and cannot be told otherwise. The agent is then asked to copy the file, which
# it may skip, botch, or hallucinate. Earlier notes in this repo concluded from
# that behaviour that "codex 图片工具此环境不可用" — the tool works fine; the
# reporting doesn't.
#
# So: we never trust the agent's claimed path. We read the thread_id off the
# --json event stream, pull the newest PNG out of that thread's own directory,
# and verify it ourselves.
#
# SCOPE — read this before reaching for it
# ----------------------------------------
# This is for the ONE case where the mark slot needs a bespoke glyph: no official
# logo in `brand-icons`, and the topic suggests no diagram. Everything else on a
# cover — titles, numbers, logos, charts, org trees — is HTML. Diffusion models
# garble CJK and invent logos. Do not ask this script for a whole cover.
set -euo pipefail

out=""; prompt=""; promptfile=""; timeout=420; transparent=0; key="#00ff00"
while [ $# -gt 0 ]; do
  case "$1" in
    --out)         out="$2"; shift 2 ;;
    --prompt)      prompt="$2"; shift 2 ;;
    --prompt-file) promptfile="$2"; shift 2 ;;
    --timeout)     timeout="$2"; shift 2 ;;
    --transparent) transparent=1; shift ;;
    --key)         key="$2"; shift 2 ;;
    -h|--help)     sed -n '2,30p' "$0"; exit 0 ;;
    *) echo "✗ unknown arg: $1" >&2; exit 2 ;;
  esac
done

[ -n "$out" ] || { echo "✗ --out is required" >&2; exit 2; }
command -v codex >/dev/null || { echo "✗ codex CLI not on PATH — install it, or draw the mark in HTML/SVG instead" >&2; exit 3; }

if [ -n "$promptfile" ]; then
  [ -s "$promptfile" ] || { echo "✗ prompt file not found: $promptfile" >&2; exit 2; }
  prompt="$(cat "$promptfile")"
fi
[ -n "$prompt" ] || { echo "✗ one of --prompt / --prompt-file is required" >&2; exit 2; }

CODEX_DIR="${CODEX_HOME:-$HOME/.codex}"
GEN="$CODEX_DIR/generated_images"

# House-style constraints. The mark has to sit next to real brand logos without
# looking like it wandered in from a different poster.
house="
Style constraints (hard):
- Flat monoline vector-style mark. Uniform stroke weight. No gradients, no
  shadows, no 3D, no bevels, no glow, no photographic texture.
- A single centered subject with generous padding. Nothing bleeds off the edges.
- No text, no letters, no numbers, no words anywhere in the image.
- No existing company logo, wordmark, or trademarked symbol.
- Square 1:1 composition."

if [ "$transparent" = 1 ]; then
  house="$house
- The background is a perfectly flat solid $key chroma-key field: one uniform
  color, no shadows, gradients, texture, reflections, floor plane, or lighting
  variation. Do not use $key anywhere in the subject itself."
else
  house="$house
- The background is a flat solid near-white #FFFDF5 field, edge to edge."
fi

tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT
log="$tmp/events.jsonl"

echo "→ codex image_gen · ${timeout}s budget"
set +e
timeout_bin="$(command -v gtimeout || command -v timeout || true)"
runner=(codex exec --json -C "$tmp" -s workspace-write --skip-git-repo-check
        "Use your image generation tool exactly once to create this image.

$prompt
$house

Generate the image and stop. Do not write SVG, HTML, or canvas code. Do not
report a file path.")
if [ -n "$timeout_bin" ]; then "$timeout_bin" "$timeout" "${runner[@]}" >"$log" 2>&1
else "${runner[@]}" >"$log" 2>&1; fi
rc=$?
set -e

thread="$(sed -n 's/.*"thread_id":"\([^"]*\)".*/\1/p' "$log" | head -1)"
if [ -z "$thread" ]; then
  echo "✗ no thread_id in codex output (rc=$rc). Is \`codex login\` still valid?" >&2
  tail -5 "$log" >&2
  exit 4
fi

# The ONLY source of truth. Newest PNG in this thread's own directory.
src="$(find "$GEN/$thread" -type f -name '*.png' 2>/dev/null | sort | tail -1)"
if [ -z "$src" ]; then
  echo "✗ codex produced no image in $GEN/$thread (rc=$rc)" >&2
  echo "  common causes: the model refused, or it emitted SVG instead. Check:" >&2
  sed -n 's/.*"type":"agent_message","text":"\(.\{0,160\}\).*/  agent said: \1/p' "$log" | tail -2 >&2
  exit 5
fi

mkdir -p "$(dirname "$out")"
if [ "$transparent" = 1 ]; then
  helper="$CODEX_DIR/skills/.system/imagegen/scripts/remove_chroma_key.py"
  if [ -f "$helper" ]; then
    python3 "$helper" --input "$src" --out "$out" \
      --auto-key border --soft-matte --transparent-threshold 12 \
      --opaque-threshold 220 --despill >/dev/null
  else
    echo "⚠ remove_chroma_key.py not found — keeping the $key background" >&2
    cp "$src" "$out"
  fi
else
  cp "$src" "$out"
fi

# Verify the artifact rather than believing anyone about it.
python3 - "$out" <<'PY'
import sys
from PIL import Image
p = sys.argv[1]
with open(p, 'rb') as f:
    if f.read(8) != b'\x89PNG\r\n\x1a\n':
        sys.exit(f"✗ not a PNG: {p}")
im = Image.open(p); im.load()
print(f"✓ {p}  {im.size[0]}×{im.size[1]}  {im.mode}")
PY

echo "  thread $thread · source $src"
echo "  → now Read the PNG. If the mark is wrong, fix the prompt and re-run; never paint over it."
