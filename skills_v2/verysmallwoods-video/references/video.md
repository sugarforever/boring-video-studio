# 视频 · 用 HyperFrames 出片

画面走 **faceless-explainer**（文章/主题/口播稿 → 无实拍讲解视频）。核心是：**画面跟着旁白的语义走**，每处内容在被念到时才出现，不前 25% 全倒、不动效走完干等。

## 建项目 + 选设计

```bash
npx hyperframes init "videos/<YYYYMMDD-slug>" --non-interactive --example=blank
node <faceless-explainer>/scripts/build-frame.mjs --preset <slug> --hyperframes .   # slug 见 designs.md
```

`frame.md` = 这期的配色/字体/版式真理，逐帧以它为准。

## 分镜 → 逐帧

1. **STORYBOARD.md** - 把内容重排成教学序列（不照文章段落顺序），一帧一个「工作」。每帧写 `voiceover`（分句成 cue，方便对齐）、`type`、`transition_in`、time-coded shot sequence。
2. **逐帧构建** - `frame-packets.mjs` 打包，每帧派一个 sub-agent 建 `compositions/frames/NN-*.html`。
3. **组装** - `assemble-index.mjs` 拼成 `index.html`。

细节直接用 faceless-explainer 的脚本与 references，别在这重写。

## 动效准则（判断力优先，几条硬的）

- `power3` 长尾稳落，**不弹跳、不过冲**。
- **VO 分句节奏披露**：t=0 只出此刻讲到的，后续每块在被念到时进。
- 覆盖即模糊：上下层重叠时后层 dim + blur，强调上层。
- seek-safe：paused GSAP timeline、`fromTo` 入场、无 `Math.random`/`Date.now`、无 CSS 动画、无 `repeat`/`yoyo`。
- **动效贴合语义**（diegetic）：讲「拆成一棵树」就画树、讲代码就用代码面；别千篇一律入场淡入。
- 字幕安全区：主内容压上 ~83%，底部留给（YouTube 上的）字幕。

## 重排内部节奏（音频到位后，很重要）

自己录的旁白语速自然、常比估算长。**动效不能走完就长时间定格**。拿到真实 cue 时间轴后，把每帧内部披露重排到「每处 reveal 落在被念到那一刻」。给每个 frame-worker 发**本帧逐句 cue 的帧内相对秒 + 文本**，让它对齐重排。做法见 `references/audio.md`「重排节奏」。

## 转场

`transitions.mjs inject` + `verify`。选 2-3 种重复用：封面→正片 `zoom-through`；并列小节 `push-slide`；其余 `crossfade`。改过时长要**重新组装 + 重注入转场**（inject 幂等）。

## 检查

```bash
npx hyperframes lint      # 0 error 才算过；warning 过一眼
npx hyperframes check     # runtime/layout/motion/contrast
npx hyperframes snapshot --at <各段中点>   # 出 contact-sheet 核对
```

- 中文字体：预制多是拉丁字体，中文靠 `assets/fonts/` 里的 Noto Sans SC + 系统回退。字体栈以通用族（`serif`/`sans-serif`）收尾，CJK 才不 tofu。别用 google fonts `@import`（渲染要联网、不确定）。

## 渲染

```bash
# 1080p60（可靠 master，8min 成片 ~90MB）：
npx hyperframes render --skill=faceless-explainer --quality high --fps 60 --output renders/<slug>-1080p.mp4
# 4K master（磁盘够再出，见 memory「4K ENOSPC」；8min ~220MB，耗时 ~22min）：
npx hyperframes render --skill=faceless-explainer --quality high --resolution landscape-4k --fps 60 --output renders/<slug>-4k.mp4
```

先出 1080p 保底，再看磁盘出 4K。渲染是分段编码，临时文件有界；渲前确认磁盘 ≥ ~15GB(1080p) / ~30GB(4K)。
