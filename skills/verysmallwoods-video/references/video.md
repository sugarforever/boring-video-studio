# 视频 · 委托给 HyperFrames

## 口径 0 · 视频不是 PPT（最优先，先读这条）

小木头的核心主张：**一段视频区别于 PPT 的，是动效与图形，不是把文字换个字体铺在屏幕上。** 所以搭画面时：

- **内容优先「动」起来** —— 能用图表/数据动画、示意图、SVG 绘制、计数器、动态排版（逐词/逐行揭示、遮罩擦除）表达的，就不要用一段静态文字；静态文字只在真正需要「一句话定格」时才用。
- **每一帧都要有生命** —— 每个场景至少一个持续/焦点动作（弧线绘制、扫描线、柱子生长、数字跳动、装饰漂移/呼吸）；装饰元素不许静止不动。
- **场景之间用真转场** —— outgoing + incoming 同时动（擦除/推移/模糊叠化），不硬切。硬切 = PPT 翻页。
- **画面分层** —— 背景（巨型幽灵字 / 纹理 / 网格 / 光晕）→ 中景（信息）→ 前景（分隔线、登记标记、元数据）；不要「居中一段字 + 空白」的网页/幻灯排版。

**因此，设计视频内容时这两个 skill 必读必用，优先级高于一切默认套路：**

- **`/hyperframes-animation`** —— 动效知识全在这：原子动效、多阶段场景蓝图、**场景转场**（`transitions/`）、逐帧技法（`techniques.md`：SVG 绘制、clip-path 揭示、计数器、图表生长、逐词动态排版）、缓动/交错与 spring 缓动（`adapters/gsap-easing-and-stagger.md`）。任何「怎么动」先来这。
- **`/hyperframes-creative`** —— 非动效的设计方向，让画面「高级」而非「像幻灯」：`references/video-composition.md`（视频不是网页：尺度、分层、幽灵字、纹理、填满画面、双焦点）+ `references/house-style.md`（避开 AI 套路味 —— 渐变字/左边框条/同款卡片网格/纯黑白居中；中性色染上主色）。

（技术契约仍看 `/hyperframes-core`，命令流程看 `/hyperframes-cli`；上面两条决定「设计得好不好、动得够不够」，务必先读再动手。）

---

出片走 HyperFrames，**不要在这里重讲那套**。入口 `/hyperframes` 会把「文章 / 主题 → 无实拍讲解」路由到 `/faceless-explainer`，由它完成全部：定 brief、选 design 生成 `frame.md`、写 STORYBOARD、逐帧搭 `compositions/frames/`、组装 `index.html`、注入转场、lint/check、渲染。步骤、gate、脚本都在 `/faceless-explainer` 与领域 skill（`/hyperframes-core` `/hyperframes-animation` `/hyperframes-creative` `/hyperframes-cli` `/media-use`）里 —— 读它们，别复制。

本 skill 在其上只补几条 faceless 没有的**用户口径**：

- **STORYBOARD 必建（铁律）** —— 每期视频都要写 `STORYBOARD.md`，**哪怕只有一个场景**。它是分场景审校与「改一处不重渲全片」的计划账本：一格一个 frame，Studio 渲成联系表可逐帧审、逐帧评论（`.hyperframes/frame-comments.json`）。faceless 里它可能被当作可选或对单场景省略 —— 本 skill 把它收成硬约定，不许跳过。格式见 `/hyperframes-core` 的 `references/storyboard-format.md`。
- **设计** —— 用 Step 0 选定的 preset（默认 `blockframe`），见 `references/designs.md`。
- **口播稿** —— 按用户的写作/口播偏好写；偏好来自上下文 / 记忆 / 会话里的风格 skill。
- **旁白** —— 见 `references/audio.md`（自录 或 TTS，由用户选）。
- **重排到真实 cue** —— 拿到真实音频 + SRT 后，把每帧内部披露重排到真实 cue 时间轴；否则动效走完会定格、旁白在静态画面上继续讲。做法见 `references/audio.md`。
- **预览 —— 渲染前必问（铁律）** —— `check` 通过后、渲染前，**显式询问用户是否要在 Studio 预览**。用户不要预览 → 跳过，直接进渲染；用户要预览 → 启动 `npx hyperframes preview`（后台常驻），把 Studio URL 交给用户：整片走 `http://localhost:<port>/#project/<name>`，看 storyboard 联系表走 `http://localhost:<port>/?view=storyboard#project/<name>`。等用户看完给反馈（改则读 `frame-comments.json` 走修订轮，见「STORYBOARD 必建」）再渲染。**不要 check 一过就自动渲染。**
- **字幕不烧进成片** —— 用户在 YouTube 上字幕；成片留底部字幕安全区即可。
- **帧率** —— 按动效规格智能判定，报给用户，可被指定覆盖。判定后告知用户：选择的帧率，依据以及不同帧率对视频产出的影响。用户明确指定帧率时以用户为准。
- **渲染** —— 1080p{fps} high 先出保底，磁盘够再出 4K master（`--resolution landscape-4k --fps {fps}`）。`{fps}` 取上一条的判定结果。
