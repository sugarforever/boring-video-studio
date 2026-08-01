#!/usr/bin/env bash
# render-cover.sh — shoot one BlockFrame cover HTML to a crisp PNG.
#
#   render-cover.sh <cover.html> <out.png> <W> <H> [dpr]
#
# Uses system Chrome headless (no npm deps). DPR defaults to 2 → output is
# (W*dpr)×(H*dpr) physical px (true 2× supersample, not an upscale). The cover's
# own local fonts (fonts/*.woff2, font-display:block) must sit next to the HTML.
#
# Why Chrome headless and not Playwright/Puppeteer: zero install, and it's the
# same engine HyperFrames already requires (`npx hyperframes doctor`).
set -euo pipefail

html="${1:?usage: render-cover.sh <cover.html> <out.png> <W> <H> [dpr]}"
out="${2:?missing out.png}"
W="${3:?missing width}"
H="${4:?missing height}"
DPR="${5:-2}"

# locate Chrome (macOS default, then PATH, then Chromium)
CHROME=""
for c in \
  "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  "/Applications/Chromium.app/Contents/MacOS/Chromium" \
  "$(command -v google-chrome-stable 2>/dev/null || true)" \
  "$(command -v google-chrome 2>/dev/null || true)" \
  "$(command -v chromium 2>/dev/null || true)"; do
  if [ -n "$c" ] && [ -x "$c" ]; then CHROME="$c"; break; fi
done
[ -n "$CHROME" ] || { echo "✗ no Chrome/Chromium found — install Chrome (HyperFrames needs it too)"; exit 1; }

# absolute file:// URL so relative fonts/ resolve
case "$html" in /*) abs="$html";; *) abs="$PWD/$html";; esac

"$CHROME" --headless --disable-gpu --hide-scrollbars --no-sandbox \
  --force-device-scale-factor="$DPR" \
  --window-size="${W},${H}" \
  --virtual-time-budget=2000 \
  --screenshot="$out" \
  "file://$abs" >/dev/null 2>&1 || true

[ -s "$out" ] || { echo "✗ render failed: $out"; exit 1; }
echo "✓ $(basename "$out")  ${W}×${H} @${DPR}x  →  $((W*DPR))×$((H*DPR))px"
