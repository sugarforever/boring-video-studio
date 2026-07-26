---
name: verysmallwoods-video
description: 小木头的个人视频流水线。把一个主题 / 一篇文章 / 一份口播稿，做成一整套可发布物料 - 成片 + 五比例封面 + YouTube/Bilibili 文案 + 博客 + 推文。视频用 HyperFrames（HTML 即视频），设计从预制 design 里选（默认 BlockFrame 糖果海报风）；旁白可 TTS 也可自己录。当我说「做个视频 / 做一期 / 把这篇文章做成视频 / 出整套物料 / 配齐封面文案博客」时用本 skill。
---

# verysmallwoods-video · 主题/文章/口播稿 → 一整套可发布物料

这是我（小木头）自己的视频流水线，整合版。**输入**一个主题、一篇文章、或一份口播稿；**输出**一个可直接发布的清单 - 不是一个 mp4。用 HyperFrames 出片（HTML 即视频，本机渲染）。

> **写法本身遵循 Claude 5 上下文工程的新规则**：这个 SKILL.md 保持轻，只讲「什么时候用它、怎么开局、交付什么、去哪查细节」；每一步的具体做法都下沉到 `references/`，用到再读。别把所有东西堆在这一个文件里。

## 两个开局选择（每期先问我，别替我定）

1. **视频设计** - 从 HyperFrames 预制 design 里选一个（**默认 BlockFrame** 糖果海报风）。设计目录、怎么选、怎么用见 `references/designs.md`。
2. **旁白来源** - 我**自己录**（我给音频 + SRT），还是 **TTS 合成**。两条路都支持，见 `references/audio.md`。

这两项定了，其余按下面的清单一路做完。**其它决定尽量用判断力**，别为每件小事都来问 - 拿不准、或涉及口径/事实/发布这类不可逆的，才问。

## 铁律（就这几条，别的都交给判断）

1. **交付是一个清单，不是一个 mp4。** 结束前对照下面「交付清单」逐项验收，有缺就没完成。
2. **字幕不烧进成片。** 我在 YouTube 上上字幕（用校对好的 SRT），成片只留底部字幕安全区。
3. **中文一律走我的写作风格**（`personal-chinese-writing-style`：弯引号、半角破折号 ` - `、`......` 省略号；不用「讲清楚」；不堆网感词/拟人化动词）。文案、博客、推文都算。
4. **数字、商标、事实必核。** 引别人的话标出处；封面/文案里的关键数字别交给图像模型编。

## 交付清单（本 skill 的「完成」定义）

- [ ] **成片** - 4K master + 1080p，各一份，旁白已合流（`renders/`）
- [ ] **五比例封面** - 16:9 / 16:10 / 4:3 / 3:4 / 9:16，缺一不可（`covers/`）
- [ ] **平台文案** - `youtube.md`（标题候选 / 简介 / 相关链接 / 章节）+ `bilibili.md`（无章节，带赞助位）
- [ ] **博客** - `blog.md`（读完来分享的口吻 + 视频截图配图）
- [ ] **推文** - 一条精简的 X 文案

## 工作流骨架（每步的「怎么做」在 references 里）

一个选题 = 一个项目目录 `studio/videos/<YYYYMMDD-slug>/`，别散成多个兄弟目录。

- **Step 0 · 定题 + 两个选择** - 理解输入、选 design、选旁白来源。→ `references/designs.md`
- **Step 1 · 视频** - HyperFrames 出片：按选定 design 逐帧搭，画面跟着旁白语义走。→ `references/video.md`
- **Step 2 · 旁白接入** - TTS 或自录；自录时校对 SRT、按段切 per-frame 语音、`sync-durations`、**把每帧内部披露重排到真实 cue 时间轴**。→ `references/audio.md`
- **Step 3 · 五比例封面** - BlockFrame HTML 海报（响应式一份适配五比例）+ 官方品牌 logo。→ `references/covers.md`
- **Step 4 · 平台文案** - YouTube + Bilibili，段落骨架固定、内容当期填。→ `references/platform-copy.md`
- **Step 5 · 博客 + 推文** - companion 博客 + 一条推。→ `references/blog-and-tweet.md`
- **Step 6 · 验收 + 渲染** - 对交付清单逐项核，1080p 先出、4K master 看磁盘。→ `references/video.md` 末尾「渲染」。

## 复用现有脚本（不重复造轮子）

本 skill 是**编排层**；底层脚本直接复用 `skills/` 里现成的，别在 skills_v2 里重写：

- 封面出图/截图：`skills/assets/cover-design/scripts/`（`gen-cover.sh` / `render-cover.sh` / `check-covers.sh`）
- 品牌 logo：`skills/assets/brand-icons/scripts/`（`find-icon.sh` / `fetch-icon.sh`）
- HyperFrames：`npx hyperframes` CLI（init / lint / check / snapshot / render）+ faceless-explainer 系列 skill 的脚本（frame-packets / assemble-index / transitions / audio）

## 去哪查

| 要做… | 读 |
|---|---|
| 选设计 / design 目录 | `references/designs.md` |
| 搭视频、逐帧、重排节奏、渲染 | `references/video.md` |
| 旁白（TTS / 自录 + 校对 + 对齐 + 重拍节奏） | `references/audio.md` |
| 五比例封面（BlockFrame HTML + logo） | `references/covers.md` |
| YouTube / Bilibili 文案 | `references/platform-copy.md` |
| 博客 + 推文 | `references/blog-and-tweet.md` |
