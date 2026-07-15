# boring-video-studio

**把一个主题、或一段口播文本,变成画面跟着声音走的 4K 成片 —— 外加全比例封面和平台文案,一次会话交付。**

一套面向**口播视频日更 / 系列**的 Agent Skills 合集。既可以用两个积木 skill 自己拼(文本 → 音频 → 成片),也可以用编排 skill **一次会话产出整套物料**(成片 + 五比例封面 + 平台文案)。声音跟着 SRT 走、画面跟着声音走,渲染本地零成本。

为 [Claude Code](https://claude.com/claude-code) 等支持 [Agent Skills](https://skills.sh) 的工具准备。

[![skills.sh](https://skills.sh/b/sugarforever/boring-video-studio)](https://skills.sh/sugarforever/boring-video-studio)

## 快速开始

```bash
npx skills add sugarforever/boring-video-studio
```

装好后按你手上有什么直接开口(见下方[「怎么选」](#怎么选从你手上有什么开始)):

- 「帮我把这篇早读做成一期视频」→ 走编排层 `blockframe-video`
- 「把这段音频 + 字幕做成成片」→ 走积木 `producing-video`
- 「给某 A 股公司做一期财经视频」→ 走 `finance-stock-video`

> **字幕校正依赖**:`listenhub-tts` 在校正环节会**优先调用**一个独立的字幕校正 skill,强烈建议一并安装:
> ```bash
> npx skills add sugarforever/01coder-agent-skills      # 含 subtitle-correction
> ```
> 没装也能跑——会退回到内置的、需用户确认的文本级校正(`srt_helper.py correct`)。

## 目录结构

Skills 按**三层职责**分目录(安装时会被展平为各自独立的 skill,分类只是源码组织):

```
skills/
├─ orchestration/            编排层 · 一次会话产出整套物料
│  ├─ blockframe-video/       主题 / 口播稿 → 成片 + 全比例封面 + 平台文案
│  └─ finance-stock-video/    财经选题 → 核实财报 → 整套财经视频物料
├─ building-blocks/          积木 · 单一职责,可自己拼
│  ├─ listenhub-tts/          口播文本 → narration-full.mp3 + narration.srt
│  └─ producing-video/        音频 + SRT → 4K MP4(HyperFrames:HTML 即视频)
└─ assets/                   配料 · 封面与品牌素材
   ├─ cover-design/           一条视频 / 一篇文章 → 整套封面
   └─ brand-icons/            品牌名 → 官方 SVG logo
```

## 包含的 skills

### 编排层 · orchestration

| Skill | 输入 → 输出 | 用途 |
|---|---|---|
| **`blockframe-video`** | 主题 / 口播稿 → **整套物料** | 一次会话产出成片 + **全比例封面**(3:4 / 9:16 / 16:9 / 16:10 / 4:3) + 平台文案(YouTube / Bilibili),按交付清单验收、缺一不可。BlockFrame 设计系统;支持移动竖屏短视频(short,主 3:4)与横版长视频(long,主 16:9)。 |
| **`finance-stock-video`** | 一个公司(代码)/ 财经主题 → **整套财经视频物料** | **财经领域层**(坐在 `blockframe-video` 之上):给个 A 股公司或「某股为什么涨」这类主题,先**核实官方财报原件**,再出客观脚本(提问开头 / 章节化 / 不构成投资建议)→ 配音 → 横竖版成片 + 4 比例封面 + 平台文案。管财经独有的**数据获取核实、客观口径红线、财报内容模板、系列身份**。 |

### 积木 · building-blocks

| Skill | 输入 → 输出 | 用途 |
|---|---|---|
| **`listenhub-tts`** | 口播文本 → `narration-full.mp3` + `narration.srt` | 上游积木:选音色(ListenHub speakers)→ 原生 `/v1/speech` 出音频 + **自带字幕**(首选,文字零识别错);云端 ASR(Groq/OpenAI Whisper)作 fallback + 文本级校正;**跑 TTS 前多音字扫描**(`scan-heteronyms.sh`,防「调用」读成 tiáo)。 |
| **`producing-video`** | 音频 + SRT → 4K MP4 | 下游积木:用 HyperFrames(HTML 即视频)按 SRT 时间轴搭合成、渲染成片。内含动效图鉴(15 类)、换场动词表、运行时适配器、视觉效果配方,全部确定性 / seek-safe。 |

### 配料 · assets

| Skill | 输入 → 输出 | 用途 |
|---|---|---|
| **`cover-design`** | 一条视频 / 一篇文章 → **整套封面** | 封面的唯一归属地(`blockframe-video` / `finance-stock-video` 都委托到这里)。用 **codex-cli 调 gpt-image** 生成手绘编辑风封面:**画风固定、构图按主题变、版式按比例变**。自带 codex 出图 wrapper、尺寸/比例校验,以及**右下徽标区 / 竖版 1:1 宫格裁切 / 120px 缩略图可读性**三道检查。需要精确数字或真实商标时,兜底走 HTML→PNG。 |
| **`brand-icons`** | 品牌名 → 官方 SVG logo | 从 LobeHub Icons CDN 取真实的 AI / 公司品牌标(OpenAI、Codex、Anthropic、GLM/智谱、Gemini……)放进封面 / 合成,不手画不 AI 生成。 |

## 怎么选:从你手上有什么开始

这套 skill 的分工是「音频和 SRT 是唯一事实源」——**声音先定,画面跟着走**。从你手上已有的东西倒推该进哪一环:

- **只有一个主题 / 一段口播稿,想一步到位出整套物料**(系列日更 / 短视频)→ 用 **`blockframe-video`**。它编排下面三个积木,补齐「整套物料」这一层:配音、成片、五比例封面、平台文案,按交付清单缺一不可。
- **财经选题**(某 A 股公司、「某股为什么涨」)→ 用 **`finance-stock-video`**。它坐在 `blockframe-video` 之上,多做一件最要紧的事:**先核实官方财报原件**,再出客观、不构成投资建议的脚本。
- **只想要积木自己拼**:
  - 只有文本 → 先 **`listenhub-tts`**(文本 → 音频 + 字幕),再 **`producing-video`**(音频 + SRT → 成片)。
  - 已经有音频 + SRT → 直接 **`producing-video`**。
- **只要封面 / 只要品牌标** → 直接用 **`cover-design`** / **`brand-icons`**。

```
                  ┌──────────────── blockframe-video(编排:清单验收,封面委托 cover-design)────────────────┐
主题 / 口播稿 ──▶ │ narration.txt ─[listenhub-tts]▶ mp3 + srt ─[producing-video]▶ 4K MP4                │ ──▶ 整套物料
                  │                                            └[cover-design]▶ 五比例封面 + 平台文案      │
                  └──────────────────────────────────────────────────────────────────────────────────────┘
```

## 依赖

### 环境变量

全部从环境变量读取,**绝不写进仓库**(`.gitignore` 已屏蔽 `.env`)。只有 `listenhub-tts` 用到 key;`producing-video` 不需要任何 key。

| 变量 | 用于 | 必需性 | 格式 / 获取 |
|---|---|---|---|
| `LISTENHUB_API_KEY` | `listenhub-tts` | **必须** | `lh_sk_...` · <https://listenhub.ai/settings/api-keys> |
| `GROQ_API_KEY` | `listenhub-tts`(ASR fallback) | 可选¹ | `gsk_...` · <https://console.groq.com/keys> |
| `OPENAI_API_KEY` | `listenhub-tts`(ASR fallback) | 可选¹ | `sk-...` · <https://platform.openai.com/api-keys> |

¹ 默认走 ListenHub 原生 `/v1/speech` 拿自带字幕,**只需 `LISTENHUB_API_KEY`**。仅当 speech 路失败、需降级到云端 ASR 时,才要 `GROQ_API_KEY` **或** `OPENAI_API_KEY`(二选一,`ASR_PROVIDER=groq|openai` 指定)。

```bash
export LISTENHUB_API_KEY=lh_sk_xxx
export GROQ_API_KEY=gsk_xxx          # 可选,仅 ASR fallback
```

### 外部 skills

| Skill | 被谁用 | 必需性 | 来源 / 缺失行为 |
|---|---|---|---|
| `personal-chinese-writing-style` | `blockframe-video` / `finance-stock-video`(口播稿处理) | **必须** | `npx skills add sugarforever/01coder-agent-skills` · 口播稿要过它**两遍**(标点一遍 + 声音一遍),是系列招牌,别省 |
| `subtitle-correction` | `listenhub-tts`(字幕校正) | 推荐 | `npx skills add sugarforever/01coder-agent-skills` · 缺失时退回内置、需用户确认的文本级校正(`srt_helper.py correct`) |
| `hyperframes` + `hyperframes-cli` | `producing-video`(搭合成 + 渲染) | **必须** | `npx hyperframes skills` 安装;缺失则无法出片 |

`cover-design` 需要 **codex-cli**(出图,用 Codex 订阅鉴权)和 **python3 + Pillow**(尺寸 / 安全区检查 + 证据图);兜底的 HTML→PNG 还需要系统 **Chrome**。**codex-cli 的必需性看用法**:出封面(单独跑 `cover-design`,或走 `blockframe-video` / `finance-stock-video` —— 封面五比例是铁律)就**必须**有;只有完全不生成封面时才用不上。需要精确数字 / 真实商标的封面走 HTML→PNG,那条兜底路不用 codex,但用 Chrome。

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
