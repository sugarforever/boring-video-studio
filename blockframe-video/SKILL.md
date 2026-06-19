---
name: blockframe-video
description: 从一个主题或一份口播稿，一次会话产出一整套 BlockFrame 风格口播视频物料 —— 成片（4K）+ 全比例封面（3:4 / 9:16 / 16:9 / 16:10 / 4:3）+ 平台文案（YouTube / Bilibili），按交付清单验收、缺一不可。编排上游 listenhub-tts（出音频+字幕）与 producing-video（出片），补齐它们之间缺的「完整物料」这一层。支持移动竖屏短视频（short，主 3:4）和横版长视频（long，主 16:9）。当用户说「做个视频 / 短视频 / 用 BlockFrame 做个视频 / 一步到位出整套物料 / 配齐封面」时用本 skill。
---

# BlockFrame-Video · 主题/口播稿 → 一整套视频物料（一次到位）

把一个**主题**或一份**口播稿**，在**一次会话**里变成可直接发布的**整套物料**：画面跟着声音走的 BlockFrame 成片 + **全比例封面** + 平台文案。本 skill 是 **`listenhub-tts`**（上游：文本→音频+字幕）和 **`producing-video`**（下游：音频+字幕→成片）之上的**编排层**，它额外负责那件最容易漏的事 —— **交付清单的完整性**。

**铁律：交付物清单缺一不可。** 每条视频的产物是一个**清单**，不是一个 mp4。封面要**所有比例**（不是只做主封面就完事），平台文案 YouTube + Bilibili 都要。结束前用 `check-deliverables.sh` 验收，**有 ✗ 就没完成**。这条 skill 存在的理由就是：以前要用户手动提醒「还要 4:3 的封面」，现在清单写死、自动配齐。

## 为什么要这一层（动机）

`listenhub-tts` + `producing-video` 已经能出片，但它们只管「文本→音频→一条 mp4」。每次都要人盯着补：封面做几个比例？平台文案写了吗？竖屏的 4K 怎么渲？本 skill 把这些**沉淀成固定流程和清单**，按 `format` 分支一次跑完，不再口头交代。

## 分工

| 谁 | 做什么 |
|---|---|
| **本 skill（你，编排）** | 定题/格式 → 调 `listenhub-tts` → 按 SRT 搭 BlockFrame 合成 → 按格式渲染（含 3:4 的 4K 超采样）→ **配齐全比例封面** → 写平台文案 → **清单验收** |
| `listenhub-tts`（上游） | 口播文本 → `narration-full.mp3` + `narration.srt`（VerySmallWoods 克隆音色，系列沿用同一音色）|
| `producing-video`（下游内核） | HyperFrames 出片的全部铁律（动画挂 `tl`、转场只用 clip-path 揭幕、字体本地 woff2、响度 -14 LUFS、空白帧自检、4K 超采样）—— **本 skill 不重复这些，照搬遵守** |

> 想了解出片细节，读 `producing-video` 的 SKILL.md；想了解配音/字幕，读 `listenhub-tts`。本 skill 只补它们之间的「整套物料」编排。

## 依赖检查（pre-flight）

```bash
npx hyperframes doctor                 # Node ≥ 22 · FFmpeg · Chrome（封面渲染也用同一个 Chrome）
echo "${LISTENHUB_API_KEY:?需要 LISTENHUB_API_KEY}" >/dev/null   # 上游配音用
```

需要在场的 skill：**`listenhub-tts`**、**`producing-video`**，以及后者要的 `hyperframes` / `hyperframes-cli`。封面用系统 **Chrome headless**（无 npm 依赖，`render-cover.sh` 自动找）。key 全走环境变量、**绝不入库**。

---

## 格式配置（一切差异都在这张表）

短/长两种格式**走同一条流水线**，只有这几格不同：

