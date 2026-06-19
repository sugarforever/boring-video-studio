# boring-video-studio

口播视频制作的 Agent Skills 合集。把一个**主题**或一段**口播文本**,变成画面跟着声音走的 4K 成片 —— 既可以用两个积木 skill 自己拼,也可以用编排 skill **一次会话产出整套物料**(成片 + 全比例封面 + 平台文案)。

为 [Claude Code](https://claude.com/claude-code) 等支持 Agent Skills 的工具准备。

## 安装

```bash
npx skills add sugarforever/boring-video-studio
```

> **字幕校正依赖**:`listenhub-tts` 在校正环节会**优先调用**一个独立的字幕校正 skill。
> 强烈建议一并安装:
> ```bash
> npx skills add sugarforever/01coder-agent-skills      # 含 subtitle-correction
> ```
> 没装也能跑——会退回到内置的、需用户确认的文本级校正(`srt_helper.py correct`)。

## 包含的 skills

| Skill | 输入 → 输出 | 用途 |
|---|---|---|
| **`blockframe-video`** | 主题 / 口播稿 → **整套物料** | **编排层**:一次会话产出成片 + **全比例封面**(3:4 / 9:16 / 16:9 / 16:10 / 4:3) + 平台文案(YouTube / Bilibili),按交付清单验收、缺一不可。BlockFrame 设计系统;支持移动竖屏短视频(short,主 3:4)与横版长视频(long,主 16:9) |
| **`listenhub-tts`** | 口播文本 → `narration-full.mp3` + `narration.srt` | 上游积木:选音色(ListenHub speakers)→ 原生 `/v1/speech` 出音频 + **自带字幕**(首选,文字零识别错);云端 ASR(Groq/OpenAI Whisper)作 fallback + 文本级校正 |
| **`producing-video`** | 音频 + SRT → 4K MP4 | 下游积木:用 HyperFrames(HTML 即视频)按 SRT 时间轴搭合成、渲染成片 |

`blockframe-video` 编排另外两个积木,补齐它们之间「整套物料」这一层:

```
                  ┌──────────────── blockframe-video(编排:全比例封面 + 平台文案 + 清单验收)────────────────┐
主题 / 口播稿 ──▶ │ narration.txt ─[listenhub-tts]▶ mp3 + srt ─[producing-video]▶ 4K MP4 + 全比例封面 + 文案 │ ──▶ 整套物料
                  └──────────────────────────────────────────────────────────────────────────────────────┘
```

- 想**一步到位出整套物料**(系列日更/短视频) → 用 `blockframe-video`。
- 只想要**积木**自己拼:只有文本 → 先 `listenhub-tts` 再 `producing-video`;已有音频 + SRT → 直接 `producing-video`。

## 依赖

### 环境变量

全部从环境变量读取,**绝不写进仓库**(`.gitignore` 已屏蔽 `.env`)。只有 `listenhub-tts` 用到 key;`producing-video` 不需要任何 key。

| 变量 | 用于 | 必需性 | 格式 / 获取 |
|---|---|---|---|
| `LISTENHUB_API_KEY` | `listenhub-tts` | **必须** | `lh_sk_...` · <https://listenhub.ai/settings/api-keys> |
| `GROQ_API_KEY` | `listenhub-tts`(ASR fallback) | 可选¹ | `gsk_...` · <https://console.groq.com/keys> |
| `OPENAI_API_KEY` | `listenhub-tts`(ASR fallback) | 可选¹ | `sk-...` · <https://platform.openai.com/api-keys> |

¹ 默认走 ListenHub 原生 `/v1/speech` 拿自带字幕,**只需 `LISTENHUB_API_KEY`**。仅当 speech 路失败、需降级到云端 ASR 时,才要 `GROQ_API_KEY` **或** `OPENAI_API_KEY`(二选一,`ASR_PROVIDER=groq|openai` 指定)。

设置示例:

```bash
export LISTENHUB_API_KEY=lh_sk_xxx
export GROQ_API_KEY=gsk_xxx          # 可选,仅 ASR fallback
```

### 外部 skills

| Skill | 被谁用 | 必需性 | 来源 / 缺失行为 |
|---|---|---|---|
| `subtitle-correction` | `listenhub-tts`(字幕校正) | 推荐 | `npx skills add sugarforever/01coder-agent-skills` · 缺失时退回内置、需用户确认的文本级校正(`srt_helper.py correct`) |
| `hyperframes` + `hyperframes-cli` | `producing-video`(搭合成 + 渲染) | **必须** | `npx hyperframes skills` 安装;缺失则无法出片 |

`producing-video` 还需 [HyperFrames](https://www.hyperframes.dev) 本机工具链:

```bash
npx hyperframes doctor      # 需要 Node ≥ 22 · FFmpeg · Chrome
npx hyperframes skills      # 安装 hyperframes / hyperframes-cli skills
```

## 成本(~3 分钟日更)

- **TTS 是大头**:ListenHub ~4 credits/分钟。
- 云端 ASR(~半美分到两美分)、LLM 文本校正(~1 美分):**可忽略**。
- 渲染本地、**零成本**。

## License

MIT
