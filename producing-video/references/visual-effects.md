# 视觉效果配方（Visual Effects）

场景级视觉效果的可复用配方：**只写机制**（纯 CSS + GSAP + 确定性渲染注意事项），外壳（描边/阴影/圆角/颜色）用 CSS 变量留口，由当前 frame/品牌填皮肤。全部在 HyperFrames 无头 Chrome 逐帧截图里验证过。

## 目录
- [通用铁律](#通用铁律)
- [① 局部高光 / 聚光 Spotlight](#-局部高光--聚光-spotlight)
- [② iOS 磨砂玻璃 Frosted Glass](#-ios-磨砂玻璃-frosted-glass)
- [③ 背景模糊 / 景深 Depth of Field](#-背景模糊--景深-depth-of-field)
- [④ 局部放大镜 Magnifier](#-局部放大镜-magnifier)
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
