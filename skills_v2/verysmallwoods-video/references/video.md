# 视频 · 委托给 HyperFrames

出片走 HyperFrames，**不要在这里重讲那套**。入口 `/hyperframes` 会把「文章 / 主题 → 无实拍讲解」路由到 `/faceless-explainer`，由它完成全部：定 brief、选 design 生成 `frame.md`、写 STORYBOARD、逐帧搭 `compositions/frames/`、组装 `index.html`、注入转场、lint/check、渲染。步骤、gate、脚本都在 `/faceless-explainer` 与领域 skill（`/hyperframes-core` `/hyperframes-animation` `/hyperframes-creative` `/hyperframes-cli` `/media-use`）里 —— 读它们，别复制。

本 skill 在其上只补几条 faceless 没有的**用户口径**：

- **设计** —— 用 Step 0 选定的 preset（默认 `blockframe`），见 `references/designs.md`。
- **口播稿** —— 按用户的写作/口播偏好写；偏好来自上下文 / 记忆 / 会话里的风格 skill。
- **旁白** —— 见 `references/audio.md`（自录 或 TTS，由用户选）。
- **重排到真实 cue** —— 拿到真实音频 + SRT 后，把每帧内部披露重排到真实 cue 时间轴；否则动效走完会定格、旁白在静态画面上继续讲。做法见 `references/audio.md`。
- **字幕不烧进成片** —— 用户在 YouTube 上字幕；成片留底部字幕安全区即可。
- **渲染** —— 1080p60 high 先出保底，磁盘够再出 4K master（`--resolution landscape-4k`）。
