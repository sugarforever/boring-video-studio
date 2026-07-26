# 封面 · BlockFrame HTML 海报（五比例）

我的封面是 **BlockFrame 糖果海报风**（粗黑边 + 硬阴影 + 糖果高亮 + 点阵底 + 巨字），走 **HTML → 无头 Chrome 截图**，不是 gpt-image。原因：中文标题 + 精确数字要**字字准**，HTML 排版可控，gpt-image 会写错汉字/数字。

> 品牌一致性：封面统一 BlockFrame，不随视频 preset 变。参照本仓 `studio/videos/20260721-to-tickets-cn/covers/cover-16x9.html` 那套响应式模板。

## 铁律

1. **封面是一套五比例**：16:9 / 16:10 / 4:3 / 3:4 / 9:16，缺一不可。
2. **出图后逐字核标题**（`Read` 每张）：无糊、无错字、无溢出。
3. **关键文字避开右下时长胶囊区**；竖版标题落在中心 1:1 方框内。

## 一份响应式 HTML 适配五比例

用 `vmin` 写一份 `covers/cover.html`，`@media (min/max-aspect-ratio: 1/1)` 分宽/窄两套排版。字体从 `../fonts/`（Space Grotesk / Noto Sans SC 900 / JetBrains Mono）。渲染：

```bash
RC=skills/assets/cover-design/scripts/render-cover.sh
$RC covers/cover.html covers/cover-16x9.png  1920 1080 2   # 逐个比例单独跑（循环易失败）
$RC covers/cover.html covers/cover-16x10.png 1920 1200 2
$RC covers/cover.html covers/cover-4x3.png   1440 1080 2
$RC covers/cover.html covers/cover-3x4.png   1080 1440 2
$RC covers/cover.html covers/cover-9x16.png  1080 1920 2
skills/assets/cover-design/scripts/check-covers.sh covers/   # 比例齐全 + 胶囊区 + 竖版中心 + 120px 可读
```

## 版式套路（可改，判断力优先）

- **钩子贴纸**：一个黄色高亮块放本期最扎的数字/看点（如「删 80%」），逆时针轻倾斜，放左上侧当贴纸。
- **kicker**：黑标 + 一句定位（如「Claude 5 · 时代 · 面向开发者」）。可嵌官方品牌 logo（见下）。
- **巨字标题**：主题词，Noto Sans SC 900，铺满宽度别挤在中间。
- **角度高亮**：一个绿/蓝高亮块放本期的「角度」（如「全新规则」）。
- 宽比例（16:9）容易挤中间留大片空 → 用 `@media (min-aspect-ratio)` 放大字号、拉开间距、铺满。

## 官方品牌 logo（别手画/AI 生成）

用 `brand-icons` 取官方矢量标（OpenAI / Anthropic / Claude / Gemini / DeepSeek / GLM…）：

```bash
SK=skills/assets/brand-icons/scripts
bash $SK/find-icon.sh claude          # slug 要搜不要猜
bash $SK/fetch-icon.sh claude-color covers/brand   # -color 品牌色 / 单色标放白块上
```

在封面里：`<img class="brandmark" src="brand/claude-color.svg">`，彩色标放奶油底、单色标放白/奶油小块（黑底会黑成一团）。渲完 `Read` 确认真渲出来了、不 tofu。

## 博客封面

博客单独一张（3:2 或直接复用 16:9），路径进 `blog-images/`。见 `references/blog-and-tweet.md`。
