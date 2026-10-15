---
name: boring-video
description: Use when developing a content-driven video from a topic, research bundle, article, or draft, or when routing an existing script or non-argument video into HyperFrames production.
---

# Boring video

Orchestrate content development and a progressively refined HyperFrames project as one chain. Content is established before it is adapted for speech or visuals; scene direction establishes rendered visual evidence, storyboard plans buildable frames, and HyperFrames owns production and playable review.

## Intake

Resolve existing decisions from the request and project files. First classify the input:

- **Content-driven:** research, evaluation, analysis, opinion, tutorial, news, profile, or another narrated work whose value depends on a complete argument and may also become a blog article.
- **Direct-production:** a locked script, product promo, UI demonstration, music-led piece, short motion graphic, or another work that does not need an article to establish its meaning.

Resolve reusable **production defaults** from explicit project, series, brand, or team guidance before asking for one-off choices. Create the workflow `BRIEF.md` at intake and record each adopted default, its source, and its scope there so every upstream skill can read it before making content or voice decisions; carry the same brief into the HyperFrames project when that project is created. A current request overrides a reusable default. Defaults may cover recurring structure, language and voice, design truth, cover ratios, publishing targets, or terminal presentation, but must not be inferred from an unavailable personal profile. Keep project-specific conventions in project files rather than universalizing them into this skill.

For content-driven work, locate the first missing approved content artifact. A supplied article counts only when the user explicitly confirms it as the content master. Store or adapt it as `content/ARTICLE.md` with this provenance:

```yaml
---
source: external
origin: <URL or path>
origin_revision: <Git revision, source digest, or captured-at timestamp>
status: approved
approved_at: YYYY-MM-DD
approved_digest: sha256:<digest>
voice:
  language: ...
  skills: []
  documents: []
  unavailable: []
  status: resolved | assumed
---
```

Compute `approved_digest` as SHA-256 of the complete file after removing only the `approved_digest:` line. Do not manufacture an article merely to satisfy the chain for direct-production work; load `/hyperframes` and let its current intent layer own intake and workflow selection.

When this intake creates or adapts `content/ARTICLE.md`, read [`references/markdown-review.md`](references/markdown-review.md) and present that authoritative Markdown before starting `/to-spec-beats`.

For content-driven work, ask one compact question for any missing production choices:

1. **Presentation:** faceless, footage, screen capture, talking head, or mixed media?
2. **Collaboration:** storyboard reviews or agent-executed production with final preview?
3. **Voice:** HyperFrames voice, ListenHub TTS, user recording, or no narration?
4. **Design:** existing design truth, named direction, or agent-proposed direction?
5. **Publishing:** which covers, platform adaptations, blog/article variants, subtitles, or social copy are requested, if any?

Record the answers and adopted production defaults in the workflow `BRIEF.md`. In agent-executed work, propose and record a design direction when the user leaves it open. For direct-production work, pass the resolved defaults and any publishing request into the `BRIEF.md` owned by `/hyperframes` rather than repeating the content-chain questions.

## Chain

Before `/to-scenes` starts the renderable project, read [`references/hyperframes-review-project.md`](references/hyperframes-review-project.md). Pass its project identity and review state forward through `SCENES.md`, `STORYBOARD.md`, and the HyperFrames project manifest; downstream skills consume those artifacts rather than this internal reference.

For content-driven work, start at the first missing or explicitly revised artifact:

1. `/develop-topic` → `content/RESEARCH.md`, experiment reports, and approved `content/TOPIC.md`
2. `/to-article` → approved `content/ARTICLE.md`
3. `/to-spec-beats` → `BEATS.md`
4. `/to-narration` → `NARRATION.md`
5. `/to-scenes` → `SCENES.md`, shared HyperFrames project, and rendered visual evidence referenced from the Markdown
6. `/to-storyboard` → HyperFrames-native `STORYBOARD.md`
7. `/to-video` → production continuation and Studio review in that project

Finish each skill's completion criterion before advancing. A downstream finding returns to the artifact that owns the decision, then propagates forward.

When publishing outputs were requested for content-driven work, open a **publication branch** after the article, narration, and scene direction are stable. Derive cover direction from the approved design truth and scene evidence; derive platform copy, blog/article adaptations, subtitles, and social copy from the approved content and narration. For direct-production work, this wrapper owns the same branch beside `/hyperframes`: open it after the locked source and HyperFrames design direction are stable, deriving copy from that source and covers from that design direction. Record requested outputs, source digests, target platforms or ratios, and output paths in `PUBLISHING.md`. Video production may continue while this branch is prepared, but neither branch may silently invent new claims or a competing visual identity.

When the user begins with an approved complete article, recompute its digest before starting at `/to-spec-beats`. When they begin with later content-driven artifacts, recompute every present artifact digest, require each child to carry the current digest of its immediate parent, and verify that the chain traces to an approved `content/ARTICLE.md`; then resume at the first missing stage. Artifact existence alone is not resumable state. Direct-production inputs bypass this content chain and begin at `/hyperframes`; never reinterpret a locked script as permission to invent an article, thesis, or claims.

## Handoff

Presentation and workflow are separate decisions. Collect the presentation intent without selecting a workflow from memory. For content-driven work, `/to-video` reads the current `/hyperframes` contract and performs the route. Direct-production work remains in `/hyperframes`; this wrapper resumes only to produce any requested publication branch.

## Done

Content-driven planning is complete when the applicable approved content artifacts, four planning artifacts, and referenced visual evidence agree and satisfy their owners. A content-driven wrapper run is complete when `/to-video` continues the reviewed HyperFrames project with the confirmed voice branch through the selected production workflow, HyperFrames Studio owns the playable timeline review, and any requested publication branch has source-linked outputs recorded in `PUBLISHING.md`. A direct-production run is complete when its `/hyperframes` workflow owns the playable review and this wrapper has recorded any requested publication outputs in `PUBLISHING.md`.
