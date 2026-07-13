# codex-cli 出图 · 契约与边界

本 skill 的封面由 `codex-cli` 调 gpt-image 生成。这份文件只讲**工具的真实行为**和**必须遵守的契约** —— 画风与构图见 `prompt-templates.md`，版式见 `ratios.md`。

## 两个入口

| 脚本 | 出什么 | 用在哪 |
|---|---|---|
| **`scripts/gen-cover.sh`** | 一张完整封面（**含标题文字**），按比例出 | 视频五比例封面、文章 3:2 封面 |
| `scripts/codex-mark.sh` | 一个**不含任何文字**的 house-style 小图形（可抠透明底） | 需要单独一枚标记 / 吉祥物时；出好后提交进仓库复用，永不重生成 |

---

## 为什么必须用 wrapper

`codex exec` 会**报告**「已保存到 ./x.png」，而它并没有。内置 `image_gen` 工具**总是**把图写到：

```
$CODEX_HOME/generated_images/<thread_id>/*.png
```

而且**没有任何参数**能改这个位置。之后 agent 被要求自己 `cp` 过去 —— 它可能跳过、可能弄错，也可能只是宣称做了。

> 本仓库早先据此得出「codex 图片工具此环境不可用（会谎称成功不落盘）」。**工具是好的，报告是假的。** 该结论已在 2026-07 实测推翻并修正。

所以两个脚本都**从不相信 agent 说的路径**：

```
codex exec --json …                        → 从事件流读 thread_id
$CODEX_HOME/generated_images/<thread_id>/  → 取里面最新的 PNG（唯一真相）
→ 落到 --out                                → 验 PNG magic + 尺寸 + 比例偏差
```

---

## 实测过的行为（codex-cli 0.143.0）

| 事项 | 事实 |
|---|---|
| 调用方式 | `codex exec --json -s read-only "<prompt>"`（出图不需要写盘权限） |
| 落盘位置 | `$CODEX_HOME/generated_images/<thread_id>/*.png` —— **不可配置** |
| **比例** | 没有 `--size` 参数。**把比例写进 prompt 第一行，模型会听。** 实测：`3:4 → 1086×1448`（正好 0.75）、`3:2 → 1536×1024`、`16:9 → 1672×941` |
| 尺寸 | 给的是**最接近的整数尺寸**，不是数学精确比例。偏差 >3% 就居中裁切或重出，**别拉伸** |
| 数量 | 一次调用一张（`n=1`）。多张 = 多次调用（**五个比例 = 五次**） |
| 鉴权 | 用户的 Codex 订阅。**不读、不发 `OPENAI_API_KEY`** |
| **中文字** | 短标题多数能渲对，中点 `·` 也行（实测 `全志科技`、`AIGC财经频道`、`GPT-5.6`、`Sol · Terra · Luna`）。**字越多越容易出错，必须逐字核对** |
| 透明底 | 内置工具不支持真透明。出 `#00ff00` 色键底 → 抠图（`codex-mark.sh --transparent` 已封装） |
| 耗时 | 单张约 40–90s |
| **stdin** | 非交互环境下 `codex exec` 会读 stdin 并**永久阻塞**（打印 `Reading additional input from stdin...`）。脚本里必须 `< /dev/null` |
| **cwd** | cwd 不是受信任的 git 目录时 codex **直接拒跑**（`Not inside a trusted directory and --skip-git-repo-check was not specified.`）。从 `/tmp` 之类的地方调用必中招 —— 脚本里必须带 `--skip-git-repo-check` |

**失败模式**，按出现频率：

1. **cwd 非 git 目录**（忘了 `--skip-git-repo-check`）—— codex 拒跑，事件流为空。
2. **模型改去写 SVG / 代码**而不是出图 —— `gen-cover.sh` 在 prompt 末尾钉了 `Output a raster image. Do not write SVG or any code.`
3. **涉及真实商标时拒绝** —— 别在 prompt 里点名品牌 logo。
4. **忘了 `< /dev/null`** —— 不是超时，是 codex 在等 stdin，会一直挂着。
5. **超时**。

全部会在脚本里**明确报错并打印 codex 的 stderr**，不会静默成功。

> ### ⚠ 为什么没有「兜底取全局最新 PNG」
> 早期版本在读不到 `thread_id` 时会退回「取 `generated_images/` 下最新的 PNG」。**实测这会抓到另一个并发 codex 进程刚生成的无关图片** —— 它是合法 PNG、尺寸也可能接近，于是 PNG magic 与尺寸校验**全部通过**，脚本报「成功」，落盘的却是彻头彻尾的错图。唯一挡住它的是「必须 Read 逐字核对」那道人工检查。
>
> 所以现在：**读不到 `thread_id` 一律硬失败**。那道人工看图的检查不是锦上添花，是最后一道防线。

---

## 契约（违反就出废图）

1. **不信 codex 自述的路径。** 永远走脚本，靠 `thread_id` 定位。
2. **出图后必须 `Read` 那张 PNG，逐字核对标题与副标题。** 糊了或错字 → **改 prompt 重出**。
3. **绝不在位图上盖字修字。** 不用 ImageMagick / Pillow / SVG 叠加去补救 —— 补上去的字和生成的画永远不是一套笔触。
4. **prompt 里不要点名真实品牌 / 商标。** 模型要么拒绝，要么画出一个「像但不对」的假商标。
5. **需要精确数字或真实 logo 时，别交给图像模型。** 那部分走 `scripts/render-cover.sh` 的 HTML→PNG 精确排版，或把数字挪进视频与正文。这是兜底，不是默认。
6. **关键文字要落在安全区内。** 模型不知道平台会在右下角盖时长胶囊、竖版会被中心裁成正方形 —— 出图后跑 `scripts/check-covers.sh`。

## prompt 怎么写主体

- **具体名词，不要形容词。**「一颗方形带引脚的 SoC 芯片，细走线连到平板与扫地机」好过「一个科技感的主视觉」。
- **说清位置与朝向**：居中作 hero、四周对称留白、某元素放哪个角。
- **标题短**：≤6 个汉字或一个短产品名；副标题 ≤12 字符。
- 画风段（暖白纸底 / 墨蓝 / 克制青蓝 / 手绘但精准 / 缩略图可读 / 无 logo 无人脸无霓虹）**原样带上**，那是系列一致性的来源。

## 前置条件

```bash
command -v codex          # codex-cli 在 PATH 上（≥ 0.143）
codex login               # 有效登录（wrapper 在 thread_id 缺失时会提示）
command -v sips           # 尺寸校验（macOS 自带）
```

没有 codex？封面这条路就断了 —— 退回 `scripts/render-cover.sh` 的 HTML→PNG，或先空着封面把成片交出去。
