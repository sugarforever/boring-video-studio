# 比例 → 构图与版式

**同一主题、同一画风，换比例只换 composition / layout。** 每个比例把下面那段 `Composition:` 和版式指令抄进提示词骨架即可。

## 目录
- [比例清单](#比例清单)
- [每个比例的版式指令](#每个比例的版式指令)
- [平台安全区（生成图同样要过）](#平台安全区生成图同样要过)
- [尺寸与校验](#尺寸与校验)

## 比例清单

| 比例 | 目标像素（下限） | 用在哪 |
|---|---|---|
| **16:9** | ≥ 1920×1080 | YouTube / B站主封面、合集封面（≥960×540） |
| **16:10** | ≥ 1920×1200 | B站横版 |
| **4:3** | ≥ 1440×1080 | 部分横版位 |
| **3:4** | ≥ 1080×1440 | 抖音 / 小红书 / 视频号 竖版主封面 |
| **9:16** | ≥ 1080×1920 | Shorts / 竖版缩略图 |
| **3:2** | ≥ 1536×1024 | **文章封面**（博客单图，不需要出全套） |

> 视频封面**五个比例缺一不可**；文章封面只出 3:2。

## 每个比例的版式指令

把 `{}` 里的句子放进骨架的 `Composition:` 与 `Visual composition:` 两处。

**16:9 / 16:10（宽）** —— 两种都行，按主题挑：
- *hero-left*：`Composition: hero-left — title and subtitle stacked in the upper-left; the illustration occupies the right two-thirds with generous negative space.`
- *hero-center*：`Composition: hero-center — title and subtitle CENTERED near the top-middle; the illustration spreads symmetrically below across the full width.`
> 16:10 比 16:9 高一点，主视觉可以再长一截；其余不变。

**4:3（方一些）**
`Composition: hero-center — title and subtitle CENTERED at top; the illustration sits directly below, more compact and vertically stacked than the widescreen version.`
> 横向空间少，**motif 要收紧**，别把设备/节点摊太开。

**3:4（竖版主封面）**
`Composition: hero-center, vertical stack — title large and CENTERED near the top, subtitle directly below it; the illustration occupies the middle band; leave the lower third calm.`
> 竖版首要是**标题大而清楚**，motif 退居中段。

**9:16（更瘦长）**
`Composition: hero-center, tall vertical stack — an even larger centered title at the top, subtitle below; the illustration is arranged vertically down the middle (elements stacked, not side-by-side); generous breathing room top and bottom.`
> 关键差别：**元素竖着排**，不要沿用横版的左右并置。

**3:2（文章封面）**
`Composition: hero-center — title and subtitle CENTERED near the top-middle; the illustration is a balanced, symmetric hero below with generous negative space.`

## 平台安全区（生成图同样要过）

跟图是怎么来的无关，`scripts/check-covers.sh` 照跑：

1. **右下时长徽标**：横版右下角会被播放器的时长胶囊盖住 —— 那一块别放文字或关键 motif。
2. **竖版 1:1 宫格裁切**：主页宫格按中心正方形裁 —— 标题必须落在中心方框内。
3. **120px 缩略图可读**：缩到 120px 宽还能认出标题，才算过。

生成图更容易踩 1 和 2（模型不知道平台会裁），出图后**务必按这三条看一遍**。

## 尺寸与校验

- gpt-image 给的是**最接近的整数尺寸**，不是数学精确比例（实测：`3:2 → 1536×1024`；`16:9 → 1672×941`）。
- `scripts/gen-cover.sh` 会自动：定位真实文件（codex 会谎报路径）→ `sips` 读尺寸 → 比例偏差 > 3% 或宽度不足时告警。
- 偏差可接受就直接用；偏得多就**重出**或**居中裁切**到目标比例（别拉伸）。
