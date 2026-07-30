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

> 列表会变，以官网为准。

## 怎么用（选完之后）

视频本身走 **faceless-explainer** 的流程（文章/主题 → 无实拍讲解），它的 Step 2 就是「选一个 preset 生成 `frame.md`」：

```bash
node <faceless-explainer>/scripts/build-frame.mjs --preset <slug> --hyperframes .
```

`frame.md` 就是这一期的配色/字体/版式。之后逐帧搭画面都以它为准。详见 `references/video.md`。
