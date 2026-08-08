# 旁白 · ListenHub TTS（含声音克隆）

> 这是 `verysmallwoods-video` 的**音频参考**，从独立 skill `listenhub-tts` 移植而来。
> 上游是 `references/audio.md` 的「TTS 合成」分支；产物 `narration-full.mp3` + `narration.srt`
> 直接进主流程（切段 / 对齐 / 重排节奏，见 `references/audio.md`「接入成片」）。

把一段**口播文本**变成「配音音频 + 时间轴准确的 SRT 字幕」。首选 ListenHub 原生
`/v1/speech`（引擎自带字幕、文字＝输入原文、零识别错）；云端 ASR（Groq / OpenAI Whisper）
作 fallback。**支持用户自己的克隆声音** —— 见下方「声音克隆」。

**铁律:时间轴是字幕的命根。** 时间戳要准 —— 这是唯一不能错的东西;个别错的中文同音字 /
英文专名,下游**文本级校正**只改字、绝不动时间轴。

## 声音克隆（本参考相对源 skill 新增的能力）

要「听起来像我」,**不需要换 TTS 提供方** —— ListenHub 支持声音克隆,克隆出的声音
**直接作为一个普通 speaker 出现在 speakers 列表里**,用它的 `speakerId` 走同一条
`/v1/speech`,下游字幕 / 时间轴 / 渲染**一律不变**。

**已实网验证(2026-08):**

- 克隆声音在 `GET /v1/speakers/list?language=zh` 里,`speakerId` 以 **`voice-clone-`** 打头。
  例:`{"name":"VerySmallWoods","speakerId":"voice-clone-6a29dd635b88331426c4ecbc","gender":"male", ...}`
- 拿这个 `speakerId` 作 `listenhub-tts.sh` 的第 3 参,`/v1/speech` 正常出 mp3 + 自带 SRT
  (文字＝输入原文、逐句 cue、零识别错),和公共音色**完全同一条链路**。

```bash
# 1) 找到自己的克隆声音 speakerId(以 voice-clone- 打头)
LISTENHUB_API_KEY=...  scripts/listenhub-speakers.sh zh --json \
  | python3 -c 'import json,sys; [print(i["name"],i["speakerId"]) for i in json.load(sys.stdin)["data"]["items"] if i["speakerId"].startswith("voice-clone-")]'

# 2) 用克隆声音出音频 + 字幕
LISTENHUB_API_KEY=...  scripts/listenhub-tts.sh narration.txt out/ voice-clone-6a29dd635b88331426c4ecbc
```

> 克隆本身在 ListenHub 网页端做(上传 / 录一段样本),不在脚本里。脚本只负责**用**克隆声音出片。
> 系列 / 日更**沿用同一 `speakerId`** 保持声音一致(和封面 / 文案的品牌纪律一脉相承)。

## 两条出字幕的路(脚本自动选)

| | **speech(默认/首选)** | **asr(fallback)** |
|---|---|---|
| 端点 | 原生 `POST /v1/speech`(把文稿切句成多段 `scripts`) | OpenAI 兼容 `/v1/audio/speech` 出 mp3 + Whisper 转写 |
| 字幕来源 | **引擎自带**(`subtitlesUrl`)——文字＝输入原文,**零识别错** | ASR 听回去转写,会有同音字/专名错 |
| 校正需求 | 几乎不需要(顶多规整标点/中英文空格) | 需要(Claude→Cloud 这类错) |
| 要的 key | 仅 `LISTENHUB_API_KEY` | 还要 `GROQ_API_KEY` / `OPENAI_API_KEY` |

脚本默认走 speech;失败(或拿不到 `subtitlesUrl`)时,有 ASR key 就**自动降级**到 asr。
`TTS_MODE=asr` 可强制走 fallback。

## 依赖检查(pre-flight)

```bash
command -v curl python3       # 两个都要;脚本纯标准库,无第三方依赖
command -v ffmpeg             # 停顿插静音 + 1.1× 提速用;没装则跳过停顿(音频不停)
```

