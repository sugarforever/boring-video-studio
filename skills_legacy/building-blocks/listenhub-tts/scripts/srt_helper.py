#!/usr/bin/env python3
"""SRT 帮手(纯标准库,无第三方依赖)。子命令:

  speakers  <json|->                        ListenHub /v1/speakers/list 的 JSON → 可读音色表
  buildreq  <txt> <speakerId> [--model M] [--pause-map P.json] [--clean-out C.txt]
                                            口播文本 → 切句 → ListenHub /v1/speech 请求体
                                            {"scripts":[{content,speakerId}...]} (打到 stdout)。
                                            识别停顿标记(空行 / [停 X] / ///),标记不进 TTS;
                                            --pause-map 写「第 N 段后插 X 秒」;--clean-out 写剥标记的原文
  insert-pauses <in.mp3> <in.srt> <pause.json> <out.mp3> <out.srt>
                                            按 pause map 在对应 cue 末尾拼静音(ffmpeg)+ SRT 顺延(零漂移)
  normalize <raw_subtitle> <out.srt>        ListenHub 自带字幕(VTT/JSON/SRT 任一)→ 规整 SRT
  build     <verbose_json> <out.srt>        云端 ASR 的 verbose_json → SRT(fallback 路径用)
  correct   <in.srt> <out.srt> --base ...   文本级 LLM 校正(只改字、不动时间轴/编号/条数)

校正铁律(同 subtitle-correction):NEVER modify timestamps / numbering / count。
"""
import sys, json, re, argparse, urllib.request, shutil, subprocess


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


# ---------- speakers:/v1/speakers/list JSON → 可读音色表 ----------
def find_speaker_list(node):
    """递归找「元素是带 speakerId 的 dict」的列表,对 {code,data:{items:[...]}} 这类 envelope 免疫。"""
    if isinstance(node, list):
        if node and isinstance(node[0], dict) and ("speakerId" in node[0] or "id" in node[0]):
            return node
        for x in node:
            r = find_speaker_list(x)
            if r:
                return r
    elif isinstance(node, dict):
        for v in node.values():
            r = find_speaker_list(v)
            if r:
                return r
    return None


def speakers(a):
    raw = sys.stdin.read() if a.input == "-" else open(a.input, encoding="utf-8").read()
    items = find_speaker_list(json.loads(raw))
    if not items:
        print("speakers: no speaker list found in JSON", file=sys.stderr); sys.exit(1)
    for s in items:
        if not isinstance(s, dict):
            continue
        sid = s.get("speakerId") or s.get("id") or "?"
        name = s.get("name", "")
        gender = s.get("gender", "")
        prof = s.get("profile") or {}
        styles = ",".join(prof.get("styles", []) or [])
        scenes = ",".join(prof.get("scenes", []) or [])
        accent = prof.get("accent", "")
        dl = prof.get("descriptionLocalized") or {}
        desc = dl.get("zh") or dl.get("en") or prof.get("description", "")
        bits = [b for b in (gender, accent, styles, scenes) if b]
        line = f"{sid}  ·  {name}"
        if bits:
            line += "  [" + " | ".join(bits) + "]"
        if desc:
            line += f"  — {desc}"
        print(line)
    print(f"\n{len(items)} speakers (复制上面的 speakerId 作脚本第 3 参)", file=sys.stderr)


# ---------- buildreq:文本 → 切句 → /v1/speech 请求体 ----------
def split_sentences(text):
    """按中英文句末标点 + 换行切句,保留标点,去空白。"""
    text = text.replace("\r", "")
    parts = re.split(r"(?<=[。！？!?…])\s*|\n+", text)
    return [p.strip() for p in parts if p and p.strip()]


# 停顿标记：单独成行的 [停 X] / [停] / [停顿] / [pause X] / ///（X 秒，缺省 0.8）。
# 空行也算段落停顿（0.8）。标记与空行都**不送 TTS**（否则会被念出来），只当停顿指令。
PAUSE_DEFAULT = 0.8
_MARK_RE = re.compile(r"^\s*(?:\[\s*(?:停顿?|pause)\s*([0-9]+(?:\.[0-9]+)?)?\s*\]|/{3,})\s*$", re.I)


def pause_of(line):
    """整行是停顿标记 → 返回秒数；否则 None（空行由调用方按段落默认处理）。"""
    m = _MARK_RE.match(line)
    if not m:
        return None
    return float(m.group(1)) if m.group(1) else PAUSE_DEFAULT


def parse_pacing(raw):
    """口播文本 → (segments, pauses, clean_lines)。
    segments：送 TTS 的干净句子；与引擎回的 cue 一一对应。
    pauses  ：[{"after_cue": n(1-based), "dur": 秒}]，同一间隙里显式标记优先于空行。
    clean_lines：剥掉标记/空行后的原文行（ASR fallback 整段 TTS 用，防标记被念出来）。"""
    raw = raw.replace("\r", "")
    segments, pauses, clean = [], [], []
    pend_explicit, pend_blank = 0.0, False
    for line in raw.split("\n"):
        mark = pause_of(line)
        if mark is not None:                       # 显式标记行
            pend_explicit = max(pend_explicit, mark)
            continue
        if not line.strip():                       # 空行 = 段落停顿
            pend_blank = True
            continue
        # 文本行：先把上一段之后的停顿落到 pause map（显式优先），再切句
        dur = pend_explicit if pend_explicit > 0 else (PAUSE_DEFAULT if pend_blank else 0.0)
        if dur > 0 and segments:
            pauses.append({"after_cue": len(segments), "dur": round(dur, 3)})
        pend_explicit, pend_blank = 0.0, False
        clean.append(line.strip())
        for s in split_sentences(line):
            segments.append(s)
    return segments, pauses, clean


