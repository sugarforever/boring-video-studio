# 转场/接缝图鉴（Scene Transitions）— 换场的动词表

SKILL 的默认转场是 **incoming 场景自身的 clip-path inset 揭幕**（Gotcha 3），它安全、干净、永远够用。但 HeyGen 官方 launch 片证明：**在同一条确定性铁律下**，换场还有一套更电影感的"动词表"——穿越变焦、顺势切、同底硬切、帧连续硬切、曲边升幕。它们都**只动场景本体**（scale / blur / opacity / clip-path 挂在 incoming/outgoing 的 `.scene.clip` 上），**从不引入一块单独的全屏幕布去扫场**——所以和 Gotcha 3 的精神一致（被禁的是"独立幕布层"，不是"给场景本体做变换"）。

跟 `motion-patterns.md`（场景**内部**的编舞）互补：这里管的是**两场之间的接缝**。

## 目录
- [通用铁律](#通用铁律)
- [默认 · incoming clip-path 揭幕](#默认--incoming-clip-path-揭幕)
- [A 同底硬切 · Matched-dark Hard Cut](#a-同底硬切--matched-dark-hard-cut)
- [B 穿越变焦 · Zoom-through（Z 单向律）](#b-穿越变焦--zoom-throughz-单向律)
- [C 顺势切 · Cut-the-curve（速度连续）](#c-顺势切--cut-the-curve速度连续)
- [D 帧连续硬切 · 共享底视频 data-media-start](#d-帧连续硬切--共享底视频-data-media-start)
- [E 曲边升幕 · Curved-lip Rise](#e-曲边升幕--curved-lip-rise)
- [交叉淡化的红线 · Crossfade-dip Law](#交叉淡化的红线--crossfade-dip-law)
- [帧网格对齐 · 陡 ease 的抗锯齿](#帧网格对齐--陡-ease-的抗锯齿)
- [选型速查](#选型速查)

## 通用铁律
和 `motion-patterns.md` / `visual-effects.md` 同一套：
- **所有接缝 tween 挂在 `tl` 上**（`tl.set/to/fromTo(sel, vars, 绝对秒)`），绝不用裸 `gsap.*`。
- **动的是场景本体**（incoming/outgoing 的整块 `.scene.clip`），不是单独的全屏色块/幕布（那会"扫进来盖住卡死"，Gotcha 3）。
- **接缝要"速度连续 + 底色连续"**：outgoing 出去的方向/模糊，和 incoming 进来的方向/模糊**同向匹配**，硬切点两侧的**底色相同**——这两条一破，硬切就露出黑闪/穿帮。
- **场景级 opacity 要显式两端 + 有收尾态**：给整场做 opacity 到 0 再回来时，务必用 `tl.set(...opacity:0, 硬切秒)` + `tl.to(...opacity:1)`，且切完后 incoming **保持可见**（别让它停在 `.from({opacity:0})` 那种可能被 seek 留在 0 的写法，Gotcha 4）。

---

## 默认 · incoming clip-path 揭幕
**何时用**：绝大多数换场。安全、无脑、够用。
```js
function wipe(sel, at){ tl.fromTo(sel,{clipPath:"inset(0 100% 0 0)"},{clipPath:"inset(0 0% 0 0)",duration:0.5,ease:"power3.inOut"}, at); }
```
下面的 A–E 是**为特定质感**才升级，不是默认。

## A 同底硬切 · Matched-dark Hard Cut
**何时用**：深色/终端/全出血场景之间。这类场景做 clip-path 揭幕或交叉淡化都别扭——**直接硬切**最干净。
**机制**：outgoing 在自己末尾**把内容（不是整场）淡成一张"空的深色底"**（内部 tween），主时间轴在**零重叠**处一刀切到 incoming，incoming **也从一张一模一样的深色底开始**，再靠自己的内部淡入/morph 长出内容。两张深色底一致 → 硬切**看不见**。
```js
// 主时间轴：零重叠硬切（outgoing 已在内部把 .content 淡到 0，只剩深色底）
T.set('#s-worker',   { opacity: 0 }, 12.2);   // 上一场退场
T.set('#s-responds', { opacity: 1 }, 12.2);   // 下一场从"满屏深色底、内容隐藏"接手
```
**坑**：别用交叉淡化换这类场景——两张**不透明的同底**在 50% 混合点会**透出页面背景**、发灰发闪（见下方"交叉淡化红线"）。

## B 穿越变焦 · Zoom-through（Z 单向律）
**何时用**：想要"镜头怼穿画面推进下一场"的电影感推进（章节推进、payoff 前）。
**机制**：outgoing **缩小 + 模糊 + 压暗**到几乎消失，在**模糊峰值**处硬切；incoming **预置为放大 + 模糊**，再 `expo.out` 咬合回原位。像一次 dolly 推穿。
```js
const CUT = 25.2;
tl.to("#out",  { scale:0.8, filter:"blur(20px)", duration:0.2, ease:"power3.in" }, CUT-0.2);
tl.to("#out",  { opacity:0.15, duration:0.2, ease:"none" }, CUT-0.2);
tl.set("#out", { opacity:0 }, CUT);
tl.set("#in",  { opacity:0.15, scale:1.25, filter:"blur(20px)" }, CUT);
tl.to("#in",   { scale:1, filter:"blur(0px)", opacity:1, duration:0.5, ease:"expo.out" }, CUT);
```
**Z 单向律**（官方 HANDOFF 明写）：**一段接缝里 Z 只往一个方向走**——要么两场都在"缩小"方向（穿出 → 迎面缩入），要么都在"放大"方向；**绝不在切点回拉**。Z 的方向 = scale 速度的符号。破了这条，观众会晕。
**变体·变焦阶梯**：连续 N 个硬切让 scale **单调爬升**（如 1.32→4.4）、节奏加速（gap `.8/.5/.4/.3/.2/.15/.12/.1`），中心押一句不变的短语——"问题一次次发生"的堆叠式蒙太奇。

## C 顺势切 · Cut-the-curve（速度连续）
**何时用**：两场之间想"零转场感"——像一个连续运动被从中剪开。
**机制**：把接缝两侧当作**同一条 ease 的上下半段**。outgoing 在末尾**加速冲出**（`power3.in`，如 `y:-280`）并在边界**带上一个固定模糊**（如 `blur(10px)`）；incoming **从同样的模糊、相反的偏移**（`y:-160`）**减速切入**（`expo.out`）。运动与模糊在切点**连续**，剪辑点就消失了。
```js
// outgoing 末段（冲出 + 边界模糊）
tl.to(".appA", { y:-280, filter:"blur(10px)", duration:0.45, ease:"power3.in" }, 3.2);
// incoming（匹配模糊、相反偏移、减速落位）
tl.fromTo(".stackB", { y:-160, filter:"blur(10px)" },
                     { y:0,   filter:"blur(0px)", duration:0.55, ease:"expo.out" }, 0);
```
**坑**：① 两侧偏移是**一对**，改一侧必须改另一侧，否则速度不连续。② 页面 body 底色给成场景底色（如 `#f5f5f7` 或深色），**杀掉切点的黑闪**。③ 文字版顺势切：outgoing 词组左冲淡出、incoming 词组从右减速接入，淡出在行程 ~25–30% 就完成（谁都没真离屏），`immediateRender:false` 防止 from 态在 t=0 抢画。

## D 帧连续硬切 · 共享底视频 data-media-start
**何时用**：多场共用**同一条背景动态视频**（品牌 loop、A-roll 底板）时，想要**无转场**的换场。
**机制**：每一场都把自己的 `<video>` 底板的 `data-media-start` 设成 **该场在成片里的 `data-start`**——于是同一条 `bg.mp4` 在硬切两侧显示**同一帧**，画面连续、切口隐形。
```html
<!-- 场景 rotary（成片 27.0s 开始）--> <video id="ro-bg" ... data-start="0" data-media-start="27.0"  data-track-index="0" muted></video>
<!-- 场景 aroll（成片 32.25s 开始）--> <video id="ar-bg" ... data-start="0" data-media-start="32.25" data-track-index="0" muted></video>
```
**坑**：视频**必须有 `id`**（无 id 渲染冻结/黑屏，lint `media_missing_id`）；框架**强制 clip `opacity:1`**，要淡入淡出请淡**外层 wrapper**、别淡 `<video>` 本身。media 相关铁律见 SKILL "媒体（视频/图片）"。

## E 曲边升幕 · Curved-lip Rise
**何时用**：想要一个比平直 clip-path 更"有机"的揭幕——incoming 从下方升起、前缘是一道弧、落位时抹平。
**机制**：incoming 盖层从屏下升入，同时 `border-radius` 从大弧 morph 到 0。
```js
gsap.set(".cover",{ y:1110, scaleX:1.08, borderRadius:"58% 58% 0 0 / 18% 18% 0 0" });
tl.to(".cover",{ y:0, scaleX:1, borderRadius:"0", duration:0.64, ease:"power4.inOut" }, at);
```
（这里的 `gsap.set` 是**初始静态摆位**、非定时动画，可用；升起 tween 在 `tl` 上。）

---

## 交叉淡化的红线 · Crossfade-dip Law
**逐帧 luma 验证过的规律**：**交叉淡化两张"同底、不透明"的全屏场景 = bug**。50% 混合点会透出页面背景、整体压暗发灰、读成一下闪。规则：
- **底色相同 → 硬切**（A / D），不要 crossfade。
- **crossfade 只留给**：换配色（colorway 变了）、或刻意的**淡到白/黑**收尾。
- 且这种 crossfade 放在**主（root）时间轴**上做，**别塞进场景内部**。

## 帧网格对齐 · 陡 ease 的抗锯齿
陡 ease（`expo.in` 等）在 30fps 网格上会**锯齿/跳步**。官方做法：把**退场安排成在某一具体帧上恰好结束**（如 start 3.6333 让 tween 落在第 115 帧、即 3.85 硬切前最后一帧），**对着离散渲染网格**编舞、而不是墙钟。起始秒再 `+0.0001` 躲开 lint 的浮点并列告警。

---

## 选型速查

| 转场（报名用） | 何时 | 底色/速度关键 |
|---|---|---|
| 默认 clip-path 揭幕 | 绝大多数换场 | 揭 incoming 本体，安全无脑 |
| A 同底硬切 | 深色/终端/全出血之间 | 两侧同底、零重叠；**别** crossfade |
| B 穿越变焦 | 电影感推进、章节/payoff | Z 单向律；out 缩模糊、in 放大咬合 |
| C 顺势切 | 想要"零转场"连续运动 | 匹配模糊 + 相反偏移成对；body 底色防黑闪 |
| D 帧连续硬切 | 多场共用底视频 | 各场 `data-media-start`=该场 `data-start` |
| E 曲边升幕 | 比平直揭幕更有机 | `border-radius` morph；升起挂 tll |

> 皮肤（色/边/圆角）沿用当前 frame 的 token；这些接缝都在 HyperFrames 无头 Chrome 逐帧渲染下 seek-safe（全挂 `tl`、无 `Date.now`/`Math.random`、无 rAF）。
