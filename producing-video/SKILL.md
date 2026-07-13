---
name: producing-video
description: Turn a user-provided voiceover audio file + SRT subtitle into a finished, narration-synced MP4 using HyperFrames (HTML-to-video). The audio + SRT are the source of truth — scenes are timed to the SRT cues, content is read from the SRT, and the audio is muxed in automatically. Use when the user hands over an mp3/wav + srt and wants a video, says "把音频做成视频", "做一期视频", "audio + srt to video", "把这期早读做成视频", "render this narration into a video", or provides a recording + subtitles for an explainer / daily / 解读 / 口播. If the user only has narration text (no audio/SRT), run the `listenhub-tts` skill first to produce them, then come back here. NOT for slide decks (use a slides skill).
---

# Producing-Video · 音频 + 字幕 → 成片

把"用户已经录好的口播音频 + SRT 字幕"做成一条**画面跟着声音走**的 MP4。用 HyperFrames（HTML 即视频）出片。

**铁律：音频和 SRT 是唯一事实源。** 画面的内容来自 SRT，画面的时间轴来自 SRT 的 cue 时间戳，音频作为一个 `<audio>` clip 直接挂进合成里、渲染时自动合流 —— **没有"先出视频再合音频"这一步**。

## 分工（很重要）

| 谁 | 做什么 |
|---|---|
| **上游** | 写稿 → 录音/合成音频 → 生成 SRT |
| **本 skill（你）** | 选 frame/品牌 → 按 SRT 搭 HyperFrames 合成 → 校对 → **preview 里让用户过目** → 渲染成片 |

本 skill 的输入就是 **音频 + SRT**，你只管出片。**配音/字幕是上游的事**：用户自己录好交给你，或者只给了口播文本时——先用 **`listenhub-tts`** skill（文本 → 音频 + 字幕）补出 `narration-full.mp3` + `narration.srt`，再回到这里走主流程。声音克隆是另一条线（见"超出范围"）。

## 依赖检查（pre-flight）

```bash
npx hyperframes doctor      # 需要 Node ≥ 22 · FFmpeg · Chrome
```

需要 `hyperframes` / `hyperframes-cli` 两个 skill 在场（编写合成 + 跑 CLI）。缺了就让用户 `npx hyperframes skills` 安装后重来。

确认用户给了**两个文件**：音频（mp3/wav/m4a）+ SRT。只给音频没给 SRT → 本 skill 需要 SRT 拿时间轴；可让用户补 SRT（很多录音工具/剪辑软件能导出），**不要**默认去跑 Whisper 转写（用户没给 SRT 往往是有意的，先问）。**只给了文本（口播稿）、连音频也没有** → 先跑 **`listenhub-tts`** skill 出音频 + 原始字幕（并按它的流程校正），拿到 mp3 + SRT 后再进下面的工作流。

---

## 工作流

### Step 1 · 选 frame / 品牌

画面的风格 = 一个 frame.md / visual-style / 既有系列品牌。三种来源，按情况选：

1. **延续系列品牌**（推荐用于日更/系列）。如果这期属于一个已有系列（如"AI 早读"），去翻该系列的封面/历史成片，**沿用同一套 token**（颜色、字体、栅格、页眉页脚），让视频和封面一脉相承。
2. **HyperFrames frame.md 模板**。用户可能直接点名，例如 `creative-mode` / `biennale-yellow` / `cobalt-grid`。取 token：
   - `curl -sSL https://www.hyperframes.dev/design/<slug>.md` （站点是 JS 渲染，多半取不到正文）；
   - **更靠谱**：在本机 `open-design` 仓库里找 `design-templates/*<slug>*/template.json`，里面有精确的 `palette` / `typography`（hex + 字体名）。
3. **8 个内置 visual-style**（Swiss Pulse / Velvet Standard / Shadow Cut / Maximalist 等）。在 `hyperframes` skill 的 `visual-styles.md` 里，直接抄 YAML token。

