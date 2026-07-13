# 配套博客（可选交付）

视频出完后，常再产一篇同主题**博客**（`studio/videos/<slug>/blog.md` + `blog-images/`）。形态 = **编辑手绘封面 + 精致数据图 + 数据表 + 客观正文**。数据口径和视频完全一致（都来自核过的 `research.md`）。

## 目录
- [一、正文写作（可派子 agent）](#一正文写作可派子-agent)
- [二、封面：codex-cli + gpt-image 编辑手绘](#二封面codex-cli--gpt-image-编辑手绘)
- [三、数据图：HTML→PNG，数字必精确](#三数据图htmlpng数字必精确)
- [四、图表库怎么选（Chart.js / D3 / 手写 SVG）](#四图表库怎么选chartjs--d3--手写-svg)

## 一、正文写作（可派子 agent）
适合派一个子 agent 写，但**必须锁死素材和口径**（否则会自己编数字）：
- **只吃 `research.md` / `script.md` / `narration.txt`**（官方原件核过的），不许编或改任何数字。
- 参考同系列已发布 `blog.md` 作格式模板。
- **Frontmatter**：`title`（有钩子、合规，含数字/事实反差，无涨跌预测/买卖/目标价）、`date`、`excerpt`、`tags`（公司名/A股上市公司速览/行业/板块/财报解读）、`cover: "blog-images/cover.png"`。
- **结构**：公司简介（含专业名词通俗解释，如 SoC）→ 主营与产品线 → 客户与销售 → 财务趋势 → 股东结构 → 小结 + 免责。**描述性 `##` 小标题，不要编号**。
- **六条口径红线（和视频同款，写错这篇就废）**：① 不构成投资建议 + 免责定格；② 「无实际控制人」等法定披露口径讲准；③ 年报「应用示例」品牌 ≠ 前五大客户（未具名的两码事）；④ 高增长如实拆（涨价/备货 vs 销量）；⑤ 连续增长 ≠ 扭亏；⑥ 国产替代/行业叙事标为「市场分析」，非公司口径。
- **风格**（用户偏好）：转述分享口吻、单破折号 ` - `、避开「讲清楚」、无网络用语、别拿英文概念词当中文名词（SoC/NPU/Fabless 等标准术语可用）。
- 交付后**回原件抽验关键数字**（别只信子 agent 自述），别自动 commit。

## 二、封面：codex-cli + gpt-image 编辑手绘
博客封面是**编辑艺术封面**（手绘、无精确数字/logo）—— 这类**可以** AI 生成，用 `codex-cli` skill 调 gpt-image。（区别于视频的**数据封面**，那种有精确数字/logo，仍走 HTML/截图，见 Step 5。）

先 `codex --version` 确认可用（≥0.143 稳）。提示词模板（填 `{}`）：
```
codex exec -s read-only "Generate an image, aspect ratio 3:2 (landscape article cover, high resolution).
Elegant hand-drawn editorial cover for a Chinese finance article.
Cover theme: {公司名}（{英文名}）— {一句公司定位 + 本期主线}.
Style: hand-drawn editorial ink.  Composition: hero-center — title/subtitle CENTERED near top-middle.
Title text: {公司名}
Subtitle text: {股票代码} · A股速览
Main visual: {该公司产品的手绘核心视觉，如 SoC 芯片 + 电路走线连到它驱动的终端设备}，居中作 hero，四周对称留白；一角画一条小的上升趋势线/三根渐高柱暗示增长.
Decorative: pencil-sketch annotations, node dots, dashed arrows, data-flow traces, a few hexagonal data tiles.
Color: warm off-white paper (#F7F3EA); deep charcoal/navy ink; restrained cyan for active paths; signal red very sparingly (one dot); muted graphite/steel-blue for grid/shadow.
Premium Chinese finance newsletter; research-notebook-meets-architecture sketch; uncluttered, readable at thumbnail.
Make all visible text crisp and EXACTLY: '{公司名}' and '{股票代码} · A股速览'.
No logos, no photorealistic people, no robot face, no dark gradient, no neon."
```
坑与规矩：
- **副标题放股票代码，别放日期**（`300458 · A股速览`）——博客非日期敏感，日期(MMDD)会被误读成日更。
- **布局 hero-center**（居中）比靠角更稳、更像封面。
- **中文字**：gpt-image 现在多数能渲对（含「·」中点），但**务必抽图核对文字是否清晰无错**；糊了/错字就重生成或改用 HTML 叠字。
- 生成后到 `${CODEX_HOME:-$HOME/.codex}/generated_images/<session>/ig_*.png` 找图（codex 常不打印路径），`sips` 验 3:2 尺寸，`cp` 到 `blog-images/cover.png`。详见 `codex-cli` skill 的「Finding Generated Images」。

## 三、数据图：HTML→PNG，数字必精确
博客里的数据图**不能 AI 生成**（生成模型画不准数字）——用 **HTML + CSS/SVG → 无头 Chrome 截图**（复用 `cover-design/scripts/render-cover.sh <html> <out.png> <W> <H> 2`，2× 高清）。
- **配色与封面一脉相承**（编辑风）：暖白纸底 `#F7F3EA` + 墨蓝 `#1f2a37` + 克制青蓝 `#2c7da0` + 钢蓝/浅灰做次级；细网格、点栅格。**别套视频那套 BlockFrame 糖果色**（两种语境）。
- 字体本地 woff2（Noto Sans SC + 数字用 Space Grotesk）。
- 三个常用原型（按数据配型）：
  - **收入结构 → 环形图**（SVG donut，`stroke-dasharray` 分段；主品类墨色、次级青/钢/浅）。
  - **多年营收+净利 → 柱 + 趋势线组合**（营收墨色柱、净利青色折线，各自刻度，值贴图上）。
  - **前十大股东 → 横向条形**（第一大青色高亮，其余墨色/钢色；配「无实控人·第一大仅 X%」注脚）。
- 出图后**抽图核对**：数字、比例、有无文字重叠（踩过：行内小标签压名字 → 去标签或加宽）。

## 四、图表库怎么选（Chart.js / D3 / 手写 SVG）
博客图是**静态 PNG**（截最终态，无需动画），所以视频那条「canvas 动画对不上 seek 时间轴」的限制**在这里不成立**。权衡：

| 方案 | 好处 | 代价 |
|---|---|---|
| **手写 SVG/CSS**（当前默认） | 完全控制、精确贴合编辑配色与手绘气质、像素级定制 | 手算坐标（柱高、donut 的 dash、折线点）易错 |
| **D3.js** | 用 `d3.scaleLinear`/`d3.pie`/`d3.arc` 算几何、**消掉手算数学**，仍输出可完全定制样式的 SVG；最贴合 bespoke 编辑风 | 代码更多；需**本地 vendor 该库**（截图端 `--virtual-time-budget` 短、可能无网，别用 CDN） |
| **Chart.js** | 标准 柱/线/饼 出图快、默认好看、自动轴/图例 | canvas 光栅、**默认观感偏通用**（难贴品牌手绘风）；静态要关动画；同样需本地 vendor |

**结论**：「更漂亮」不是自动的 —— 要**独特的品牌编辑观感**，手写 SVG / D3 胜过 Chart.js 的通用精致；Chart.js 适合**快出标准图、能接受通用观感**的场合。本系列建议**留在 SVG 路线**：图少就手写，**图变多/变复杂时上 D3**（省掉易错的手算、观感不降）。
> 视频里（确定性渲染）：Chart.js 的 canvas + 自带动画对不上 seek，不用；但可用 **D3 只算静态 SVG 几何**，再用 GSAP 挂 `tl` 做动画 —— 这条对视频也成立。
