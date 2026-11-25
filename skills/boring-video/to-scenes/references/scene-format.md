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
hyperframes_revision: Revision containing the current scene HTML and review decisions
html_review: Path or URL to the working scene review entry point
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
- preset: Optional mapping with `family` and `mode` from [`scene-presets.md`](scene-presets.md), for example `{family: matched-comparison, mode: before-after}`; omit for custom scenes. Include the selected family’s required evidence labels and theme tokens in this mapping.
- composition: Production HTML path and scene-specific playback link
- narration: Stable narration IDs and exact corresponding text, with audio source and cue mapping
- review: Review record link, project revision, reviewed intervals, reviewer, and pending | changes_requested | passed status
- content_findings: Content suitability, accuracy, redundancy, and unresolved decisions
- visual_findings: Scene design, readability, cue alignment, and unresolved decisions
- remaining_work: Finishing work deferred to production and its effect on review
- proof: Optional supplemental images or media with render IDs and state names
- visual_risks: Typography, density, evidence surface, motion, continuity, or other risks playback and supplemental evidence resolve

For screen evidence or explanatory visual sequences, read [`screen-evidence.md`](screen-evidence.md) and add a `screen_contract`:

- `viewer_question`: What the viewer should understand or be able to repeat.
- `cue_evidence`: Narration anchor → exact source state or explanatory relationship → visible interval.
- `temporal_structure`: Causal, operational, comparison, concurrent, or inspection structure, with meaningful state dependencies and what remains visible. Storyboard shot moments supply numeric timing under the referenced contract.
- `framing`: Full view, detail, inset, or diagram, with the inspection purpose of each crop or move.
- `setup_delta`: For configuration or repeated startup, the normal path, observed restriction, and behavior-changing differences from the earlier setup; omit when irrelevant.

When the scene contains a demonstration, add a `demo_contract`:

- `content`: The exact ordered actions, inputs, outputs, states, and stopping point the viewer will see.
- `truth_mode`: `real session` for captured footage of the actual interaction; `evidence replay` for a reconstruction backed by retained execution or session evidence; or `instructional reconstruction` for a teaching-oriented sequence that is not represented as an actual session.
- `code_surfaces`: For every code view, visibly label it as `real code`, `real code excerpt`, or `illustrative code`. An excerpt or illustration must not be presented as unmodified real code.

Two or three sentences describing what the viewer experiences.

Link each scene to the HTML review entry point and its persisted review record. For supplemental proofs, use Markdown image syntax or supported media links with render ID, state, and current project revision. The HTML loads the same production compositions; `SCENES.md` owns scene intent and decision references.
```

Compute `artifact_digest` as SHA-256 of the complete scenes file after removing only the `artifact_digest:` line.

## Scene audit

- Each scene contains an event with a visible state change or a declared result/topology inspection whose readable hold serves the viewer question.
- The hero, world, and event express the beat rather than decorate it.
- Adjacent scenes vary at least two of world, scale, camera behavior, action, and rhythm where the sequence permits; record intentional matched views or inspection holds instead of adding cosmetic motion.
- The full film includes establishing, medium, and detail scales where the content supports them.
- Continuity fields form an unbroken chain or name an intentional cut.
- Feasibility identifies expensive or uncertain treatments before storyboarding.
- Every scene has playable production HTML and corresponding narration, with current passed joint review recorded under [the shared review contract](../../boring-video/references/hyperframes-review-project.md).
- Adjacent scenes and the assembled sequence have been played to check repetition, continuity, and rhythm; unresolved content, visual, or spoken pacing findings keep the review open.
- Supplemental stills expose named risks without substituting for playback.
- Typography, code, terminal, and component risks use real or near-final material rather than generic placeholders.
- Screen scenes satisfy the viewing contract in `screen-evidence.md`; their proof set exposes the stated framing, evidence, and reveal risks.
- Any scene declaring a `preset` from `scene-presets.md` satisfies that preset's selection condition, declared mode, input bounds, readable-hold timing, and fallback rules without weakening `screen-evidence.md` or `demo_contract` truthfulness.
- Every demonstration specifies its complete visible content, truth mode, and code-surface labels; its presentation does not imply stronger evidence than the declared mode.
- Every beat ID appears in at least one scene and every narration anchor remains owned by its beat.