**字体一律本地 woff2**（见 Gotcha "字体"）。中文必须配 `Noto Sans SC`（400/500/700/900 视用量）；英文 display 按 frame 选（Archivo Black / Manrope / Oswald…）；标签数字常用 `JetBrains Mono`。从 `fontsource` CDN 下到项目的 `fonts/`：
```bash
curl -sSL -o fonts/<name>.woff2 "https://cdn.jsdelivr.net/fontsource/fonts/<family>@latest/<subset>-<weight>-normal.woff2"
# 中文：subset 用 chinese-simplified；拉丁：latin
```

### Step 2 · 起项目

```bash
cd <repo>/studio/videos                       # 仓库约定：成片放这里
npx hyperframes init <YYYYMMDD-slug> --example blank --non-interactive
cd <YYYYMMDD-slug> && mkdir -p fonts audio
cp <user-audio> audio/narration-full.mp3
cp <user-srt>   audio/narration.srt
```

> **目录已有源文件时**（日更目录常已放了 `script.md` / `narration.txt`）：`hyperframes init` 拒绝非空目录（报 `Directory already exists and is not empty`）。先 `init` 到一个临时目录，再 `cp -R __tmp/. <slug>/` 把脚手架并进来，或先 `init` 再放稿。

### Step 3 · 解析 SRT → 切场景

读完整 SRT（`scripts/srt-cues.mjs` 可打印每条 cue 的开始秒数 + 文本，方便规划）。然后：

1. **按内容把 cue 归成"幕/场景"**。一条 SRT cue 通常是一句话；把讲同一件事的几条 cue 合成一个场景（scene）。一支 6~7 分钟的日更，大约 12~16 个场景比较舒服（平均 ~30s/场，画面不至于久不动）。
2. **场景开始时间 = 它第一条 cue 的开始时间戳**（秒）。
3. **场景时长 = 下一场开始 − 本场开始 + ~0.5s**（这 0.5s 重叠让转场 wipe 能盖住上一场，避免穿帮）。最后一场到音频结束。
4. **场景内的逐步出现（sub-reveal）= 对应子 cue 的开始时间**。让标题/要点/数字"在被念到的那一刻"出现 —— 这是同步感的关键。
5. **画面文案从 SRT 来，且不能和口播打架**。可以精炼成海报式短句，但不能说的是 A、画面写 B。顺手核对事实（数字、专有名词、人名）—— 用户很在意准确。

> 把场景开始时间放进一个 JS 数组 `const B = [...]`，所有 tween 用 `B[i-1] + 局部偏移` 定位。日后微调时间轴只改数组，不用逐条改 tween。

### Step 4 · 编写合成（index.html）

- **持久 chrome（宁少勿多）**：栅格/边框/进度条/一个角落的品牌 pill 这类每场都在的元素，放在场景**之外**（直接挂 `#root`，不是 clip），整片不动。**克制是关键**：chrome 只承担定位和品牌，**别塞填充式文字标签** —— "AI 资讯 · 客观分享""横版 · 16:9""竖版 · 3:4"这种既不是核心内容、又每一帧都杵在那儿的字，是噪声，一律删掉。够用的持久 chrome ＝ 细边框 + 进度条 + 一个小小的品牌 pill，别的都不要（页眉的系列/主题名可留一个，或也删）。
- **音频一条连续 clip**（"音频即时钟"）：
  ```html
  <audio id="vo" src="audio/narration-full.mp3" data-start="0" data-duration="<总时长>" data-track-index="20" data-volume="1"></audio>
  ```
  媒体元素不需要 `class="clip"`；给它独立的 `data-track-index`。
- **每个场景一个全画布 `.scene.clip`**，各自独立 `data-track-index`（重叠的 wipe 需要不同 track），`z-index` 递增（后面的盖前面的）。
- **转场只用"incoming 场景自身的 clip-path 揭幕"**（见 Gotcha「转场」）：
  ```js
  function wipe(sel, at){ tl.fromTo(sel,{clipPath:"inset(0 100% 0 0)"},{clipPath:"inset(0 0% 0 0)",duration:0.5,ease:"power3.inOut"}, at); }
  ```
