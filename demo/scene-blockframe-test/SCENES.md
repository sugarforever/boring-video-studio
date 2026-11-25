---
artifact_digest: sha256:fc99c93d4705d57f8b6d26fa40021167039ecef11d59358cfdccce8ba723f551
source_beats: BEATS.md
source_beats_digest: sha256:2d18b3081a3a495676ba0710c8421f936340d2048ec6b0548d0f4176d5f5c253
source_narration: NARRATION.md
source_narration_digest: sha256:38f5249693baf8f6e57c74103944a1bda7aaabb15a18a302dd23cd255f799ab9
hyperframes_project: .
hyperframes_revision: blockframe-pr-r1
html_review: review.html
concept: 把场景规划变成可观看、可修改、可装配的实际场景
continuity: 同一播放器中的信息，从出现到收拢，再进入装配轨道
fixture_mode: synthetic
---

# Blockframe 场景测试

本轮用户指定 blockframe 糖果色块，采用随附的官方 [frame.md](frame.md) 的颜色、粗黑边、硬阴影和方角。中文由显式 Noto Sans SC 字体文件承担对应字重。

[打开 HTML 审阅入口](review.html)。它直接读取下列生产源文件；HyperFrames 的 [整片入口](index.html) 挂载同一组文件，只安排它们的开始时间。没有独立的低保真视觉副本。

用户明确选择本轮只看画面。以下视觉实现供用户审阅，音频与音画联合审阅仍待完成；不把本轮视觉输出标记为完整场景已通过。

## Scene 01 - 文字规划看着都合理

- beats: B01
- purpose: 从纸面规划进入实际播放
- world: 奶油色纸面进入蓝色预览
- hero: 规划稿、逻辑通过印章与真正发生变化的预览
- event: 规划稿建立 → 印章落下 → 同一视野切换为实际播放器 → 两个重点按顺序出现
- camera: 全景到播放器中景；规划稿缩退，播放器接替视觉中心
- focus: 色块面积、位置、运动和内容保留决定视觉重点
- continuity_in: 开场
- continuity_out: 转入同一播放器中的信息密度演示
- rhythm: 建立上下文、发生变化、稳定阅读
- feasibility: native；本轮按用户选择不生成音频
- composition: [compositions/s01.html](compositions/s01.html)
- source_digest: sha256:d07cf49ba24f2fb7f7b709437fdede64fde3f9490f2f593b771f6297697f0c48
- narration: b01-p01, b01-p02；音频 deferred_by_user
- timing: 8 秒；关键本地时间 2, 6 秒
- boundary_handles: 进入 0 秒，退出 0 秒；硬切可直接装配，叠化或重叠转场必须另审边界
- review: [本场播放](review.html?scene=s01)、[审阅记录](review/manifest.json)；blockframe-pr-r1；pending_user_review
- content_findings: 等待用户审阅对应口播是否合适
- visual_findings: 等待用户审阅视觉设计；结构与采样检查见 REVIEW.md
- assembly_work: 通过后挂载同一 HTML、安排全局位置和边界转场；不在后续重做内部视觉
- visual_risks: 实际信息密度是否成立、变化过程是否清楚、最终阅读停留是否足够

### 对应口播与暂定提示区间

- 0–4 秒，b01-p01：文字规划里，每个场景都能写得很合理。
- 4–8 秒，b01-p02：但画面到底好不好看，只读文字还判断不了。

### 已实现的本地时序

- 0–3.7 秒：纸面规划与逻辑通过印章。
- 4–5.4 秒：进入实际画面；先建立问题，再出现说明。
- 5.4–8 秒：结果阅读停留。

### screen_contract

- viewer_question: 文字规划能确认什么，还有什么看不见？
- temporal_structure: 同一主体的连续状态变化；每个关键状态的具体时间已在本场实现，后续分镜继承这些时间
- cue_evidence: 两句口播分别对应该场前后半段的可见状态；本轮提示时间暂定，未声称音画已通过
- framing: 全景到播放器中景；规划稿缩退，播放器接替视觉中心
- truth_mode: instructional reconstruction；这是设计方法的教学示意，不是实测软件录像

## Scene 02 - 播放才看见问题

