---
name: to-scenes
description: Use when a narrated video's beats and draft narration need visual direction, scene concepts, metaphors, worlds, action, camera logic, or visual continuity before storyboarding.
---

# To scenes

Turn `BEATS.md` and `NARRATION.md` into `SCENES.md`. A scene is a small event in a world, not a container for information. Its visuals serve the narration: they reveal, demonstrate, compare, or hold exactly when the spoken idea needs them.

## Process

1. Read both inputs, the applicable design truth, and [`references/hyperframes-capability-envelope.md`](references/hyperframes-capability-envelope.md). Recompute the beats and narration artifact digests; continue only when the narration's `source_digest` matches the current beats and both stored artifact digests match their files. The envelope constrains feasibility without prescribing implementation. Treat draft narration as revisable evidence; preserve explicitly locked narration or user-recorded audio when resolving visual timing.
2. For screen evidence or explanatory visual sequences, including product, code, configuration, diagram, chart, or comparison scenes, read [`references/screen-evidence.md`](references/screen-evidence.md). Establish the viewer question, cue-to-evidence mapping, temporal structure and dependencies, framing purpose, and any setup differences. Give each abstract beat a physical or spatial expression. Use a visible state change for a transformation, or a deliberate readable hold for result or topology inspection. Coordinate that change with the narration's explanation, emphasis, and pauses instead of designing a separate visual performance.
3. Group beats that belong to one continuous event; split a beat when its explanation requires distinct visual events.
4. Design the film as a whole: establish a continuity object or motion, vary worlds and shot scales, place visual peaks, and name the rhythm.
5. Flag narration sentences whose order, length, or duplication fights the visual event. Revise `NARRATION.md` only after preserving the originating beat's claim and job. After any revision, recompute its `artifact_digest` and revalidate its beats and article lineage before using it as a source.
6. Write `SCENES.md` using [`references/scene-format.md`](references/scene-format.md). Read that file before drafting or auditing scenes, and record the current beats and narration digests. For every demonstration, define the exact visible sequence, choose its truth mode, and declare how every code surface is labeled; do not leave those decisions for production.
7. Create or select the single HyperFrames review project and record its path and revision in `SCENES.md`. Build each scene's smallest useful 16:9 proof: Hero when one state is sufficient, Start/Hero/End when change or continuity must be judged, and additional states only for a named risk. Use real typography, near-final copy, and real code or evidence-backed terminal components wherever those determine the result. Embed or link those proof images from the owning scene section in `SCENES.md`, with their state IDs and project revision.
8. Classify every scene's feasibility using the capability envelope, naming dependencies and fallbacks where required.
9. Run the scene audit in the format reference. If narration changes after scenes exist, revise every affected scene, refresh `source_narration_digest`, recompute the scenes `artifact_digest`, mark affected rendered proof stale, and repeat the audit before completion.

Resolve the visual grammar and declared scene risks with the rendered evidence referenced from `SCENES.md` before advancing. Record project identity, revision, source digests, proof paths, aspect ratio, reviewed risks, and decisions in project state and `SCENES.md`.

Before presenting `SCENES.md`, a changed `NARRATION.md`, or any later revision, follow [`../boring-video/references/markdown-review.md`](../boring-video/references/markdown-review.md). The authoritative `SCENES.md` pairs each semantic scene contract with inspectable rendered evidence from the shared HyperFrames project. Do not represent unrendered prose as visual evidence.

`SCENES.md` is complete when every beat has a feasible visual event, the film has deliberate variation and continuity, each declared visual risk is inspectable through evidence referenced from the Markdown, the shared project and proof revision are recorded, and the Markdown review completion criterion is satisfied for `SCENES.md` and any `NARRATION.md` revised by this stage.
