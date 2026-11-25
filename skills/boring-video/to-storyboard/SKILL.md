---
name: to-storyboard
description: Use when approved HyperFrames scenes need an assembly plan for scene placement, cuts, and boundary transitions.
---

# To storyboard

Turn `SCENES.md` and `NARRATION.md` into the canonical HyperFrames `STORYBOARD.md` assembly plan.

## Process

1. Recompute beats, narration, and scenes digests; require matching files and parent lineage. Read [the shared project contract](../boring-video/references/hyperframes-review-project.md), require its scene review gate, and open the recorded project revision. Load `/hyperframes` and its current `references/storyboard-format.md`; that contract owns storyboard fields and parser behavior.
2. Map approved scenes to canonical frames under the shared contract's assembly boundary. In each frame's narrative body, reference the scene HTML and review decision, then inherit its local shot moments: stable ID, offset, state change, camera/attention path, narration anchor or `silent`, and handoff. Translate local offsets when the canonical format requires frame/global time.
3. Plan scene order, placement, cuts, transition durations/overlaps, and required handles. For screen sequences, carry [their viewing-contract](../to-scenes/references/screen-evidence.md) dependencies and readable holds into the plan. Preserve demonstrations' truth modes and code labels; inherit terminal replay evidence from `/record-terminal`. Internal changes return to `/to-scenes`.
4. Add `boring_source_scenes_digest`, `boring_source_narration_digest`, `boring_hyperframes_project`, `boring_hyperframes_revision`, and `boring_artifact_digest` once in global YAML frontmatter, where the canonical parser preserves them under `globals.extra`. Frame extras such as `boring_scene_id` stay on frames. Use canonical fields for meanings they already represent.
5. Keep new assembly frames at `status: outline`; existing scene HTML alone does not certify a canonical frame `src`. Leave scene compositions unchanged. Audit narration coverage, inherited timing, transition handles, continuity, evidence labels, and total duration before handing the plan to `/to-video` for integration.

Compute `boring_artifact_digest` as SHA-256 of the complete storyboard after removing only that digest line. Present the current file under [Markdown review](../boring-video/references/markdown-review.md).

Complete when every approved scene and narration anchor is mapped, each boundary transition fits declared handles, the canonical frame schema and lineage checks pass, and the current Markdown is presented. Planned joins await assembled playback; passed scene review remains the evidence for internal shots.
