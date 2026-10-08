---
name: to-scenes
description: Use when a narrated video's beats and draft narration need visual direction, scene concepts, metaphors, worlds, action, camera logic, or visual continuity before storyboarding.
---

# To scenes

Turn `BEATS.md` and `NARRATION.md` into `SCENES.md`. A scene is a small event in a world, not a container for information.

## Process

1. Read both inputs, the applicable design truth, [`references/hyperframes-capability-envelope.md`](references/hyperframes-capability-envelope.md), and [`../boring-video/references/hyperframes-review-project.md`](../boring-video/references/hyperframes-review-project.md). Recompute the beats and narration artifact digests; continue only when the narration's `source_digest` matches the current beats and both stored artifact digests match their files. The envelope constrains feasibility without prescribing implementation. Treat narration as revisable evidence, not a locked timeline.
2. Find a physical or spatial expression for each abstract beat: give the concept a body, put it in a world, and cause a visible state change.
3. Group beats that belong to one continuous event; split a beat when its explanation requires distinct visual events.
4. Design the film as a whole: establish a continuity object or motion, vary worlds and shot scales, place visual peaks, and name the rhythm.
5. Flag narration sentences whose order, length, or duplication fights the visual event. Revise `NARRATION.md` only after preserving the originating beat's claim and job. After any revision, recompute its `artifact_digest` and revalidate its beats and article lineage before using it as a source.
6. Write `SCENES.md` using [`references/scene-format.md`](references/scene-format.md). Read that file before drafting or auditing scenes, and record the current beats and narration digests.
7. Create or select the single HyperFrames review project and record its path and revision in `SCENES.md`. Build each scene's smallest useful 16:9 proof: Hero when one state is sufficient, Start/Hero/End when change or continuity must be judged, and additional states only for a named risk. Use real typography, near-final copy, and real code or evidence-backed terminal components wherever those determine the result.
8. Classify every scene's feasibility using the capability envelope, naming dependencies and fallbacks where required.
9. Run the scene audit in the format reference. If narration changes after scenes exist, revise every affected scene, refresh `source_narration_digest`, recompute the scenes `artifact_digest`, mark affected rendered proof stale, and repeat the audit before completion.

Read [`../artifact-preview/references/visual-review-gates.md`](../artifact-preview/references/visual-review-gates.md). Resolve the visual grammar and declared scene risks with the shared project's rendered direction board before advancing.

**REQUIRED SUB-SKILL:** Use `artifact-preview` for `SCENES.md` before declaring it complete and after every later source change. When this stage changes `NARRATION.md`, use `artifact-preview` for that source too. Build `SCENES.preview.html` as a **visual direction board**: pair the semantic scene contract with inspectable renders from the shared HyperFrames project. Do not represent unrendered prose as visual evidence.

`SCENES.md` is complete when every beat has a feasible visual event, the film has deliberate variation and continuity, each declared visual risk is inspectable in rendered pixels, the shared project and proof revision are recorded, and the `artifact-preview` completion criterion is satisfied for `SCENES.preview.html` and any `NARRATION.preview.html` refreshed by this stage.
