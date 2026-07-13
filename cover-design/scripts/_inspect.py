#!/usr/bin/env python3
"""_inspect.py — one cover in, one status line out. Called by check-covers.sh.

    _inspect.py <png> <logical_W> <logical_H> <pill_w> <pill_h> <has_pill> <proof_dir>

Prints  "ok|msg"  /  "warn|msg;;detail"  /  "bad|msg"  and exits 0.

Three jobs:

1. SIZE. The PNG must be an exact integer multiple of the logical size (we shoot
   at 2× DPR). Off-ratio means someone hand-edited a template's width/height and
   the platform will letterbox or crop it.

2. PILL ZONE. YouTube and Bilibili stamp a duration badge over the bottom-right
   of a landscape thumbnail. Anything you put there is gone. We measure how much
   ink sits in that corner and warn. The measurement insets 4% from the canvas
   edge first, so the cover's own border frame isn't counted as content.

3. PROOF SHEETS. A 240px-wide thumbnail (mobile feed size) and a 1:1 center crop
   (how 抖音 / 视频号 / 小红书 主页 grids display a cover). These exist to be LOOKED
   at — no script can tell you a title stopped being readable.
"""
import os
import sys

from PIL import Image


def pixels(im):
    """RGB tuples without Image.getdata(), which Pillow 14 removes."""
    raw = im.tobytes()
    return (tuple(raw[i:i + 3]) for i in range(0, len(raw), 3))

png, W, H, pill_w, pill_h, has_pill, proof = sys.argv[1:8]
W, H, has_pill = int(W), int(H), has_pill == "1"
pill_w, pill_h = float(pill_w), float(pill_h)

im = Image.open(png).convert("RGB")
w, h = im.size

# ── 1. size ────────────────────────────────────────────────────────────────────
if w % W or h % H or (w // W) != (h // H):
    print(f"bad|{w}×{h} is not an integer multiple of {W}×{H}")
    sys.exit(0)
dpr = w // W
msg = f"{w}×{h} @{dpr}x"

# ── 3. proof sheets ────────────────────────────────────────────────────────────
stem = os.path.splitext(os.path.basename(png))[0]
im.resize((240, max(1, round(240 * h / w))), Image.LANCZOS).save(f"{proof}/{stem}-240.png")
side = min(w, h)
im.crop(((w - side) // 2, (h - side) // 2, (w + side) // 2, (h + side) // 2)) \
  .resize((320, 320), Image.LANCZOS).save(f"{proof}/{stem}-1x1.png")

# ── 2. pill zone ───────────────────────────────────────────────────────────────
if not has_pill:
    print(f"ok|{msg}")
    sys.exit(0)

# modal color ≈ the ground; sample coarsely, it only needs to be close
small = im.resize((160, 160), Image.NEAREST)
bg = max(small.getcolors(160 * 160), key=lambda c: c[0])[1]

inset = 0.04                       # skip the cover's own border frame + shadow
x0, x1 = int(w * (1 - pill_w)), int(w * (1 - inset))
y0, y1 = int(h * (1 - pill_h)), int(h * (1 - inset))
band = im.crop((x0, y0, x1, y1))

ink = sum(1 for p in pixels(band)
          if max(abs(p[0] - bg[0]), abs(p[1] - bg[1]), abs(p[2] - bg[2])) > 40)
frac = ink / max(1, band.width * band.height)

if frac > 0.015:
    print(f"warn|{msg};;{frac:.1%} ink under the duration badge — 抬高内容，右下 "
          f"{pill_w:.0%}×{pill_h:.0%} 留空")
else:
    print(f"ok|{msg} · pill zone clear")
