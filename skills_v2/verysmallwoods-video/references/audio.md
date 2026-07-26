# 旁白

旁白音频生成支持以下两种方式，由用户做选择。

1. 用户自行录制，并提供音频文件和 SRT
2. TTS 合成：
    - HyperFrames 内置的 TTS 服务
    - 用户安装的 Skill 提供的 TTS 服务

用户提供的 SRT 文件，基于口播稿内容校对、核准（只改术语/人名/同音字，时间戳不动）。

## 接入成片（切段 + 对齐 + 重排节奏）

拿到音频 + SRT 后：

1. **按段切 per-frame 语音** —— 一帧 = 一个 narration 小节；按 SRT cue 边界把整段音频切成 `assets/voice/NN.mp3`，写 `audio_meta.json`（`voices[{frame,path,duration_s,words}]`，`words` 为帧内相对 cue）。切段/挂载契约见 `/faceless-explainer` 的 `scripts/audio.mjs` + `assemble-index.mjs`。
2. **sync 时长** —— `audio.mjs sync-durations` 把每帧时长对齐音频段，然后组装、注入转场。
3. **重排节奏（关键）** —— 把每帧内部披露重排到真实 cue 时间轴：给每个 frame-worker 本帧逐句的帧内相对秒 + 文本，让每处 reveal 落在被念到那一刻，末尾留 1-2s 定格。差 < ~2s 的帧可不动。
4. **字幕不烧** —— 用校对好的 SRT 在 YouTube 上字幕，不烧进成片。
