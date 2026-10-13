# HyperFrames review project

Use one HyperFrames project from scene direction through final production. Create or select it during `/to-scenes`, record its path and revision in the planning artifacts, leave it unchanged while `/to-storyboard` plans frames, and continue it during `/to-video`. A stage does not rebuild an approved visual language in a second project.

## Shared project state

Keep a review manifest in project state with:

- project path and revision;
- delivery aspect ratio and resolution;
- source artifact digests;
- font sources and loaded families/weights;
- scene-to-frame or scene-to-composition mapping;
- rendered-proof paths, reviewed risks, and decisions;
- evidence-manifest paths for terminal, code, data, or other factual replays.

A source or design change that invalidates a reviewed image or timeline marks the affected proof stale. Re-render the smallest affected scope and update its decision record.

## Font contract

Unless project design truth overrides the typography, use these roles:

| Role | Family | Weights |
| --- | --- | --- |
| Chinese body and labels | `Noto Sans SC` | 400, 700, 800, 900 as used |
| English interface headings | `Montserrat` | 700 |

Define shared CSS tokens rather than component-local stacks:

```css
:root {
  --font-zh: "Noto Sans SC", sans-serif;
  --font-en: Montserrat, "Noto Sans SC", sans-serif;
}

html { font-synthesis: none; }
```

Chinese glyphs keep an explicit `Noto Sans SC` fallback. A brand family may replace the defaults; retain a verified Chinese fallback and disable synthetic faces. Terminal and full-screen TUI surfaces follow the independent font contract owned by `record-terminal`.

Before review, inspect rendered output and the browser's resolved font for representative Chinese, Latin, and emphasized text. Confirm every used family and weight is actually loaded, not merely named in CSS.

## Scene rendered evidence

During `/to-scenes`, build near-final 16:9 pixels in the shared project. Each scene gets the smallest evidence set that exposes its visual decision:

- one Hero frame when composition and state are stable;
- Start/Hero/End when entry, transformation, exit, or continuity changes the judgment;
- another small set only when a declared risk cannot be judged from those states.

Use real fonts, near-final copy, real source code, and evidence-backed terminal or data surfaces. A generic placeholder box cannot approve a scene whose risk is typography, code, terminal fidelity, density, or component behavior. The board may remain low fidelity in non-risk areas.

`SCENES.md` is the review surface for these rendered states. Pair each scene's concise direction and risks with Markdown image references to inspectable delivery-aspect-ratio frames from the shared project. Identify each render's state ID and project revision. Prose alone does not complete this stage.

## Storyboard plan

During `/to-storyboard`, translate scene decisions into HyperFrames-native frame boundaries and ordered shot moments in `STORYBOARD.md`. Plan:

- approximate offsets for entrances, actions, holds, camera moves, and transitions;
- narration anchors or intentionally silent moments;
- deterministic behavior required from typing, code, terminal, data, or UI evidence;
- continuity expectations at every cut and transition boundary.

Keep new frames at `status: outline`. This stage records the project and proof revision it inherits but does not implement composition HTML, mutate the project, or claim that planned timing has been played.

`STORYBOARD.md` is the review surface for the plan. HyperFrames production implements it, and HyperFrames Studio becomes the review surface for actual timing, motion, transitions, and scrubbing after the composition exists.

## Production continuation

During `/to-video`, open the project recorded by the planning artifacts and continue from its reviewed revision. Build the canonical storyboard's `outline` frames, advance their statuses as the canonical HyperFrames contract permits, and use Studio for playable review. Preserve approved layout, typography, camera logic, planned transitions, and evidence lineage unless a recorded revision reopens the relevant gate.