- **入场动画**用 `tl.from(sel, vars, 位置秒)`（**必须挂在注册到 `window.__timelines` 的 `tl` 上**，第三参是 tl 上的绝对秒），定位在对应 cue 时间。短（0.3–0.7s），错峰，变化 ease。**绝不用裸 `gsap.from()` / `gsap.to()`** —— 它们挂到 gsap 全局时间轴，而渲染只 seek `tl`，会导致部分场景（尤其后段）在 seek 渲染里整片空白（见 Gotcha 12）。
- **复用一套 class 化的 CSS 工具件**（kicker / headline / note / stat / chip-xform / cards / numbered-list / accent-mark），15 个场景共享，别每场写一套 id 样式。
- **品牌纪律**：严格按 frame 的 token；强调色当"标点"不当"填充"（深色系：强调色只给小而实的标记；浅色系：强调色做色块、文字用墨色压在色块上）。
- **动效编舞**（15 类常见 Motion：换场 Push/Slide、错峰入场、状态变化、点击涟漪、滚动、导航、加载骨架、数据长柱/滚字、列表重排、拖拽回弹、脉冲引导、logo 装饰、3D 翻卡/视差、粒子爆发、打字机）：要给某场安排"怎么动"时，看 **`references/motion-patterns.md`** —— 每类有**标准名**（跟 Agent 沟通直接报名）+ 设计中立的 seek-safe GSAP 配方，另附编舞辅助（自定义 cubic-bezier ease / `shiftChildren` 整块 retiming / `timeScale` 先慢写后压缩）。数据页的柱子长出/数字滚动（第 08 类，含 typeNum / 码表变体）尤其常用。
- **换场接缝**（穿越变焦 / 顺势切 / 同底硬切 / 帧连续硬切 / 曲边升幕）：默认转场仍是 incoming 的 clip-path 揭幕（Gotcha 3）；想要更电影感的换场时，看 **`references/scene-transitions.md`** —— 一套仍然 seek-safe 的"换场动词表"，全部**只动场景本体**、附"交叉淡化红线"与"Z 单向律"。
- **命令式引擎**（WebGL 着色器 / Canvas 粒子场 / Lottie / 伪 3D）：GSAP tween 表达不了的东西，看 **`references/runtime-adapters.md`** —— 核心是**代理时钟桥**（`tl` 上 `ease:"none"` 补一个 `{t}` 代理、`onUpdate` 里绘制，绝不 rAF），外加 Lottie 帧驱动、WebGL→2D 兜底、CSS 伪 3D。
- **视觉效果**（局部高光/聚光、iOS 磨砂玻璃、背景模糊/景深、局部放大镜、材质填充大字、光带扫字、半调 canvas 底）：要给某个场景加这类**画面质感**时，看 **`references/visual-effects.md`** —— 里面是设计中立的机制（纯 CSS + GSAP + 确定性渲染注意事项，外壳用 CSS 变量留口）。都在无头 Chrome 里验证过能逐帧渲染（含 `backdrop-filter`）。
- **每场都要有"动效论点"**（motion thesis），不只是一个入场：想清楚这一场**先动什么、往哪动、背景怎么呼应**，且**首个可见运动在 0.2s 内**发生（别让开头几帧是死的）。强调装饰件（绿光标、小球）遵守**"一秒律"**——它的整段生命对齐**一个被念到的词**（飞入→点击→退场 ~0.9s），久留则廉价。**多品牌/多 logo 同框**时给各自**专属色道与地面**（如某色只活在终端窗里，出了窗就是 bug），强调色按 frame 配给、宁少勿滥。

### Step 5 · 校对（每次改完都跑）

```bash
npx hyperframes lint        # 0 error 才继续（var(--x) 字体告警是误报，可忽略）
npx hyperframes validate    # WCAG AA 对比度；改掉过暗的次级灰
npx hyperframes inspect --samples 30   # 版面溢出，带时间戳；场景多就多采样
```
装饰元素故意出血到画外 → 标 `data-layout-ignore`。真实溢出 → 改容器/字号/padding。