- beats: B02
- purpose: 用实际信息量体现拥挤，再收拢成一个重点
- world: 沿用播放器，背景切为绿色
- hero: 同一个播放器中的六个完整信息块
- event: 六项信息竞争注意力 → 五项退出 → 一个大重点占据原有舞台 → 保留阅读时间
- camera: 固定全景；同一空间做连续状态变化
- focus: 色块面积、位置、运动和内容保留决定视觉重点
- continuity_in: 延续播放器与信息块主体；硬切换背景
- continuity_out: 同一重点进入编辑示例
- rhythm: 建立上下文、发生变化、稳定阅读
- feasibility: native；本轮按用户选择不生成音频
- composition: [compositions/s02.html](compositions/s02.html)
- source_digest: sha256:d14a9ac412f086ed83effa126c04a4e9c5a736a555d8245e074ed1005eeb57e5
- narration: b02-p01, b02-p02；音频 deferred_by_user
- timing: 10 秒；关键本地时间 2, 7 秒
- boundary_handles: 进入 0 秒，退出 0 秒；硬切可直接装配，叠化或重叠转场必须另审边界
- review: [本场播放](review.html?scene=s02)、[审阅记录](review/manifest.json)；blockframe-pr-r1；pending_user_review
- content_findings: 等待用户审阅对应口播是否合适
- visual_findings: 等待用户审阅视觉设计；结构与采样检查见 REVIEW.md
- assembly_work: 通过后挂载同一 HTML、安排全局位置和边界转场；不在后续重做内部视觉
- visual_risks: 实际信息密度是否成立、变化过程是否清楚、最终阅读停留是否足够

### 对应口播与暂定提示区间

- 0–5 秒，b02-p01：一播放，才发现信息太挤，观众来不及看。
- 5–10 秒，b02-p02：留住一个重点，再给它足够的停留时间。

### 已实现的本地时序

- 0–0.9 秒：六块内容进入。
- 0.9–4.6 秒：同时保留六项供密度判断。
- 4.6–5.8 秒：收起多余内容，替换为单一重点。
- 6.1–10 秒：单一问题与阅读停留。

### screen_contract

- viewer_question: 为什么同样的说明，实际画面读起来不同？
- temporal_structure: 同一主体的连续状态变化；每个关键状态的具体时间已在本场实现，后续分镜继承这些时间
- cue_evidence: 两句口播分别对应该场前后半段的可见状态；本轮提示时间暂定，未声称音画已通过
- framing: 固定全景；同一空间做连续状态变化
- truth_mode: instructional reconstruction；这是设计方法的教学示意，不是实测软件录像

## Scene 03 - 口播和画面一起改

- beats: B03
- purpose: 内容与场景一起改，后续只拼接
- world: 粉色编辑世界，最终落到拼接轨道
- hero: 正在修改的口播稿、相邻的场景与装配时间线
- event: 删除冗余口播 → 新口播落下 → 场景收拢为重点 → 同一播放器缩到装配时间线上方
- camera: 双主体中景；编辑完成后拉远显示装配关系
- focus: 色块面积、位置、运动和内容保留决定视觉重点
- continuity_in: 延续播放器与信息块主体；硬切换背景
- continuity_out: 装配时间线与结论停留
- rhythm: 建立上下文、发生变化、稳定阅读
- feasibility: native；本轮按用户选择不生成音频
- composition: [compositions/s03.html](compositions/s03.html)
- source_digest: sha256:3c7d2af08996711b996e7d1c9347264a78ddf009e6906100c22309253196550b
- narration: b03-p01, b03-p02；音频 deferred_by_user
- timing: 10 秒；关键本地时间 2.5, 8 秒
- boundary_handles: 进入 0 秒，退出 0 秒；硬切可直接装配，叠化或重叠转场必须另审边界
- review: [本场播放](review.html?scene=s03)、[审阅记录](review/manifest.json)；blockframe-pr-r1；pending_user_review
- content_findings: 等待用户审阅对应口播是否合适
- visual_findings: 等待用户审阅视觉设计；结构与采样检查见 REVIEW.md
- assembly_work: 通过后挂载同一 HTML、安排全局位置和边界转场；不在后续重做内部视觉
- visual_risks: 实际信息密度是否成立、变化过程是否清楚、最终阅读停留是否足够

### 对应口播与暂定提示区间

- 0–5 秒，b03-p01：所以，场景阶段就该把口播和画面放在一起审。
- 5–10 秒，b03-p02：内容不合适就改稿，画面不满意就改同一份场景。

### 已实现的本地时序

- 0–1.6 秒：建立稿子和当前场景。
- 1.6–2.6 秒：划掉旧句，显示新句。
- 4.7–5.55 秒：移走多余信息，显示修改后的重点。
- 6.6–7.6 秒：退出稿子，播放器缩到装配时间线。
- 7.6–10 秒：拼接结论阅读停留。

### screen_contract

- viewer_question: 逐场审阅后，修改应该写回哪里？
- temporal_structure: 同一主体的连续状态变化；每个关键状态的具体时间已在本场实现，后续分镜继承这些时间
- cue_evidence: 两句口播分别对应该场前后半段的可见状态；本轮提示时间暂定，未声称音画已通过
- framing: 双主体中景；编辑完成后拉远显示装配关系
- truth_mode: instructional reconstruction；这是设计方法的教学示意，不是实测软件录像
