#!/usr/bin/env bash
# listenhub-tts.sh — listenhub-tts skill：口播文本 → 音频 + 字幕
#
# 上游 skill：当用户只给了**文本**（没给音频/SRT）时，用本脚本出音频 + 字幕，校正后
# 交给 producing-video 出片。校正不在本脚本里做 —— 见 SKILL.md「Step 2 · 字幕校正」，由
# agent 编排（优先调用可用的字幕校正 skill，没有再确认后用 srt_helper.py correct）。
#
# 两条出字幕的路（TTS_MODE 选，默认 speech）：
#   speech（默认/首选）：ListenHub 原生 /v1/speech —— 把文稿切句成多段 scripts，引擎
#                        直接回 audioUrl + subtitlesUrl（自带字幕，文字＝输入原文、零识别错）。
#   asr （fallback）   ：OpenAI 兼容 /v1/audio/speech 出 mp3，再用 Groq/OpenAI Whisper
#                        转写出字幕。speech 路失败（或拿不到字幕）时自动降级到这条。
#
# 用法：
#   LISTENHUB_API_KEY=...  [GROQ_API_KEY=... | OPENAI_API_KEY=...] \
#     scripts/listenhub-tts.sh <input.txt> <out-dir> [ttsSpeakerId] [ttsModel] [--probe]
#
#   TTS_MODE=speech|asr   强制走某条路（默认 speech，失败自动 fallback 到 asr）
#   --probe               只打 /v1/speech 的原始 JSON 响应就退出（首次实跑用来确认
#                         字段名 audioUrl/subtitlesUrl 与字幕格式，再信任解析）
#   ASR_PROVIDER=groq|openai   fallback 时选 ASR 提供方（非交互不弹提示）
#
# 产物（out-dir 下）：
#   narration-full.mp3   ListenHub 音频
#   narration.srt        原始字幕（未校正；交给 agent 校正后再喂 producing-video）
#
# 依赖：curl · python3（srt_helper.py 同目录）
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LH_BASE="${LISTENHUB_API_BASE:-https://api.marswave.ai/openapi/v1}"

# --probe 可出现在任意位置;先从参数里摘掉,剩下的按位置解析
PROBE=0
[ "${PROBE_RAW:-}" = "1" ] && PROBE=1
ARGS=()
for a in "$@"; do
  if [ "$a" = "--probe" ]; then PROBE=1; else ARGS+=("$a"); fi
done
set -- "${ARGS[@]:-}"

INPUT="${1:?need input text file}"
OUTDIR="${2:?need output dir}"
TTS_SPEAKER="${3:-CN-Man-Beijing-V2}"     # speakers 列表见 GET /v1/speakers/list?language=zh
TTS_MODEL="${4:-flowtts}"
MODE="${TTS_MODE:-speech}"

command -v curl >/dev/null || { echo "need curl" >&2; exit 1; }
command -v python3 >/dev/null || { echo "need python3" >&2; exit 1; }
[ -f "$INPUT" ] || { echo "input not found: $INPUT" >&2; exit 1; }
: "${LISTENHUB_API_KEY:?set LISTENHUB_API_KEY (https://listenhub.ai/settings/api-keys)}"
mkdir -p "$OUTDIR"

MP3="$OUTDIR/narration-full.mp3"
SRT="$OUTDIR/narration.srt"
TMP="$(mktemp -d -t lh)"
trap 'rm -rf "$TMP"' EXIT

# 预处理：切句 + 解析停顿标记（空行 / [停 X] / ///，标记**不进 TTS**）。
#   req.json    送 /v1/speech 的请求体（干净分段）
#   pauses.json 「第 N 段后插 X 秒」；speech 路出片后据此拼静音、顺延字幕
#   clean.txt   剥掉标记的原文（ASR fallback 整段 TTS 用，防标记被念出来）
REQ="$TMP/req.json"; PAUSEMAP="$TMP/pauses.json"; CLEAN="$TMP/clean.txt"
python3 "$HERE/srt_helper.py" buildreq "$INPUT" "$TTS_SPEAKER" --model "$TTS_MODEL" \
  --pause-map "$PAUSEMAP" --clean-out "$CLEAN" > "$REQ"
has_pauses() { [ -s "$PAUSEMAP" ] && [ "$(cat "$PAUSEMAP")" != "[]" ]; }

