# 旁白 · TTS 或自己录（每期让我选）

音频和 SRT 是画面时间轴的事实源。两条路，开局先问我走哪条。

## 路 A · 我自己录（默认，效果最好）

我交来 `音频文件 + SRT`（SRT 一般是剪映识别的，术语/人名常有误）。

### A1. 校对 SRT（基于口播稿）

- **只改术语/人名/同音字**（Claude Code、Thariq、unhobbling、SKILL.md、CLAUDE.md、ToolSearch、codex…），用口播稿 `narration.txt` 当拼写参照。
- **保留我实际说的话** - 我录的时候常即兴改词，别硬套 narration.txt 逐字。
- **时间戳一律不动**。
- 产物存 `narration.srt`（校对版），音频转 `narration-full.mp3`（`ffmpeg -q:a 3`）。

### A2. 按段切 per-frame 语音 + audio_meta

pipeline 要**每帧一段语音**（`assemble` 按帧挂 `<audio>`，时长 = 帧时长）。所以：
- 把每帧映射到它那一段 narration 的 SRT cue 区间（一帧 = 一个 narration 小节）。
- 按 cue 边界用 `ffmpeg -ss/-t` 把整段音频切成 `assets/voice/NN.mp3`。
- 写 `audio_meta.json`：`{ bgm:null, sfx:[], voices:[ {frame, path, duration_s, words:[{text,start,end}]} ] }`，`words` 是本帧逐句 cue 的**帧内相对**时间。封面帧无语音，只给 `duration_s`（片头静音段）。

### A3. sync-durations + 重排节奏

```bash
node <faceless-explainer>/scripts/audio.mjs sync-durations --audio-meta ./audio_meta.json --storyboard ./STORYBOARD.md
```

把每帧时长对齐到音频段。**然后必须重拍内部节奏**（见下），否则动效走完会长时间定格、旁白在静态画面上继续讲。

### A4. 重排节奏（把披露对齐真实 cue）

从 `audio_meta.json` 导出每帧逐句的**帧内相对秒 + 文本**，发给对应 frame-worker，让它把内部 Scene 的 reveal 重排到「每处内容在被念到那一刻才现」，最后留 1-2s 定格。差 < ~2s 的帧可不动。改完 **re-assemble + 重注入转场**。

## 路 B · TTS 合成

只有口播文本、不想自己录时走这条。用 `listenhub-tts`（`skills/building-blocks/listenhub-tts/`）：文本 → `narration-full.mp3` + `narration.srt`（引擎自带字幕、零识别错）。之后接入方式和路 A 的 A2 起一致（切段 / audio_meta / sync / 重排）。

> 中文口播尤其用 listenhub（HyperFrames 自带 Kokoro 不支持中文）。选音色/换声音也在这。

## 字幕：不烧进成片

两条路都**不把字幕烧进 HyperFrames 成片** - 我在 YouTube 上用校对好的 `narration.srt` 上字幕。成片留底部字幕安全区即可。（若哪期确实要自包含带字幕的 MP4，再单独说，用 `captions.mjs` 烧。）

## 相关

- audio_meta / 切段 / sync-durations 的脚本契约：faceless-explainer 的 `scripts/audio.mjs` + `assemble-index.mjs`（`voices[]` 挂 track 10）。
- 见 memory [[feedback_user_audio_srt_repace]]。
