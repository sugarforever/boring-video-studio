# 运行时适配器（Runtime Adapters）— 把命令式引擎接进确定性时间轴

有时候一个场景想要 GSAP tween 表达不了的东西：真着色器（WebGL）、Canvas2D 粒子场、Lottie 矢量动画、绕环的 3D 阵列。HyperFrames 渲染**只 seek 一个 `tl`**、**不跑 `requestAnimationFrame`**——所以这些引擎**不能自己持有时钟**。本文给出把它们接进来的通用桥，全部在 HeyGen 官方 launch 片里逐帧渲染验证过。

> 更全的七种官方 adapter（GSAP/Lottie/Three.js/Anime.js/CSS/WAAPI/TypeGPU）见外部 `hyperframes-animation` skill；本文是本仓库工作流里最常用的几种的**自足配方**。

## 目录
- [通用铁律](#通用铁律)
- [① 代理时钟桥 · Proxy-clock Bridge（万能）](#-代理时钟桥--proxy-clock-bridge万能)
- [② 着色器 · WebGL / Canvas u_time](#-着色器--webgl--canvas-u_time)
- [③ Lottie 帧驱动 · 中和 goToAndStop](#-lottie-帧驱动--中和-gotoandstop)
- [④ 伪 3D · CSS preserve-3d（不用 three.js）](#-伪-3d--css-preserve-3d不用-threejs)
- [⑤ DOM→纹理捕获 · 任意两个 HTML 场景之间跑着色器](#-dom纹理捕获--任意两个-html-场景之间跑着色器)
- [硬化清单 · 永不黑屏](#硬化清单--永不黑屏)

## 通用铁律
- **引擎不持有时钟，`tl` 才是时钟**。渲染 = 时间轴进度的**纯函数**。
- **绝不 `requestAnimationFrame`**（渲染里不跑 rAF）。用一个**代理对象**在 `tl` 上 `ease:"none"` 补间，真正的绘制放 `onUpdate`。
- **只用确定性逻辑**：着色器噪声用 **hash 型 value noise**（`hash(dot(uv,…))`），**不用** `Math.random`、不用外部纹理种子；粒子散布用**黄金角**或**种子化 PRNG**（见 `motion-patterns.md` 14）。
- **先画 frame-0**：初始化后立刻 `render(起始 t)` 画一帧，否则 seek-to-0 是黑的。

## ① 代理时钟桥 · Proxy-clock Bridge（万能）
**这是接任何命令式引擎的唯一配方**：tween 一个 `{t}` 代理，`onUpdate` 里把 `t` 喂给引擎的绘制函数。
```js
function renderFrame(t){ /* 用 t 更新 uniform / 重画 canvas / 摆放粒子 */ gl.uniform1f(uTime, t); draw(); }
renderFrame(0.5);                              // 先画 frame-0，seek-to-0 不黑
const proxy = { t: 0.5 };
tl.to(proxy, { t: 1.44, duration: 0.94, ease: "none",
               onUpdate(){ renderFrame(proxy.t); } }, 0);
```
引擎的"帧"参数（`u_time` / Lottie frame / 粒子相位）**全部只从 `proxy.t` 来**，于是同一 `t` 永远出同一像素 —— 逐帧 seek 可重算、可复现。

## ② 着色器 · WebGL / Canvas u_time
**机制**：编一个全屏 quad，fragment 用 `u_time`（由代理时钟喂）做溶解/扭曲/发光；噪声用 hash：
```glsl
float hash(vec2 p){ return fract(sin(dot(p, vec2(127.1,311.7)))*43758.5453); }
// fbm(p + fbm(p)) 域扭曲、cosine 调色板做发光边，全是 uv+u_time 的纯函数
```
```js
tl.to(prog, { t:1, duration:1.4, ease:"power2.inOut", onUpdate(){ gl.uniform1f(uTime, prog.t); draw(); } }, at);
```
**已验证效果**：RGB 通道裂开重组（三块 `AdditiveBlending` 平面）、径向 portal 揭幕、从 logo 发出的体积光 ray-march。都靠"状态对象 + 代理时钟"驱动，seek-safe。

## ③ Lottie 帧驱动 · 中和 goToAndStop
**机制**：`autoplay:false, loop:false` 加载，抓住原始 `goToAndStop`，再**把该方法替换成 no-op**（防止运行时自动推进），然后用代理时钟驱动帧。
```js
const anim = lottie.loadAnimation({container:box, renderer:'svg', loop:false, autoplay:false, animationData:data});
const orig = anim.goToAndStop.bind(anim);
const setFrame = (f)=>{ try{ orig(f, true); }catch(e){} };   // 第二参 true = 按帧（非时间）
anim.goToAndStop = function(){};                             // 中和自动推进
anim.addEventListener('DOMLoaded', ()=> setFrame(0));
const bf = {frame:0};
tl.to(bf, { frame:55, duration:1.3, ease:"none", onUpdate(){ setFrame(bf.frame); } }, 0.05);
```
**坑**：JSON 用 `fetch('assets/bell.json')`（相对路径）加载，`../files/...` 在渲染时 404。

## ④ 伪 3D · CSS preserve-3d（不用 three.js）
**何时用**：装饰性的 1–2s 3D 小节（绕环文字、翻牌、旋转卡组）。比 WebGL 便宜得多，无头稳。
**机制**：DOM span 用 `rotateY(θ) translateZ(R)` 摆成环，父层给 `perspective` + `transform-style:preserve-3d`，GSAP 补父层的 `rotationX/Y`。
```css
.ring{ perspective:1200px; transform-style:preserve-3d; }
.ring .cell{ position:absolute; transform:rotateY(var(--a)) translateZ(360px); }
```
```js
tl.to(".ring", { rotationY:360, transformOrigin:"center", ease:"none", repeat:1, duration:6 }, at);
```
**坑（血泪）**：CSS `filter:blur()` 会**压平 `preserve-3d`**——要做模糊入场，把 blur 加在**另一层平面元素**上，绝不加在 3D 节点上。

## ⑤ DOM→纹理捕获 · 任意两个 HTML 场景之间跑着色器
**何时用**：想在**两个任意 HTML 场景**之间跑一个真着色器转场（域扭曲溶解等）。
**机制**：写一个 `captureScene(el)`，遍历离屏场景的元素、把底色矩形 + 文字画到一张 2D canvas，再 `texImage2D` 上传成 GL 纹理——于是"from 场景""to 场景"都是着色器里的采样源，进度是代理时钟标量。
```js
tl.to(prog, { p:1, duration:1.4, ease:"power2.inOut",
  onStart(){ warp.render(0); }, onUpdate(){ warp.render(prog.p); } }, at)
  .call(()=> warp.renderTo(), null, at+1.4);   // 收敛到 to 纹理
```

## 硬化清单 · 永不黑屏
命令式引擎最容易在无头/无 GPU 渲染里翻车，逐条兜底：
- **GPU 兜底**：`getContext('webgl')` 为 null → 画一张静态 2D 渐变兜底、照样注册一条**补时长的** `tl`、`return`。这一小节**永不黑屏**。
- **挂载重试**：init 时若合成 div 还没进 DOM → `if(!root){ setTimeout(init,50); return; }`。
- **补时长**：短小节末尾 `tl.to({}, { duration: TARGET }, 0)`，把 `tl.duration()` 撑满它的主槽（否则 HF 提前隐藏这一场 → 帧尾黑闪，见 SKILL Gotcha「补时长契约」）。
- **先画 frame-0**：见通用铁律，seek-to-0 不黑。
- **别用 `repeat:-1`**（lint 禁），循环用有限次数 `Math.floor(total/cycle)-1`。
