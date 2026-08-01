---
name: cover-design
description: 给一条视频或一篇文章出封面：用 codex-cli 调 gpt-image 生成手绘编辑风封面。画风固定（暖白纸底 + 墨线 + 克制青蓝），构图按主题变，版式按比例变（视频五比例 / 文章 3:2）。自带 codex 出图 wrapper（codex 会谎报保存路径）、尺寸与比例校验、平台安全区三道检查。当用户说「做封面 / 配齐封面 / 换个封面设计 / 文章封面 / 合集封面 / 封面漏了某个比例」时用本 skill。
---

# cover-design · 主题 → 一整套封面

**本 skill 拥有封面。** `blockframe-video` 与 `finance-stock-video` 的封面步骤都委托到这里。

三件事：

1. **一套画风**：手绘编辑墨线（暖白纸底 `#F7F3EA` + 墨蓝 + 克制青蓝 + 极少量琥珀/信号红）。系列一致性的来源，**不要改**。
2. **一条生成管线**：`codex-cli` → gpt-image → 定位真实文件 → 校验尺寸/比例 → 落盘。
3. **三道看得见的检查**：右下时长徽标安全区、竖版 1:1 宫格裁切、120px 缩略图可读性。

> **铁律一：封面是「一套」，不是「一张」。** 视频封面五个比例（16:9 / 16:10 / 4:3 / 3:4 / 9:16）缺一不可；文章封面只出 3:2。
> **铁律二：出图后必须逐字核对标题。** 生成模型会写错汉字与数字。糊了或错字 → **改 prompt 重出**，绝不在图上盖字修字。
> **铁律三：codex 会谎报路径。** 它报告「已保存到 ./x.png」，而其实写在 `$CODEX_HOME/generated_images/<thread>/`。永远走 `scripts/gen-cover.sh`，别信它的话，也别编路径。

## 依赖检查

```bash
codex --version                  # ≥ 0.143 稳；缺了就停下告诉用户
command -v sips                  # 尺寸校验（macOS 自带）
```

## 工作流

### Step 1 · 定标题与钩子

- **主标题**：≤6 个汉字，或一个短产品名（`全志科技` / `GPT-5.6` / `AIGC财经频道`）。
- **副标题**：≤12 字符。放**股票代码 / 系列名 / 一句定位**，**别放日期**（`0709` 会被读成日更）。
- 字越多越容易渲错。想说的细节留给正文和视频，别堆在封面上。

### Step 2 · 选构图配方（按主题）

去 **`references/prompt-templates.md`** 的「主题 → 构图配方」表挑一行（芯片 / 模型发布 / 财务增长 / 工具框架 / 安全治理 / 频道合集），拿到这条主题的 motif。新主题就往表里**加一行**，别每次即兴。

### Step 3 · 按比例出图

同一主题、同一画风，**换比例只换 composition / layout**。每个比例的版式指令抄 **`references/ratios.md`**。

```bash
# 提示词写进文件，逐个比例出（比例那行由脚本自动加在最前）
scripts/gen-cover.sh covers/cover-16x9.png  16:9  /tmp/p-h.txt   1600
scripts/gen-cover.sh covers/cover-16x10.png 16:10 /tmp/p-h.txt   1600
scripts/gen-cover.sh covers/cover-4x3.png   4:3   /tmp/p-43.txt  1200
scripts/gen-cover.sh covers/cover-3x4.png   3:4   /tmp/p-v.txt   1000
scripts/gen-cover.sh covers/cover-9x16.png  9:16  /tmp/p-916.txt 1000
# 文章封面只要一张
scripts/gen-cover.sh blog-images/cover.png  3:2   /tmp/p-art.txt 1500
```

`gen-cover.sh` 会：跑 codex → **定位真实生成文件**（不信它报的路径）→ `sips` 读尺寸 → 比例偏差 >3% 或宽度不足时告警 → 拷到目标路径。

> gpt-image 给的是最接近的整数尺寸，不是数学精确比例（实测 `3:2 → 1536×1024`，`16:9 → 1672×941`）。偏差小就用；偏得多就重出或**居中裁切**（别拉伸）。

### Step 4 · 校验

**视频封面（五比例）** —— 三道自动检查 + 一道人工：

```bash
scripts/check-covers.sh covers/     # 比例齐全 + 右下徽标安全区 + 1:1 宫格裁切 + 120px 可读
```

**文章封面（单张 3:2）** —— **不要跑 `check-covers.sh`**：它按视频五比例（`3x4 9x16 16x9 16x10 4x3`）验收，对只出 3:2 的文章封面会把五个比例全报 MISSING、必然失败。文章封面只需要：**120px 缩略图可读** + 下面那道人工核对。（右下时长胶囊、竖版宫格裁切是视频平台的事。）

**最后一道只能人看，也是最后一道防线**：`Read` 每张图，**逐字核对标题与副标题**是否清晰无错别字。生成图容易踩两件事 —— 模型不知道平台会在右下角盖时长胶囊、也不知道竖版会被中心裁成正方形，**关键文字务必落在安全区内**。

> 一旦 `gen-cover.sh` 报「没读到 thread_id」，**停下排查，不要信任任何产物**（见 `references/codex-imagegen.md`）。

## 什么时候**不**用生成图

一条兜底规则，不是默认路径：

- **需要精确数字或真实商标时**（财务数据封面、必须准确的百分比、公司 logo），那部分别交给图像模型 —— 用 `scripts/render-cover.sh <html> <out.png> <W> <H> 2` 走 HTML → 无头 Chrome → 2× PNG 精确排版；或者干脆把数字挪进视频与正文。
- `scripts/render-cover.sh` 也是通用的 HTML→PNG 截图器，博客里的**精确数据图**（环形图、柱状图、排名条）就用它。
- 走 HTML 路时想要**质感 hero 标题**（金属/石材/织物填充的巨字、或一道金色光带扫过），用 `producing-video/references/visual-effects.md` 的「⑤ 材质填充大字 / ⑥ 光带扫字」——纯 CSS `background-clip:text`，静态封面直接截图即可，无需动效。

## 参考

- **`references/prompt-templates.md`** —— 提示词骨架、固定画风段、主题→构图配方表、已验证实例、文字规矩
- **`references/ratios.md`** —— 每个比例的版式指令、平台安全区、尺寸与校验
- **`references/platforms.md`** —— 各平台封面位与安全区细节
- **`references/codex-imagegen.md`** —— codex 出图的契约与边界（为什么必须走 wrapper）
- `legacy/` —— 旧的 HTML 封面模板与批量渲染脚本（已退役，留档备查）

## 交付清单

- [ ] 视频：五个比例齐全（16:9 / 16:10 / 4:3 / 3:4 / 9:16）；文章：3:2 一张
- [ ] 每张都 `sips` 验过尺寸，比例偏差在可接受范围
- [ ] **逐字核对过标题/副标题**，无糊无错字
- [ ] 视频封面：`check-covers.sh` 三道检查全过（文章封面跳过它，只验 120px 可读）
- [ ] 关键文字避开右下徽标区；竖版标题落在中心 1:1 方框内
- [ ] 封面 PNG 收在项目的 `covers/`（文章封面进 `blog-images/`），不落项目外
