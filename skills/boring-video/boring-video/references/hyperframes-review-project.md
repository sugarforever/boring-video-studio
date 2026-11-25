# HyperFrames review project

Use one HyperFrames project from scene direction through final production. Create or select it during `/to-scenes`, record its path and revision in the planning artifacts, leave it unchanged while `/to-storyboard` plans frames, and continue it during `/to-video`. A stage does not rebuild an approved visual language in a second project.

## Shared project state

Keep a review manifest in project state with:

- project path and revision;
- delivery aspect ratio and resolution;
- source artifact digests;
- font sources and loaded families/weights;
- scene-to-frame or scene-to-composition mapping;
- HTML review entry point, scene composition paths, narration/audio cue mappings, reviewed intervals, findings, and decisions;
- supplemental rendered-proof paths and reviewed risks;
- evidence-manifest paths for terminal, code, data, or other factual replays.

A source or design change that invalidates a reviewed image or timeline marks the affected proof stale. Re-render the smallest affected scope and update its decision record.

## Font contract

Unless project design truth overrides the typography, use these roles:

| Role | Family | Weights |
| --- | --- | --- |
| Chinese body and labels | `Noto Sans SC` | 400, 700, 800, 900 as used |
| English interface headings | `Montserrat` | 700 |

Define shared CSS tokens rather than component-local stacks:

```css
:root {
  --font-zh: "Noto Sans SC", sans-serif;
  --font-en: Montserrat, "Noto Sans SC", sans-serif;
}

html { font-synthesis: none; }
```

Chinese glyphs keep an explicit `Noto Sans SC` fallback. A brand family may replace the defaults; retain a verified Chinese fallback and disable synthetic faces. Terminal and full-screen TUI surfaces follow the independent font contract owned by `record-terminal`.

Before review, inspect rendered output and the browser's resolved font for representative Chinese, Latin, and emphasized text. Confirm every used family and weight is actually loaded, not merely named in CSS.

## Scene HTML review

During `/to-scenes`, implement each scene as playable HTML in the shared HyperFrames project. Load `/hyperframes` and follow its current composition and preview contract. These compositions are production sources: subsequent stages refine the same files. Use the delivery aspect ratio and resolution from `BRIEF.md`.

Provide an HTML scene review entry point in the project with:

- a scene index and direct access to each scene;
- the actual composition, with play, pause, replay, and seeking through the scene;
- the scene's complete narration text, stable narration IDs, and a visible indication of the current sentence;
- narration audio synchronized to the visual sequence, using available recorded audio or a clearly labeled scratch track;
- separate content and visual findings, review status, and the project revision being reviewed.

The review entry point loads the production compositions rather than copying their markup or animation logic. Review controls and narration text sit outside the delivery frame. If Studio supplies only part of this interface, add the missing review shell around the same compositions; do not defer per-scene review until final production. Persist findings in the project review manifest and reference them from `SCENES.md`; editable browser controls are optional.

Use real typography, near-final copy, and actual or evidence-backed code, terminal, and data surfaces. Implement the meaningful entrances, state changes, demonstrations, and readable holds needed to judge the explanation. A deliberately static scene still plays for its narration duration. Fine easing, sound effects, and final mixing may remain unfinished when they do not affect the decision. Declare remaining work per scene.

Use the selected voice route for scratch audio when available and authorized. Scratch audio does not approve a final voice or replace the production voice gate. Preserve locked narration and user-recorded audio. If audio is unavailable, expose sentence cues and provisional timings, record the limitation, and leave spoken pacing review pending; silent playback cannot complete the joint review.

### Viewing and decisions

Play every scene with its narration. Review both whether the content earns its place and whether the visual event explains it: claim accuracy, redundancy, metaphor, density, legibility, cue alignment, and time to inspect. Watch adjacent scenes together, then the assembled sequence, to judge repetition, continuity, and rhythm. Hero or Start/Hero/End images may supplement this review but do not replace playback.

Record actual reviewed scene intervals, narration source and timing basis, source digests, composition paths, content findings, visual findings, unresolved limitations, and decisions against the reviewed project revision. Distinguish `pending`, `changes_requested`, and `passed`. A pass requires both content and visual review, resolved blocking findings, and no pending spoken pacing review. Record reviewer identity; in user-review collaboration, only explicit user acceptance marks a scene passed. In agent-executed collaboration, perform and record the viewing review yourself under the agreed `BRIEF.md` mode.

Apply content feedback to `NARRATION.md` or its owning upstream artifact while preserving beat claims and lineage. Apply visual feedback to the same composition files. Refresh affected digests, audio, cues, and review state, then replay the affected scenes and boundaries. A source or design change marks affected decisions stale; completion requires current passed decisions for every scene and the assembled sequence.

`SCENES.md` remains the authoritative scene intent and decision record. Link the HTML review entry point and each scene's composition, narration anchors, review record, and current project revision from it. Present the working HTML entry point for joint review alongside the Markdown; merely generating files does not establish that playback works or has been reviewed.

## Storyboard plan

During `/to-storyboard`, translate scene decisions into HyperFrames-native frame boundaries and ordered shot moments in `STORYBOARD.md`. Plan:

- approximate offsets for entrances, actions, holds, camera moves, and transitions;
- narration anchors or intentionally silent moments;
- deterministic behavior required from typing, code, terminal, data, or UI evidence;
- continuity expectations at every cut and transition boundary.

Keep new storyboard frames at `status: outline` until the canonical HyperFrames checks justify a later status. Reference the existing reviewed scene HTML in each frame's narrative body; its presence alone does not establish an implemented canonical frame `src`. This stage records the project revision it inherits without mutating the compositions. Distinguish already viewed scene timing from planned changes to frame boundaries or transitions; changes that invalidate scene decisions return to `/to-scenes`.

`STORYBOARD.md` is the review surface for the integration plan. Existing scene playback remains the evidence for inherited decisions. HyperFrames production implements new integration decisions, and Studio reviews their actual timing, motion, transitions, and scrubbing on the assembled timeline.

## Production continuation

During `/to-video`, open the project recorded by the planning artifacts and continue from its reviewed revision. Reuse the reviewed scene compositions when implementing the canonical storyboard's `outline` frames, advance their statuses as the canonical HyperFrames contract permits, and use Studio for final timeline review. Retest narration alignment when final audio replaces a scratch track; changed pacing reopens affected scene decisions. Preserve approved layout, typography, camera logic, planned transitions, and evidence lineage unless a recorded revision reopens the relevant gate.
