#!/usr/bin/env bash
# fetch-icon.sh — download a LobeHub brand icon SVG into your project.
#
#   fetch-icon.sh <slug> [outdir]        # outdir defaults to ./assets/brand
#
# Downloads <slug>.svg plus its -color and -text variants if they exist.
# Example:  fetch-icon.sh chatglm assets/brand
#           fetch-icon.sh openai
#
# slugs come from find-icon.sh. Real slugs look like: openai, chatglm, glmv, zhipu,
# anthropic, claude, gemini, deepseek, mistral, qwen, ... (don't guess — verify with find-icon.sh).
set -euo pipefail

slug="${1:?usage: fetch-icon.sh <slug> [outdir]}"
out="${2:-assets/brand}"
mkdir -p "$out"

ver="$(curl -sSL "https://data.jsdelivr.com/v1/packages/npm/@lobehub/icons-static-svg/resolved" 2>/dev/null \
  | python3 -c "import json,sys;print(json.load(sys.stdin)['version'])" 2>/dev/null)"
[ -n "$ver" ] || { echo "✗ could not resolve package version (network?)"; exit 1; }
cdn="https://cdn.jsdelivr.net/npm/@lobehub/icons-static-svg@${ver}/icons"

got=0
for v in "" "-color" "-text"; do
  f="${slug}${v}.svg"
  tmp="$(mktemp)"
  if curl -sSL -f "${cdn}/${f}" -o "$tmp" 2>/dev/null && grep -q '<svg' "$tmp"; then
    mv "$tmp" "$out/$f"; echo "✓ $out/$f"; got=$((got+1))
  else
    rm -f "$tmp"
  fi
done
[ "$got" -gt 0 ] || { echo "✗ no icon for slug '$slug' — run find-icon.sh '$slug' to check the real slug"; exit 1; }
echo "— done. Use on a WHITE/cream chip (mono icons are black); -color for brand color, -text for the wordmark. Render a preview and eyeball it."
