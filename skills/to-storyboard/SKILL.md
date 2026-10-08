---
name: to-storyboard
description: Use when complete, lineage-valid video scenes need to be translated into shots, key frames, compositions, camera moves, transitions, and timing estimates before production.
---

# To storyboard

Turn `SCENES.md` and `NARRATION.md` into HyperFrames `STORYBOARD.md`. Scenes define events; the storyboard defines how the viewer sees them.

## Process

1. Recompute the beats, narration, and scenes artifact digests. Continue only when `NARRATION.md` points to the current beats and `SCENES.md` points to the current beats and narration, with every stored artifact digest matching its file. Read [`../boring-video/references/hyperframes-review-project.md`](../boring-video/references/hyperframes-review-project.md), open the HyperFrames project and revision recorded by `SCENES.md`, then load `/hyperframes` and read its current `references/storyboard-format.md`. That canonical contract is authoritative for `STORYBOARD.md`.
2. Choose the HyperFrames frame boundary:
   - start a new frame for a hard edit, independent transition, new visual world, materially different media source, or independently buildable unit;
   - keep continuous camera movement and shared object state in one frame, describing its internal shot moments.
3. Treat each HyperFrames frame as one buildable block. Within its narrative body, write an ordered `Shot moments` list at changes in viewpoint, shot scale, subject action, or information focus. Each moment declares:
   - moment ID and approximate offset;
   - initial state → action → final state;
   - camera and attention path;
   - narration anchors, or `silent`;
   - handoff to the next moment or frame.
4. Use canonical metadata wherever the current contract already carries the meaning. Put the document-level `boring_source_scenes_digest`, `boring_source_narration_digest`, and `boring_artifact_digest` exactly once as unknown keys in the global YAML frontmatter, where the canonical parser preserves them under `globals.extra`. Compute `boring_artifact_digest` as SHA-256 of the complete storyboard file after removing only that single global frontmatter line. Frame-level workflow extras, such as `boring_scene_id`, remain on their frames and never carry document digests.
5. Use the scene's world, hero, event, continuity, rhythm, and feasibility as constraints. Preserve the cognitive job from `BEATS.md`.
   - When a frame shows code entry, shell commands, CLI output, database output, or a TUI, read [`../record-terminal/references/terminal-presentation.md`](../record-terminal/references/terminal-presentation.md). Plan an evidence-backed HTML replay using its default dark style unless the user chose another treatment, and make the treatment explicit in the shot moments.
6. Treat canonical HyperFrames fields as authoritative. A `boring_*` extra supplements the contract; it never restates a canonical field.
7. Extend that same project into a complete low-fidelity animatic. Implement real durations and deterministic, seek-safe start, action, hold, and end states for every frame, including typing, code highlighting, terminal output, camera behavior, and transitions named by the shot moments.
8. Audit the sequence: every narration anchor is covered by one or more shot moments, intentionally silent moments carry no anchor, frame boundaries follow the rules above, the action is legible without reading the narration, and playback confirms that speech, reading, typing, holds, and transitions fit their real durations.
9. Read [`../artifact-preview/references/visual-review-gates.md`](../artifact-preview/references/visual-review-gates.md). Carry forward direction-board decisions and review the complete animatic at its beginning, intermediate states, every transition boundary, and its end.

**REQUIRED SUB-SKILL:** Use `artifact-preview` for `STORYBOARD.md` before declaring it complete and after every later source change. Build `STORYBOARD.preview.html` as an **animatic review** backed by the same HyperFrames project: the reviewer must be able to play and seek the timeline and inspect transition states. Keep the shot plan alongside it for traceability.

The storyboard is complete when every frame is an independently buildable block, its shot moments fully describe the scene event, every transition connects actual end and start states in a playable and seekable full-length animatic, the shared project revision is recorded, and the `artifact-preview` completion criterion is satisfied for `STORYBOARD.preview.html`.
