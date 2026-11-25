---
name: to-scenes
description: Use when turning video beats and narration into finished, playable HyperFrames scenes, or revising scene content, design, or local timing before assembly.
---

# To scenes

Turn `BEATS.md` and `NARRATION.md` into finished scene HTML and its `SCENES.md` contract. A scene is an event in a world: its visuals reveal, demonstrate, compare, or hold when the spoken idea needs them.

## Process

1. Read both inputs, project design truth, and [the capability envelope](references/hyperframes-capability-envelope.md). Recompute beats and narration artifact digests; require narration's `source_digest` to match current beats and each stored artifact digest to match its file.
2. For screen evidence or explanatory sequences, read [the viewing contract](references/screen-evidence.md). For relationship diagrams, matched comparisons, or ordered/grouped cards, also read [scene presets](references/scene-presets.md). Define the viewer question, visible evidence, narration cues, dependencies, and framing purpose under those contracts.
3. Group beats into continuous events; split events that need distinct scenes. Establish the film's continuity, variation in worlds and shot scales, visual peaks, and rhythm. Classify each scene's feasibility and resolve essential dependencies or fallbacks before implementation.
4. Revise narration whose order, length, or repetition fights the event, preserving its beat's claim and job. Follow `/to-narration` for content-lineage changes; preserve locked narration and user-recorded audio. Refresh its digest and validate lineage before using the revision.
5. Read [the shared project contract](../boring-video/references/hyperframes-review-project.md) and [scene format](references/scene-format.md), load `/hyperframes`, and create or select the project. Draft `SCENES.md` with source lineage and scene decisions; declare demonstrations' content, truth mode, and code labels before implementation.
6. Finish scenes and their HTML review entry point under the shared contract's delivery and voice rules. For terminal-hosted demonstrations, use `/record-terminal`. Update `SCENES.md` with actual local timing, composition paths, project revision, and review references.
7. Present the working HTML entry point, run the scene audit, and perform the shared contract's per-scene and consecutive-sequence review. Apply findings to their owning narration or scene source; refresh lineage and repeat affected reviews until decisions pass in the agreed collaboration mode.

Present `SCENES.md` and any revised `NARRATION.md` under [Markdown review](../boring-video/references/markdown-review.md).

Complete when every beat is covered, the scene audit passes, the shared contract's scene review gate passes, and current source digests, project revision, and presented Markdown agree. A visual-only checkpoint may be presented with outstanding audio review recorded as pending.