| | **short（移动竖屏，默认）** | **long（横版）** |
|---|---|---|
| 主画布 `#root` | **3:4 · 1080×1440** | **16:9 · 1920×1080** |
| 主封面 | `cover-3x4.png` | `cover-16x9.png` |
| 封面模板 | `cover-vertical.html` | `cover-horizontal.html` |
| 渲染分辨率 | 见下「3:4 的 4K」 | `--resolution landscape-4k`（直接超采样到 3840×2160）|
| 节奏 | 快、信息密度高、~2–3 分钟 | 可舒展、~5–10 分钟 |
| 封面比例集（**都要做全**）| 3:4 · 9:16 · 16:9 · 16:10 · 4:3 | 16:9 · 3:4 · 9:16 · 16:10 · 4:3 |

封面比例集**两种格式都是同一套五个**，只是主封面不同 —— 这正是「别再漏 4:3」的写死之处。

### 3:4 的 4K：`--resolution` 没有 3:4 预设

`hyperframes render --resolution` **只认命名预设**：`landscape`/`portrait`/`landscape-4k`/`portrait-4k`/`square`/`square-4k`。**没有 3:4 的**。所以：

- **16:9 → `landscape-4k`**（=3840×2160）✓ 直接用。
- **9:16 → `portrait-4k`**（=2160×3840）✓ 直接用。
- **3:4 → 没预设 → 用 `zoom:2` 超采样**（已实测可行，2160×2880 真·超采样、文字重栅格化、不是放大）：
  每个 segment 临时生成一份 `index-4k.html`，把捕获画布翻倍 + `#root{zoom:2}`：
  ```bash
  # 在每个 build/seg-XX/ 下：
  sed -e 's/data-width="1080" data-height="1440"/data-width="2160" data-height="2880"/' \
      -e 's|</head>|<style>#root{zoom:2;}</style></head>|' \
      index.html > index-4k.html
  npx hyperframes render -c index-4k.html --quality high --output renders/seg-XX-4k.mp4
  rm index-4k.html          # 渲完即删，别把临时文件留在 build 里
  ```
  > `zoom:2` 会把 1080 宽的内容铺满 2160 捕获画布、并**重新栅格化**（比 `transform:scale` 清晰）；GSAP 的 clip-path/入场动画在 `zoom` 父级下照常驱动，seek 渲染正常。**先在 seg-01 draft 验一帧**（确认 2160×2880、非空白）再批量。

---

## 工作流

### Step 0 · 定题 + 格式

- 拿到**主题**或**口播稿**。没稿先和用户敲定要点（或用研究类 skill 找素材），写成 `narration.txt`（纯文本、按句分行，利于逐句 cue）。
- 定 `format`：移动端 → **short**；横版长视频 → **long**。默认 short。
- 涉及命令行/架构/流程这类内容，**事实必须实证**（真实命令的真实输入输出、真实目录结构），别编 —— 这是系列的招牌。把核验过的事实点记进 `PLAN.md`。
- **口播稿必须过 `personal-chinese-writing-style`，而且过两遍（强制，别省）。** 一遍不够 —— 单遍通常只清掉标点和最扎眼的词，留下声音层的问题（最常见的是把工具 / agent 拟人成「人在打零工」的口语动词：默默干、喊一声、活儿、长在、丢进……）。两遍的分工：
  - **第一遍 · 标点 + 结构**：弯引号 “ ”、半角破折号 ` - `、ASCII 省略号 `......`、中文句子用中文标点；按句分行。
  - **第二遍 · 声音 + 措辞**：翻译腔（worth-X / can't-afford 直译）、网络黑话、以及上面那类拟人化口语动词，换成中性动词（运行 / 触发 / 场景 / 就在 / 放进）。真正生动的口语（「用眼睛去点屏幕」「留一道你自己来确认」）保留。
  - 产物另存 `narration.txt`（喂 TTS 的最终版）；建议同时留一份处理前的草稿，`diff` 一下确认两遍都落了地。口播稿可以口语、可以亲切，但不要拟人到「唠家常」。