# ============================================================
# 路 A · 原生 /v1/speech：切句多段 → audio + 自带字幕
# 返回 0=audio+字幕都拿到；2=拿到 audio 但没字幕（让 ASR 补字幕）；1=整体失败（fallback）
# ============================================================
speech_path() {
  echo "[speech] build request (切句成多段 scripts, 已剥停顿标记) → POST $LH_BASE/speech" >&2
  local resp="$TMP/resp.json"

  local code
  code=$(curl -sS -w '%{http_code}' -o "$resp" -X POST "$LH_BASE/speech" \
    -H "Authorization: Bearer $LISTENHUB_API_KEY" -H "Content-Type: application/json" \
    --data-binary @"$REQ")

  if [ "$PROBE" = "1" ]; then
    echo "── /v1/speech 原始响应 (HTTP $code) ──" >&2
    cat "$resp"; echo
    echo "── 上面确认 audioUrl / subtitlesUrl 字段名与字幕格式后，去掉 --probe 正式跑 ──" >&2
    exit 0
  fi
  if [ "$code" != "200" ]; then
    echo "[speech] HTTP $code，转 fallback：" >&2; head -c 600 "$resp" >&2; echo >&2
    return 1
  fi

  # 防御性提取 audioUrl / subtitlesUrl（字段名未知，递归找常见命名）
  local urls audio_url sub_url
  urls=$(python3 - "$resp" <<'PY'
import json,sys
d=json.load(open(sys.argv[1],encoding="utf-8"))
AK=("audiourl","audio_url","audio","url","mp3url","mp3_url")
SK=("subtitlesurl","subtitleurl","subtitles_url","subtitle_url","subtitles","subtitle","srturl","srt_url","vtturl","vtt_url","captionurl","caption_url")
af=[None]; sf=[None]
def walk(x):
    if isinstance(x,dict):
        for k,v in x.items():
            lk=k.lower()
            if isinstance(v,str) and v.startswith("http"):
                if af[0] is None and lk in AK: af[0]=v
                if sf[0] is None and lk in SK: sf[0]=v
            walk(v)
    elif isinstance(x,list):
        for v in x: walk(v)
walk(d)
print((af[0] or "")+"\t"+(sf[0] or ""))
PY
)
  audio_url="${urls%%$'\t'*}"; sub_url="${urls#*$'\t'}"

  if [ -z "$audio_url" ]; then
    echo "[speech] 响应里没找到 audioUrl（可能是异步/字段名不同），转 fallback。" >&2
    echo "         可加 --probe 看原始响应确认契约。" >&2
    return 1
  fi
  echo "[speech] audio: $audio_url" >&2
  curl -sSL -o "$MP3" "$audio_url"
  file "$MP3" | grep -qiE 'audio|mpeg|MP3' || { echo "[speech] 下载的音频不是音频，转 fallback" >&2; return 1; }
  echo "[speech]   ok: $(du -h "$MP3" | cut -f1)" >&2

  if [ -z "$sub_url" ]; then
    echo "[speech] 没有自带字幕 URL → 用 ASR 给这段音频补字幕。" >&2
    return 2
  fi
  echo "[speech] subtitle: $sub_url" >&2
  curl -sSL -o "$TMP/sub.raw" "$sub_url"
  python3 "$HERE/srt_helper.py" normalize "$TMP/sub.raw" "$SRT" >&2
  # 停顿：speech 路 cue 与输入段 1:1，在对应 cue 末尾拼静音 + 顺延 SRT（零漂移）
  if has_pauses; then
    if command -v ffmpeg >/dev/null; then
      echo "[speech] 插入停顿静音 + 顺延字幕" >&2
      if python3 "$HERE/srt_helper.py" insert-pauses "$MP3" "$SRT" "$PAUSEMAP" "$TMP/paused.mp3" "$TMP/paused.srt" >&2; then
        mv "$TMP/paused.mp3" "$MP3"; mv "$TMP/paused.srt" "$SRT"
      else
        echo "[speech] 停顿插入失败，保留无停顿版本继续" >&2
      fi
    else
      echo "[speech] 有停顿标记但未装 ffmpeg，跳过停顿（音频从头讲到尾）" >&2
    fi
  fi
  return 0
}

