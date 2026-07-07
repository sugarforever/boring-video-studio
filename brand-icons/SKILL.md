---
name: brand-icons
description: 给视频封面 / 合成 / 幻灯片取「官方的」AI、LLM、公司品牌矢量 logo（OpenAI、Anthropic、Claude、Gemini、DeepSeek、GLM / 智谱、Qwen、Mistral、Codex……），从 LobeHub Icons 的静态 SVG CDN 直接拉，不用手画也不用 AI 生成。提供按关键词搜图标 + 下载到项目的脚本。当用户说「加个 X 的 logo / 品牌图标」「封面放 OpenAI 标」「找 GLM 的 icon」「需要某模型的官方标识」时用本 skill。配合 blockframe-video（封面 / 合成里用）。
---

# Brand-Icons · 取官方 AI / 公司品牌 SVG logo

给 BlockFrame 封面、HyperFrames 合成、幻灯片配一个**真实的官方品牌标**（OpenAI 花标、Codex 终端标、智谱大象、Anthropic、Gemini、DeepSeek……），而不是手画或 AI 生成一个像但不对的。来源是 **LobeHub Icons**（`@lobehub/icons`）—— 一套专门收 AI / LLM 品牌 logo 的开源图标库，静态 SVG/PNG、无依赖。

## 为什么不直接 WebFetch 官网

`https://lobehub.com/icons/<brand>` 这个人看的页面**挡在 Vercel 机器人验证后面**（WebFetch / curl 都会拿到 `Vercel Security Checkpoint`，HTTP 403）。所以**别去抓那个页面**，直接走它的**静态 SVG npm 包 + jsDelivr CDN**（公开、无验证）：包名 `@lobehub/icons-static-svg`，图标在 `/icons/<slug>.svg`。

## 依赖

```bash
command -v curl python3      # 都要；脚本纯标准库
```

## 工作流

### Step 1 · 按关键词找图标 slug

别凭空猜 slug（GLM 的不是 `glm` 而是 `chatglm` / `glmv`；智谱是 `zhipu`）。先搜：

```bash
scripts/find-icon.sh <keyword>     # 如 glm / openai / anthropic / gemini / deepseek / qwen
```

每个品牌一般有 3 个变体：

| 文件 | 是什么 | 用在哪 |
|---|---|---|
| `<slug>.svg` | 单色（黑）标 | 浅底 / 需要描边的地方 |
| `<slug>-color.svg` | 品牌色标 | 想要原汁原味品牌色 |
| `<slug>-text.svg` | 文字 logo（含名字） | 当作 wordmark |

（不是每个品牌三个都齐，缺哪个 `fetch` 会自动跳过。）

### Step 2 · 下载到项目

```bash
scripts/fetch-icon.sh <slug> [outdir]      # outdir 默认 ./assets/brand
# 例：scripts/fetch-icon.sh chatglm assets/brand
#     scripts/fetch-icon.sh openai
```

把拿到的 SVG 放进项目（`assets/brand/`，再 `cp` 一份到 `build/brand/` 给合成、`cp` 到封面 HTML 同级给封面引用）。

### Step 3 · 在 BlockFrame 里用

- **单色标是黑的** → 放在**白/奶油色小块**里（黑底里会黑成一团看不见）。常见做法：墨色徽标条里嵌一个白底圆角小方块装 `<img>`：
  ```html
  <span class="badge"><img src="brand/openai.svg" alt="OpenAI"><span class="bt">OPENAI · 标题</span></span>
  ```
  ```css
  .badge img{width:58px;height:58px;background:#fff;border-radius:8px;padding:6px;}
  ```
- 想要品牌色就用 `-color.svg`；想直接显示牌子名用 `-text.svg`。
- **SVG 在 HyperFrames 合成里给 `<img>` 加 `data-layout-ignore`**（图标本身不需要 inspect 量版面）。
- **渲完一定 `Read` 看一眼**：确认 logo 真渲出来了、不是 tofu/空白，且不和深色背景撞色。

## Gotchas

1. **别 WebFetch `lobehub.com/icons/*`** —— Vercel 机器人验证，403。走 jsDelivr CDN（脚本已这么做）。
2. **slug 要搜不要猜。** GLM=`chatglm`/`glmv`、智谱=`zhipu`、Claude 系也分 `anthropic`/`claude`。先 `find-icon.sh`。
3. **单色标放浅底/白块**，别直接搁深色块上（黑底黑标看不见）。
4. **版权/商标**：这些是各家的注册商标，用于**介绍 / 评测 / 资讯**类内容的指代是合理使用范畴；别拿去做会让人误以为是「官方出品 / 背书」的东西。
5. **离线/封网**：脚本要联网拉 CDN。拿到的 SVG 建议**入库到项目 `assets/brand/`**，这样重渲不必再次联网。

## 超出范围

- **画原创 logo / 插画**：本 skill 只取**已有品牌**的官方标。要原创视觉用 `cover-image` 这类生成式 skill。
- **非 AI 品牌**：LobeHub 主收 AI/LLM/科技公司；冷门牌子可能没有，`find-icon.sh` 查不到就别硬凑。
- **出片 / 封面排版**：那是 `blockframe-video` / `producing-video` 的活，本 skill 只负责「把图标取到手」。
