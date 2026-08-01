# 选设计 · HyperFrames 预制 design 目录

视频的观感由一个 **frame preset（预制设计）** 决定 - 配色、字体、版式一整套。用户从以下列表选择（默认 BlockFrame）。

> **将以下表格中的设计完整列给用户做选择。**

来源 - https://www.hyperframes.dev/design

## 目录（slug + 一句风格）

| slug | 风格 |
|---|---|
| **blockframe**（默认） | 新粗野主义：粗黑边 + 硬阴影 + 糖果撞色。海报感、高点击率 |
| biennale-yellow | 暖羊皮纸 + 太阳黄，Instrument Serif，靛蓝墨，1px 细线 |
| blue-professional | 企业羊皮纸 + 钴蓝主色，Space Grotesk + Inter。稳、专业 |
| bold-poster | Shrikhand 倾斜大字 + 红点，奶油底。杂志封面能量 |
| broadside | 工业报纸海报：奶油/墨黑，Barlow，火橙点缀 |
| capsule | 胶囊编辑风：奶油纸 + 糖果色，Bodoni Moda 衬线标题 |
| cartesian | 极简留白：暖羊皮纸，墨色显示体，灰褐点缀，细线 |
| cobalt-grid | 编辑羊皮纸 + 钴蓝网格，Newsreader + Hanken Grotesk |
| code-editorial | 暖米纸 + 珊瑚点睛 + JetBrains Mono 代码面，EB Garamond。技术随笔感 |
| coral | Bebas Neue 大写标题 + 珊瑚，奶油底 |
| creative-mode | 奶油 + 饱和糖果，Archivo Black + JetBrains Mono |
| daisy-days | 阳光花园粉彩，3px 炭笔描边，硬阴影，Fredoka + Quicksand |
| editorial-forest | 绿/粉/奶油编辑三色，Source Serif 4 + JetBrains Mono，细线 |

> 官网列表会变，以官网为准。

## 本 skill 扩展的设计

这些 preset 存在本仓库 `references/frame-presets/<slug>/`，跟官网 preset 同一套 `FRAME.md` 契约，用法完全一样，只是取用时要加 `--preset-dir` 指到本地目录（见下）。

| slug | 风格 |
|---|---|
| **swiss-minimalism** | 瑞士国际主义 / Müller-Brockmann：素白纸 + 近黑墨 + **单一信号红**，Inter Tight / Inter / JetBrains Mono，严格 12 列网格 + 12px 基线，左对齐右不齐，极端字号反差，同心弧 / 点阵几何。零阴影 · 零渐变 · 零圆角 |
| **raycast-dark** | 暗色开发者工具（inspired by Raycast）：近黑蓝调 `#07080a` + macOS 多层阴影/内高光质感 + **信号红 `#FF6363` 点睛**，Inter（正字距）+ JetBrains Mono，键帽、命令面板行、对角红条纹。深度即身份 |
| **claude-warm** | 暖色编辑风（inspired by Claude/Anthropic）：羊皮纸 `#f5f4ed` + 近黑墨 + **赤陶 `#c96442` 点睛** + 静默橄榄绿次色，Newsreader 衬线标题 + Inter + JetBrains Mono，书卷气行高、手绘感下划线、柔和卡片。温暖、文气 |

每个本地 preset 目录交付三件：`FRAME.md`（规范）、`frame-showcase.html`（预览页，浏览器直接打开看效果）、`caption-skin.html`（卡拉 OK 字幕皮肤）。