# ============================================================
# 路 B · fallback：/v1/audio/speech 出 mp3（若还没有）+ Whisper ASR 出字幕
# ============================================================
asr_path() {
  # 1) 没有 mp3 才用 OpenAI 兼容端点出一版（用剥掉停顿标记的 clean.txt，别把标记念出来）
  if ! file "$MP3" 2>/dev/null | grep -qiE 'audio|mpeg|MP3'; then
    has_pauses && echo "[asr] 注意：ASR 整段合成 + Whisper 重分句，cue 与输入段不 1:1，本路**不插停顿**（停顿只在 speech 主路生效）。" >&2
    echo "[asr] TTS via $LH_BASE/audio/speech → $MP3  (speaker=$TTS_SPEAKER model=$TTS_MODEL)" >&2
    local code
    code=$(curl -sS -w '%{http_code}' -o "$MP3" -X POST "$LH_BASE/audio/speech" \
      -H "Authorization: Bearer $LISTENHUB_API_KEY" -H "Content-Type: application/json" \
      --data "$(T="$(cat "$CLEAN")" SP="$TTS_SPEAKER" MD="$TTS_MODEL" python3 -c '
import json,os; print(json.dumps({"input":os.environ["T"],"voice":os.environ["SP"],"response_format":"mp3","model":os.environ["MD"]}))')")
    if [ "$code" != "200" ] || ! file "$MP3" | grep -qiE 'audio|mpeg|MP3'; then
      echo "[asr] TTS failed (HTTP $code):" >&2; head -c 600 "$MP3" >&2; echo >&2; exit 1
    fi
    echo "[asr]   ok: $(du -h "$MP3" | cut -f1)" >&2
  else
    echo "[asr] 复用已有音频 $MP3，只补字幕。" >&2
  fi

  # 2) 选 ASR 提供方（各自从 env 找 key）
  local provider="${ASR_PROVIDER:-}"
  if [ -z "$provider" ]; then
    if [ -t 0 ]; then
      echo "选择字幕 ASR 提供方：" >&2
      echo "  1) Groq   whisper-large-v3   (需 GROQ_API_KEY)" >&2
      echo "  2) OpenAI whisper-1          (需 OPENAI_API_KEY)" >&2
      read -rp "输入 1 或 2 [默认 1]: " ans
      case "${ans:-1}" in 2) provider=openai;; *) provider=groq;; esac
    else
      provider=groq; echo "[非交互] 未设 ASR_PROVIDER，默认 groq" >&2
    fi
  fi
  local asr_base asr_key asr_model
  case "$provider" in
    groq)   asr_base="https://api.groq.com/openai/v1"; asr_key="${GROQ_API_KEY:-}";   asr_model="whisper-large-v3"
            [ -n "$asr_key" ] || { echo "需要 GROQ_API_KEY（选了 Groq）" >&2; exit 1; } ;;
    openai) asr_base="https://api.openai.com/v1";      asr_key="${OPENAI_API_KEY:-}"; asr_model="whisper-1"
            [ -n "$asr_key" ] || { echo "需要 OPENAI_API_KEY（选了 OpenAI）" >&2; exit 1; } ;;
    *) echo "未知 ASR_PROVIDER: $provider（用 groq|openai）" >&2; exit 1 ;;
  esac

  # 3) ASR → verbose_json → SRT
  echo "[asr] ASR ($provider · $asr_model, zh) → $SRT" >&2
  local vj="$TMP/asr.json" code
  code=$(curl -sS -w '%{http_code}' -o "$vj" -X POST "$asr_base/audio/transcriptions" \
    -H "Authorization: Bearer $asr_key" \
    -F file=@"$MP3" -F model="$asr_model" -F response_format=verbose_json -F language=zh)
  [ "$code" = "200" ] || { echo "[asr] ASR failed (HTTP $code):" >&2; head -c 600 "$vj" >&2; echo >&2; exit 1; }
  python3 "$HERE/srt_helper.py" build "$vj" "$SRT" >&2
}

have_asr_key() { [ -n "${GROQ_API_KEY:-}" ] || [ -n "${OPENAI_API_KEY:-}" ]; }

# ---------------- 主流程 ----------------
if [ "$MODE" = "asr" ]; then
  asr_path
else
  set +e; speech_path; rc=$?; set -e
  case "$rc" in
    0) : ;;                                   # 原生：audio + 字幕都拿到
    2) asr_path ;;                            # 有 audio、缺字幕 → ASR 补字幕
    *) if have_asr_key; then
         echo "[fallback] speech 路失败 → 走 ASR 路。" >&2
         asr_path
       else
         echo "speech 路失败，且没有 GROQ_API_KEY/OPENAI_API_KEY 可 fallback。" >&2
         echo "排查：scripts/listenhub-tts.sh $INPUT $OUTDIR $TTS_SPEAKER $TTS_MODEL --probe" >&2
         exit 1
       fi ;;
  esac
fi

echo "done →"
echo "  audio: $MP3"
echo "  srt  : $SRT   (原始，未校正)"
echo "下一步（agent 编排）：优先用可用的字幕校正 skill 修字幕；没有则确认后用"
echo "  scripts/srt_helper.py correct（只改文字、不动时间轴），见 SKILL.md「Step 2 · 字幕校正」。"
echo "校正后把 mp3 + srt 作为 audio/narration-full.mp3 + audio/narration.srt 进主流程。"
