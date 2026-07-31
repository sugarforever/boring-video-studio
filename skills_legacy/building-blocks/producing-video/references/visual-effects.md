# 视觉效果配方（Visual Effects）

场景级视觉效果的可复用配方：**只写机制**（纯 CSS + GSAP + 确定性渲染注意事项），外壳（描边/阴影/圆角/颜色）用 CSS 变量留口，由当前 frame/品牌填皮肤。全部在 HyperFrames 无头 Chrome 逐帧截图里验证过。

## 目录
- [通用铁律](#通用铁律)
- [① 局部高光 / 聚光 Spotlight](#-局部高光--聚光-spotlight)
- [② iOS 磨砂玻璃 Frosted Glass](#-ios-磨砂玻璃-frosted-glass)
- [③ 背景模糊 / 景深 Depth of Field](#-背景模糊--景深-depth-of-field)
- [④ 局部放大镜 Magnifier](#-局部放大镜-magnifier)
- [⑤ 材质填充大字 Text-as-Material](#-材质填充大字-text-as-material)
- [⑥ 光带扫字 Light-band Shimmer](#-光带扫字-light-band-shimmer)
- [⑦ 半调 canvas 底 Halftone Field](#-半调-canvas-底-halftone-field)
- [外壳变量（皮肤）](#外壳变量皮肤)

## 通用铁律
- **所有 tween 挂在注册到 `window.__timelines` 的 `tl` 上**，绝不用裸 `gsap.to/from`（渲染只 seek tl；裸 tween 在 seek 渲染里不跑）。
- **只用确定性逻辑**：无 `Date.now()`/`Math.random()`。
- 效果本身**设计中立**；描边/阴影/圆角/颜色一律走下方「外壳变量」，别把某个设计（如 BlockFrame 的黑边硬阴影）焊死进机制。

## ① 局部高光 / 聚光 Spotlight
把四周压暗、留一个亮圈，用来强调某个数字/元素（财经片念到「占 85%」时聚光那一格，加分且侵入性小）。

**机制**：一个覆盖场景的遮罩层，`radial-gradient` 中心透明、外圈半透明黑；用 **CSS 变量** `--sx/--sy` 定位亮圈中心，GSAP 动画移动它。CSS 变量驱动的径向渐变在无头 Chrome 里能逐帧重算（已验证）。

```css
#spot{ position:absolute; inset:0; z-index:50; pointer-events:none;
  background:radial-gradient(circle var(--fx-spot-r,250px) at var(--sx) var(--sy),
    rgba(0,0,0,0) 0%, rgba(0,0,0,0) 60%, var(--fx-dim, rgba(0,0,0,.80)) 100%); }
```
```html
<div id="spot" style="--sx:960px; --sy:540px;"></div>
```
```js
// 亮圈从画面中心移到目标元素中心（用场景内绝对坐标）
tl.set("#spot",{"--sx":"960px","--sy":"540px"}, at);
tl.to("#spot",{"--sx":"960px","--sy":"470px", duration:1.2, ease:"power2.inOut"}, at+0.2);
tl.to("#spot",{opacity:0, duration:0.6}, at+4.4);   // 收起
```

## ② iOS 磨砂玻璃 Frosted Glass
半透明卡片虚化其身后的内容 —— iOS 那种「毛玻璃」。视觉高级。

**机制**：`backdrop-filter: blur() saturate()` + 半透明底。**已验证在无头 Chrome/swiftshader 能出图**，但注意：
- 每帧多一层合成，**4K 长片渲染会略慢**（功能没问题，评估时留意时长）。
- 卡片**身后必须有非纯色内容**（色块/大字/图）才看得出模糊；纯底上看不出效果。
- 卡片 `z-index` 要压在背景之上。

```css
.glass{ background:var(--fx-glass-bg, rgba(255,255,255,.30));
  border:var(--fx-glass-border, 5px solid rgba(0,0,0,.85));
  border-radius:var(--fx-glass-radius, 0px);
  box-shadow:var(--fx-glass-shadow, 20px 20px 0 rgba(0,0,0,.85));
  backdrop-filter:blur(22px) saturate(1.6); -webkit-backdrop-filter:blur(22px) saturate(1.6); }
```
入场用普通 `tl.from(..., {opacity:0,y:120})` 即可；模糊本身是静态 CSS，不需要动画。
> 皮肤差异大：iOS 风 = 圆角 + 柔和阴影 + 细亮边；BlockFrame = 直角 + 硬阴影 + 粗黑边。别在机制里写死。

## ③ 背景模糊 / 景深 Depth of Field
背景层模糊、前景卡片清晰，营造景深，突出一个 callout。

**机制**：背景层 `filter: blur()`（可从 0 动画到 N），前景另起一层保持清晰。`filter:blur` 在渲染里稳定可靠。

```js
tl.fromTo("#bg", {filter:"blur(0px)"}, {filter:"blur(9px)", duration:0.8, ease:"power2.inOut"}, at);
tl.from("#callout", {opacity:0, scale:0.7, duration:0.6, ease:"back.out(1.6)", transformOrigin:"center"}, at+0.4);
```

## ④ 局部放大镜 Magnifier
圆形镜片滑过一行内容（芯片型号/财报小字），镜片内放大 m 倍并跟随。

**机制**：镜片 = 圆形裁剪（`border-radius:50%; overflow:hidden`）。镜片内放一份**目标内容的副本**（按场景坐标定位），整体 `scale(m)`（`transform-origin:0 0`）。镜片平移时，内部副本**反向平移 m 倍**，使镜心正下方的内容始终被放大居中。

几何（镜片左上 `(Lx,Ly)`、边长 `S`、放大 `m`）：
- 内部副本 `left = S/2 − (Lx+S/2)·m`，`top = S/2 − (Ly+S/2)·m`（让镜心场景点落在镜心 `(S/2,S/2)`）。
- 移动：镜片 `x` 走 `D`，内部副本 `x` 走 `−D·m`（`f` 会约掉，任意时刻镜心恒对齐）。

```js
tl.fromTo("#lens",       {x:0}, {x:D,        duration:3.4, ease:"power1.inOut"}, at);
tl.fromTo(".lens .inner",{x:0}, {x:-(D*m),   duration:3.4, ease:"power1.inOut"}, at);
```
**关键坑**：被放大的那行文字要**锁 `line-height` = `font-size`（并给等高 `height`）**，否则行盒的真实竖直中心不确定，放大点会上下偏（踩过）。

## ⑤ 材质填充大字 Text-as-Material
给巨号标题填上真实材质（金属/石材/织物），**零 WebGL、确定性、渲染直接嵌得进**。用来做片头/片尾/封面的 hero 标题。

**机制**：一层**纯色渐变**叠在一张**材质 PNG** 上、`multiply` 混合，整体 `background-clip:text` 裁进字形。所有观感走 CSS 变量，一套 class 服务 N 种材质。
```css
.mat-word{
  color:transparent;
  background-image: var(--solid-fill), var(--texture-url);        /* linear-gradient(#c,#c), url(masks/metal.png) */
  background-blend-mode: multiply;
  background-size: 100% 100%, 125% 125%;
  background-position: center, var(--mask-pos, 40% 50%);
  -webkit-background-clip:text; background-clip:text;
  -webkit-text-stroke: 1px rgba(255,255,255,.22);
}
```
**变体·材质翻页**：一个 `styleFrames[]`（材质 slug + 填充 + mask 位置 + 微偏移），用 `tl.set`/`tl.call` 在固定步长（如 0.105s）逐个换——一段确定性的"材质采样"快剪。微偏移（`x:-8..12`）保持生动而不引入随机。

## ⑥ 光带扫字 Light-band Shimmer
一道高光/金色带扫过一个词——廉价的"高级感"，同步到口播念到那个词的收尾。

**机制**：渐变裁进文字、动 `backgroundPosition`。
```css
.shine{ background-image:linear-gradient(90deg,#8a6a1a,#d4a72c,#f4d35e,#d4a72c,#8a6a1a);
  background-size:200% 100%; -webkit-background-clip:text; color:transparent; }
```
```js
tl.fromTo(".shine",{backgroundPosition:"100% 0"},{backgroundPosition:"0% 0",duration:0.6,ease:"power2.inOut"}, at);
```

## ⑦ 半调 canvas 底 Halftone Field
一整块**会呼吸的背景**（半调点阵采 fbm 域扭曲场 + 一层模糊色雾），不是装饰点、是"视频纹理底"。给氛围场用。

**机制**：整张 canvas 是 `bgState` 对象的**纯函数**——一条**线性主 tween** 推进单调参数、`onUpdate` 重画；噪声用整数 hash value-noise（无 `Math.random`），所以确定性、seek-safe。这是"代理时钟桥"（见 `runtime-adapters.md`）的一个 canvas 实例。
```js
tl.to(bgState, { flow:FINAL_FLOW, phase:FINAL_PHASE, duration:TOTAL, ease:"none",
                 onUpdate(){ drawHalftone(bgState); } }, 0);
```
**关键设计律·单调 vs 可绽放拆开**：`flow`/`phase`（"始终在动"的参数）**只由那条线性主 tween 推进、永远无零速边界**——否则背景会"动-停-动-停"卡顿感；每次换场的过场 tween **只准碰"可绽放"参数**（`density/radius/palette/wash/warp` 等）。再给一组静息基线常量（`REST_LIFT/REST_WASH…`），让落定的场景永远不发黑。**大位移别露边**：canvas plate 开到超出画布（如 `4320×3300`）。

## 外壳变量（皮肤）
机制留这些口，由 frame/品牌填值：

| 变量 | 含义 | BlockFrame 皮肤 | iOS/柔和皮肤 |
|---|---|---|---|
| `--fx-dim` | 聚光外圈压暗色 | `rgba(0,0,0,.80)` | `rgba(0,0,0,.55)` |
| `--fx-glass-bg` | 磨砂底色 | `rgba(255,255,255,.30)` | `rgba(255,255,255,.55)` |
| `--fx-glass-border` | 磨砂边 | `5px solid #000` | `1.5px solid rgba(255,255,255,.7)` |
| `--fx-glass-radius` | 磨砂圆角 | `0px` | `28px` |
| `--fx-glass-shadow` | 磨砂阴影 | `20px 20px 0 #000`（硬） | `0 24px 60px rgba(0,0,0,.25)`（柔） |

> BlockFrame 具体皮肤示例见 `blockframe-video/references/effects-blockframe.md`。
