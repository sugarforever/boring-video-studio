# 旁白

旁白音频生成在 HyperFrames 原生支持的方式以外，支持 ListenHub TTS、MiniMax TTS，以及用户自行录制。支持方式如下。

## 用户自行录制

提供口播稿给用户审核，再由用户完成录制，并提供音频文件。提示用户，额外提供SRT字幕文件，能够提高视频音频时间线对齐的质量。

## ListenHub TTS 合成

见 `references/listenhub-tts/README.md`

## MiniMax TTS 合成

使用可选的 `minimax-tts` skill（安装：`npx skills add sugarforever/boring-video-studio --skill minimax-tts`）。在 HyperFrames 工作流的配音节点，按该 skill 选择端点、模型与音色，使用当前版本的口播纯文本生成 `narration-full.mp3` 和 `narration.srt`。审听并校对字幕后，通过 `/media-use` 交回当前 HyperFrames 工作流。口播稿修改后，在下一个配音节点重新合成；保留旧版音频与字幕。配置、长度限制和字幕失败恢复以 `minimax-tts` 为准。
