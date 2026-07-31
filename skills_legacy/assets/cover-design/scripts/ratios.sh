#!/usr/bin/env bash
# ratios.sh — the canonical cover ratio → pixel-size table. SOURCE this; don't run it.
#
# One table, two consumers (render-covers.sh, check-covers.sh) — so a ratio can never
# be renderable but uncheckable, or vice versa. Adding a ratio is one line here.
#
# Sizes are LOGICAL px. Renders are shot at 2× DPR, so cover-16x9.png lands as
# 3840×2160 physical. Platforms downscale; supersampling keeps CJK strokes crisp.

# ratio slug → "W H"
dims_for() {
  case "$1" in
    3x4)   echo "1080 1440" ;;   # 竖版主封面：抖音 / 小红书 / 视频号
    9x16)  echo "1080 1920" ;;   # Shorts / 全屏竖屏缩略图（视频本体不出 9:16）
    16x9)  echo "1920 1080" ;;   # 横版主封面：YouTube / 通用缩略图
    16x10) echo "1920 1200" ;;   # B 站横版封面
    4x3)   echo "1440 1080" ;;   # 横版 4:3
    3x2)   echo "1536 1024" ;;   # 文章/博客封面（单张，不属于视频五比例）
    1x1)   echo "1080 1080" ;;   # 可选方图
    *)     echo "" ;;
  esac
}

# The set every episode must ship. Both formats ship all five; only the MAIN
# cover differs (short → 3x4, long → 16x9). This is the "别又只做主封面" guard.
REQUIRED_RATIOS=(3x4 9x16 16x9 16x10 4x3)

# Which ratios get a duration pill / platform chrome stamped bottom-right by the
# host platform. Those covers must leave that corner quiet — see check-covers.sh.
PILL_RATIOS=(16x9 16x10 4x3)

# Fraction of the frame the platform may cover, measured from the bottom-right.
PILL_W=0.22
PILL_H=0.16

# ratio slug of a cover-<slug>.html / .png path
ratio_of() { local b; b="$(basename "$1")"; b="${b#cover-}"; echo "${b%%.*}"; }