起项目（仓库约定成片放 `studio/videos/`）：
```bash
cd <repo>/studio/videos
npx hyperframes init <slug> --example blank --non-interactive    # 目录非空时见 producing-video 的并入技巧
cd <slug> && mkdir -p fonts audio build
cp <本 skill>/assets/kit.css build/_template/kit.css             # BlockFrame 内核，按本期增删
```
字体下到 `fonts/`（Noto Sans SC + Space Grotesk + JetBrains Mono，见 producing-video）。

### Step 1 · 上游：音频 + 字幕（`listenhub-tts`）

按 `listenhub-tts` 流程，用 **VerySmallWoods 克隆音色**（系列沿用，保持声音一致）出 `audio/narration-full.mp3` + `audio/narration.srt`。**时间轴是字幕的命根**，只做文本级校正、绝不动时间轴。

### Step 2 · 按 SRT 搭 BlockFrame 合成（`producing-video` 内核）

- `#root` 画布按格式设（short 1080×1440 / long 1920×1080）。
- 一条连续 `<audio>` clip 作时钟；每个场景一个全画布 `.scene.clip`，**场景开始时间 = 它首条 cue 的时间戳**。
- 复用 `kit.css` 的 BlockFrame 组件（chrome / 标题 / hl 高亮块 / 终端窗口 / 卡片 / chips / grid），按本期加自己的小部件。
- **照搬 `producing-video` 的全部 gotcha**：定时动画一律挂注册到 `window.__timelines["main"]` 的 `tl`（**绝不裸 `gsap.from/to`**）；转场只用 incoming 场景自身 clip-path 揭幕；强调色当标点、彩块上压墨色字；CJK 在彩块里给足 `~0.2em` 竖直 padding。
- 长片建议**按段分目录** `build/seg-01..NN/`，每段一份 `index.html` 配自己那几条 cue（短片也可单文件）。

校对（每次改完都跑）：
```bash
npx hyperframes lint        # 0 error
npx hyperframes validate    # WCAG AA 对比度
npx hyperframes inspect --samples 30    # 版面溢出；装饰出血标 data-layout-ignore
```

### Step 3 · 渲染（按格式分支）

- **long（16:9）**：`npx hyperframes render --resolution landscape-4k --quality high --output renders/<slug>-4k.mp4`
- **short 9:16**：`--resolution portrait-4k --quality high`
- **short 3:4**：无预设 → 走上面「3:4 的 4K」的 `zoom:2` 逐段渲染，再 `ffmpeg concat` 拼接。
- **响度规范化**（口播常偏安静，视频流不重渲）：
  ```bash
  ffmpeg -i renders/<slug>.mp4 -af loudnorm=print_format=summary -f null -    # 量
  ffmpeg -y -i renders/<slug>.mp4 -af loudnorm=I=-14:TP=-1.5:LRA=11 -c:v copy -c:a aac -b:a 192k renders/<slug>-loud.mp4
  ```
- 验收：`ffprobe` 确认 video(h264)+audio(aac) 两轨、时长=音频时长；抽帧确认每场落在 cue 上、跨场景帧大小无异常雷同（防空白场景）。同时把 `renders/<slug>.srt`（= 校正后字幕）放好。

### Step 4 · 配齐全比例封面（**别漏任何一个**）

复用 BlockFrame 系列封面设计。从模板起：

```bash
cp <本 skill>/assets/cover-vertical.html   cover-3x4.html      # 填内容（«PLACEHOLDER»）
cp cover-3x4.html cover-9x16.html                              # 改 .cover 高 → 1920
cp <本 skill>/assets/cover-horizontal.html cover-16x9.html     # 填内容
cp cover-16x9.html cover-16x10.html                            # 改 .cover 高 → 1200
cp cover-16x9.html cover-4x3.html                              # 改 .cover 宽 → 1440
```
封面 HTML 引用 `fonts/`（与成片同一套本地 woff2，已在 Step 0 下好）。**一条命令渲染全套**：

