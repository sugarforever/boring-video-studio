---
name: to-storyboard
description: Use when complete, lineage-valid video scenes need to be translated into HyperFrames frame boundaries, shot moments, transitions, and timing before production.
---

# To storyboard

Turn `SCENES.md` and `NARRATION.md` into HyperFrames `STORYBOARD.md`. Scenes define events; the storyboard defines how the viewer sees them.

## Process

1. Recompute the beats, narration, and scenes artifact digests. Continue only when `NARRATION.md` points to the current beats and `SCENES.md` points to the current beats and narration, with every stored artifact digest matching its file. Open the HyperFrames project and revision recorded by `SCENES.md`, then load `/hyperframes` and read its current `references/storyboard-format.md`. That canonical contract is authoritative for the single current `STORYBOARD.md`.
2. Choose the HyperFrames frame boundary:
   - start a new frame for a hard edit, independent transition, new visual world, materially different media source, or independently buildable unit;
   - keep continuous camera movement and shared object state in one frame, describing its internal shot moments.
3. Treat each HyperFrames frame as one buildable block. Within its narrative body, write an ordered `Shot moments` list at changes in viewpoint, shot scale, subject action, or information focus. Each moment declares:
   - moment ID and approximate offset;
   - initial state → action → final state;
   - camera and attention path;
   - narration anchors, or `silent`;
   - handoff to the next moment or frame.
4. Use canonical metadata wherever the current contract already carries the meaning. Put the document-level `boring_source_scenes_digest`, `boring_source_narration_digest`, `boring_hyperframes_project`, `boring_hyperframes_revision`, and `boring_artifact_digest` exactly once as unknown keys in the global YAML frontmatter, where the canonical parser preserves them under `globals.extra`. Compute `boring_artifact_digest` as SHA-256 of the complete storyboard file after removing only that single digest line. Frame-level workflow extras, such as `boring_scene_id`, remain on their frames and never carry document digests or project identity.
5. Use the scene's world, hero, event, continuity, rhythm, and feasibility as constraints. Preserve the cognitive job from `BEATS.md`.
   - When a frame shows terminal-hosted code entry, shell commands, CLI output, database output, or a TUI, **REQUIRED SUB-SKILL:** Use `record-terminal`. Carry its evidence-backed, seek-safe replay contract and selected visual treatment into the shot moments.
6. Treat canonical HyperFrames fields as authoritative. A `boring_*` extra supplements the contract; it never restates a canonical field.
7. Leave every new frame at `status: outline`; planning does not create or claim an implemented `src`. Reference relevant scene proofs when a frame's composition depends on an already reviewed visual decision. HyperFrames production owns composition HTML and advances frames to `built` or `animated`.
8. Audit the sequence: every narration anchor is covered by one or more shot moments, intentionally silent moments carry no anchor, frame boundaries follow the rules above, the planned action is legible without reading the narration, and duration allocations fit the target. Treat timing as a plan until HyperFrames Studio confirms it against the built timeline.
9. Carry forward the rendered-evidence decisions recorded by `SCENES.md` and project state. Record the current project identity and revision for continuity, but do not mutate the project or build an animatic in this stage.

Before presenting `STORYBOARD.md` or any later revision, follow [`../boring-video/references/markdown-review.md`](../boring-video/references/markdown-review.md). Review frame boundaries, shot moments, narration mapping, planned durations, and transitions in the authoritative Markdown. HyperFrames Studio later owns playable motion, timing, and transition review.

The storyboard is complete when every frame is an independently buildable `outline`, its shot moments fully describe the scene event, every narration anchor and planned transition is accounted for, the shared project identity and source revision are recorded, and the Markdown review completion criterion is satisfied. No playable animatic is required before `/to-video` begins production.
