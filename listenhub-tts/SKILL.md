---
name: listenhub-tts
description: Turn a narration script (口播文本) into a voiceover audio file + a time-accurate SRT subtitle. Preferred path uses ListenHub's native /v1/speech (the audio engine emits its own subtitles — text == input, no recognition errors); a cloud ASR (Groq / OpenAI Whisper) path is the fallback. Then orchestrates a text-level subtitle correction. The output (narration-full.mp3 + narration.srt) is exactly what the `producing-video` skill needs as its source of truth. Use when the user has only the narration text (no audio/SRT) and says "把文稿做成音频", "生成配音", "文本转语音", "口播配音 + 字幕", "text to speech with subtitles", "做配音", or hands over a script for a daily / 解读 / 口播 and wants the audio + subtitles produced. Also covers picking the voice (speaker) — "选音色", "换个声音", "用女声", "choose a voice" — by listing ListenHub speakers. NOT for voice cloning (use a cloud TTS that supports it) and NOT for rendering the video itself (that's `producing-video`).
---

# ListenHub-TTS · 文稿 → 音频 + 字幕

把一段**口播文本**变成「配音音频 + 时间轴准确的 SRT 字幕」。这是视频制作链路的**上游**：产物 `narration-full.mp3` + `narration.srt` 直接喂给 **`producing-video`** skill 出片。

**铁律:时间轴是字幕的命根。** 字幕的时间戳要准——这是这步唯一不能错的东西;个别错的中文同音字/英文专名,下游**文本级校正**只改字、绝不动时间轴。

## 分工

| 谁 | 做什么 |
|---|---|
| **用户** | 写口播稿(纯文本 `narration.txt`) |
| **本 skill(你)** | ListenHub 出音频 + 字幕(原生优先,ASR fallback)→ 编排校正 → 交出 mp3 + SRT |
| **下游** | `producing-video` 拿 mp3 + SRT 出成片 |

> 用户已经自己有音频/字幕 → **跳过本 skill**,直接用 `producing-video`。本 skill 只在「只有文本」时补这一段。

## 两条出字幕的路(脚本自动选)

| | **speech(默认/首选)** | **asr(fallback)** |
|---|---|---|
| 端点 | 原生 `POST /v1/speech`(把文稿切句成多段 `scripts`) | OpenAI 兼容 `/v1/audio/speech` 出 mp3 + Whisper 转写 |
| 字幕来源 | **引擎自带**(`subtitlesUrl`)——文字＝输入原文,**零识别错** | ASR 听回去转写,会有同音字/专名错 |
| 校正需求 | 几乎不需要(顶多规整标点/中英文空格) | 需要(Claude→Cloud 这类错) |
| 要的 key | 仅 `LISTENHUB_API_KEY` | 还要 `GROQ_API_KEY` / `OPENAI_API_KEY` |

脚本默认走 speech;失败(或拿不到 `subtitlesUrl`)时,有 ASR key 就**自动降级**到 asr。`TTS_MODE=asr` 可强制走 fallback。

## 依赖检查(pre-flight)

```bash
command -v curl python3       # 两个都要;脚本纯标准库,无第三方依赖
```

