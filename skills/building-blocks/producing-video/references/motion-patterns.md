# 动效图鉴（Motion Patterns）— 15 类常见动效

屏幕上最常见的 13 类 Motion 动效的**可复用配方**：给每类一个**标准名**（跟 AI Agent 沟通时直接报名，省得写一长段"从右边快速滑入停下时回弹一下"）+ **设计中立的机制**（纯 CSS + GSAP，外壳走 CSS 变量留口，皮肤由当前 frame/品牌填）。

跟 `visual-effects.md`（聚光/磨砂/景深/放大镜这类**画面质感**）互补：那边是"看起来"，这边是"动起来"——场景/元素的**编舞**。所有配方都按本项目的确定性渲染铁律写，**13 类已用一支 13 场合成在 HyperFrames 无头 Chrome 里渲染、逐帧抽验通过**（含最易翻车的两类：数字滚动的 `onUpdate` 在 seek 里逐帧重算、3D 翻面的 backface）。

## 目录
- [通用铁律](#通用铁律)
- [01 页面与视图切换 · Push / Slide](#01-页面与视图切换--push--slide)
- [02 元素进入与退出 · Staggered Entrance](#02-元素进入与退出--staggered-entrance)
- [03 状态变化 · State Morph](#03-状态变化--state-morph)
- [04 操作反馈 · Press + Ripple](#04-操作反馈--press--ripple)
- [05 滚动动画 · Scroll-Driven Transform](#05-滚动动画--scroll-driven-transform)
- [06 导航动画 · Sliding Indicator + Drawer](#06-导航动画--sliding-indicator--drawer)
- [07 加载与等待 · Spinner + Skeleton Shimmer](#07-加载与等待--spinner--skeleton-shimmer)
- [08 数据变化 · Bar Growth + Count-Up](#08-数据变化--bar-growth--count-up)
- [09 布局重排 · Reorder（显式坐标 FLIP）](#09-布局重排--reorder显式坐标-flip)
- [10 手势与物理运动 · Drag + Spring](#10-手势与物理运动--drag--spring)
- [11 引导与提示 · Pulse + Popover](#11-引导与提示--pulse--popover)
- [12 品牌与装饰动画 · Orbit + Assemble](#12-品牌与装饰动画--orbit--assemble)
- [13 3D 与空间运动 · 3D Flip + Parallax](#13-3d-与空间运动--3d-flip--parallax)
- [14 粒子与爆发 · Particle Burst（黄金角）](#14-粒子与爆发--particle-burst黄金角)
- [15 打字机 · Seek-safe Typewriter（clip-path + steps）](#15-打字机--seek-safe-typewriterclip-path--steps)
- [编舞辅助 · 自定义 ease / 整块retiming / 压缩时长](#编舞辅助--自定义-ease--整块retiming--压缩时长)
- [选型速查](#选型速查)

> 换场（两场**之间**的接缝：穿越变焦 / 顺势切 / 同底硬切 / 帧连续硬切 / 曲边升幕）单独成篇，见 `scene-transitions.md`；命令式引擎（WebGL / Canvas / Lottie / 伪 3D）见 `runtime-adapters.md`。本文只管场景**内部**的编舞。

## 通用铁律
和 `visual-effects.md` 同一套，务必遵守：
- **所有 tween 挂在注册到 `window.__timelines` 的 `tl` 上**（`tl.from/to/fromTo(sel, vars, 位置秒)`），绝不用裸 `gsap.to/from`（渲染只 seek `tl`；裸 tween 在 seek 渲染里不跑，见 SKILL Gotcha 12）。
- **只用确定性逻辑**：无 `Date.now()`/`Math.random()`。ease（含 `elastic`/`back`）、`stagger`、有限/无限 `repeat`、`yoyo`、`onUpdate` 都是**时间的纯函数**，逐帧 seek 能重算 —— 这些都 seek-safe。
- **不 seek-safe 的东西要绕开**：任何"播放时测一次"的动作——真·GSAP FLIP 插件 / `getBoundingClientRect` 测量 / 监听 scroll·drag·click 事件——渲染里不 seek、测不到、事件不触发，一律改成**显式坐标/固定路径**（见 05 / 09 / 10）。
- 动效本身**设计中立**：色/边/圆角/阴影走当前 frame 的 token 或 `visual-effects.md` 的外壳变量（`--accent` 等），别把某套设计焊死进机制。

---

## 01 页面与视图切换 · Push / Slide
**何时用**：从一场切到下一场，或列表页 → 详情页这种**有层级/方向**的跳转。（表方向感时用它；只要干净揭幕就用 SKILL 默认的 clip-path wipe。）

**机制**：两个**真实 scene clip** 同时在场，outgoing 整块往左推出、incoming 从右推入。位移的是**场景本体**，不是单独的全屏幕布——单独幕布会"扫进来盖住后卡住"（SKILL Gotcha 3）。incoming 的 `track-index` / `z-index` 更高。
```js
tl.to("#sceneA",   {xPercent:-100, duration:0.6, ease:"power3.inOut"}, at);
tl.fromTo("#sceneB",{xPercent:100}, {xPercent:0, duration:0.6, ease:"power3.inOut"}, at);
```
详情页"盖上来"的层级感：改成 B 从右滑入 + 轻微 `scale` 与投影，A 不动。

## 02 元素进入与退出 · Staggered Entrance
**何时用**：场景内标题/要点/卡片"被念到就出现"——同步感的主力（SKILL Step 3 的 sub-reveal）。

**机制**：一组元素用 GSAP `stagger` 错峰入场。三种基元：淡入（`opacity`）、滑入（`y`/`x`）、缩放（`scale`）。全在 `tl` 上，`stagger` seek-safe。
```js
// 淡入 + 上滑
tl.from(".card", {opacity:0, y:40, duration:0.5, ease:"power2.out", stagger:0.12}, at);
// 缩放入场（带一点回弹）
tl.from(".chip", {opacity:0, scale:0.6, transformOrigin:"center",
  duration:0.5, ease:"back.out(1.7)", stagger:0.08}, at);
```
退出对称做 `tl.to(".card",{opacity:0, y:-40, stagger:0.08}, atOut)`。**别**给外层容器套整体 opacity 的 "pushIn" 包装（容器级 opacity 在 seek 里可能留在 0，整场变黑，SKILL Gotcha 4）——用每个元素各自的 `tl.from`。

## 03 状态变化 · State Morph
**何时用**：展示"默认态 → 激活态"——开关打开、点赞变红、按钮变 ready、勾选打对勾。

**机制**：属性从 A 补到 B。
```js
// 开关：旋钮平移 + 轨道变色
tl.to(".knob", {x:28, duration:0.3, ease:"power2.out"}, at);
tl.to(".track",{backgroundColor:"var(--accent)", duration:0.3}, at);
// 点赞：心形弹一下 + 填充
tl.to(".heart",{scale:1.3, transformOrigin:"center", duration:0.15, ease:"power2.out"}, at)
  .to(".heart",{scale:1, duration:0.2, ease:"power2.in"}, at+0.15);
tl.to(".heart",{color:"var(--accent)", duration:0.01}, at);
// 对勾：路径描出（draw）
tl.fromTo(".check path",{strokeDashoffset:60},{strokeDashoffset:0,
  duration:0.4, ease:"power1.inOut"}, at);
```
描线需给 path 设 `stroke-dasharray:60`（≈路径长度）。

## 04 操作反馈 · Press + Ripple
**何时用**：演示一次点击/确认（口播念到"点一下就…"）。

**机制**：按钮 press（略缩再回弹）+ 从触点扩散的 ripple 圆（`scale` 0→大、`opacity` 1→0）。
```js
tl.to(".btn",{scale:0.94, transformOrigin:"center", duration:0.1}, at)
  .to(".btn",{scale:1, duration:0.18, ease:"back.out(2)"}, at+0.1);
tl.fromTo(".ripple",{scale:0, opacity:0.5},
  {scale:4, opacity:0, transformOrigin:"center", duration:0.6, ease:"power2.out"}, at);
```
ripple 圆放触点/按钮中心，`border-radius:50%; pointer-events:none`。

**进阶·声波环 + 指尖压扁（连点节奏）**：官方 launch 片里，每次点击发一圈**扩散环**（"声音"的视觉替身），配合光标**指尖压扁** + 按钮**按下**。环要**预先建好**（别在 `onUpdate` 里 `createElement`，否则 seek 不确定），`immediateRender:false` 防止所有环在 t=0 就画出 from 态；节奏可编成"2 慢 + 10 连击"。
```js
const CLICKS=[1.2,1.7]; for(let i=0;i<10;i++) CLICKS.push(2.3+i*0.2);   // 2 慢，10 连击
const rings=CLICKS.map(()=>{const r=document.createElement('div');r.className='ring';btn.appendChild(r);return r;});
CLICKS.forEach((t,i)=>{
  tl.to(cursor,{scale:.84,duration:.08,transformOrigin:'21% 14%'}, t);                        // 指尖压扁
  tl.to(btn,{scale:.94,backgroundColor:'#171614',duration:.09}, t);                           // 按下
  tl.fromTo(rings[i],{scale:1,opacity:.6},{scale:6,opacity:0,duration:.9,ease:'power2.out',immediateRender:false}, t);
});
```
（真实交互：**放大并点真按钮本体**、把周边 chrome 淡出，别盖一层假 overlay——避免克隆脱同步。）

## 05 滚动动画 · Scroll-Driven Transform
**何时用**：一屏长内容"随滚动"依次进入（长列表、时间线）。

**机制**：渲染里**没有真滚动**（监听不到 scroll 事件）——用 `tl` 驱动容器 `y` 平移**模拟**滚动，子项在越过"视口线"时各自 fade/slide。
```js
tl.to(".scroller",{y:-600, duration:3, ease:"none"}, at);              // 模拟滚动
tl.from(".row",   {opacity:0, y:30, duration:0.4, stagger:0.4}, at+0.3); // 逐行进入视口
```
外层容器 `overflow:hidden` 当视口框。**别**用真实滚动条/`scroll` 监听。

## 06 导航动画 · Sliding Indicator + Drawer
**何时用**：tab 切换的下划线滑动；侧边抽屉推入。

**机制**：指示条 tween `x`（可选连 `width`）到目标 tab；抽屉从屏外 `x` 滑入 + 半透明遮罩淡入。
```js
tl.to(".indicator",{x:180, width:96, duration:0.35, ease:"power2.inOut"}, at);
tl.from(".drawer",  {x:-320, duration:0.4, ease:"power3.out"}, at);
tl.from(".scrim",   {opacity:0, duration:0.4}, at);
```

## 07 加载与等待 · Spinner + Skeleton Shimmer
**何时用**：表达"处理中/加载中"的过场。

**机制**：spinner = 旋转（有限 `repeat`，`ease:"none"`）；skeleton = 灰块上一道高光横扫（平移高光条，`repeat`）。都是时间纯函数，seek-safe。
```js
tl.to(".spinner",{rotation:360, transformOrigin:"center", ease:"none", repeat:3, duration:1}, at);
tl.fromTo(".shimmer",{xPercent:-100},{xPercent:200, ease:"none", repeat:3, duration:1}, at);
```
用**有限** `repeat` 次数（别 `repeat:-1`，方便按场景时长收口）；高光条半透明白 + `mix-blend-mode:overlay`。

## 08 数据变化 · Bar Growth + Count-Up
**何时用**：数据页——柱子长出来、数字滚动到目标（财经片高频）。

**机制**：柱 = `scaleY` 0→1（`transformOrigin:"bottom"`）；数字 = tween 一个**代理对象**，`onUpdate` 里写 `textContent` 并**取整**（纯时间函数，逐帧 seek 重算）。
```js
tl.from(".bar",{scaleY:0, transformOrigin:"bottom", duration:0.7, ease:"power3.out", stagger:0.1}, at);
const n = {v:0};
tl.to(n, {v:84, duration:1, ease:"power1.out", lazy:false,
  onUpdate(){ document.querySelector(".pct").textContent = Math.round(n.v) + "%"; }}, at);
```
坑：① 数字务必 `Math.round`/`gsap.utils.snap`，否则逐帧出现抖动小数。② 加 `lazy:false` 保证每帧都 `onUpdate`（否则 GSAP 可能跳过"值没变"的帧）。③ 柱内文字用墨色压 accent 底（SKILL Gotcha 8 的对比度误报）。

**变体·带千分位的逐字打（typeNum）**：当**逗号格式**要紧（计数、金额），逐字打比数值 count-up 更好读——用 `steps(N)` 打出格式化字符串：
```js
const el=R.querySelector('#lines'), o={p:0}; el.textContent='';
tl.to(o,{p:1,duration:.7,ease:'steps(6)',onUpdate(){ el.textContent="87,291".slice(0,Math.round(o.p*6)); }}, at);
```
**变体·柱码表（odometer）**：把数字做成**两行裁切列**、上滚一行高度，比 count-up 文字更有"翻牌"质感——`34.1k→34.2k`：`tl.to(countCol,{y:-36,duration:.4,ease:"power2.inOut"}, at)`（外层 `overflow:hidden`，两行等高）。

## 09 布局重排 · Reorder（显式坐标 FLIP）
**何时用**：排名/列表重排（第 3 名升到第 1）。

**机制**：**不要用 GSAP 的 Flip 插件**——它靠 `getBoundingClientRect` 在**播放时测一次**首末位置，渲染只 seek、测不到，不 seek-safe。改成：布局时把每个"槽位"坐标算好，元素在旧槽位/新槽位之间 tween `x`/`y`。
```js
tl.to("#itemC",{y:-140, duration:0.5, ease:"power2.inOut"}, at);       // C 升到顶
tl.to("#itemA",{y:70,  duration:0.5, ease:"power2.inOut"}, at+0.05);
tl.to("#itemB",{y:70,  duration:0.5, ease:"power2.inOut"}, at+0.1);
```
错峰给一点偏移更自然。

## 10 手势与物理运动 · Drag + Spring
**何时用**：表达"可拖动 / 有惯性"的元素，落位回弹。

**机制**：渲染里没有真手势——沿**固定路径**位移演示，收尾用弹性 ease（`elastic.out`/`back.out`）模拟惯性回弹。ease 是确定性的，seek-safe。
```js
tl.to(".card",{x:260, y:-40, duration:0.6, ease:"power1.inOut"}, at);          // 拖拽段
tl.to(".card",{x:220, y:0,   duration:0.7, ease:"elastic.out(1,0.4)"}, at+0.6); // 落位回弹
```

## 11 引导与提示 · Pulse + Popover
**何时用**：指向某处的引导（"从这里开始"），脉冲光圈 + 气泡弹出。

**机制**：光圈 `scale`/`opacity` 循环脉冲（有限 `repeat`）；气泡从锚点 `scale`/`opacity` 弹出（`back.out`）。
```js
tl.to(".pulse",{scale:1.6, opacity:0, transformOrigin:"center",
  ease:"power1.out", repeat:3, duration:0.9}, at);
tl.from(".popover",{opacity:0, scale:0.8, y:10, transformOrigin:"left top",
  duration:0.4, ease:"back.out(1.7)"}, at+0.3);
```

## 12 品牌与装饰动画 · Orbit + Assemble
**何时用**：片头/片尾 logo sting、装饰性点缀。

**机制**：装饰点绕中心公转（容器 `rotation`，有限 `repeat`）；logo 碎片从各自偏移"聚拢"归位（`x`/`y`/`rotation`/`opacity` 补到 0）。
```js
tl.to(".orbit",{rotation:360, transformOrigin:"center", ease:"none", repeat:1, duration:6}, at);
tl.from(".logo-a",{x:-60, y:-40, rotation:-30, opacity:0, duration:0.6, ease:"power3.out"}, at);
tl.from(".logo-b",{x: 60, y: 40, rotation: 30, opacity:0, duration:0.6, ease:"power3.out"}, at+0.08);
```
装饰若标了 `data-layout-ignore`，**别单独 tween 它**（会报 `GSAP target not found`，SKILL Gotcha 13）——随场景 wipe 一起揭出即可。

## 13 3D 与空间运动 · 3D Flip + Parallax
**何时用**：翻卡揭示正反面；多层视差营造纵深。

**机制**：父层给 `perspective`，卡片 `rotateY` 翻转，两面都 `backface-visibility:hidden`；视差 = 多层按同一 `tl` 以**不同幅度**平移。
```css
.stage{ perspective:1200px; }
.card3d{ transform-style:preserve-3d; }
.card3d .front,.card3d .back{ backface-visibility:hidden; }
.card3d .back{ transform:rotateY(180deg); }
```
```js
tl.to(".card3d",{rotationY:180, transformOrigin:"center", duration:0.8, ease:"power2.inOut"}, at);
// 视差：近层动得多、远层动得少
tl.to(".layer-far", {x:-30, ease:"none", duration:2}, at);
tl.to(".layer-near",{x:-90, ease:"none", duration:2}, at);
```
坑：3D 变换在无头 Chrome 一般可渲，但翻面瞬间易闪——两面务必 `backface-visibility:hidden`，且 `rotationY` 用**整段**补间（别拆成两段接力）。

## 14 粒子与爆发 · Particle Burst（黄金角）
**何时用**：一个 stat 命中时喷一把硬币/星屑/图标（财经片"涨停"、payoff 的庆祝）。
**机制**：散布位置**不用随机数**——用**黄金角** `i * 2.39996323` rad + 按序号递增半径，得到向日葵式的均匀非重复散开（比 `Math.random` 分布更好，且**天然确定性、无需 PRNG 状态**）。每个粒子先喷出（`power4.out`）再落下淡出（`power2.in`），`d` 做错峰。
```js
const specs=[]; for(let i=0;i<16;i++){
  const ang=i*2.39996323, rad=150+(i%4)*46;                 // 黄金角 + 阶梯半径
  specs.push({x:Math.cos(ang)*rad, y:Math.sin(ang*1.13)*(rad*.6),
              rot:((i*43)%140)-70, d:(i%6)*0.03});          // d = stagger
}
specs.forEach((s,i)=>{
  tl.fromTo(`#p${i}`,{x:0,y:0,opacity:0,scale:.4},{x:s.x,y:s.y,rotation:s.rot,opacity:1,scale:1,duration:.5,ease:"power4.out"}, HIT+0.1+s.d);
  tl.to(`#p${i}`,{y:s.y+220,opacity:0,duration:.7,ease:"power2.in"}, HIT+0.6+s.d);
});
```
（需要真随机质感时才退回**种子化 PRNG**：`mulberry32(seed)`；仍禁 `Math.random`。）

## 15 打字机 · Seek-safe Typewriter（clip-path + steps）
**何时用**：Agent/终端里"敲出一句 prompt / 编辑文件名"，逐字出现且 seek 下逐帧精确。
**机制**：**别**用 JS 逐帧改 `textContent`（每帧改 DOM，seek 下不稳）。用 `clip-path` 或 `width` + `steps(N)` ease 揭字——纯 CSS 补间、无 DOM churn。
```js
// 比例字体：clip-path 揭字（N=字符数）
gsap.set("#p",{clipPath:"inset(0 100% 0 0)"});
tl.to("#p",{clipPath:"inset(0 0% 0 0)",duration:1.05,ease:"steps("+text.length+")"}, at);
// 等宽字体：width 走 ch，配一个手搓闪烁光标
tl.to("#p",{width:text.length+"ch",duration:1.0,ease:"steps("+text.length+")"}, at);
tl.to("#caret",{opacity:0,duration:.5,ease:"steps(1)",repeat:3,yoyo:true}, at);
```
**进阶·像素级比例打字**：要精确到每个比例字形宽度，用隐藏 `.meas` span 预量每个前缀宽度，把宽度塞进 tween 的 `vars` 后 `tl.invalidate()`，并在 `document.fonts.ready` 后重量（web 字体度量才准）。

## 编舞辅助 · 自定义 ease / 整块retiming / 压缩时长
不是动效本身，是**让编舞更好写**的三件小工具（官方 launch 片高频使用，全确定性）：
- **自定义 cubic-bezier ease（免 CustomEase 插件）**：12 次牛顿迭代求解，命名一次、到处复用，保持动效词汇一致。
  ```js
  function cbz(x1,y1,x2,y2){ /* Newton 解 t→y */ }
  const breathe=cbz(0.37,0,0.63,1), snap=cbz(0.22,1.15,0.36,1);
  tl.to(el,{scale:1.04,duration:.78,ease:breathe}, at);
  ```
  也可直接给 GSAP 传纯函数 ease：`ease:(t)=> -0.806*t*t + 1.806*t`（快起慢落）。
- **整块 retiming**：`tl.addLabel("phoneExit", 4.04)` 后把 tween 挂在 label 上；或 `tl.shiftChildren(START, true, 0)` **一次性**把整段编舞平移到主时钟某处——重排多幕时不用逐条改 `data-start`。
- **先慢写后压缩**：内层 `const inner=gsap.timeline()` 用**舒服的节奏**写完（如 ~6.4s），再 `inner.timeScale(2.56)` 压到本场的紧预算（~2.5s），最后 `tl.add(inner,0)`。把"编写节奏"和"成片时长"解耦，密集场景好调太多。

---

## 选型速查

| 类别（报名用） | 口播片里的典型用途 | seek-safe 关键 |
|---|---|---|
| 01 Push / Slide | 换场、列表→详情的方向感 | 位移的是场景本体，不是全屏幕布 |
| 02 Staggered Entrance | 标题/要点"被念到就出现" | `stagger` 在 `tl` 上；勿套容器级 opacity |
| 03 State Morph | 开关/点赞/勾选的状态切换 | 属性补间；描线用 `strokeDashoffset` |
| 04 Press + Ripple | 演示一次点击/确认 | 纯 `scale`/`opacity` 补间 |
| 05 Scroll-Driven | 长列表随"滚动"进入 | 用 `tl` 驱动 `y`，不监听真 scroll |
| 06 Indicator + Drawer | tab 下划线、侧边抽屉 | `x`/`width` 补间到已知坐标 |
| 07 Spinner + Shimmer | 加载/等待过场 | 有限 `repeat`，别 `repeat:-1` |
| 08 Bar Growth + Count-Up | 数据页柱子长出、数字滚动 | 代理对象 `onUpdate` + `Math.round` + `lazy:false` |
| 09 Reorder | 排名/列表重排 | 显式槽位坐标，**不用 Flip 插件** |
| 10 Drag + Spring | 可拖动/惯性回弹 | 固定路径 + `elastic`/`back` ease |
| 11 Pulse + Popover | 引导指向、气泡提示 | 有限 `repeat` 脉冲 + `back.out` 弹出 |
| 12 Orbit + Assemble | 片头/片尾 logo sting | 有限 `repeat` 公转；`data-layout-ignore` 别单独 tween |
| 13 3D Flip + Parallax | 翻卡、多层纵深 | 两面 `backface-visibility:hidden`；整段 `rotationY` |
| 14 Particle Burst | stat 命中喷硬币/星屑 | 黄金角散布，无需 `Math.random` |
| 15 Seek-safe Typewriter | 敲 prompt / 编辑文件名 | `clip-path`/`width` + `steps(N)`，别改 `textContent` |

> 这些是场景**内部**的编舞，皮肤（色/边/圆角/阴影）沿用当前 frame 的 token 与 `visual-effects.md` 的外壳变量；强调色仍当"标点"不当"填充"（SKILL Step 4）。换场接缝见 `scene-transitions.md`，命令式引擎见 `runtime-adapters.md`。BlockFrame 皮肤值见 `blockframe-video/references/effects-blockframe.md`。
