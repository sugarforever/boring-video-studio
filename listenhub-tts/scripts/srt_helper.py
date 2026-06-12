#!/usr/bin/env python3
"""SRT 帮手(纯标准库,无第三方依赖)。子命令:

  buildreq  <txt> <speakerId> [--model M]   口播文本 → 切句 → ListenHub /v1/speech 请求体
                                            {"scripts":[{content,speakerId}...]} (打到 stdout)
  normalize <raw_subtitle> <out.srt>        ListenHub 自带字幕(VTT/JSON/SRT 任一)→ 规整 SRT
  build     <verbose_json> <out.srt>        云端 ASR 的 verbose_json → SRT(fallback 路径用)
  correct   <in.srt> <out.srt> --base ...   文本级 LLM 校正(只改字、不动时间轴/编号/条数)

校正铁律(同 subtitle-correction):NEVER modify timestamps / numbering / count。
"""
import sys, json, re, argparse, urllib.request


# ---------- 时间戳工具 ----------
def ts(sec):
    if sec is None or sec < 0:
        sec = 0
    ms = int(round(float(sec) * 1000))
    h, ms = divmod(ms, 3600000)
    m, ms = divmod(ms, 60000)
    s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def parse_ts(text):
    """'00:01:23,456' 或 '00:01:23.456' 或 纯秒/毫秒数字 → 秒(float)。"""
    text = str(text).strip()
    m = re.match(r"(\d+):(\d{1,2}):(\d{1,2})[,.](\d+)", text)
    if m:
        h, mn, s, frac = m.groups()
        return int(h) * 3600 + int(mn) * 60 + int(s) + int(frac) / (10 ** len(frac))
    m = re.match(r"(\d+):(\d{1,2})[,.](\d+)", text)          # mm:ss,mmm
    if m:
        mn, s, frac = m.groups()
        return int(mn) * 60 + int(s) + int(frac) / (10 ** len(frac))
    try:
        v = float(text)
        return v / 1000.0 if v > 10000 else v                # 大数当毫秒
    except ValueError:
        return 0.0


# ---------- buildreq:文本 → 切句 → /v1/speech 请求体 ----------
def split_sentences(text):
    """按中英文句末标点 + 换行切句,保留标点,去空白。"""
    text = text.replace("\r", "")
    parts = re.split(r"(?<=[。！？!?…])\s*|\n+", text)
    return [p.strip() for p in parts if p and p.strip()]


def buildreq(a):
    text = open(a.input, encoding="utf-8").read()
    sents = split_sentences(text)
    if not sents:
        print("no sentences in input", file=sys.stderr); sys.exit(1)
    scripts = [{"content": s, "speakerId": a.speaker} for s in sents]
    payload = {"scripts": scripts}
    if a.model:
        payload["model"] = a.model
    sys.stdout.write(json.dumps(payload, ensure_ascii=False))


# ---------- normalize:ListenHub 自带字幕 → SRT ----------
def write_srt(cues, out):
    """cues: list of (start_sec, end_sec, text)。"""
    blocks = []
    for i, (st, en, tx) in enumerate(cues, 1):
        blocks.append(f"{i}\n{ts(st)} --> {ts(en)}\n{str(tx).strip()}\n")
    open(out, "w", encoding="utf-8").write("\n".join(blocks) + "\n")


def cues_from_vtt(raw):
    cues = []
    for block in re.split(r"\n\s*\n", raw.strip()):
        lines = [l for l in block.splitlines() if l.strip()]
        tl = next((l for l in lines if "-->" in l), None)
        if not tl:
            continue
        a, _, b = tl.partition("-->")
        b = b.split()[0] if b.strip() else b                 # 去掉 VTT cue settings
        txt = " ".join(lines[lines.index(tl) + 1:]).strip()
        cues.append((parse_ts(a), parse_ts(b), txt))
    return cues


def cues_from_json(raw):
    """防御性:ListenHub 字幕 JSON 形态未知。从常见字段名里捞 start/end/text。"""
    data = json.loads(raw)
    segs = None
    if isinstance(data, list):
        segs = data
    elif isinstance(data, dict):
        for k in ("segments", "subtitles", "cues", "result", "data", "words"):
            if isinstance(data.get(k), list):
                segs = data[k]; break
    if not segs:
        raise ValueError("no segment list found in subtitle JSON")
    S = ("start", "startTime", "begin", "from", "startMs", "start_ms", "offset")
    E = ("end", "endTime", "to", "endMs", "end_ms")
    T = ("text", "content", "word", "caption", "value")

    def conv(seg, keys):
        for k in keys:
            if k in seg:
                v = seg[k]
                # 字段名带 ms 且是数字 → 明确按毫秒，别靠 parse_ts 猜阈值
                if "ms" in k.lower() and isinstance(v, (int, float)):
                    return float(v) / 1000.0
                return parse_ts(v)
        return 0.0

    cues = []
    for seg in segs:
        if not isinstance(seg, dict):
            continue
        tx = next((seg[k] for k in T if k in seg), "")
        cues.append((conv(seg, S), conv(seg, E), tx))
    return cues


