---
name: to-video
description: Use when approved video-planning artifacts must be handed to HyperFrames for production, with optional ListenHub narration.
---

# To video

Hand approved planning to HyperFrames. HyperFrames owns animatic or review passes, timing, media assembly, animation, verification, approval, and rendering.

## Process

1. Confirm `BEATS.md`, `NARRATION.md`, `SCENES.md`, and `STORYBOARD.md` agree on stable beat and narration IDs. Recompute every artifact digest and confirm each immediate child records the current parent digest: article → beats → narration → scenes → storyboard, with the storyboard also matching its narration source. For content-driven work, also confirm approval digests match and lineage reaches an approved `content/ARTICLE.md` and an approved `content/TOPIC.md` when that contract exists. Return a conflict, digest mismatch, or stale approval to the skill that owns that artifact.
2. Load `/hyperframes`, let it select the workflow, then read that workflow's current route contract. Carry presentation as an input; do not infer a workflow from `faceless` alone.
3. Give the selected workflow the four planning artifacts, applicable content artifacts, source material, design constraints, presentation choice, collaboration preference, and voice choice. Treat them as project truth while allowing HyperFrames' own review loop to revise them. A material content revision returns to the owning content artifact and its approval gate before it propagates forward.
   - For terminal or coding shots, read [`../record-terminal/references/terminal-presentation.md`](../record-terminal/references/terminal-presentation.md) and carry its selected capture or replay treatment, evidence, and verification contract into production.
4. When the user chooses ListenHub, wait for the selected HyperFrames workflow's voice gate, then use `/listenhub-tts` on that narration version. Give its audio and SRT back through `/media-use`. If the workflow later revises the narration, treat those outputs as stale and regenerate them at the next voice gate.
5. Leave production inside the selected HyperFrames workflow through its own completion criterion.

The handoff is complete when HyperFrames has accepted the planning artifacts and any requested ListenHub outputs into its project state.