```bash
bash <本 skill>/scripts/render-all-covers.sh .     # 把每个 cover-*.html 渲成 cover-*.png（2× 超采样）
```
> 维度映射写在脚本里（3x4=1080×1440 / 9x16=1080×1920 / 16x9=1920×1080 / 16x10=1920×1200 / 4x3=1440×1080）。新增比例：丢一个 `cover-<ratio>.html` 并在脚本 `dims_for()` 加一行。每个比例都 `Read` 出来的 PNG 看一眼，确认字体加载、无溢出。

### Step 5 · 平台文案

写 `youtube.md` + `bilibili.md`（沿用系列模板：标题、简介、章节时间戳、链接、标签）。从 `narration.srt` 的 cue 时间生成**章节时间戳**。带上用户的推广位（油管会员 / B 站赞助 / 知识星球 / Twitter）。

### Step 6 · 清单验收（收尾必跑）

```bash
bash <本 skill>/scripts/check-deliverables.sh <slug-dir> short   # 或 long
```
全 ✓ 才算完成；有 ✗ 回去补齐。**不要自动提交**（除非用户明确要）。

---

## 交付清单（这条 skill 的「完成」定义）

- [ ] `renders/<slug>.mp4`（已 `loudnorm` 到 -14 LUFS）+ `renders/<slug>.srt`
- [ ] 封面**五个比例全有**：`cover-3x4.png` `cover-9x16.png` `cover-16x9.png` `cover-16x10.png` `cover-4x3.png`（主封面按格式：short=3:4 / long=16:9）
- [ ] `youtube.md` + `bilibili.md`（含章节时间戳 + 推广位）
- [ ] `PLAN.md`（含实证过的事实点）+ `narration.txt`
- [ ] 口播稿过了 `personal-chinese-writing-style` **两遍**（标点一遍 + 声音一遍，见 Step 0）
- [ ] `check-deliverables.sh` 全 ✓
- [ ] `lint` 0 error · `validate` 全过 · `inspect` 0 真实溢出
- [ ] 抽帧确认每场对得上 cue、无空白场景；`ffprobe` 两轨齐、时长对
- [ ] 未自动提交

## Gotchas（本层特有，叠加在 producing-video 之上）

1. **封面是「一套」不是「一张」。** 永远跑 `render-all-covers.sh` 出全比例，再 `check-deliverables.sh` 验。这是本 skill 的头号存在意义 —— 别又只做主封面。
2. **3:4 没有 4K 预设。** 别试 `--resolution 2160x2880`（会被拒）。用 `zoom:2` 超采样法（Step 3），先验一帧再批量。9:16 用 `portrait-4k`、16:9 用 `landscape-4k`，这两个有预设。
3. **临时 `index-4k.html` 渲完即删。** 别把超采样临时文件留在 `build/` 里。
4. **封面渲染依赖本地字体。** `cover-*.html` 引用 `fonts/`，必须和成片同一套 woff2 一起在项目里；缺字体会渲出 tofu —— 渲完每张都 `Read` 看一眼。
5. **系列一致性。** 音色、配色、字体、页眉页脚、封面版式都沿用系列；新一期延续而非另起。
6. **事实实证。** 命令/架构/流程类内容，真实跑过再放进画面，别编输入输出。
7. **口播稿过两遍 `personal-chinese-writing-style`，不是一遍。** 单遍会放过声音层的拟人化口语动词（默默干、喊一声、活儿、长在、丢进……）。第一遍清标点、第二遍清声音；`diff` 草稿确认两遍都落地（见 Step 0）。
8. **producing-video 的 12 条 gotcha 全部生效**（尤以「动画必须挂 `tl`」「转场只用 clip-path 揭幕」最常翻车）——本 skill 不复述，照办。

## 超出范围

- **配音/字幕**（文本→音频+SRT）：是 `listenhub-tts` 的活。
- **出片铁律细节**（HyperFrames 合成/渲染）：是 `producing-video` 的活，本 skill 照搬。
- **声音克隆**：用支持克隆的云端 TTS，只换「出声那一步」，下游不变。
- **发布上传**：本 skill 只产物料、不上传平台。