def buildreq(a):
    segments, pauses, clean = parse_pacing(open(a.input, encoding="utf-8").read())
    if not segments:
        print("no sentences in input", file=sys.stderr); sys.exit(1)
    scripts = [{"content": s, "speakerId": a.speaker} for s in segments]
    payload = {"scripts": scripts}
    if a.model:
        payload["model"] = a.model
    sys.stdout.write(json.dumps(payload, ensure_ascii=False))
    if a.pause_map:
        json.dump(pauses, open(a.pause_map, "w", encoding="utf-8"), ensure_ascii=False)
    if a.clean_out:
        open(a.clean_out, "w", encoding="utf-8").write("\n".join(clean) + "\n")
    print(f"[buildreq] {len(segments)} 段 · {len(pauses)} 处停顿"
          + (f" → {a.pause_map}" if a.pause_map else ""), file=sys.stderr)


# ---------- insert-pauses：按 pause map 在音频对应 cue 末尾拼静音 + SRT 顺延（零漂移） ----------
def insert_pauses(a):
    pauses = json.load(open(a.pause_map, encoding="utf-8")) if a.pause_map else []
    cues = cues_from_srt(open(a.srt, encoding="utf-8").read())
    n = len(cues)
    valid = [p for p in pauses if 1 <= int(p["after_cue"]) <= n and float(p["dur"]) > 0]
    if not valid:                                  # 没有可用停顿 → 原样透传
        if a.out_audio != a.in_audio:
            shutil.copy(a.in_audio, a.out_audio)
        if a.out_srt != a.srt:
            shutil.copy(a.srt, a.out_srt)
        print("[insert-pauses] 无停顿，原样透传", file=sys.stderr)
        return
    if not shutil.which("ffmpeg"):
        print("[insert-pauses] 未找到 ffmpeg，跳过（音频不插停顿）", file=sys.stderr)
        if a.out_audio != a.in_audio:
            shutil.copy(a.in_audio, a.out_audio)
        if a.out_srt != a.srt:
            shutil.copy(a.srt, a.out_srt)
        return
    # 插入点：第 after_cue 条 cue 的结束时刻，插 dur 秒静音
    ins = sorted(({"t": cues[int(p["after_cue"]) - 1][1], "d": float(p["dur"]),
                   "after": int(p["after_cue"])} for p in valid), key=lambda x: x["t"])
    parts, labels, prev = [], [], 0.0
    for i, x in enumerate(ins):
        parts.append(f"[0:a]atrim=start={prev:.3f}:end={x['t']:.3f},asetpts=N/SR/TB,"
                     f"aformat=sample_rates=44100:channel_layouts=stereo[a{i}]")
        labels.append(f"[a{i}]")
        parts.append(f"anullsrc=r=44100:cl=stereo:d={x['d']:.3f}[s{i}]")
        labels.append(f"[s{i}]")
        prev = x["t"]
    fi = len(ins)
    parts.append(f"[0:a]atrim=start={prev:.3f},asetpts=N/SR/TB,"
                 f"aformat=sample_rates=44100:channel_layouts=stereo[a{fi}]")
    labels.append(f"[a{fi}]")
    filt = "; ".join(parts) + "; " + "".join(labels) + f"concat=n={len(labels)}:v=0:a=1[out]"
    subprocess.run(["ffmpeg", "-y", "-i", a.in_audio, "-filter_complex", filt,
                    "-map", "[out]", "-c:a", "libmp3lame", "-q:a", "2", a.out_audio],
                   check=True, stderr=subprocess.DEVNULL)
    # SRT 顺延：第 j(1-based) 条 cue 后移量 = 所有 after<j 的停顿之和（零漂移）
    shifted = []
    for j, (st, en, tx) in enumerate(cues, 1):
        sh = sum(x["d"] for x in ins if x["after"] < j)
        shifted.append((st + sh, en + sh, tx))
    write_srt(shifted, a.out_srt)
    print(f"[insert-pauses] 插入 {len(ins)} 处停顿 (+{sum(x['d'] for x in ins):.2f}s) "
          f"→ {a.out_audio} · {a.out_srt}", file=sys.stderr)


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

sp = sub.add_parser("speakers"); sp.add_argument("input"); sp.set_defaults(fn=speakers)

br = sub.add_parser("buildreq"); br.add_argument("input"); br.add_argument("speaker")
br.add_argument("--model", default="")
br.add_argument("--pause-map", dest="pause_map", default="", help="停顿指令写到这个 JSON")
br.add_argument("--clean-out", dest="clean_out", default="", help="剥掉标记的干净文本写到这里(ASR 路用)")
br.set_defaults(fn=buildreq)

ip = sub.add_parser("insert-pauses")
ip.add_argument("in_audio"); ip.add_argument("srt"); ip.add_argument("pause_map")
ip.add_argument("out_audio"); ip.add_argument("out_srt"); ip.set_defaults(fn=insert_pauses)

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
