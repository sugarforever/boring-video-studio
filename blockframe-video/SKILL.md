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
| `cover-design`（封面） | codex+gpt-image 生成手绘编辑风封面：主题→构图配方 + 每比例版式 + 平台安全区/1:1 裁切/120px 三道检查 —— **本 skill 不重复，直接委托** |
| `producing-video`（下游内核） | HyperFrames 出片的全部铁律（动画挂 `tl`、转场只用 clip-path 揭幕、字体本地 woff2、响度 -14 LUFS、空白帧自检、4K 超采样）—— **本 skill 不重复这些，照搬遵守** |

> 想了解出片细节，读 `producing-video` 的 SKILL.md；想了解配音/字幕，读 `listenhub-tts`。本 skill 只补它们之间的「整套物料」编排。

## 依赖检查（pre-flight）

```bash
npx hyperframes doctor                 # Node ≥ 22 · FFmpeg · Chrome（出片用）
codex --version                        # 封面出图用（cover-design）
echo "${LISTENHUB_API_KEY:?需要 LISTENHUB_API_KEY}" >/dev/null   # 上游配音用
```

需要在场的 skill：**`listenhub-tts`**、**`producing-video`**、**`cover-design`**（封面全套），以及 `producing-video` 要的 `hyperframes` / `hyperframes-cli`。封面走 `cover-design` 的 codex 出图（用 Codex 订阅鉴权，不读 OPENAI_API_KEY）。key 全走环境变量、**绝不入库**。

---

## 格式配置（一切差异都在这张表）

短/长两种格式**走同一条流水线**，只有这几格不同：

| | **short（移动竖屏，默认）** | **long（横版）** |
|---|---|---|
| 主画布 `#root` | **3:4 · 1080×1440** | **16:9 · 1920×1080** |
| 主封面 | `cover-3x4.png` | `cover-16x9.png` |
| 封面版式 | `cover-design` 的 3:4 竖版版式 | `cover-design` 的 16:9 横版版式 |
| 渲染分辨率 | 见下「3:4 的 4K」 | `--resolution landscape-4k`（直接超采样到 3840×2160）|
| 节奏 | 快、信息密度高、~2–3 分钟 | 可舒展、~5–10 分钟 |
| 封面比例集（**都要做全**）| 3:4 · 9:16 · 16:9 · 16:10 · 4:3 | 16:9 · 3:4 · 9:16 · 16:10 · 4:3 |

封面比例集**两种格式都是同一套五个**，只是主封面不同 —— 这正是「别再漏 4:3」的写死之处。

> **竖版固定 3:4（1080×1440），不要做 9:16。** 9:16（1080×1920）太瘦高，移动端观看体验差、信息密度低；3:4 在抖音 / 小红书 / 视频号都正常播放，是竖版主画布的唯一选择。9:16 只作为**封面比例之一**保留（Shorts 缩略图等），但**视频本体不出 9:16**。这是用户明确定下的偏好，别再漂回 9:16。

### 3:4 的 4K：`--resolution` 没有 3:4 预设

`hyperframes render --resolution` **只认命名预设**：`landscape`/`portrait`/`landscape-4k`/`portrait-4k`/`square`/`square-4k`。**没有 3:4 的**。所以：

- **16:9 → `landscape-4k`**（=3840×2160）✓ 直接用，真·2× DPR 超采样。
- **3:4（竖版默认）→ 没预设 → 原生渲 1080×1440 + lanczos 放大到 2160×2880**（可靠路径）：
  ```bash
  cd build-v
  npx hyperframes render -c index.html --quality high --output /tmp/v-native.mp4   # 原生 1080×1440
  # lanczos 放大 + loudnorm 一步到位（要重编码视频，因为变了分辨率）
  ffmpeg -y -i /tmp/v-native.mp4 -vf "scale=2160:2880:flags=lanczos" \
    -af loudnorm=I=-14:TP=-1.5:LRA=11 -c:v libx264 -preset slow -crf 16 -pix_fmt yuv420p -c:a aac -b:a 192k \
    renders/<slug>-v-4k.mp4
  ```
  > **诚实说**：这是「高质量原生渲染 + lanczos 放大」，不是真·超采样。但 `--quality high` 的原生 1080×1440 本身已经很清晰（1080 宽 = 手机竖屏满分辨率），放大到 2160×2880 主要是抗平台二压、文件更大更耐看。3:4 没有真 4K 预设，这是当前最稳的路。

