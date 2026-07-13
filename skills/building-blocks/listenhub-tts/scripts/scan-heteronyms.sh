#!/usr/bin/env bash
# scan-heteronyms.sh — flag high-risk 多音字 in a narration file BEFORE running TTS.
#
#   scan-heteronyms.sh <narration.txt>
#
# Reads the curated list from ../heteronyms.md (the SCAN-CONFIG block) and, for each
# high-risk character, reports occurrences. A line is marked:
#   ⚠ REVIEW  — the char appears OUTSIDE every known safe compound (bare or unfamiliar word) → likely needs a fix
#   ✓         — every occurrence on the line sits inside a known safe compound → usually fine
#
# Judgment stays with you (the agent): rules are too brittle (同一个「调」在 调用/调试 里相反).
# Fix ladder: ① expand to an unambiguous compound → ② rephrase → ③ (if it slips to the final) single-sentence splice.
set -euo pipefail

txt="${1:?usage: scan-heteronyms.sh <narration.txt>}"
here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
md="$here/../heteronyms.md"
[ -f "$md" ] || { echo "✗ heteronyms.md not found at $md"; exit 1; }
[ -f "$txt" ] || { echo "✗ no such file: $txt"; exit 1; }

python3 - "$md" "$txt" <<'PY'
import sys, re
md, txt = sys.argv[1], sys.argv[2]

# parse SCAN-CONFIG block: CHAR \t reading \t safe1,safe2,...
cfg = {}
inblock = False
for line in open(md, encoding="utf-8"):
    if "SCAN-CONFIG" in line and "/SCAN-CONFIG" not in line:
        inblock = True; continue
    if "/SCAN-CONFIG" in line:
        break
    if not inblock:
        continue
    parts = line.rstrip("\n").split("\t")
    if len(parts) >= 3 and len(parts[0]) == 1:
        ch, reading, safes = parts[0], parts[1], parts[2]
        cfg[ch] = (reading, [s for s in safes.split(",") if s])

lines = open(txt, encoding="utf-8").read().splitlines()
review_lines = 0
safe_hit_lines = 0
for i, ln in enumerate(lines, 1):
    if not ln.strip():
        continue
    bare_chars = []   # (char, reading) appearing OUTSIDE any safe compound
    any_hit = False
    for ch, (reading, safes) in cfg.items():
        if ch not in ln:
            continue
        any_hit = True
        covered = [False] * len(ln)
        for sw in safes:
            start = 0
            while True:
                j = ln.find(sw, start)
                if j < 0: break
                for k in range(j, j+len(sw)): covered[k] = True
                start = j + 1
        if any(ln[p] == ch and not covered[p] for p in range(len(ln))):
            bare_chars.append((ch, reading))
    if not any_hit:
        continue
    if not bare_chars:
        safe_hit_lines += 1
        continue
    # only print lines that actually need a look
    review_lines += 1
    print(f"⚠ L{i}: {ln}")
    for ch, reading in bare_chars:
        print(f"      「{ch}」裸字/陌生词，应读 {reading} → 看是否选错音，扩成无歧义的词或换说法")
    print()

print("—")
if review_lines == 0:
    print(f"✓ 扫了 {len(cfg)} 个高危字 · {safe_hit_lines} 行命中但都在安全词内 · 无需 REVIEW。")
else:
    print(f"⚠ {review_lines} 行需 REVIEW(另有 {safe_hit_lines} 行命中但在安全词内、通常没事)。")
    print("  逐行判断:① 扩成无歧义的词(调→调用)→ ② 换说法 → ③ 漏到成片再单句挖补。")
    print("  注:这是预防,发音没法从音频自动验证;残余靠审听兜底。")
PY
