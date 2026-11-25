---
name: to-storyboard
description: Use when complete, lineage-valid video scenes need to be translated into HyperFrames frame boundaries, shot moments, transitions, and timing before production.
---

# To storyboard

Turn `SCENES.md` and `NARRATION.md` into HyperFrames `STORYBOARD.md`. Scenes already contain the finished shots, audio, and local timing. The storyboard defines how those finished scenes are assembled.

## Process

1. Recompute the beats, narration, and scenes artifact digests. Continue only when `NARRATION.md` points to the current beats and `SCENES.md` points to the current beats and narration, with every stored artifact digest matching its file. Require current passed scene and assembled-sequence joint reviews in the project manifest; return missing or stale decisions to `/to-scenes`. Open the HyperFrames project and revision recorded by `SCENES.md`, then load `/hyperframes` and read its current `references/storyboard-format.md`. That canonical contract is authoritative for the single current `STORYBOARD.md`.
2. Map finished scenes to canonical HyperFrames frames, preserving their approved source files and durations. Keep continuous scene-local camera movement and shared state together. Record placement, order, hard cuts, and boundary transitions; a mapping that requires changing a scene returns to `/to-scenes`.
3. For each frame, reference its approved scene composition and copy the existing local `Shot moments` into its narrative body. Preserve the reviewed timings rather than designing new internal shots. Each inherited moment declares:
   - moment ID and approved scene-local offset, translated to the frame/global offset when required;
   - initial state → action → final state;
   - camera and attention path;
   - narration anchors, or `silent`;
   - handoff to the next moment or frame.
   For screen evidence or explanatory visual sequences, read [`../to-scenes/references/screen-evidence.md`](../to-scenes/references/screen-evidence.md). Carry the approved numeric state intervals, dependencies, narration cues, and readable holds into these shot moments, including deliberate simultaneous views. Budget transition overlaps against declared scene handles while preserving the approved operation and narration. A required internal timing or content tradeoff returns to `/to-scenes`.
4. Use canonical metadata wherever the current contract already carries the meaning. Put the document-level `boring_source_scenes_digest`, `boring_source_narration_digest`, `boring_hyperframes_project`, `boring_hyperframes_revision`, and `boring_artifact_digest` exactly once as unknown keys in the global YAML frontmatter, where the canonical parser preserves them under `globals.extra`. Compute `boring_artifact_digest` as SHA-256 of the complete storyboard file after removing only that single digest line. Frame-level workflow extras, such as `boring_scene_id`, remain on their frames and never carry document digests or project identity.
5. Use the scene's world, hero, event, continuity, rhythm, and feasibility as constraints. Preserve the cognitive job from `BEATS.md`.
   - Preserve each demonstration's exact content, truth mode, and visible code labels in the relevant shot moments. Do not upgrade an instructional reconstruction into apparent evidence.
   - When a frame shows terminal-hosted code entry, shell commands, CLI output, database output, or a TUI, **REQUIRED SUB-SKILL:** Use `record-terminal`. Carry its evidence-backed, seek-safe replay contract and selected visual treatment into the shot moments.
6. Treat canonical HyperFrames fields as authoritative. A `boring_*` extra supplements the contract; it never restates a canonical field.
7. Leave every new storyboard frame at `status: outline`; planning does not claim an implemented canonical `src`. Reference the reviewed scene HTML paths and decisions in each frame's narrative body so production mounts those finished compositions unchanged. New boundary transitions may be outlined here; existing scene HTML is already implemented, and an `outline` assembly frame does not authorize rebuilding it. HyperFrames production integrates them into canonical frames and advances statuses only after its checks pass.
8. Audit the sequence: every narration anchor is covered by one or more shot moments, the visual state supports the spoken idea at that moment, intentionally silent moments carry no anchor, frame boundaries follow the rules above, demonstrations preserve their declared truth and labels, and duration allocations fit the target. Screen-state holds and causal reveal intervals must be inspectable in the shot moments; resolve an insufficient budget before marking the plan complete. Preserve the approved local timing; only scene placement and boundary-transition timing are new plans to confirm against the assembled timeline. Return changes that invalidate joint scene review to `/to-scenes`.
9. Carry forward the rendered-evidence decisions recorded by `SCENES.md` and project state. Record the current project identity and revision for continuity, but do not mutate the project or build an animatic in this stage.

Before presenting `STORYBOARD.md` or any later revision, follow [`../boring-video/references/markdown-review.md`](../boring-video/references/markdown-review.md). Review frame boundaries, shot moments, narration mapping, planned durations, and transitions in the authoritative Markdown. Use the existing HTML scene review as evidence for inherited decisions; HyperFrames Studio later confirms the integrated timeline and new transition decisions.

The storyboard is complete when every frame is an independently buildable `outline`, its shot moments fully describe the scene event, every narration anchor and planned transition is accounted for, the shared project identity and source revision are recorded, and the Markdown review completion criterion is satisfied. The passed scene HTML review is required input; a separate storyboard animatic is not required.
