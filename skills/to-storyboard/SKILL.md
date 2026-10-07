---
name: to-storyboard
description: Use when complete, lineage-valid video scenes need to be translated into shots, key frames, compositions, camera moves, transitions, and timing estimates before production.
---

# To storyboard

Turn `SCENES.md` and `NARRATION.md` into HyperFrames `STORYBOARD.md`. Scenes define events; the storyboard defines how the viewer sees them.

## Process

1. Recompute the beats, narration, and scenes artifact digests. Continue only when `NARRATION.md` points to the current beats and `SCENES.md` points to the current beats and narration, with every stored artifact digest matching its file. Load `/hyperframes`, then read its current `references/storyboard-format.md`. That canonical contract is authoritative for `STORYBOARD.md`.
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
7. Audit the sequence: every narration anchor is covered by one or more shot moments, intentionally silent moments carry no anchor, frame boundaries follow the rules above, the action is legible without reading the narration, and estimated duration accommodates both speech and action.
8. Read [`../artifact-preview/references/visual-review-gates.md`](../artifact-preview/references/visual-review-gates.md). Carry forward the visual risks and identify the smallest representative shots that can prove the visual grammar, typography, density, terminal/editor treatment, camera behavior, and transitions before full production.

**REQUIRED SUB-SKILL:** Use `artifact-preview` for `STORYBOARD.md` before declaring it complete and after every later source change. Present it as a **shot-plan review**, not as evidence of final visuals. Its completion approves buildability, coverage, and timing intent only; visual approval happens through the pixel and motion gates after handoff.

The storyboard is complete when every frame is an independently buildable block, its shot moments fully describe the scene event, every transition connects actual end and start states, and the `artifact-preview` completion criterion is satisfied for `STORYBOARD.preview.html`. HyperFrames owns sketching and storyboard review after handoff.