需要的 key(env,**勿入库**):
- `LISTENHUB_API_KEY` —— **必须**(<https://listenhub.ai/settings/api-keys>,格式 `lh_sk_...`)。
- `GROQ_API_KEY` **或** `OPENAI_API_KEY` —— **可选**,仅 fallback(asr 路)时需要。

> **不依赖 `listenhub` CLI。** 官方 marswaveai 有个 `tts` skill 走 `listenhub` CLI + 一整套 auth/config/shared 生态、且强交互;本 skill 刻意保持**自包含 curl + 非交互**,适合做自动化管道的上游。CLI 的 OpenAPI 模式读的也是同一个 `LISTENHUB_API_KEY`。

---

## 工作流

### Step 0 · 选音色(speaker)

一个旁路、单声道叙述,选**一个** speakerId。先列表再挑:

```bash
LISTENHUB_API_KEY=...  scripts/listenhub-speakers.sh zh         # 可读音色表(name·特征·描述)
LISTENHUB_API_KEY=...  scripts/listenhub-speakers.sh zh --json  # 原始 JSON,给 agent 解析
# 端点:GET /v1/speakers/list?language=zh,每个 speaker 有 speakerId/name/gender/profile
#       (profile: styles/scenes/accent/description) + demoAudioUrl 试听
```

- **用 `AskUserQuestion` 把候选音色端给用户挑**(用 `name` + 性别/风格/适用场景,如「专业·解读」),拿到 `speakerId`。用户不在意就用默认 `CN-Man-Beijing-V2`。
- **首次用某个 id 前,先 `listenhub-speakers.sh zh` 确认它在列表里**(默认 id 可能随 ListenHub 更新而变);`demoAudioUrl` 可让用户试听再定。
- **系列/日更沿用同一音色**:这期用了哪个 speakerId,记下来,下期继续用,保持声音一致(和 producing-video 的品牌纪律一脉相承)。
- 选定的 speakerId 作 Step 1 脚本的**第 3 个参数**。

### Step 1 · 出音频 + 原始字幕(一条脚本)

`scripts/listenhub-tts.sh` 默认走原生 speech 路:把文稿**切句成多段 `scripts`**(让自带字幕有逐句 cue)→ `POST /v1/speech` → 拿 `audioUrl` + `subtitlesUrl` → 下音频 + 把字幕规整成 SRT。

```bash
LISTENHUB_API_KEY=...  [GROQ_API_KEY=...] \
  scripts/listenhub-tts.sh <narration.txt> <out-dir> [speakerId] [ttsModel]
# 出 <out-dir>/narration-full.mp3 + <out-dir>/narration.srt(原始,未校正)
```

- 第 3 参 = Step 0 选定的 `speakerId`(省略则用默认 `CN-Man-Beijing-V2`)。
- **首次实跑先 `--probe`**:`... <narration.txt> <out-dir> "" "" --probe` 只打 `/v1/speech` 的原始 JSON 响应,**确认 `audioUrl`/`subtitlesUrl` 字段名与字幕格式**(脚本的解析是防御性的,但实网契约没见过),确认无误再去掉 `--probe` 正式跑。
- fallback(asr 路):`TTS_MODE=asr` 强制走;或 speech 失败时自动降级。ASR 提供方非交互用 `ASR_PROVIDER=groq|openai`(默认 groq);Groq `large-v3` 比 `large-v3-turbo` 略准,日更这个量级别为成本牺牲准确度,用完整版。

### Step 2 · 字幕校正(你来编排,按此顺序)

**先看走的是哪条路:**
- **speech 路(原生字幕)**:字幕文字 = TTS 的输入原文,**没有识别错**,通常**可跳过校正**(顶多让校正器规整一下标点/中英文空格)。先抽看几条,没问题就直接进 Step 3。
- **asr 路(Whisper 转写)**:中文里的英文专名/同音字会有个别错(如 Claude→Cloud、Vercel→Verso),**需要校正**。

**铁律仍是不动时间轴/编号/条数。** 需要校正时,按此顺序:

1. **先扫描可用的「字幕校正」skill,优先用它。** 在当前 skill 列表里找名字含 `subtitle` / `字幕` / `correction` 的(如 **`subtitle-correction`**)。有就把原始 SRT 交给它修 —— 交互式、会问术语、质量更高、自带 `validate` 兜底。**本项目不复制该 skill,只引用**;README 注明需同时安装。
2. **没有这类 skill** → **先跟用户确认**:「要用同一 ASR 提供方的 chat 模型做一次**文本级**校正吗?(只改文字、按原条目重挂时间戳,零时间轴风险)」。**用户同意**再跑:
   ```bash
   python3 scripts/srt_helper.py correct narration.srt narration.fixed.srt \
     --base <ASR_BASE> --key <ASR_KEY> --model <chatModel> --terms "OpenAI, Anthropic, Claude, Vercel, ..."
   # Groq → base https://api.groq.com/openai/v1 · model llama-3.3-70b-versatile
   # OpenAI → base https://api.openai.com/v1 · model gpt-4o-mini
   # base/key 复用 Step 1 的 ASR 那套
   ```
   `srt_helper.py correct` 只把字幕文本发给 LLM、按原条目重挂时间戳/编号;LLM 出错或条数不符**自动退回原始 SRT**(零时间轴风险)。
3. 校正完,若有 `subtitle-correction` 的 `subtitle_tool.py`,再 `validate <raw> <fixed>` 兜底确认时间轴/条数/编号没变。

### Step 3 · 交付

把 `narration-full.mp3` + **校正后的** SRT 命名为 `narration-full.mp3` + `narration.srt`,交给 **`producing-video`** skill(它会放进 `audio/narration-full.mp3` + `audio/narration.srt` 进主流程)。

```
narration.txt ──(本 skill)──▶ narration-full.mp3 + narration.srt ──▶ producing-video ──▶ 4K MP4
```

---

## 成本(~3 分钟日更)

- **TTS 是大头**:ListenHub credits,~4 credits/分钟。
- 云端 ASR:~半美分到两美分,**可忽略**——且走 speech 路时**根本不产生**(自带字幕)。
- LLM 文本校正:~1 美分,**可忽略**——speech 路通常跳过。
- 走 speech 路只需 ListenHub 一家、一个 key,链路更短更省。

## 超出范围

- **声音克隆 / 「听起来像我」**:本 skill 用通用音色。要克隆自己的声音,用支持克隆的云端 TTS(MiniMax / ElevenLabs)——克隆只换"出声那一步",下游字幕/时间轴/渲染不变。
- **出片**:把音频 + 字幕变成视频是 **`producing-video`** 的活,不在本 skill。
- **改时间轴的字幕重排**:本 skill 的校正是**纯文本级**(条数/编号/时间戳一律不动)。需要重新切条/对齐 → 回到 ASR 或用专门工具。

## Gotchas

1. **首次实跑先 `--probe`**。`/v1/speech` 的响应字段名(`audioUrl`/`subtitlesUrl`)与字幕格式(SRT/VTT/JSON)实网没验证过;脚本解析是防御性的,但先 `--probe` 看一眼原始响应再信任它。`srt_helper.py normalize` 能吃 VTT/JSON(秒/毫秒/时间戳串)/SRT 三种,但**字幕 cue 粒度由 ListenHub 决定** —— 所以输入按句切多段(脚本已做),逼它给逐句 cue;若实测粒度仍太粗(整段一条),就 `TTS_MODE=asr` 走 ASR 拿细粒度时间轴。
2. **时间轴 > 文字**。要的是准时间戳;错字交给 Step 2 修,**别为了"识别更准"去牺牲时间轴**(重新分句会打乱 cue)。
3. **校正绝不动时间轴/编号/条数**。这是 `subtitle-correction` 的铁律,本 skill 的 `srt_helper.py correct` 也照此实现(长度不符自动回退原始)。speech 路文字已是原文,通常无需校正。
4. **优先用 `subtitle-correction` skill**,它质量更高、会问术语;`srt_helper.py correct` 是没有该 skill 时的、需用户确认的回退方案。
5. **key 走 env,绝不入库**。`LISTENHUB_API_KEY` / `GROQ_API_KEY` / `OPENAI_API_KEY` 都从环境变量读。
6. **本地 whisper 的坑**:`hyperframes transcribe -m large-v3` 当前是坏的(传 `--dtw large-v3`,新版 whisper.cpp 要 `large.v3` → `unknown DTW preset`)。云端 ASR 绕开此问题;若非要本地直调 `whisper-cli -osrt`、别加 `--dtw`。
