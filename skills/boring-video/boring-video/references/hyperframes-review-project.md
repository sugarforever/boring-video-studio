# HyperFrames review project

Use one HyperFrames project from scene direction through final production. Create or select it during `/to-scenes`, record its path and revision in the planning artifacts, leave it unchanged while `/to-storyboard` plans frames, and continue it during `/to-video`. A stage does not rebuild an approved visual language in a second project.

## Shared project state

Keep a review manifest in project state with:

- project path and revision;
- delivery aspect ratio and resolution;
- source artifact digests;
- approved composition and asset digests, final scene durations, local shot/cue timings, and representative parity-check timestamps;
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

During `/to-scenes`, implement each scene as playable HTML in the shared HyperFrames project. Load `/hyperframes` and follow its current composition and preview contract. Each approved scene is the finished scene that appears in the final video. This stage owns its content, composition, assets, typography, internal camera work, animation, local timing, and scene-local audio. Subsequent stages assemble these exact compositions and add boundary transitions. Use the delivery aspect ratio and resolution from `BRIEF.md`.

Provide an HTML scene review entry point in the project with:

- a scene index and direct access to each scene;
- the actual composition, with play, pause, replay, and seeking through the scene;
- the scene's complete narration text, stable narration IDs, and a visible indication of the current sentence;
- the delivery narration audio synchronized to the visual sequence; scratch tracks are explicitly provisional and keep approval pending;
- separate content and visual findings, review status, and the project revision being reviewed.

The review entry point loads the production compositions rather than copying their markup or animation logic. Review controls and narration text sit outside the delivery frame. If Studio supplies only part of this interface, add the missing review shell around the same compositions; do not defer per-scene review until final production. Persist findings in the project review manifest and reference them from `SCENES.md`; editable browser controls are optional.

Complete the scene at delivery quality: final copy, fonts, media, code or evidence-backed surfaces, entrances, camera moves, easing, state changes, demonstrations, readable holds, scene-local effects, and narration cues. A deliberately static scene still plays for its narration duration. Resolve every scene-internal content or design finding here. Only assembly work may remain: scene placement, boundary transitions, and whole-film audio mastering. Scene-internal finishing is not deferred to `/to-video`.

Resolve the selected voice route and its voice approval before marking scenes passed. Read the selected HyperFrames workflow's current voice contract; when ListenHub or MiniMax is chosen, use the installed `/listenhub-tts` or `/minimax-tts` and ingest the resulting audio and subtitles through `/media-use` during this stage. Preserve locked narration and user-recorded audio. Scratch audio and sentence cues support work in progress only: replace them with delivery audio and repeat the affected review before approval. Unavailable audio keeps narrated scenes pending; a scene explicitly intended to be silent is reviewed as silent. Audio or subtitle replacements after approval reopen the affected scenes.

### Viewing and decisions

Play every scene with its narration. Review both whether the content earns its place and whether the visual event explains it: claim accuracy, redundancy, metaphor, density, legibility, cue alignment, and time to inspect. Watch adjacent scenes together, then the assembled sequence, to judge repetition, continuity, and rhythm. Hero or Start/Hero/End images may supplement this review but do not replace playback.

Record actual reviewed scene intervals, narration source and timing basis, source digests, composition paths, content findings, visual findings, unresolved limitations, and decisions against the reviewed project revision. Distinguish `pending`, `changes_requested`, and `passed`. A pass requires completed content and visual review, resolved scene-internal findings, delivery assets and audio, and verified scene-local timing. Record intentional silence where applicable. Scene completion is judged against the final-video scene, not a representative prototype. Record reviewer identity; in user-review collaboration, only explicit user acceptance marks a scene passed. In agent-executed collaboration, perform and record the viewing review yourself under the agreed `BRIEF.md` mode.

Apply content feedback to `NARRATION.md` or its owning upstream artifact while preserving beat claims and lineage. Apply visual feedback to the same composition files. Refresh affected digests, audio, cues, and review state, then replay the affected scenes and boundaries. A source or design change marks affected decisions stale; completion requires current passed decisions for every scene and the assembled sequence.

`SCENES.md` remains the authoritative scene intent and decision record. Link the HTML review entry point and each scene's composition, narration anchors, review record, and current project revision from it. Present the working HTML entry point for joint review alongside the Markdown; merely generating files does not establish that playback works or has been reviewed.

## Storyboard plan

During `/to-storyboard`, write the assembly plan in HyperFrames-native `STORYBOARD.md`:

- placement and order of finished scenes, with their approved durations;
- references to existing composition sources and inherited local shot moments, cues, and deliberate silence;
- hard cuts or boundary transitions, with duration, overlap, and required handles;
- continuity expectations at every join.

Read internal timings from the reviewed scenes. New internal reveals, camera work, timing budgets, or scene designs return to `/to-scenes` before the assembly plan advances.

Keep new storyboard frames at `status: outline` until the canonical HyperFrames checks justify a later status. Reference the existing reviewed scene HTML in each frame's narrative body; its presence alone does not establish an implemented canonical frame `src`. This stage records the project revision it inherits without mutating the compositions. Distinguish already viewed scene timing from planned changes to frame boundaries or transitions; changes that invalidate scene decisions return to `/to-scenes`.

`STORYBOARD.md` is the review surface for the integration plan. Existing scene playback remains the evidence for inherited decisions. HyperFrames production implements new integration decisions, and Studio reviews their actual timing, motion, transitions, and scrubbing on the assembled timeline.

## Production continuation

During `/to-video`, mount the finished scene compositions according to `STORYBOARD.md`, add the planned boundary transitions, complete whole-film audio mastering, and run rendering/export checks. Advance canonical frame statuses only when HyperFrames checks justify them.

Verify composition and asset digests against the approved manifest. Compare representative scene-local timestamps in isolated scene playback and the assembled timeline outside declared transition overlaps; the picture and local audio/cues must match after accounting for each scene's global offset. Review every join for clipping, hidden first/last states, overlapping speech, and continuity. Transition handles or overlaps must preserve approved readable holds and narration; insufficient handles return the affected scene to `/to-scenes`.

New scene-internal problems discovered in full playback also return to `/to-scenes` for correction and reapproval, then propagate into assembly. A production pass never silently redesigns an approved scene or replaces its voice, assets, or timing.
