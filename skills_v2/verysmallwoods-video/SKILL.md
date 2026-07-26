---
name: verysmallwoods-video
description: 小木头的个人视频流水线。基于一个主题，一篇文章，或一份口播稿，生成一整套可发布物料：视频成片，封面图，YouTube/Bilibili 文案，博客，以及社交媒体推广文案。视频制作采用 HyperFrames。
---

你是这条流水线的**编排者**。输入一个主题 / 一篇文章 / 一份口播稿，产出一整套可发布物料（见「交付清单」）—— 不是一个 mp4。按工作流骨架走，逐项对交付清单验收。

**视频出片委托给 HyperFrames，不要在这里重讲那套。** 入口是 `/hyperframes`（核心入口，它把「文章/主题 → 无实拍讲解」路由到 `/faceless-explainer` 这个 workflow 去搭画面、逐帧、渲染）。本 skill 是它**之上**的一层编排 —— 把视频、封面、文案、博客、推文凑成整套，并贯彻用户（小木头）的口径。任何视频生成上的不确定 → 先读 `/hyperframes`。

**开局先问用户两件事**（别替他定）：① **视频设计** —— 从预制 design 选一个（默认 `blockframe`，见 `references/designs.md`）；② **旁白来源** —— 自己录 或 TTS（见 `references/audio.md`）。其余决定尽量用判断，只在拿不准、或涉及事实/口径/发布这类不可逆时才问用户。

## 交付清单（本 skill 的「完成」定义）

- [ ] **成片** - 4K master + 1080p，各一份，旁白已合流（`renders/`）
- [ ] **五比例封面** - 16:9 / 16:10 / 4:3 / 3:4 / 9:16（`covers/`）
- [ ] **平台文案** - `youtube.md` 和 `bilibili.md`
- [ ] **博客** - `blog.md`
- [ ] **推文** - 一条精简的社交媒体推广文案

## 工作流骨架（每步的「怎么做」在 references 里）

一个选题 = 一个项目目录 `studio/videos/<YYYYMMDD-slug>/`

- Step 0 · 定选题、问两个选择（设计 + 旁白来源）→ `references/designs.md`
- Step 1 · 视频 —— 走 `/hyperframes` → `/faceless-explainer` 出片，本 skill 只补口径 → `references/video.md`
- Step 2 · 旁白接入 → `references/audio.md`
- Step 3 · 生成五比例封面 → `references/covers.md`
- Step 4 · 生成平台文案 → `references/platform-copy.md`
- Step 5 · 博客 + 推文 → `references/blog-and-tweet.md`
- Step 6 · 验收 + 渲染 - 对交付清单逐项核，1080p 先出、再出 4K master

## 参考

| 要做… | 读 |
|---|---|
| 选设计 / design 目录 | `references/designs.md` |
| 搭视频、逐帧、重排节奏、渲染 | `references/video.md` |
| 旁白（TTS / 自录 + 校对 + 对齐 + 重拍节奏） | `references/audio.md` |
| 五比例封面 | `references/covers.md` |
| YouTube / Bilibili 文案 | `references/platform-copy.md` |
| 博客 + 推文 | `references/blog-and-tweet.md` |