> **⚠️ 别用 `zoom:2` 超采样法（已废弃）。** 曾经推荐过给 `#root` 加 `zoom:2` + 翻倍 `data-width/height` 做「真超采样」—— **实测它会搞坏所有用 `bottom:` 定位的绝对元素**（页脚、`.wrap` 的 `bottom`、封面底部 chips 全部错位 / 消失）。早期「验证」只看了「非空白」、没核对底部内容，是个假阳性。**单文件多场景合成尤其会翻车。** 老老实实走上面的「原生 + lanczos」。

> （9:16 有 `portrait-4k` 预设，但**视频本体不出 9:16**，见格式表的说明；只有万一要单独出 9:16 封面/特例时才用。）

---

## 项目目录结构（一个选题 = 一个项目目录，别散成多个兄弟目录）

**铁律：一个选题一个项目目录，所有物料收在里面。** 别散成 `<slug>-cn` / `<slug>-3x4` / `<slug>-16x9` 这种平级兄弟目录（散乱、易漏、难归档 —— 踩过）。横竖两版是**同一项目的两个 `build-*` 子目录**，共用上层 `audio/` `assets/` `fonts/`。

```
<repo>/studio/videos/<YYYYMMDD-slug>/          # ← 一个项目，就这一个目录
├── PLAN.md / research.md      # 要点核验 / 备料（财经类必有 research.md，逐项标源）
├── script.md                 # 脚本（画面 cue + 口播 + 章节 + 出处）
├── narration.txt             # 纯口播（喂 TTS 的最终版）
├── audio/
│   ├── narration-full.mp3
│   ├── narration.srt
│   └── cue-starts.json       # 逐句精确时间轴（逐句合成时产出）
├── assets/                   # 素材：官方截图 / 产品图 / logo（官方来源，带出处）
├── fonts/                    # 本地 woff2 一份（build-* 里软链引用，不重复拷）
├── build-h/                  # 横版 16:9 合成（独立 hyperframes 项目）
├── build-v/                  # 竖版 3:4 合成（独立 hyperframes 项目）
├── renders/                  # 只留母版 + 响度版（中间自检渲染删掉）
│   ├── <slug>-h-4k.mp4   <slug>-h-4k-14lufs.mp4
│   └── <slug>-v.mp4      <slug>-v-14lufs.mp4
├── covers/
│   │                                            # 生成图，见 cover-design
│   └── cover-16x9.png  cover-4x3.png  cover-3x4.png  cover-9x16.png   # 全比例
├── publish.md                # 标题候选 / 描述 / 标签 / 章节时间戳（横竖通用）
└── blog.md + blog-images/    # 配套文章（如有）
```

规则：
- **`build-h` / `build-v` 各是独立 hyperframes 项目**（各有 `index.html` + `hyperframes.json` + `meta.json`），但**音频 / 字体 / 素材共用上层一份**，用软链引进去 —— 保证两版同一份音频时间轴、不重复占空间：
  ```bash
  cd build-v && ln -s ../fonts fonts && ln -s ../audio audio && ln -s ../assets assets
  ```
- **`renders/` 只留最终物**：横版 4K 母版 + `-14lufs`，竖版母版 + `-14lufs`；`standard` 自检渲染验完即删。
- **封面 PNG 收在 `covers/`**，codex 生成图立刻从 `~/.codex/generated_images/` 拷进来，**别落项目外 / 仓库根**。
- 命名统一：`<slug>-h-*`（横）/ `<slug>-v-*`（竖）。
- 收尾用 `scripts/check-deliverables.sh` 对着这个结构验收，缺一不可。

