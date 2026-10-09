# `SCENES.md` format

```markdown
---
source_beats: BEATS.md
source_beats_digest: sha256:<BEATS artifact_digest>
source_narration: NARRATION.md
source_narration_digest: sha256:<NARRATION artifact_digest>
artifact_digest: sha256:<digest>
concept: One sentence naming the visual world
continuity: What carries through the whole film
hyperframes_project: Path to the shared review and production project
hyperframes_revision: Revision containing the current direction board
---

## Scene 01 — Title
- beats: B01
- purpose: The cognitive job inherited from BEATS.md
- world: The spatial environment and its depth
- hero: The concept given a body
- event: Initial state → action → changed state
- camera: Viewpoint, shot-scale progression, and movement logic
- focus: Light, contrast, depth, or motion that directs attention
- continuity_in: The object or motion received from the previous scene
- continuity_out: The object or motion handed to the next scene
- rhythm: Quick hit, development, hold, or release
- audio_intent: Narration emphasis and meaningful sound opportunity
- feasibility: Envelope class, named dependency, and fallback when required
- proof: Hero or Start/Hero/End render IDs, selected by what must be judged
- visual_risks: Typography, density, evidence surface, motion, continuity, or other risks the proof resolves

Two or three sentences describing what the viewer experiences.
```

Compute `artifact_digest` as SHA-256 of the complete scenes file after removing only the `artifact_digest:` line.

## Scene audit

- Each scene contains an event with a visible state change.
- The hero, world, and event express the beat rather than decorate it.
- Adjacent scenes vary at least two of world, scale, camera behavior, action, and rhythm.
- The full film includes establishing, medium, and detail scales where the content supports them.
- Continuity fields form an unbroken chain or name an intentional cut.
- Feasibility identifies expensive or uncertain treatments before storyboarding.
- Each proof set is the smallest set that exposes its scene's declared risks; scenes are not mechanically assigned three frames.
- Typography, code, terminal, and component risks use real or near-final material rather than generic placeholders.
- Every beat ID appears in at least one scene and every narration anchor remains owned by its beat.