### Step 6 · 预览 · 让用户先过目（渲染前的人工闸门）

渲染很贵（4K 长片几分钟到十几分钟），**别把没人看过的合成直接送去渲染**。先用 HyperFrames 自带的 preview studio 在浏览器里「播放」合成，让用户肉眼确认效果、点头了再进 Step 7 渲染。

```bash
cd studio/videos/<slug>              # 横竖分目录时进到对应的 build-h / build-v
npx hyperframes preview             # 默认 3002 端口，自动开浏览器
```

它起一个本地 studio，**真正按时间轴播放**你的合成：带播放头 + 刻度可任意 scrub、音频一起放（当场判断画面与口播同不同步）、改 `index.html` 热更新（秒级反馈，不用重渲）。这是「不出视频就预览」的主力 —— 中间所有迭代都在这里做，`render` 只留到最后出片一次。

- **别直接双击打开 `index.html`** —— 那样只看到静态第一帧。原因见 Gotcha 12：所有定时动画挂在 `window.__timelines` 的 `tl` 上、靠外部 seek 驱动；裸开 HTML 没人 seek，wipe / 入场全停在初始态（场景叠在一起或空白）。**必须走 preview**（它替你驱动 tl）。
- **这是人工闸门**：把 preview 地址/画面交给用户，请他过一遍 —— 尤其数据页的数字、转折页的节奏、和口播的同步 —— **拿到明确 OK 再进 Step 7**。渲染前多这一眼，省掉「渲完才发现要改、又重渲一遍」。
- **contact-sheet 先行（复杂片可选）**：动手写动效前，先做一张**无动效的 HTML 分镜表**（0 GSAP：一格 16:9、`aspect-ratio:16/9; overflow:hidden`，每格下一句"这场先动什么、往哪切、背景怎么呼应"的注记），跟用户对齐关键帧、**批准了再写动效**——省掉"渲完才发现构图不对"。分镜表复用成片同一套 kit.css/token，批准的格子能近乎逐字搬进合成。
- **agent 精修**：`npx hyperframes preview --context`（或 `--selection`，加 `--json`）能把 studio 里当前选中的元素/上下文吐成文本，据此帮用户精确定位改哪块。
- **清理**：`--list` 看在跑的预览、`--kill-all` 全部关掉；换项目或端口占用时加 `--force-new`。

### Step 7 · 渲染 + 验收

- **先 standard 跑一版自检**（快），用 `ffmpeg` 抽几帧验证同步：在"你知道这一刻在讲什么"的时间点抽帧，确认画面对得上。
  ```bash
  ffmpeg -y -ss <秒> -i renders/x.mp4 -frames:v 1 /tmp/f.png   # 然后看图
  ```
- **空白场景廉价自检**：每个场景中点各抽一帧，先比 PNG 文件大小 / 哈希 —— 跨场景出现一模一样的尺寸＝同一张空白帧的强信号（深色主题尤其靠这个，别只信肉眼）。命中再针对性看图。
  ```bash
  for t in <每场中点秒>; do ffmpeg -y -ss $t -i renders/x.mp4 -frames:v 1 /tmp/f_$t.png; done; ls -la /tmp/f_*.png   # 同尺寸 = 可疑
  ```
- **接缝"量"而非"看"（转场存疑时）**：`onUpdate` 在 snapshot 上是冻的、**媒体/驱动效果的对错只有真渲染 + ffmpeg 抽帧才算数**。要证明某个换场是"干净硬切"还是"发灰交叉淡化"，用 `signalstats` 逐帧量亮度——硬切是 `luma 191→62`**一步跳变、无中间灰帧**，交叉淡化会在切点附近出一串压暗的过渡帧（即"交叉淡化红线"，见 `scene-transitions.md`）：
  ```bash
  ffmpeg -i renders/x.mp4 -vf "select='between(t,<切点-0.3>,<切点+0.3>)',signalstats,metadata=print" -f null - 2>&1 | grep YAVG
  ```
  改版对拍时，把两版强制成同规格（同 fps/时长/帧数）再逐帧比亮度/做 contact sheet（`fps=1/1.6,scale=300:169,tile=6x4`），把"像不像"变成每个 beat 的数值差 → 定位到具体要改哪一场。
