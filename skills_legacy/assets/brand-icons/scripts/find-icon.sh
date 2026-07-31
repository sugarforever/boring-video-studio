#!/usr/bin/env bash
# find-icon.sh — search LobeHub Icons (AI/LLM/company brand logos) by keyword.
#
#   find-icon.sh <keyword>          # e.g. glm, openai, anthropic, gemini, deepseek
#
# Lists matching icon slugs from @lobehub/icons-static-svg (served via jsDelivr).
# Each brand usually has 3 variants: <slug>.svg (mono), <slug>-color.svg, <slug>-text.svg.
# Pass a slug to fetch-icon.sh to download it.
#
# Note: the human page https://lobehub.com/icons/<slug> is behind Vercel bot-check
# (WebFetch returns 403) — this script goes straight to the package file index instead.
set -euo pipefail

kw="${1:?usage: find-icon.sh <keyword>}"
kw_lc="$(printf '%s' "$kw" | tr '[:upper:]' '[:lower:]')"

ver="$(curl -sSL "https://data.jsdelivr.com/v1/packages/npm/@lobehub/icons-static-svg/resolved" 2>/dev/null \
  | python3 -c "import json,sys;print(json.load(sys.stdin)['version'])" 2>/dev/null)"
[ -n "$ver" ] || { echo "✗ could not resolve package version (network?)"; exit 1; }

curl -sSL "https://data.jsdelivr.com/v1/packages/npm/@lobehub/icons-static-svg@${ver}?structure=flat" 2>/dev/null \
  | python3 -c "
import json,sys
kw='''$kw_lc'''
files=[f['name'] for f in json.load(sys.stdin).get('files',[])]
hits=sorted(set(f for f in files if f.startswith('/icons/') and kw in f.lower()))
if not hits:
    print('no match for \"$kw\" — try a shorter/different keyword'); sys.exit()
print('matches (@lobehub/icons-static-svg@%s):'%'$ver')
for h in hits: print('  '+h)
print()
print('→ fetch with:  fetch-icon.sh <slug>   (slug = filename without /icons/ and .svg)')
"