需要的 key(env,**勿入库**):
- `LISTENHUB_API_KEY` —— **必须**(<https://listenhub.ai/settings/api-keys>,格式 `lh_sk_...`)。
- `GROQ_API_KEY` **或** `OPENAI_API_KEY` —— **可选**,仅 fallback(asr 路)时需要。
- `LISTENHUB_API_BASE` —— 可选,默认 `https://api.marswave.ai/openapi/v1`。

---

## 工作流

### Step 0 · 选音色(speaker)

一个旁路、单声道叙述,选**一个** speakerId。先列表再挑:

```bash
LISTENHUB_API_KEY=...  scripts/listenhub-speakers.sh zh         # 可读音色表(name·特征·描述)
LISTENHUB_API_KEY=...  scripts/listenhub-speakers.sh zh --json  # 原始 JSON,给 agent 解析
# 端点:GET /v1/speakers/list?language=zh,每个 speaker 有 speakerId/name/gender/profile
```

- **要克隆声音** → 直接用自己的 `voice-clone-…`(见上「声音克隆」),跳过挑公共音色。
- 用公共音色 → 用 `AskUserQuestion` 把候选端给用户挑(name + 性别/风格/适用场景),拿到
  `speakerId`。用户不在意就用默认 `CN-Man-Beijing-V2`(原野,沉稳磁性·叙事)。
- **适合 AI 解读/日更/科普**(已验证存在):`CN-Man-Beijing-V2` 原野、`suzhe-45bbbe54` 苏哲、
  `liyan2-ef9401ec` 国栋、`chat-girl-105-cn` 晓曼(女声)。`demoAudioUrl` 可试听再定。
- ⚠️ **真实 speakerId 形如 `suzhe-45bbbe54` / `voice-clone-…`(不是猜的)**,务必从列表里取。
- 选定的 speakerId 作 Step 1 脚本的**第 3 个参数**。

### Step 0.5 · 多音字扫描(跑 TTS 前必做)

**TTS 对多音字常选错读音** —— 典型:`调用` 的「调」该读 **diào**,裸「调」/上下文不清时引擎
读成 **tiáo**。所以**在出音频之前**先扫一遍稿子:

```bash
scripts/scan-heteronyms.sh <narration.txt>
```

对每个 `⚠`,**人工判断**该读哪个音,按梯子修:①**扩成无歧义的词**(首选,如
`决定调哪个函数` → `决定调用哪个函数`);②**换种说法**(扩词救不了时);③**漏到成片了** →
单句重生成 + 挖补换音轨。不用引擎拼音/SSML(ListenHub 原生 `/v1/speech` 无公开支持,
且字幕=输入原文,标注会污染字幕)。清单 `heteronyms.md` 遇新坑就加。

### Step 0.7 · 停顿 / 呼吸节奏(长稿建议)

在 `narration.txt` 里标停顿点,脚本会把标记**剥掉再送 TTS**(绝不会被念出来),在音频里插真实
静音、SRT 时间顺延。两种标记(都单独成行):**空行** = 段落停顿(默认 0.8s);**`[停 X]`** =
显式停顿 X 秒(`[停]` / `///` = 一个 0.8s 呼吸拍)。语义驱动别均匀撒:章节间 0.8-1.2s、
抛结论后 0.4-0.6s、转折前 0.3-0.5s。机制走 ffmpeg,没装则跳过、并提示。

### Step 1 · 出音频 + 原始字幕(一条脚本)

```bash
LISTENHUB_API_KEY=...  [GROQ_API_KEY=...] \
  scripts/listenhub-tts.sh <narration.txt> <out-dir> [speakerId] [ttsModel]
# 出 <out-dir>/narration-full.mp3 + <out-dir>/narration.srt(原始,未校正)
```

- 第 3 参 = Step 0 选定的 `speakerId`(省略则用默认 `CN-Man-Beijing-V2`);要克隆声音就传
  `voice-clone-…`。
- **已验证的响应契约**(2026-06/08):`{"code":0,"data":{...,"audioUrl":"…mp3","subtitlesUrl":"…srt"}}`。
  `subtitlesUrl` 直接是标准 SRT、逐句 cue、文字＝输入原文。脚本递归提取 URL、`normalize`
  直接吃这份 SRT。排查用 `--probe` 打原始响应。
- fallback(asr 路):`TTS_MODE=asr` 强制走;或 speech 失败时自动降级。`ASR_PROVIDER=groq|openai`。

### Step 2 · 字幕校正(按此顺序)

- **speech 路**:字幕文字 = 输入原文,**没有识别错**,通常**可跳过**(顶多规整标点/中英文空格)。
- **asr 路**:英文专名/同音字会有个别错,**需要校正**。

**铁律仍是不动时间轴/编号/条数。** 需要校正时:①**先找可用的字幕校正 skill**(名字含
`subtitle` / `字幕` / `correction`,如 `subtitle-correction`),优先用它(交互式、会问术语、
自带 `validate`);②没有 → **先跟用户确认**,再用 `srt_helper.py correct`(只改文字、按原条目重挂
时间戳,长度不符自动回退原始);③校正完用 `subtitle_tool.py validate <raw> <fixed>` 兜底。

### Step 2.5 · 提速(作者语速偏慢时,可选但常用)

交付前统一 **1.1× 提速 + 响度规范化**,音频和字幕**一起**处理(只提速音频不缩 SRT,字幕会越到
后面偏得越离谱):

```bash
ffmpeg -y -i narration-full.mp3 -af "atempo=1.1,loudnorm=I=-14:TP=-1.5:LRA=11" \
  -c:a libmp3lame -q:a 2 narration-full.mp3
# SRT:所有时间戳按 1/1.1 缩放(python 逐条 *1/1.1 重写)
```

### Step 3 · 交付

把 `narration-full.mp3` + **校正后的** SRT 交回 `references/audio.md`「接入成片」流程(切段 →
`sync-durations` → 重排节奏 → 合流 → 出片)。

```
narration.txt ──(本参考)──▶ narration-full.mp3 + narration.srt ──▶ references/audio.md 接入成片 ──▶ 4K MP4
```

---

## 成本(~3 分钟日更)

- **TTS 是大头**:ListenHub credits,~4 credits/分钟。
- 云端 ASR / LLM 校正:走 speech 路时**根本不产生**(自带字幕、通常跳过校正)。
- 走 speech 路只需 ListenHub 一家、一个 key,链路更短更省。

## Gotchas

1. **cue 粒度 = 每个 `scripts` 段一条**。输入按句切多段(脚本已做)→ 自带 SRT 就是逐句 cue、
   时间戳精确。**切句别太粗**(一段塞一大段话 → 一条长 cue,不利于切场景)。
2. **时间轴 > 文字**。要的是准时间戳;错字交给 Step 2 修,别为「识别更准」牺牲时间轴。
3. **校正绝不动时间轴/编号/条数**。speech 路文字已是原文,通常无需校正。
4. **key 走 env,绝不入库**。`LISTENHUB_API_KEY` / `GROQ_API_KEY` / `OPENAI_API_KEY` 都读环境变量。
5. **克隆声音沿用同一 `speakerId`**,系列声音才一致。

## 脚本清单

| 文件 | 作用 |
|---|---|
| `scripts/listenhub-speakers.sh` | 列 speakers(含 `voice-clone-` 克隆声音),选 speakerId |
| `scripts/listenhub-tts.sh` | 文本 → mp3 + srt(speech 主路 / asr fallback) |
| `scripts/scan-heteronyms.sh` | 跑 TTS 前扫多音字 |
| `scripts/srt_helper.py` | buildreq / normalize / insert-pauses / correct / speakers 等子命令 |
| `heteronyms.md` | 多音字高危清单(遇新坑就加) |
