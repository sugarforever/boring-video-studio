# 提示词模板与主题构图配方

封面用 `codex-cli` 调 gpt-image 生成。**画风固定、构图按主题变、版式按比例变。**

## 目录
- [提示词骨架（填空）](#提示词骨架填空)
- [固定画风段（每次原样带上）](#固定画风段每次原样带上)
- [主题 → 构图配方](#主题--构图配方)
- [已验证的实例](#已验证的实例)
- [文字规矩](#文字规矩)

## 提示词骨架（填空）

比例那一行由 `scripts/gen-cover.sh` 自动加在最前面，这里只写正文：

```
Create an elegant hand-drawn editorial cover image for a Chinese {领域} article/video.
Cover theme: {一句主题 + 本期主线}.
Style: hand-drawn editorial ink.
Composition: {见「按比例的版式」——hero-center / hero-left …}.

Title text: {主标题，≤6 个汉字或一个短产品名}
Subtitle text: {副标题，≤12 字符，放代码/系列名，不放日期}

Visual composition:
- {版式指令：标题居中于上方 / 左上；副标题紧随其下}
- Main visual: {主题配方里的 motif，作 hero；四周对称留白}
- Decorative elements: pencil-sketch annotations, node dots, dashed arrows, data-flow traces, a few small hexagonal data tiles.

Color scheme:
- Background: warm off-white paper (#F7F3EA)
- Primary ink: deep charcoal / navy-black
- Accent: restrained cyan blue for active data paths. {可选：a warm amber used sparingly for X}
- Secondary: muted graphite and pale steel blue for grid lines and shadow lines.

Style notes:
- Premium Chinese {finance|tech} newsletter cover; research-notebook-meets-systems-architecture sketch.
- Hand-drawn but precise. Uncluttered and readable at thumbnail size.
- Make all visible text crisp, legible, and EXACTLY as specified: '{主标题}' and '{副标题}'.
- No logos, no photorealistic people, no generic robot face, no dark gradient background, no glowing neon effects.
```

## 固定画风段（每次原样带上）

暖白纸底 `#F7F3EA` + 墨蓝主线 + **克制的青蓝**做数据路径 + 极少量信号红/琥珀点缀；铅笔标注、节点圆点、虚线箭头、几块六边形数据格。**手绘但精准**，缩略图尺寸下仍可读。这一段不要改，它是系列的一致性来源。

## 主题 → 构图配方

| 主题类型 | Motif（hero） | 备注 |
|---|---|---|
| **芯片 / 硬件公司** | 中央一颗 SoC 芯片（方形带引脚），细电路走线向外连到它驱动的终端设备（平板、扫地机、摄像头、车机），对称环绕 | 一角画小的上升柱/趋势线暗示增长 |
| **模型发布（多档位）** | 用天体表达档位：太阳（旗舰）居中、地球（均衡）与月牙（最省）分列两侧，细数据流串联 | 有并行/多智能体概念时：下方画 N 个节点汇聚成一条线 |
| **财务 / 增长** | 上升的 K 线或渐高柱 + 一条平滑上扬曲线；旁边配财报文档 + 钢笔、硬币堆 | **精确数字不要交给模型**，见「文字规矩」 |
| **工具 / 框架** | 管线示意：源文件 → 渲染 → 帧序列 → 成片；箭头串联 | 适合讲流程的选题 |
| **安全 / 治理** | 分层护盾（同心层）+ 被拦截的节点；一枚小红点作警示 | 别画武器、别画人脸 |
| **频道 / 合集** | 该频道主业的抽象场景（如神经网络节点 → K 线图），四周点缀领域符号 | 标题用频道名，副标题用一句定位 |

新主题就往这张表里加一行，**别每次即兴**。

## 已验证的实例

这三张都是真出过、文字渲染正确的（可直接抄改）：

| 用途 | Title / Subtitle | Motif |
|---|---|---|
| 财经文章封面（3:2） | `全志科技` / `300458 · A股速览` | SoC 芯片 + 走线连到平板/扫地机/摄像头/车机 |
| AI 文章封面（3:2） | `GPT-5.6` / `Sol · Terra · Luna` | 太阳+地球+月牙三档 + 四个并行节点汇聚成一条线 |
| B站合集封面（16:9） | `AIGC财经频道` / `AI 驱动 · 客观财经数据分享` | 神经网络节点 → 上升 K 线图，配财报/硬币/环形图 |

## 文字规矩

- **标题短、副标题更短**。实测中文标题（`全志科技`、`AIGC财经频道`）与中点 `·` 都能渲对，但**字越多越容易出错**。
- **副标题放股票代码 / 系列名，别放日期**（`MMDD` 会被读成日更）。
- **出图后必须逐字核对**（`gen-cover.sh` 会提醒）。糊了或错字：改 prompt 重出，**绝不在生成图上盖字修字**。
- **需要精确数字、精确商标时**（财务数据封面、带 logo 的封面）：那部分不要交给图像模型 —— 用 `scripts/render-cover.sh` 走 HTML→PNG 精确排版，或把数字挪到视频/正文里。这条是兜底，不是默认。