- **成片渲染**（master）：
  ```bash
  npx hyperframes render --resolution landscape-4k --quality high --output renders/<slug>-4k.mp4
  ```
  `--resolution landscape-4k` 是把同一合成按 2× DPR 真·超采样到 3840×2160（不是放大）；4K master 即使观众看 1080p 也更耐平台二压。4K + 长片渲染较久（几分钟到十几分钟），可后台跑。
  > **快速捕获默认开（0.7.38+）**：macOS 硬件 GPU 下 drawElement 快速捕获已默认启用，捕获约 2× 提速，且带逐帧自校验 —— 某帧证明不了正确会自动回退经典截图路径，正常情况不用管、白拿提速。**万一渲出异常帧/花屏，关掉它复现**：`PRODUCER_EXPERIMENTAL_FAST_CAPTURE=false npx hyperframes render ...`（回退到经典路径再排查）。渲染中途要停用 Studio 的 render cancel，或直接杀进程。
- **响度核查 + 规范化**：用户的口播 / TTS 常偏安静。先 `ffmpeg -i renders/x.mp4 -af loudnorm=print_format=summary -f null -` 量整体响度；低于约 -16 LUFS 就规范化到网络标准（-14 LUFS）—— **视频流 `-c:v copy` 不重渲，几秒搞定**：
  ```bash
  ffmpeg -y -i renders/x.mp4 -af loudnorm=I=-14:TP=-1.5:LRA=11 -c:v copy -c:a aac -b:a 192k renders/x-loud.mp4
  ```
  顺手把源 `audio/narration-full.mp3` 也规范化，将来重渲（竖屏 / 改版）自动继承。
- 验收：`ffprobe` 确认有 video(h264) + audio(aac) 两条轨且时长对得上（**CLI 汇总行的时长可能误报，以 `ffprobe` 为准**）；抽帧确认每场落在它的 cue 上。

成片留在 `studio/videos/<slug>/renders/`。**不要自动提交**（除非用户明确要）。

### Step 8 · 封面（同套 token，核心优先）

各平台封面用**独立的静态 HTML**（无 GSAP，全部元素直接可见），复用成片的 `kit.css` + `fonts/`，截图成 PNG（本地 `python3 -m http.server` + Playwright，`scale:'device'` 取 2×）。常见尺寸：`cover-16x9`（横版主）、`cover-3x4` / `cover-9x16`（竖版）、`cover-4x3`（备用）。

**封面纪律 = 少即是多**：一个压倒性的核心标题 + 少量辅助信息，别的都删。

- **删掉填充式 chrome**：eyebrow/kicker（"上一期…的 follow-up" 这类前缀）、页眉次级说明行、页脚 tagline、比例标签（"横版 · 16:9"）—— 这些都不是核心，全去掉。
- **留什么**：核心标题（大号衬线/黑体）＋ 一句副标题＋（可选）一个小 rail 预览 3–4 条内容要点；再加一个小小的品牌 pill 就够了。
- 删掉 eyebrow 后记得把标题块的垂直定位重新居中一下（原来给 eyebrow 留的位置会让标题偏高）。

### 语速与 1.1× 提速（上游音频阶段）

口播偏慢的作者（本项目常见），在上游出音频时就该提速再交付：`ffmpeg -af "atempo=1.1,loudnorm=I=-14:TP=-1.5:LRA=11"`，**同时把 SRT 时间戳按 1/1.1 缩放**（否则字幕与画面全部错位）。校验：`ffprobe` 量成片时长应等于「原始 TTS 时长 ÷ 1.1」，不是原始时长 —— 用这个比值确认提速真的生效了。详见 `listenhub-tts` skill。

### 系列模板（variables）· 一套合成 → 每期换数据

