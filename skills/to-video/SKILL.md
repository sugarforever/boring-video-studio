---
name: to-video
description: Use when approved video-planning artifacts must be handed to HyperFrames for production, with optional ListenHub narration.
---

# To video

Continue the approved HyperFrames review project into final production. Preserve reviewed pixels, timing, motion grammar, and evidence lineage while replacing low-fidelity material with production assets.

## Process

1. Confirm `BEATS.md`, `NARRATION.md`, `SCENES.md`, and `STORYBOARD.md` agree on stable beat and narration IDs. Recompute every artifact digest and confirm each immediate child records the current parent digest: article → beats → narration → scenes → storyboard, with the storyboard also matching its narration source. For content-driven work, also confirm approval digests match and lineage reaches an approved `content/ARTICLE.md` and an approved `content/TOPIC.md` when that contract exists. Return a conflict, digest mismatch, or stale approval to the skill that owns that artifact.
2. Open the exact project and reviewed revision recorded by `SCENES.md`, `STORYBOARD.md`, and project state; fail back to the owning stage if they name different projects or stale revisions. Load `/hyperframes`, let it select the workflow, then read that workflow's current route contract. Carry presentation as an input; do not infer a workflow from `faceless` alone.
3. Give the selected workflow the four planning artifacts, applicable content artifacts, source material, design constraints, presentation choice, collaboration preference, and voice choice. Continue implementation in that project instead of re-creating the reviewed direction or animatic. Treat the artifacts and recorded review decisions as project truth while allowing explicit revisions through HyperFrames' review loop. A material content revision returns to the owning content artifact and its approval gate before it propagates forward.
   - For terminal-hosted coding, shell, CLI, database, or TUI shots, **REQUIRED SUB-SKILL:** Use `record-terminal` and carry its evidence-backed, seek-safe replay, selected visual treatment, and verification contract into production.
   - Verify that direction-board and animatic decisions refer to the current project revision, and reopen only gates invalidated by later changes.
4. When the user chooses ListenHub, wait for the selected HyperFrames workflow's voice gate, then use `/listenhub-tts` on that narration version. Give its audio and SRT back through `/media-use`. If the workflow later revises the narration, treat those outputs as stale and regenerate them at the next voice gate.
5. Leave production inside the selected HyperFrames workflow through its own completion criterion.

The handoff is complete when HyperFrames has opened the reviewed project revision and accepted the planning artifacts and any requested ListenHub outputs into its state. Production starts from the approved direction board and full animatic; it does not restart their implementation.
