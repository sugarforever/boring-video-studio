# Changelog

本项目所有重要变更记录于此。遵循 [Keep a Changelog](https://keepachangelog.com/) 风格;
版本号遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

`npx skills add sugarforever/boring-video-studio` 跟踪的是 `main` 分支最新内容;
tag(如 `v0.1.0`)用于标记发版节点,方便对照。

## [0.1.0] — 2026-06-12

口播视频制作 skills 的首个版本。两个扁平 skill,组成 `文稿/音频 → 4K 成片` 链路。

### Added

- **`listenhub-tts`** —— 口播文本 → 音频 + 字幕(视频制作链路的上游)。
  - **原生 speech 路(首选)**:ListenHub `/v1/speech`,把文稿切句成多段 `scripts`,
    引擎直接回 `audioUrl` + `subtitlesUrl`(**标准 SRT、逐句 cue、文字＝输入原文、零识别错**)。
    只需 `LISTENHUB_API_KEY` 一个 key。
  - **ASR 路(fallback)**:speech 路拿不到字幕时,用 Groq `whisper-large-v3` 或
    OpenAI `whisper-1` 基于音频转写补字幕(需 `GROQ_API_KEY` / `OPENAI_API_KEY`,
    `TTS_MODE=asr` 可强制)。
  - **选音色**:`listenhub-speakers.sh` 拉 `/v1/speakers/list`,列出可用 speaker
    供 `AskUserQuestion` 挑选;系列沿用同一音色保持一致。
  - **字幕校正**:优先调外部 `subtitle-correction` skill;缺失则内置文本级校正
    (`srt_helper.py correct`,只改字、不动时间轴/编号/条数)。
- **`producing-video`** —— 音频 + SRT → 4K MP4。用 HyperFrames(HTML 即视频)按 SRT
  时间轴搭合成、渲染成片。含出片铁律:定时动画必须挂 `tl`、转场只用场景自身 clip-path
  揭幕、字体本地 woff2、响度 `loudnorm` 到 -14 LUFS、空白场景抽帧自检、4K 超采样等。
- `README.md` 写明环境变量与外部 skill 依赖;`LICENSE`(MIT);`.gitignore`。

### Verified

- ListenHub `/v1/speech` 响应契约实网验证(2026-06):
  `{code,data:{audioUrl, subtitlesUrl(.srt), audioDuration, credits}}`。
- 端到端跑通 `文本 → mp3 + srt`,下游 `srt-cues` 解析正常,**仅用 `LISTENHUB_API_KEY`、
  未碰 ASR**(credits=2 / ~16s 测试音频)。

### Notes

- 外部依赖各自独立分发:`subtitle-correction`(来自 `sugarforever/01coder-agent-skills`)、
  `hyperframes` / `hyperframes-cli`(HyperFrames 工具链)。详见 README。
- producing-video 从 `sugarforever/01coder-agent-skills` 迁出;原 PR #12 关闭,该 skill
  不再留在 01coder。

[0.1.0]: https://github.com/sugarforever/boring-video-studio/releases/tag/v0.1.0