日更/系列想**复用同一套合成**、每期只换标题/图/强调色时，用 HyperFrames 的**合成变量**（HeyGen 官方 variables 机制，契约见 `hyperframes-core` 的 `variables-and-media.md`）。这样品牌 chrome、栅格、动效编舞**只写一次**，每期喂一份数据。

1. **声明**（`<html>` 上，一个**声明数组**，每条要 `id/type/label/default`；type 支持 `string/number/color/boolean/enum`）：
   ```html
   <html data-composition-variables='[
     {"id":"title","type":"string","label":"标题","default":"本期标题"},
     {"id":"accent","type":"color","label":"强调色","default":"#66d9ef"}
   ]'>
   ```
2. **消费**（零 JS，三条绑定，preview/render 一致、seek-safe）：
   ```html
   <h1 data-var-text="title">占位标题</h1>          <!-- 换文字，保留子 clip -->
   <img data-var-src="heroImage" src="fallback.jpg"> <!-- 换 src，authored src 即 fallback -->
   <style>.kicker{ color: var(--accent); }</style>   <!-- 每个标量自动暴露成 --{id} CSS 变量 -->
   ```
   循环/派生值才需读一次：`const {title,accent}=window.__hyperframes.getVariables();`（变量渲染中不变）。
3. **每期覆盖**（**对象**、按 id 键；注意和声明数组是两种形状）：
   ```bash
   npx hyperframes render --variables-file day-042.json     # 每期一份 JSON，批量出片
   npx hyperframes render --variables '{"title":"Q4 营收"}'
   ```
   CI 加 `--strict-variables`：未声明键 / 类型不符 / enum 越界都变**报错**，出片前拦住脏数据。

> **注意时间轴差异**：本 skill 的场景时间轴是**按每期 SRT 量出来的**，每期时长/切点不同——所以 variables 最适合复用**品牌 token + chrome + 版式 + 动效配方**这类**不随时长变**的部分（尤其固定格式的短片）；逐期变化的**时间轴/场景切分**仍按主流程按 SRT 重排，别指望一个纯静态模板吃掉时间轴。编排层的系列身份见 `blockframe-video`。

---

## Gotchas（血泪，务必遵守）

这些是踩过的坑，违反任何一条都会出废片：

