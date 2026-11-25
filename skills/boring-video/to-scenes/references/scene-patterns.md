# Scene patterns

Use for chronology, comparisons, evidence, evaluations, and conclusions, or when studying a reference video's reusable structure. Select by the viewer's question and the visible event; then apply the project's design truth. A pattern supplies content slots, spatial relationships, reveal order, and constraints. A frame preset supplies type, palette, borders, depth, and geometry. Their combination becomes a specific scene in `SCENES.md`.

## Select and adapt

1. Read the [catalog](../assets/scene-patterns/catalog.json). Match the viewer question, then check required inputs and constraints. Combine or depart from patterns when the explanation requires it; variety comes from distinct events, not cycling layouts.
2. Open the [gallery](../assets/scene-patterns/gallery.html), filter by purpose, choose a theme, edit props, and inspect relevant times. The bundled adapters cover BlockFrame, Swiss Minimalism, Raycast Dark, and Claude Warm. They are review scaffolds based on existing FRAME contracts; the actual project FRAME.md remains authoritative. Other presets require an adapter and visual inspection, not a renamed theme.
3. Copy the selection into the project's component/scene record with ID, revision, props, theme, ratio, and duration. Preserve the source implementation or its digest so later updates cannot change a prior export. Use the review record required by [the shared project contract](../../boring-video/references/hyperframes-review-project.md).
4. The gallery uses original fictional case studies and locally drawn SVG assets. Keep reference-video identities, timestamps, frames, and links outside the distributable library. Replace fictional copy, numbers, illustrations, and source labels with the project's actual evidence. Map reveal steps to narration cues. Default eight-second timing demonstrates order only; it does not establish a readable duration for the project's copy.
5. Implement the selected event in the existing HyperFrames project, using the current HyperFrames composition contract. Carry fonts and tokens into project assets. Record inspected start/hero/end and reveal states, overflow checks, actual-content proofs, and limitations. Follow `screen-evidence.md` for evidence framing.

Gallery renderer API (same implementation drives playback and seeking):

```js
const scene = ScenePatterns.render(element, 'metric-scorecard', {
  title: '本次测试结果', source: '项目证据路径 / 版本',
  columns: ['方案 A', '方案 B'],
  metrics: [{label: '耗时', a: '12', b: '24', unit: '分钟'}]
}, {theme: 'blockframe', time: 4});
scene.setTime(1.5); // explicit local seconds; direct and backward seek are supported
```

This is a standalone HTML review library, not a registered HyperFrames composition. Its renderer shows staged reveals; `motion` in the catalog describes the fuller event the project must implement, including evidence focus, camera moves, real recordings, and exits. Bundled examples use fictional data and original SVG illustrations. Media inputs currently render still images; video, audio, terminal replays, and synchronized comparison playback belong in the production project. The gallery's outer playback uses animation frames; scene state itself depends only on props and explicit time. All bundled examples are opaque 16:9. Recompose and inspect separately for other ratios or alpha delivery.

## Contract ownership

The catalog owns pattern selection questions, example props, and content constraints. Existing [scene presets](scene-presets.md) own bounds and timing for relationship diagrams, matched comparisons, and ordered/grouped cards. When a pattern uses one of those structures, preserve its preset mode and constraints. A price pair supplies case content for a comparison; it does not establish a second comparison contract.

The gallery owns reusable design inspection. The shared project contract owns actual scene completion, narration alignment, media, and assembled review. A gallery preview cannot pass a project's scene review gate.

A presenter inset, source label, highlighted word, and progress marker are composable overlays. Product demos are content inside `demo-stage`; their visual identity does not become the video's packaging.

## Study another reference

Sample across the full duration, record exact timestamps, then inspect adjacent states for distinct layouts and changes. A regular sample is a discovery pass and may miss short shots; inspect denser intervals around unclear scenes. Classify observed content before naming reusable patterns. Separate outer packaging from embedded demos and inherited source UI. Store source URL, metadata, sampling method, representative frames, timestamp-to-pattern mapping, and observations in a study outside the distributable skill. Keep third-party frames as attributed study evidence; templates use original geometry and project-owned media.

Only claim motion that adjacent inspected frames support. A static frame establishes composition, not entrance direction or transition speed. Distinguish observed structure from proposed adaptation.

## Maintain and verify

The canonical records live in `catalog.json`. After editing them, run `python3 scripts/build_scene_catalog.py` from the `to-scenes` directory; `--check` verifies the generated file-compatible `catalog.js` has not drifted.

Run `node scripts/verify_scene_gallery.cjs` from the `to-scenes` directory with Playwright available. If it is installed elsewhere, pass its absolute module path as the first argument. This checks all 80 theme variants for default-content overflow, loaded images, deterministic seeking, and gallery interactions. It does not establish actual-content or assembled-video acceptance.

## Completion

A pattern addition has a distinct viewer question, explicit slots and constraints in the catalog, an original example, theme-token mapping, and a reachable gallery entry. If derived from a reference, retain observations separately from the distributable library. Inspect all advertised theme variants and direct/backward seeking, record the result, and keep scaffolds distinct from production-accepted scenes. Final scenes still satisfy the full `to-scenes` completion criteria.
