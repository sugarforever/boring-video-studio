---
name: boring-video
description: Use when developing a content-driven video from a topic, research bundle, article, or draft, or when routing an existing script or non-argument video into HyperFrames production.
---

# Boring video

Orchestrate content development and a progressively refined HyperFrames project as one chain. Content is established before it is adapted for speech or visuals; scene direction begins the renderable project, storyboard turns it into an animatic, and production continues it.

## Intake

Resolve existing decisions from the request and project files. First classify the input:

- **Content-driven:** research, evaluation, analysis, opinion, tutorial, news, profile, or another narrated work whose value depends on a complete argument and may also become a blog article.
- **Direct-production:** a locked script, product promo, UI demonstration, music-led piece, short motion graphic, or another work that does not need an article to establish its meaning.

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

When this intake creates or adapts `content/ARTICLE.md`, **REQUIRED SUB-SKILL:** Use `artifact-preview` for that file and satisfy its completion criterion for `content/ARTICLE.preview.html` before starting `/to-spec-beats`.

For content-driven work, ask one compact question for any missing production choices:

1. **Presentation:** faceless, footage, screen capture, talking head, or mixed media?
2. **Collaboration:** storyboard reviews or agent-executed production with final preview?
3. **Voice:** HyperFrames voice, ListenHub TTS, user recording, or no narration?
4. **Design:** existing design truth, named direction, or agent-proposed direction?

Record the answers in the HyperFrames `BRIEF.md`. In agent-executed work, propose and record a design direction when the user leaves it open. Direct-production work skips this wrapper intake because `/hyperframes` owns that brief.

## Chain

Before `/to-scenes` starts the renderable project, read [`references/hyperframes-review-project.md`](references/hyperframes-review-project.md). Pass its project identity and review state forward through `SCENES.md`, `STORYBOARD.md`, and the HyperFrames project manifest; downstream skills consume those artifacts rather than this internal reference.

For content-driven work, start at the first missing or explicitly revised artifact:

1. `/develop-topic` → `content/RESEARCH.md`, experiment reports, and approved `content/TOPIC.md`
2. `/to-article` → approved `content/ARTICLE.md`
3. `/to-spec-beats` → `BEATS.md`
4. `/to-narration` → `NARRATION.md`
5. `/to-scenes` → `SCENES.md`, shared HyperFrames project, and visual direction board
6. `/to-storyboard` → `STORYBOARD.md` and a full animatic in that project
7. `/to-video` → production continuation in that project

Finish each skill's completion criterion before advancing. A downstream finding returns to the artifact that owns the decision, then propagates forward.

When the user begins with an approved complete article, recompute its digest before starting at `/to-spec-beats`. When they begin with later content-driven artifacts, recompute every present artifact digest, require each child to carry the current digest of its immediate parent, and verify that the chain traces to an approved `content/ARTICLE.md`; then resume at the first missing stage. Artifact existence alone is not resumable state. Direct-production inputs bypass this content chain and begin at `/hyperframes`; never reinterpret a locked script as permission to invent an article, thesis, or claims.

## Handoff

Presentation and workflow are separate decisions. Collect the presentation intent without selecting a workflow from memory. `/to-video` reads the current `/hyperframes` contract and performs the route.

## Done

Content-driven planning is complete when the applicable approved content artifacts, four planning artifacts, direction board, and seekable animatic agree and satisfy their owners. The wrapper run is complete when `/to-video` continues the reviewed HyperFrames project with the confirmed voice branch through the selected production workflow.
