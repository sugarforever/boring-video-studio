# Changelog

本项目所有重要变更记录于此。遵循 [Keep a Changelog](https://keepachangelog.com/) 风格;
版本号遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

`npx skills add sugarforever/boring-video-studio` 跟踪的是 `main` 分支最新内容;
tag(如 `v0.1.0`)用于标记发版节点,方便对照。

## [0.2.0] — 2026-06-18

新增编排 skill,把两个积木升级成「一次会话产出整套物料」。

### Added

- **`blockframe-video`** —— 主题 / 口播稿 → **整套视频物料**(编排 `listenhub-tts` + `producing-video`)。
  补齐两个积木之间最容易漏的「交付完整性」这一层:
  - **交付清单写死、自动验收**:成片(已 `loudnorm` -14 LUFS)+ 字幕 + **全比例封面**
    (3:4 / 9:16 / 16:9 / 16:10 / 4:3)+ 平台文案(`youtube.md` / `bilibili.md`)。
    `scripts/check-deliverables.sh` 收尾验,有 ✗ 不算完成 —— 不再靠人手动提醒「还要 4:3 封面」。
  - **全比例封面一键渲**:`scripts/render-all-covers.sh` 遍历 `cover-*.html` → `cover-*.png`,
    用系统 Chrome headless 2× 超采样(`scripts/render-cover.sh`,无 npm 依赖)。
  - **格式分支**:short(移动竖屏,主 3:4)/ long(横版,主 16:9)走同一流水线,只换画布/分辨率/封面集/节奏。
  - **3:4 的 4K 解法**(实测):`hyperframes render --resolution` 无 3:4 预设;用 `zoom:2` + 翻倍捕获画布
    做真·超采样到 2160×2880(9:16 用 `portrait-4k`、16:9 用 `landscape-4k`)。
  - **assets**:`kit.css`(BlockFrame HyperFrames 组件内核)+ `cover-vertical.html` / `cover-horizontal.html`
    (全比例封面模板)。

### Verified

- 封面渲染:系统 Chrome headless `--screenshot --force-device-scale-factor=2` 实测出 2× 清晰 PNG、本地 woff2 字体正常。
- 3:4 4K:seg-01 实测 `zoom:2` 超采样渲出 2160×2880、文字重栅格化、GSAP seek 渲染正常、非空白。

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

[0.2.0]: https://github.com/sugarforever/boring-video-studio/releases/tag/v0.2.0
[0.1.0]: https://github.com/sugarforever/boring-video-studio/releases/tag/v0.1.0