1. **音频即时钟**。场景时长从 SRT 量出来，不要凭感觉定时长再硬塞音频。
2. **有 SRT 就别转写**。用户给了 SRT = 精确时间轴免费拿到，不需要 Whisper。（没 SRT 想自己转写前先问用户。）
3. **转场只用场景自身 clip-path 揭幕**。**绝不**用单独的全屏色块/幕布/刀闸/砸场板去做转场 —— 在渲染引擎里它会"扫进来盖住下一场后卡住不走"，整场变成纯色/黑屏。揭幕揭的是 incoming 场景本体。
4. **不要给 `.pad` 容器套整体 opacity 的 "pushIn" 包装**。容器级 opacity 动画在 seek 渲染里可能留在 0，把整场变黑。用每个元素各自的 `tl.from()`（挂在 `tl` 上，不是裸 `gsap.from`，见 Gotcha 12）。
5. **配对 tween 不要加 `overwrite:"auto"`**。它会把配对的另一条 tween 杀掉（比如"扫入"在、"扫出"没了）。lint 的 overlapping_gsap_tweens 是无害告警，宁可留着。
6. **字体必须本地 woff2**。Google Fonts `<link>` 会被 lint 标记、且 sandbox 渲染里不可靠。中文配 Noto Sans SC；**中文字在彩色 accent 色块里要给足竖直 padding/line-height**（CJK 字形比 em 框高，padding 太紧 inspect 会报 text_box_overflow，给到 ~0.2em 竖直 padding + line-height ~1.12）。
7. **深色主题别信亮度探测**。1×1 平均亮度对深底+稀疏文字永远偏低，会把正常场景误判成黑屏。**靠抽帧看图**确认。
8. **浅色主题的对比度误报**。validate 在固定几个时间戳采样**所有** DOM 文字，包括当时未激活的场景。浅底上"浅色文字"（白字、奶油字）一旦不在自己场景的激活时刻被采到，就报低对比度——这是误报。规避：**accent 色块上一律用墨色（深）文字**，未激活时墨字压奶油底仍是高对比，零误报。
9. **确定性**。禁止 `Date.now()` / `Math.random()`（破坏可复现渲染）；要随机用种子化 PRNG。
10. **每个场景独立 track-index**；音频单独高 track-index。装饰出血标 `data-layout-ignore`。
11. **画质**：原生 1080p 在 Retina 上看会发虚（被放大 + H.264 4:2:0 软化彩色字缘）；master 用 `--resolution landscape-4k --quality high`。
12. **定时动画必须挂在 `tl` 上**（最高频废片坑）。一律 `tl.from / tl.to / tl.fromTo(sel, vars, 位置秒)`。**绝不用裸 `gsap.from()` / `gsap.to()`** —— 它们挂到 gsap 全局时间轴，而 HyperFrames 渲染只 seek 注册到 `window.__timelines` 的那个 `tl`。结果 wipe（在 tl）与入场（在全局轴）各跑各的，**后段场景的 clip-path 不被驱动 → 整片只剩持久 chrome、内容空白**。现象很隐蔽：前几场正常、越往后越空。preview 里 scrub 到后段就能一眼看出（Step 6），或用 Gotcha 7 / Step 7 的「空白场景廉价自检」。
13. **`data-layout-ignore` 元素保持静态**。标了它的装饰元素（大水印数字等）会被 validate 从 DOM 上下文剔除，再对它 `tl.from` 会报 `GSAP target not found`。装饰随场景 wipe 一起揭出即可，别单独 tween 它。
14. **补时长契约**。HF 用**场景 `tl` 的 `timeline.duration()`**（不是 host 的 `data-duration`）来决定这场显示多久——非 root host 上的 `data-duration` 会被运行时剥掉。`tl` 比它的主槽短 → **提前隐藏 → 帧尾黑闪**。凡是动效比场景短的场景，末尾补一句空 tween 撑满：`tl.to({}, { duration: 本场时长 }, 0);`。（studio 控制台里枚举 `iw.__timelines` 各时长、比对主 `data-duration`，低于的标出。）
15. **媒体（视频/图片）铁律**。① `<video>`/`<img class="clip">` **必须挂在 master `index.html`**，放进子合成 template 里会**渲染成黑**（对 master 级媒体做 transform 没问题）。② 视频**必须有 `id`**（无 id 冻结/黑屏，lint `media_missing_id`）。③ 框架**强制 clip `opacity:1`**——想淡入淡出请淡**外层 wrapper**，别淡 `<video>` 本身。④ 视频**真 3D/perspective 祖先会杀掉它**。⑤ HF **不会 hold 最后一帧**：`data-duration` 超过素材长度 → 空窗；要定格末帧就**烘进文件** `ffmpeg -vf "tpad=stop_mode=clone:stop_duration=0.7"`，或用 poster/截屏 `<img>` 在视频窗口边界用 `tl.set` 切换来补窗。⑥ 多场共享底视频要**帧连续硬切**时用 `data-media-start`（见 `scene-transitions.md` D）。
16. **`immediateRender` 竞争**。默认 `immediateRender` 的 `fromTo`/`from` 会在**构建时**（函数式测量 `set()` 跑之前）就把 from 态应用上——若入场 tween 和一个"测量摆位"（`getBoundingClientRect`，含祖先 transform）共享元素/祖先，摆位会**过冲**（踩过：卡片落到屏外 1250px）。给这类入场 tween 加 `immediateRender:false`。连点环/连续词接力也靠它防止所有 from 态在 t=0 抢画。
17. **多合成编排（进阶）**。场景多（10+）或想逐场隔离预览时，可把每场拆成 `compositions/*.html` 子合成、master `index.html` 用**一条零 tween 的 `gsap.timeline({paused:true})` 当纯时钟**、只在接缝处摆位。此时两条额外铁律：① 子合成脚本取 root 要带 fallback——`const R=(document.currentScript&&document.currentScript.closest('#root'))||document.querySelector('#root'); if(!R||!window.gsap) return;`（运行时把子合成**内联**进 index 后 `currentScript` 在 root 之外，`closest` 会 null → 脚本 bail → **单独预览正常、进 index 却整场静止**）。② 每个子合成遵守 Gotcha 14 补时长。**本 skill 的单文件 index（场景为内联 `.scene.clip`）仍是默认**，多合成只是长/复杂片的可选结构。

