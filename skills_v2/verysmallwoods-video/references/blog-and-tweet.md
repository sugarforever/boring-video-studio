# 博客 + 推文

## 博客（companion）

一篇配套博客，草稿存项目里 `blog.md`。发布是把它挪到我的站 `verysmallwoods` 仓库 `src/content/blog/YYYYMMDD-slug.md`、图挪到 `public/images/blog-assets/`（那次移动才算发布）。

### 口吻与结构

- **读完来分享的口吻** - 转述外文文章时别以老师拆解/答疑自居；「我读完挺受启发，来分享」。
- 反思型深度：常用一个 **题眼**（本文最要紧的一件事）当骨架，其余围着它转。
- 结尾轻收，别 `## 总结`/`## 最后` 硬收，别堆链接。给出处链接就好。
- 全程我的写作风格（`personal-chinese-writing-style`：弯引号、半角 ` - `、`......`；不用「讲清楚」；不堆网感/拟人词）。
- 参照本仓 `studio/videos/20260721-to-tickets-cn/blog.md` 的调性。

### frontmatter

```yaml
---
title: "..."          # 带钩子
date: "YYYY-MM-DD"
excerpt: "..."
tags: [...]           # 用规范 tag（Context Engineering / Claude Code / Agent Skills / AI 编程…），别堆同义词
lang: "zh"
cover: "blog-images/blog-cover.png"
---
```

### 配图 = 视频截图

从成片里挑几张**有代表性、且已完全展开**的帧，插到对应小节。做法：

```bash
npx hyperframes snapshot --at <各代表帧的完全展开时刻>   # 取绝对秒
```

把 `snapshots/frame-*.png` 拷到 `blog-images/`，用 `![说明](blog-images/xxx.png)` 插进对应段落。选 4-6 张即可（开场钩子、题眼、主体一张、落地清单、实战各一）。

## 推文（X）

一条精简的：

- 开头一句钩子（本期最扎的数字/结论）。
- 主体用箭头/序号列关键点（如六条规则 `旧 → 新`），可扫读。
- 一句话收（论点），别堆空洞自我总结。
- 出处链接（原文）。可选：挂自己的视频链接。

给一版即可，我要更短/挂视频再说。