> 只出一版时就只建对应的一个 `build-*`；只出文章时省掉 `build-*`/`renders/`，保留 `assets/` + `blog.md` + `blog-images/`。

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
- **第三遍 · 多音字扫描（喂 TTS 前必做）。** 风格处理完、跑 `listenhub-tts` 之前，扫一遍多音字 —— TTS 常把「调用」的「调」读成 tiáo（该 diào），用户实际踩过。跑 `listenhub-tts` 的 `scripts/scan-heteronyms.sh narration.txt`，对每个 `⚠` 按梯子修：① 扩成无歧义的词（`决定调哪个` → `决定调用哪个`）→ ② 换说法 → ③ 漏到成片再单句挖补。改 `narration.txt` 音频和字幕一起受益。细节见 `listenhub-tts` 的「Step 0.5 · 多音字扫描」。

起项目（仓库约定成片放 `studio/videos/`，结构见上「项目目录结构」）：
```bash
cd <repo>/studio/videos && mkdir -p <slug>/{audio,assets,fonts} && cd <slug>
# 字体下到根 fonts/（Noto Sans SC + Space Grotesk + Inter + JetBrains Mono，见 producing-video）
# 每个要出的画幅建一个 build-*，各是独立 hyperframes 项目，软链共用上层音频/字体/素材：
for b in build-h build-v; do
  npx hyperframes init "$b" --example blank --non-interactive
  ( cd "$b" && rm -rf fonts audio assets && ln -s ../fonts fonts && ln -s ../audio audio && ln -s ../assets assets )
done   # 只出一版就只建对应的一个
```

### Step 1 · 上游：音频 + 字幕（`listenhub-tts`）

按 `listenhub-tts` 流程，用 **VerySmallWoods 克隆音色**（系列沿用，保持声音一致）出 `audio/narration-full.mp3` + `audio/narration.srt`。**时间轴是字幕的命根**，只做文本级校正、绝不动时间轴。

### Step 2 · 按 SRT 搭 BlockFrame 合成（`producing-video` 内核）

- `#root` 画布按格式设（short 1080×1440 / long 1920×1080）。
- 一条连续 `<audio>` clip 作时钟；每个场景一个全画布 `.scene.clip`，**场景开始时间 = 它首条 cue 的时间戳**。
- 复用 `kit.css` 的 BlockFrame 组件（chrome / 标题 / hl 高亮块 / 终端窗口 / 卡片 / chips / grid），按本期加自己的小部件。
- **视觉效果**（聚光 / 磨砂玻璃 / 背景模糊 / 放大镜 / 材质大字 / 光带扫字 / 半调底）：机制见 `producing-video/references/visual-effects.md`（设计中立）；BlockFrame 的皮肤填值与现成片段见 **`references/effects-blockframe.md`**。
- **动效 / 换场 / 命令式引擎**：编舞看 `producing-video/references/motion-patterns.md`（15 类）；想要比 clip-path 揭幕更电影感的换场（穿越变焦 / 顺势切 / 同底硬切）看 `references/scene-transitions.md`；WebGL/Canvas/Lottie 看 `references/runtime-adapters.md`（代理时钟桥）——三者都 seek-safe。
- **系列复用（可选）**：BlockFrame 系列日更想让品牌 chrome / 版式 / 动效**只写一次、每期换数据**，用合成变量（`data-composition-variables` + `data-var-text/src` + `--variables-file`），见 `producing-video` 的「系列模板（variables）」。注意时间轴仍按每期 SRT 重排。
- **照搬 `producing-video` 的全部 gotcha**：定时动画一律挂注册到 `window.__timelines["main"]` 的 `tl`（**绝不裸 `gsap.from/to`**）；转场只用 incoming 场景自身 clip-path 揭幕；强调色当标点、彩块上压墨色字；CJK 在彩块里给足 `~0.2em` 竖直 padding。
- 长片建议**按段分目录** `build/seg-01..NN/`，每段一份 `index.html` 配自己那几条 cue（短片也可单文件）。