def cues_from_srt(raw):
    cues = []
    for block in re.split(r"\n\s*\n", raw.strip()):
        lines = block.splitlines()
        tl = next((l for l in lines if "-->" in l), None)
        if not tl:
            continue
        a, _, b = tl.partition("-->")
        txt = "\n".join(lines[lines.index(tl) + 1:]).strip()
        cues.append((parse_ts(a), parse_ts(b), txt))
    return cues


def normalize(a):
    raw = open(a.input, encoding="utf-8").read()
    head = raw.lstrip()[:1] if raw.strip() else ""
    upper = raw.lstrip().upper()
    if upper.startswith("WEBVTT"):
        cues = cues_from_vtt(raw)
    elif head in "[{":
        cues = cues_from_json(raw)
    else:
        cues = cues_from_srt(raw)
    if not cues:
        print("normalize: no cues parsed", file=sys.stderr); sys.exit(2)
    write_srt(cues, a.output)
    print(f"normalized {len(cues)} cues -> {a.output}")


# ---------- build:ASR verbose_json → SRT(fallback 路径) ----------
def build(a):
    data = json.load(open(a.input, encoding="utf-8"))
    segs = data.get("segments") or []
    out = []
    for i, seg in enumerate(segs, 1):
        out.append(f"{i}\n{ts(seg.get('start'))} --> {ts(seg.get('end'))}\n{(seg.get('text') or '').strip()}\n")
    open(a.output, "w", encoding="utf-8").write("\n".join(out) + "\n")
    print(f"built {len(segs)} cues -> {a.output}")


# ---------- correct:文本级 LLM 校正 ----------
def parse_srt(path):
    blocks = re.split(r"\n\s*\n", open(path, encoding="utf-8").read().strip())
    cues = []
    for b in blocks:
        lines = b.splitlines()
        if len(lines) >= 3:
            cues.append({"num": lines[0], "time": lines[1], "text": "\n".join(lines[2:]).strip()})
    return cues


def chat(base, key, model, system, user):
    body = json.dumps({"model": model, "temperature": 0,
                       "messages": [{"role": "system", "content": system},
                                    {"role": "user", "content": user}]}).encode()
    req = urllib.request.Request(base.rstrip("/") + "/chat/completions", data=body,
                                 headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=180) as r:
        return json.load(r)["choices"][0]["message"]["content"]


def correct(a):
    cues = parse_srt(a.input)
    if not cues:
        print("no cues, copy through", file=sys.stderr)
        open(a.output, "w", encoding="utf-8").write(open(a.input, encoding="utf-8").read())
        return
    sysmsg = (
        "你是中文字幕校对器。输入是一个 JSON 数组，每个元素是一条字幕文本（语音识别结果，"
        "可能有同音字、英文专名/术语拼写错误、中英文间空格与标点不规整）。逐条修正这些错误，"
        "规整标点与中英文空格。严格要求：(1) 返回同样长度、同样顺序的 JSON 字符串数组；"
        "(2) 不合并、不拆分、不增删任何条目；(3) 只改文本，不要任何解释或多余字段。"
        + (f" 已知术语（按此拼写为准）：{a.terms}" if a.terms else ""))
    user = json.dumps([c["text"] for c in cues], ensure_ascii=False)
    fixed = None
    try:
        resp = chat(a.base, a.key, a.model, sysmsg, user)
        m = re.search(r"\[.*\]", resp, re.S)
        fixed = json.loads(m.group(0)) if m else None
    except Exception as e:
        print(f"correction skipped (LLM error: {e})", file=sys.stderr)
    if not isinstance(fixed, list) or len(fixed) != len(cues):
        got = None if fixed is None else len(fixed)
        print(f"correction skipped (len {got} != {len(cues)}); keeping raw", file=sys.stderr)
        open(a.output, "w", encoding="utf-8").write(open(a.input, encoding="utf-8").read())
        return
    out = [f"{c['num']}\n{c['time']}\n{str(t).strip()}\n" for c, t in zip(cues, fixed)]
    open(a.output, "w", encoding="utf-8").write("\n".join(out) + "\n")
    print(f"corrected {len(cues)} cues -> {a.output}")


p = argparse.ArgumentParser()
sub = p.add_subparsers(dest="cmd", required=True)

br = sub.add_parser("buildreq"); br.add_argument("input"); br.add_argument("speaker")
br.add_argument("--model", default=""); br.set_defaults(fn=buildreq)

nz = sub.add_parser("normalize"); nz.add_argument("input"); nz.add_argument("output")
nz.set_defaults(fn=normalize)

b = sub.add_parser("build"); b.add_argument("input"); b.add_argument("output"); b.set_defaults(fn=build)

c = sub.add_parser("correct")
c.add_argument("input"); c.add_argument("output")
c.add_argument("--base", required=True); c.add_argument("--key", required=True)
c.add_argument("--model", required=True); c.add_argument("--terms", default="")
c.set_defaults(fn=correct)

a = p.parse_args()
a.fn(a)
