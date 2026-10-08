# HyperFrames review project

Use one HyperFrames project from scene direction through final production. Create or select it during `/to-scenes`, record its path and revision in the planning artifacts, and evolve that same project in `/to-storyboard` and `/to-video`. A stage may simplify fidelity, but it does not rebuild an approved visual language in a second project.

## Shared project state

Keep a review manifest in project state with:

- project path and revision;
- delivery aspect ratio and resolution;
- source artifact digests;
- font sources and loaded families/weights;
- scene-to-frame or scene-to-composition mapping;
- proof and animatic artifact paths, durations, reviewed risks, and decisions;
- evidence-manifest paths for terminal, code, data, or other factual replays.

A source or design change that invalidates a reviewed image or timeline marks the affected proof stale. Re-render the smallest affected scope and update its decision record.

## Font contract

Unless project design truth overrides the typography, use these roles:

| Role | Family | Weights |
| --- | --- | --- |
| Chinese body and labels | `Noto Sans SC` | 400, 700, 800, 900 as used |
| English interface headings | `Montserrat` | 700 |
| Code, commands, terminal output | `JetBrains Mono` | 400, 700 |

Define shared CSS tokens rather than component-local stacks:

```css
:root {
  --font-zh: "Noto Sans SC", sans-serif;
  --font-en: Montserrat, "Noto Sans SC", sans-serif;
  --font-code: "JetBrains Mono", "Noto Sans SC", monospace;
}

html { font-synthesis: none; }
```

Chinese glyphs keep an explicit `Noto Sans SC` fallback even inside code or terminal surfaces. A brand family may replace the defaults; retain a verified Chinese fallback and disable synthetic faces.

Before review, inspect rendered output and the browser's resolved font for representative Chinese, Latin, code, and emphasized text. Confirm every used family and weight is actually loaded, not merely named in CSS, and verify monospace alignment at delivery resolution.

## Scene direction board

During `/to-scenes`, build near-final 16:9 pixels in the shared project. Each scene gets the smallest evidence set that exposes its visual decision:

- one Hero frame when composition and state are stable;
- Start/Hero/End when entry, transformation, exit, or continuity changes the judgment;
- another small set only when a declared risk cannot be judged from those states.

Use real fonts, near-final copy, real source code, and evidence-backed terminal or data surfaces. A generic placeholder box cannot approve a scene whose risk is typography, code, terminal fidelity, density, or component behavior. The board may remain low fidelity in non-risk areas.

`SCENES.preview.html` is the review surface for these rendered states. It pairs each scene's concise direction and risks with inspectable delivery-aspect-ratio frames from the shared project. Embed local renders as data URLs when a self-contained preview is required. Prose alone does not complete this stage.

## Storyboard animatic

During `/to-storyboard`, extend the same project into a complete, playable, seekable low-fidelity animatic. It represents real scene duration and the observable start, action, hold, and end states, including:

- entrances, exits, holds, camera moves, and transitions;
- deterministic typing, code highlighting, terminal output, scrolling, and caret behavior;
- narration timing or a provisional timing track;
- continuity at every cut and transition boundary.

All time-dependent state derives from composition time. Scrubbing to the same timestamp must reproduce the same frame without accumulated DOM state or live timers. Placeholder art is acceptable only where it preserves composition, action, and timing; placeholder timing is not.

`STORYBOARD.preview.html` is the animatic review surface. It must let the reviewer play and seek the shared-project timeline and inspect representative boundary states. A prose shot list may accompany it but cannot substitute for it.

## Production continuation

During `/to-video`, open the project recorded by the planning artifacts and continue from its reviewed revision. Promote low-fidelity assets and repeated motion systems in place. Preserve approved layout, typography, camera logic, transitions, timing, and evidence lineage unless a recorded revision reopens the relevant gate.