**版面填充（竖屏 9:16 / 3:4 尤其重要，别让内容挤在上半部）。** 默认 `.wrap` 顶对齐，内容少的页会全挤到顶上、底部一大片空白 —— 实测填充率常只有 **14–33%**（即安全区六七成是空的），看着像没做完。这是竖屏短视频最常见的版面病。治法：
- **用 `.wrap.fill`（三段式：顶部标签区 / 中部 hero / 底部落点卡）**，`justify-content:center` + `gap:60px` 把内容当**一整块居中**。不要用 `justify-content:space-between` 硬撑到边 —— 它会在区块之间留大缝、显得「抻」。
- **每页选一个 hero 放大**到占住中部：大数字、大图示、大对比（巨号版本、加密 relay、流程图、↓↓ 大卡）。竖屏有 ~1610px 纵向余量，字号/卡片放心大一档。
- **顶区别只放一个光秃秃的 kicker** —— 它会浮在顶上留缝。给它配一句 lead（`kicker + 一行 lead`），顶区才有分量。
- **薄页补底部「为什么/落点」卡**（口播里本来就有的因果），凑齐三段。
- 目标填充 **75–85%**（不是 100%；留点对称呼吸是 BlockFrame 的味道）。

校对（每次改完都跑）：
```bash
npx hyperframes lint        # 0 error
npx hyperframes validate    # WCAG AA 对比度
npx hyperframes inspect --samples 30    # 版面溢出；装饰出血标 data-layout-ignore
```