## SRT → 场景时间轴（配方）

```
场景[i].start    = cue[第一条].start                 (秒)
场景[i].duration = 场景[i+1].start − 场景[i].start + 0.5   (末场到音频末尾)
场景内某元素入场 = 它对应 cue 的 start
音频 clip        = data-start=0, data-duration=总时长
root data-duration = 音频末句之后留 ~3s 收尾
```

JS 里：
```js
const B = [0, 38.63, 53.96, /* ...每场 start... */];   // 从 SRT 量
const at = (i, off) => B[i-1] + off;                   // i 是 1-based 场号
function wipe(sel, i){ tl.fromTo(sel, {clipPath:"inset(0 100% 0 0)"}, {clipPath:"inset(0 0% 0 0)", duration:0.5, ease:"power3.inOut"}, B[i-1]); }
```

## 超出范围

- **配音 / 字幕（上游）**：把口播文本变成音频 + SRT 是 **`listenhub-tts`** skill 的活（ListenHub 原生 `/v1/speech` 出音频 + 自带字幕，云端 ASR 作 fallback）。本 skill 只吃 audio + SRT。
- **声音克隆 / 「听起来像我」**：上游 TTS 用的是通用音色。要克隆自己的声音，用支持克隆的云端 TTS（MiniMax / ElevenLabs），克隆只换"出声那一步"，下游时间轴/挂载/渲染不变。HyperFrames 自带的 Kokoro TTS **做不了中文**（CLI 传 `zh`、espeak 要 `cmn`，且质量差）；本机临时方案 macOS `say -v Tingting`。
- **幻灯片 deck**：要的是横向翻页 deck 而非视频 → 用 slides 类 skill。

## 输出清单

- [ ] `lint` 0 error · `validate` 全过 · `inspect` 0 issue
- [ ] **已在 `hyperframes preview` 里播放过、用户看过并 OK**，再进渲染（别跳过这道人工闸门）
- [ ] 所有定时动画挂在 `tl` 上（无裸 `gsap.from/gsap.to`，见 Gotcha 12）；短场景已补时长撑满主槽（Gotcha 14，无帧尾黑闪）
- [ ] 若用了视频/图片：媒体挂在 master、视频有 `id`、淡的是 wrapper 不是 `<video>`（Gotcha 15）
- [ ] 每场有"动效论点"、首个运动在 0.2s 内；换场/命令式引擎按 `scene-transitions.md` / `runtime-adapters.md` 且仍 seek-safe
- [ ] 抽帧确认每场落在它的 cue 上（尤其数据页/转折页）；跨场景帧大小无异常雷同（无空白场景）
- [ ] `ffprobe`：video + audio 两轨、时长 = 音频时长（CLI 汇总行时长可能误报）
- [ ] 响度已核查：低于 -16 LUFS 已 `loudnorm` 到 -14（`-c:v copy` 不重渲）
- [ ] master 用 4K high（除非用户另说）
- [ ] chrome 精简：无填充式页眉/页脚标签（"AI 资讯 · 客观分享""横版 · 16:9" 之类），只剩边框 + 进度条 + 小品牌 pill
- [ ] 封面核心优先：无 eyebrow / 页眉次级行 / 页脚 tagline / 比例标签，突出主标题
- [ ] 若作者语速偏慢：音频已 1.1× 提速且 SRT 已按 1/1.1 缩放（成片时长 = 原始 TTS ÷ 1.1）
- [ ] 成片在 `studio/videos/<slug>/renders/`，未自动提交
