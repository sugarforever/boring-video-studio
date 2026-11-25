# HyperFrames review project

Use one project from scene implementation through export. `/to-scenes` finishes and reviews scenes; `/to-storyboard` plans their assembly without changing them; `/to-video` implements joins and delivers the assembled film. Each stage reads the relevant sections below.

## Shared project state

Keep a review manifest with project path, revision, selected HyperFrames route, delivery dimensions, and:

- planning-source digests and scene-to-composition/frame mapping;
- composition and asset digests, delivery durations, local shot/cue timings, and parity-check timestamps;
- font sources and loaded families/weights;
- HTML review entry point, narration/audio mappings, review intervals, findings, reviewer identities, and decisions;
- referenced supplemental renders and terminal/code/data evidence manifests.

`SCENES.md` owns scene intent and links each scene to its composition and manifest record. A source or design change invalidates affected review decisions and evidence; refresh their lineage and repeat the affected review.

## Font contract

Use project design truth; otherwise default to Noto Sans SC for Chinese body/labels (400, 700, 800, 900 as used) and Montserrat 700 for English interface headings. Define shared CSS family tokens with an explicit Chinese fallback and `font-synthesis: none`. Terminal surfaces use `/record-terminal`'s font contract.

Before review, inspect rendered output and resolved fonts for Chinese, Latin, and emphasized text. Verify that every used family and weight is loaded rather than merely declared.

## Scene delivery

An approved scene is the finished scene that appears in the final video: content, final copy/assets/fonts, composition, internal shots and animation, easing, readable holds, local timing, narration, and scene-local effects. Implement it using the current `/hyperframes` composition contract at the `BRIEF.md` delivery dimensions. Only scene placement, boundary transitions, and whole-film mastering remain downstream.

### Voice

Resolve the selected HyperFrames route and its voice contract during `/to-scenes`. For ListenHub or MiniMax, use the installed `/listenhub-tts` or `/minimax-tts` and ingest the audio/subtitles through `/media-use`. Preserve locked narration and user-recorded audio.

Scratch tracks and provisional sentence cues support unfinished review. Replace them with delivery audio before passing narrated scenes. Missing or explicitly deferred audio keeps that review pending; deliberately silent scenes receive silent review. Audio/subtitle changes invalidate affected decisions.

### HTML review entry point

Load the production compositions directly, with their actual animation logic. Keep review controls outside the delivery frame. Provide scene selection, play/pause/replay, seeking, complete narration text with stable IDs and an active-sentence cue, synchronized delivery audio, and separate content/visual findings and status for the current revision.

Use the existing HyperFrames preview capabilities where sufficient; add the missing review shell around the same compositions. Persist findings in the manifest; editable browser controls are optional. Stills supplement playback evidence.

## Scene review gate

Present the working HTML entry point alongside `SCENES.md`. Play every scene at delivery size and normal speed, reviewing content suitability/accuracy, visual explanation, metaphor, density, legibility, cue alignment, and readable holds. Play scenes consecutively to judge repetition, continuity, and rhythm before planning final joins. This sequence review covers the scenes; final transition playback belongs to assembly.

Record actual reviewed intervals, source revision, audio/timing basis, content/visual findings, limitations, reviewer, and `pending`, `changes_requested`, or `passed` decisions. A pass requires finished scene internals, delivery assets/audio or declared silence, verified local timing, and resolved content/visual findings. Under user-review collaboration, require explicit user acceptance; under agent-executed collaboration, perform and record that review yourself as agreed in `BRIEF.md`.

The gate passes when every scene and the consecutive sequence have current passed decisions. A visual-only checkpoint leaves the joint review pending. Findings return to the owning content artifact or composition; refresh digests, affected audio/cues, and review decisions before advancing.

## Storyboard plan

`STORYBOARD.md` records scene order/placement, approved durations and source references, inherited local shot moments/cues, cuts, transition durations/overlaps, handles, and continuity expectations. Internal design and timing come from the reviewed scenes; required changes return to `/to-scenes`.

Keep new assembly frames at `status: outline` until canonical HyperFrames checks justify a later status. Existing scene HTML does not by itself certify an implemented canonical frame `src`. Storyboard planning leaves scene compositions unchanged.

## Production continuation

Mount approved scene compositions according to `STORYBOARD.md`, add boundary transitions, master global audio levels and cross-scene music continuity, then run HyperFrames playback/export checks. Reuse reviewed narration, subtitles, and scene-local effects.

Verify composition/asset digests and compare representative local timestamps in isolated and assembled playback outside declared transition overlaps. Pictures and local audio/cues must match after accounting for global placement. Check every join for clipped first/last states, shortened readable holds, overlapping speech, and continuity. Transition overlaps must fit declared handles and protect narration/holds.

Scene-internal findings, missing required audio, or inadequate handles return to `/to-scenes` for correction and reapproval before reassembly. Record actual viewing intervals and the validated project revision for export.