**版面填充自检（和 inspect 对称，抓「留白过多」）。** 起本地服务、用浏览器量每页内容包围盒占安全区的比例，低于 ~50% 的页要回去加 hero / 补底部卡：
```bash
( cd build && python3 -m http.server 8799 & )    # 起服务
# 用 Playwright/Chrome 打开 http://localhost:8799/index.html，在 console 跑：
#   document.querySelectorAll('section.scene').forEach(sec=>{
#     const w=sec.querySelector('.wrap'); if(!w)return;
#     const k=[...w.children]; let t=1/0,b=-1/0;
#     k.forEach(e=>{const r=e.getBoundingClientRect();t=Math.min(t,r.top);b=Math.max(b,r.bottom)});
#     console.log(sec.id, Math.round((b-t)/1610*100)+'%');   // 1610 = 1920-150-160 安全区
#   });
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

### Step 4 · 配齐全比例封面（**委托 `cover-design`**）

**封面归 `cover-design` 管。** 提示词模板、构图配方、生成脚本、检查脚本全在那边一份，别在这里另起。

封面用 **codex-cli 调 gpt-image 生成**（手绘编辑墨线画风）：**画风固定、构图按主题变、版式按比例变。**

```bash
# 见 cover-design/SKILL.md 的 Step 1–4
# 1) 按主题挑 motif（cover-design/references/prompt-templates.md）
# 2) 按比例写版式（cover-design/references/ratios.md），提示词写进文件
# 3) 逐个比例出图（脚本会定位 codex 真实落盘的图，并校验尺寸与比例）
bash <cover-design>/scripts/gen-cover.sh covers/cover-16x9.png 16:9 /tmp/p-h.txt 1600
bash <cover-design>/scripts/gen-cover.sh covers/cover-3x4.png  3:4 /tmp/p-v.txt 1000
# …其余比例同理（16:10 / 4:3 / 9:16）
# 4) 三道检查 + 逐字核对标题
bash <cover-design>/scripts/check-covers.sh covers/
```

本层只保证两件事：**五个比例齐**（`check-deliverables.sh` 会验），以及**系列一致**（画风与标题口径沿用本系列，新一期延续而非另起）。

设计怎么做（主题→构图配方、每个比例的版式、平台安全区、120px 可读性、以及**出图后必须逐字核对标题**）→ 读 `cover-design/SKILL.md`。

> 需要**精确数字或真实商标**的封面 / 数据图，不要交给图像模型 —— 走 `cover-design/scripts/render-cover.sh` 的 HTML→PNG 精确排版。

### Step 5 · 平台文案

写 `youtube.md` + `bilibili.md`（沿用系列模板：标题、简介、章节时间戳、链接、标签）。从 `narration.srt` 的 cue 时间生成**章节时间戳**。带上用户的推广位（油管会员 / B 站赞助 / 知识星球 / Twitter）。

### Step 6 · 清单验收（收尾必跑）

```bash
bash <本 skill>/scripts/check-deliverables.sh <slug-dir> short   # 或 long
```
全 ✓ 才算完成；有 ✗ 回去补齐。**不要自动提交**（除非用户明确要）。

---

## 可选片段：封面开篇 + CTA 尾页（提高完播 / 转化）

两个增强片段，按需加，能明显提观感和转化。

### 封面开篇（cover-as-intro）

把封面图当**视频开篇标题卡**：停留约 3 秒（开场白念完）后转场进正片。封面一图两用 —— 既是发布封面，也是片头。
- **scene 0 = 封面设计**（和 `cover-9x16` 同款，全画布），`data-start=0`、时长盖到转场结束（如 4.2s）。
- **持久页眉/页脚/进度条在封面阶段隐藏**：给它们统一加个 `.chrome` 类，`tl.from(".chrome",{opacity:0,duration:0.5}, <转场时刻>)` —— `from` 的 immediateRender 会在 0 时刻就设成透明，封面期干净，转场时随正片淡入。
- **转场 = 正片首场自己 clip-path 揭幕**（`wipe("#s1", <转场时刻>)`），别去 wipe-out 封面（违反 producing-video 转场铁律）。封面被首场盖住即可。
- **转场时刻对齐开场白结束**（首条 cue 之后那条 cue 的起点），转场跟着语音走最自然；想严格卡 3.0s 也行，但别切断开场白。

### CTA 尾页（一键三连）

narration 念完后加一页**静音尾卡**：点赞 / 关注 / 分享，停留约 5 秒。
- 末场之后加 `scene`（如 `data-start=75.5 data-duration=5.5`），**root `data-duration` 和进度条 `tl.fromTo(".pf",…,duration)` 都要顺延**到新结尾，否则尾页被截掉。
- 内容：大标题「喜欢就一键三连」+ 三个动作块（👍点赞 / ＋关注 / ↗分享）。emoji 在彩块上能渲（headless Chrome 支持），但和 BlockFrame 的扁平感会有点冲，介意就用纯字形。
- 音频 clip 时长**不变**（仍到 narration 末尾），尾页是静音的 —— 短视频的标准收尾。

> **重渲尾页/任何改动后的坑（踩过）**：渲染和 `loudnorm` 两步**别让后台任务撞车**。`loudnorm` 用 `-c:v copy`，若它在新渲染写完前跑、盯的又是同一个目标文件名，会把**旧版**规范化后覆盖进去。**铁律：渲到临时文件 → 完全写完（探测大小稳定）→ loudnorm → 装回最终名**，并从**最终文件**抽帧复核（时长对、关键页在）。

---

## 交付清单（这条 skill 的「完成」定义）

- [ ] `renders/<slug>.mp4`（已 `loudnorm` 到 -14 LUFS）+ `renders/<slug>.srt`
- [ ] 封面**五个比例全有**：`cover-3x4.png` `cover-9x16.png` `cover-16x9.png` `cover-16x10.png` `cover-4x3.png`（主封面按格式：short=3:4 / long=16:9）
- [ ] `youtube.md` + `bilibili.md`（含章节时间戳 + 推广位）
- [ ] `PLAN.md`（含实证过的事实点）+ `narration.txt`
- [ ] 口播稿过了 `personal-chinese-writing-style` **两遍**（标点一遍 + 声音一遍，见 Step 0）
- [ ] 口播稿喂 TTS 前过了 **多音字扫描**（`scan-heteronyms.sh`，`⚠` 行都处理过，见 Step 0 第三遍）
- [ ] `check-deliverables.sh` 全 ✓
- [ ] `lint` 0 error · `validate` 全过 · `inspect` 0 真实溢出
- [ ] **版面填充自检**：每页填充率 ≥ ~50%（竖屏别让内容挤上半部、底部留白过多，见 Step 2）
- [ ] 抽帧确认每场对得上 cue、无空白场景；`ffprobe` 两轨齐、时长对
- [ ] 加了 CTA 尾页 / 封面开篇的话：root 时长 + 进度条已顺延；**从最终文件**抽帧复核（防渲染/loudnorm 撞车覆盖）
- [ ] 未自动提交

## Gotchas（本层特有，叠加在 producing-video 之上）

1. **封面是「一套」不是「一张」。** 委托 `cover-design` 逐比例跑 `gen-cover.sh` + `check-covers.sh` 出全比例，再 `check-deliverables.sh` 收口。这是本 skill 的头号存在意义 —— 别又只做主封面。
2. **竖版固定 3:4，不要做 9:16 视频。** 9:16 太瘦高、移动端体验差（用户明确偏好）；竖版主画布一律 3:4（1080×1440）。9:16 只留作封面比例之一，视频本体不出。
3. **3:4 没有 4K 预设，别用 `zoom:2`。** 别试 `--resolution 2160x2880`（会被拒）。`zoom:2` 超采样**已废弃**（搞坏 `bottom:` 定位的页脚/chips，假阳性踩过）。用「原生 1080×1440 `--quality high` + ffmpeg lanczos 放大到 2160×2880」（Step 3）。16:9 用 `landscape-4k`（有真预设）。
3. **临时 `index-4k.html` 渲完即删。** 别把超采样临时文件留在 `build/` 里。
5. **系列一致性。** 音色、配色、字体、页眉页脚、封面版式都沿用系列；新一期延续而非另起。
6. **事实实证。** 命令/架构/流程类内容，真实跑过再放进画面，别编输入输出。
7. **口播稿过两遍 `personal-chinese-writing-style`，不是一遍。** 单遍会放过声音层的拟人化口语动词（默默干、喊一声、活儿、长在、丢进……）。第一遍清标点、第二遍清声音；`diff` 草稿确认两遍都落地（见 Step 0）。
8. **竖屏别让内容挤上半部。** 默认顶对齐的 `.wrap` 在内容少时填充率只有 14–33%、底部一大片空。用 `.wrap.fill` 三段式 + hero 放大 + 底部落点卡，目标 75–85%；顶区别放孤零零一个 kicker（配一句 lead）。版面填充自检见 Step 2。
9. **改完重渲别和 loudnorm 撞车。** 渲到临时文件 → 完全写完 → loudnorm → 装回最终名，并从最终文件抽帧复核。直接渲到目标名 + 并行 loudnorm 会把旧版覆盖进去（踩过）。
10. **producing-video 的 12 条 gotcha 全部生效**（尤以「动画必须挂 `tl`」「转场只用 clip-path 揭幕」最常翻车）——本 skill 不复述，照办。

## 超出范围

- **封面设计与渲染**：是 `cover-design` 的活。本层只验「五个比例齐」。
- **配音/字幕**（文本→音频+SRT）：是 `listenhub-tts` 的活。
- **出片铁律细节**（HyperFrames 合成/渲染）：是 `producing-video` 的活，本 skill 照搬。
- **声音克隆**：用支持克隆的云端 TTS，只换「出声那一步」，下游不变。
- **发布上传**：本 skill 只产物料、不上传平台。
