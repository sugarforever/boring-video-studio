# Blockframe 第二次测试

[输入](INPUT.md) · [场景与口播](SCENES.md) · [HTML 审阅](review.html) · [记录](review/manifest.json)

采用随附的 HyperFrames blockframe 的设计规范，颜色循环使用奶油、绿和粉；4px 黑边与 8px 硬阴影、方角、Inter 800–900 和 Space Grotesk 标签。中文用显式 Noto Sans SC 对应字重。场景中的画幅相对尺寸使用 cqw；这是用户指定的预设，不是仅凭名称自行仿造的配色。

## 输出与当前状态

- 三个实际生产场景：纸面规划进入播放、六项信息收拢为一个重点、修改稿子和画面后进入装配。
- 单场审阅直接读取 compositions/ 下的文件。HyperFrames 整片入口 index.html 只挂载相同文件，安排 0、8、18 秒三个起点，未另画一份预览。
- 每场内部动画、字重、可读性与关键阅读停留已经实现，待用户判断设计是否满意。
- 按用户明确选择，本轮只看画面；音频、音画节奏和联合审阅保留 pending，不声称场景完成审批。

## 检查与实际修正

- HyperFrames 0.9.92 完整 check：lint、runtime、layout、contrast 均零错误、零警告。
- 第一轮实际渲染发现字体接口返回了常规字重而非所声明范围。重新保存实际字重文件并声明准确格式，现已呈现粗黑中文标题；原先几处小字也已放大。
- 删除线是本场讲解动作，针对该行文字声明了刻意遮挡；其他文字仍接受遮挡检查。
- 已查看六个实际渲染状态，包含每场变化前后，并生成开场、中点、接缝与手机尺寸的 review 采样。
- 浏览器已验证切换场景、直接跳至 S02 的 7 秒，再回到 2 秒，恢复六个信息块的初始状态。
- 没有配置独立 motion assertions，也没有额外认证所有像素级单场/整片等价；已核对源文件共享、挂载起点及源文件摘要。

## 保留的警告与待审问题

- film_silent：用户明确选择本轮只看画面，故保留静音。
- dead_stretch：S02 在信息挤满后保留约 3.25 秒供观察。这里的静止是刻意的阅读任务，不添加装饰运动消除提示；最终音频接入后仍需判断这个停留长度。
- 最弱的一处仍是 S03：方法说明的含义偏抽象，是否足够直观，需要用户通过播放实际判断。

本轮不生成最终 MP4；先提供可逐场审阅和连播的实际场景。通过后继续挂载这些源文件，后续只处理拼接和边界转场；若配音导致内部时长变化，返回场景阶段重审。

## PR packaging verification

The copied HTML has been formatted for review, machine-specific paths and ports have been removed, referenced font/runtime files and font licenses are bundled, and source/artifact digests have been refreshed. A fresh HyperFrames check in this checkout passed with zero lint/runtime/layout/contrast errors or warnings; its portable [summary](review/check-summary.json) records the current scene source digests. The two craft warnings remain the requested silence and the intentional dense-reading hold.
