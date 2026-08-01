# 视觉效果 · BlockFrame 皮肤

效果的**机制**（聚光/磨砂玻璃/背景模糊/放大镜）是设计中立的，写在 **`producing-video/references/visual-effects.md`**。本文件只给 BlockFrame 这套设计的**外壳皮肤值**（粗黑描边 + 硬阴影 + 糖果色 + 直角）和现成片段。

## 外壳变量填值（BlockFrame）
```css
:root{
  --fx-dim: rgba(0,0,0,.80);                 /* 聚光外圈压暗 */
  --fx-glass-bg: rgba(255,255,255,.30);      /* 磨砂底 */
  --fx-glass-border: 5px solid #000;         /* 粗黑边 */
  --fx-glass-radius: 0px;                     /* 直角，不圆角 */
  --fx-glass-shadow: 20px 20px 0 #000;        /* 硬阴影 */
}
```

## 现成片段

**磨砂玻璃卡（BlockFrame 皮肤）** —— 身后需铺糖果色块/大字才看得出模糊：
```html
<div class="glass" style="background:var(--fx-glass-bg); border:var(--fx-glass-border);
  box-shadow:var(--fx-glass-shadow); backdrop-filter:blur(22px) saturate(1.6);
  -webkit-backdrop-filter:blur(22px) saturate(1.6); padding:70px 80px; text-align:center;">
  <h2 style="font-weight:900;">磨砂玻璃卡片</h2>
</div>
```

**放大镜镜框（BlockFrame 皮肤）**：
```css
.lens{ border:8px solid #000; box-shadow:12px 12px 0 #000; border-radius:50%; overflow:hidden; }
```

**聚光被照卡片**：照常用 `.card`/`.stat`（黑边硬阴影糖果底），聚光层盖在其上即可，参数用 `--fx-dim`。

## 完整示例
四个效果都套 BlockFrame 皮肤的可跑合成，见示例项目：
`studio/videos/20260709-allwinner-a-stock-cn/fx-demo/`（全志这期做的效果验证 demo，逐帧抽验过）。

> 换 iOS/柔和皮肤时，只改上面的变量值（圆角 + 柔和阴影 + 细亮边），机制一行不动 —— 见 `producing-video/references/visual-effects.md` 的「外壳变量」表。
