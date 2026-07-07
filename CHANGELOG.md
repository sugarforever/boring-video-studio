# Changelog

本项目所有重要变更记录于此。遵循 [Keep a Changelog](https://keepachangelog.com/) 风格;
版本号遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

`npx skills add sugarforever/boring-video-studio` 跟踪的是 `main` 分支最新内容;
tag(如 `v0.1.0`)用于标记发版节点,方便对照。

## [0.4.2] — 2026-07-07

- **`producing-video`** —— 新增 **Step 6「预览 · 让用户先过目」**，一道渲染前的人工闸门。
  用 `npx hyperframes preview` 起本地 studio 在浏览器里**按时间轴播放**合成（带播放头/scrub、
  音频同放、热更新），中间迭代全在这里做，`render` 只留到最后一次。要点：**别直接双开
  `index.html`**（定时动画挂在 `window.__timelines` 的 `tl` 上、靠外部 seek 驱动，裸开只看到静态
  第一帧）；把 preview 交给用户过目、拿到 OK 再渲染，省掉「渲完才发现要改、又重渲」。
  渲染/封面步骤顺延为 Step 7/8，输出清单加「已 preview 且用户 OK」勾项。

## [0.4.1] — 2026-07-07

- **`blockframe-video`** —— 新增**「项目目录结构」规范**：一个选题一个项目目录，横竖两版是
  `build-h` / `build-v` 两个子目录、共用上层 `audio/` `assets/` `fonts/`（软链引入）；
  `renders/` 只留母版+响度版、`covers/` 收全比例封面、`publish.md`/`blog.md` 各就各位。
  **明确别再散成 `<slug>-cn`/`-3x4`/`-16x9` 平级兄弟目录**（踩过：散乱易漏难归档）。
  Step 0 起项目片段同步。`finance-stock-video` 引用该结构。

## [0.4.0] — 2026-07-07

- **`finance-stock-video`（新）** —— 财经/A股个股视频**专用领域层**，坐在 `blockframe-video` 之上。
  给一个公司（股票代码）或一个财经主题（「某股为什么爆发」），产出《A股上市公司速览》整套物料。
  基于两期寒武纪实战沉淀，编码用户偏好：
  - **数据获取与核实**：数据源优先级（巨潮 cninfo 原件 > 交易所/官网 > 权威媒体 > 谨慎自媒体）；
    必挖官方数据 checklist（分产品/产销量/前五大客户逐个/存货明细/供应商/风险章节/前十大股东……）；
    **核实铁律**（下 PDF → `pdftotext` → `grep` 核对原件，不只信子 agent/媒体转述）；
    来源三级标注【官方/第三方/存疑】。
  - **客观口径红线**：不构成投资建议；出口管制/国产替代等市场叙事**必打标签**「市场分析·非公司口径」+ 画面横幅隔离；
    匿名客户不猜真身；年报没披露的不编；真人用名片、企业/产品用官方图。
  - **系列身份**：BlockFrame + 灵依 1.2x + 头部品牌条；平台映射（横 16:9→B站/YT，竖 3:4→抖音/小红书/视频号）。
  - **两种模板**：个股速览（8 分块）/ 深挖归因（章节化）；提问式开头钩子。
  - **精确配音**：`scripts/regen_tts.py` 逐句合成灵依→拼接→精确 SRT→1.2x（灵依不吐自带字幕，别用缩放近似）。
  - 财经画面组件：数据大字报 / **正负发散柱（共享零轴）** / 客户榜 / 备货对比 / 风险卡 / 市场分析横幅 / 官方芯片实拍图。
  - **公众号文章标题方法论（高点击 × 合规）**：三招最有效合规钩子（具体数字 / 事实反差 / 清单承诺）、
    可用 vs 避开红线对照表（禁涨跌预测/买卖暗示/收益承诺/震惊体）、8 个填空式标题模板。
    「客观 / 只看财报」降为可信度背书、不当主钩子；避开「客观数据盘点」这种抽象无钩子写法。

## [0.3.3] — 2026-06-23

- **`listenhub-tts`** —— 新增**跑 TTS 前多音字扫描**(`scan-heteronyms.sh` + `heteronyms.md`)。
  TTS 常把多音字读错(实例:`调用` 的「调」读成 tiáo,该 diào)。扫描对照高危清单
  (AI/编程领域,可增长)把裸字 / 陌生词标 `⚠`,人工按梯子修:① 扩成无歧义的词
  (`调`→`调用`)→ ② 换说法 → ③ 漏到成片单句挖补。文本改写让音频 + 字幕一起受益;
  不用引擎 SSML/拼音(ListenHub 无公开支持、且会污染字幕=输入原文的字幕)。
  blockframe-video 把它列为口播稿**第三遍**(两遍风格 + 一遍多音字)。

## [0.3.2] — 2026-06-22

- **`blockframe-video`** —— **废弃 3:4 的 `zoom:2` 超采样**。实测它搞坏所有 `bottom:` 定位的
  绝对元素（页脚、`.wrap` bottom、封面底部 chips 错位/消失），单文件多场景合成尤其翻车；
  早期「验证」只看了非空白、是假阳性。改用可靠路径：**原生渲 1080×1440 `--quality high`
  + ffmpeg lanczos 放大到 2160×2880**。Step 3 + gotcha 同步。

## [0.3.1] — 2026-06-22

- **`blockframe-video`** —— 竖版主画布钉死 **3:4（1080×1440）**，明确**不再做 9:16 视频本体**
  （9:16 太瘦高、移动端观看体验差，用户偏好）。9:16 仅保留为封面比例之一。
  渲染走 `zoom:2` 超采样（3:4 无 4K 预设）。格式表 + 两条 gotcha 同步。

## [0.3.0] — 2026-06-21

新增品牌图标 skill;给编排层补上版面填充、封面开篇、CTA 尾页三套实战经验。

### Added

- **`brand-icons`** —— 品牌名 → 官方 SVG logo。从 LobeHub Icons 的静态 SVG 包
  (`@lobehub/icons-static-svg` via jsDelivr)取真实的 AI / 公司品牌标,放进封面 / 合成。
  - `scripts/find-icon.sh <keyword>` 按关键词搜 slug(GLM=`chatglm`/`glmv`、智谱=`zhipu`,
    别凭空猜);`scripts/fetch-icon.sh <slug>` 下载 `<slug>.svg` + `-color` + `-text` 变体。
  - 记录关键坑:人看的 `lobehub.com/icons/*` 页挡在 Vercel 机器人验证后(403),
    **别 WebFetch**,直接走 CDN;单色标要放白/浅底块。

### Changed

- **`blockframe-video`** —— 补三套竖屏实战经验,并更新 `assets/kit.css`:
  - **版面填充**:默认顶对齐的 `.wrap` 在内容少时填充率只有 14–33%、底部大片空。
    新增 `.wrap.fill`(三段式居中 + `gap`)+ `.botcard`(底部落点卡),配 hero 放大,
    目标 75–85%;附「填充率自检」(浏览器量每页包围盒,<50% 回去补)。
  - **封面开篇**:封面图当片头标题卡停留 ~3 秒、`.chrome` 淡入、正片 clip-path 揭幕转场。
  - **CTA 尾页**:narration 后加静音「一键三连」尾卡(`.ctawrap`/`.cta`),
    root 时长 + 进度条要顺延。
  - **新 gotcha**:改完重渲别和 `loudnorm` 撞车 —— 渲到临时文件、完全写完再装回最终名,
    并从最终文件抽帧复核(踩过:并行 loudnorm 把旧版覆盖进去)。

## [0.2.0] — 2026-06-18

新增编排 skill,把两个积木升级成「一次会话产出整套物料」。

### Added

- **`blockframe-video`** —— 主题 / 口播稿 → **整套视频物料**(编排 `listenhub-tts` + `producing-video`)。
  补齐两个积木之间最容易漏的「交付完整性」这一层:
  - **交付清单写死、自动验收**:成片(已 `loudnorm` -14 LUFS)+ 字幕 + **全比例封面**
    (3:4 / 9:16 / 16:9 / 16:10 / 4:3)+ 平台文案(`youtube.md` / `bilibili.md`)。
    `scripts/check-deliverables.sh` 收尾验,有 ✗ 不算完成 —— 不再靠人手动提醒「还要 4:3 封面」。
  - **全比例封面一键渲**:`scripts/render-all-covers.sh` 遍历 `cover-*.html` → `cover-*.png`,
    用系统 Chrome headless 2× 超采样(`scripts/render-cover.sh`,无 npm 依赖)。
  - **格式分支**:short(移动竖屏,主 3:4)/ long(横版,主 16:9)走同一流水线,只换画布/分辨率/封面集/节奏。
  - **3:4 的 4K 解法**(实测):`hyperframes render --resolution` 无 3:4 预设;用 `zoom:2` + 翻倍捕获画布
    做真·超采样到 2160×2880(9:16 用 `portrait-4k`、16:9 用 `landscape-4k`)。
  - **assets**:`kit.css`(BlockFrame HyperFrames 组件内核)+ `cover-vertical.html` / `cover-horizontal.html`
    (全比例封面模板)。

### Verified

- 封面渲染:系统 Chrome headless `--screenshot --force-device-scale-factor=2` 实测出 2× 清晰 PNG、本地 woff2 字体正常。
- 3:4 4K:seg-01 实测 `zoom:2` 超采样渲出 2160×2880、文字重栅格化、GSAP seek 渲染正常、非空白。

## [0.1.0] — 2026-06-12

口播视频制作 skills 的首个版本。两个扁平 skill,组成 `文稿/音频 → 4K 成片` 链路。

### Added

- **`listenhub-tts`** —— 口播文本 → 音频 + 字幕(视频制作链路的上游)。
  - **原生 speech 路(首选)**:ListenHub `/v1/speech`,把文稿切句成多段 `scripts`,
    引擎直接回 `audioUrl` + `subtitlesUrl`(**标准 SRT、逐句 cue、文字＝输入原文、零识别错**)。
    只需 `LISTENHUB_API_KEY` 一个 key。
  - **ASR 路(fallback)**:speech 路拿不到字幕时,用 Groq `whisper-large-v3` 或
    OpenAI `whisper-1` 基于音频转写补字幕(需 `GROQ_API_KEY` / `OPENAI_API_KEY`,
    `TTS_MODE=asr` 可强制)。
  - **选音色**:`listenhub-speakers.sh` 拉 `/v1/speakers/list`,列出可用 speaker
    供 `AskUserQuestion` 挑选;系列沿用同一音色保持一致。
  - **字幕校正**:优先调外部 `subtitle-correction` skill;缺失则内置文本级校正
    (`srt_helper.py correct`,只改字、不动时间轴/编号/条数)。
- **`producing-video`** —— 音频 + SRT → 4K MP4。用 HyperFrames(HTML 即视频)按 SRT
  时间轴搭合成、渲染成片。含出片铁律:定时动画必须挂 `tl`、转场只用场景自身 clip-path
  揭幕、字体本地 woff2、响度 `loudnorm` 到 -14 LUFS、空白场景抽帧自检、4K 超采样等。
- `README.md` 写明环境变量与外部 skill 依赖;`LICENSE`(MIT);`.gitignore`。

### Verified

- ListenHub `/v1/speech` 响应契约实网验证(2026-06):
  `{code,data:{audioUrl, subtitlesUrl(.srt), audioDuration, credits}}`。
- 端到端跑通 `文本 → mp3 + srt`,下游 `srt-cues` 解析正常,**仅用 `LISTENHUB_API_KEY`、
  未碰 ASR**(credits=2 / ~16s 测试音频)。

### Notes

- 外部依赖各自独立分发:`subtitle-correction`(来自 `sugarforever/01coder-agent-skills`)、
  `hyperframes` / `hyperframes-cli`(HyperFrames 工具链)。详见 README。
- producing-video 从 `sugarforever/01coder-agent-skills` 迁出;原 PR #12 关闭,该 skill
  不再留在 01coder。

[0.3.0]: https://github.com/sugarforever/boring-video-studio/releases/tag/v0.3.0
[0.2.0]: https://github.com/sugarforever/boring-video-studio/releases/tag/v0.2.0
[0.1.0]: https://github.com/sugarforever/boring-video-studio/releases/tag/v0.1.0
