# Scene patterns

Select a pattern by viewer question in the [gallery](../assets/scene-patterns/gallery.html). Patterns define content and spatial structure; project `FRAME.md` controls appearance. Existing [scene presets](scene-presets.md) remain authoritative for comparison, diagram, and card bounds and timing.

## Use

1. Choose a pattern and theme, edit its case props, and inspect relevant times. Cases use fictional data and original SVGs; replace them with project content and evidence.
2. Copy the selection into the project's scene record: ID, revision, props, theme, duration, ratio, and background. Preserve its implementation and media files so the selection remains reproducible.
3. Implement the event in the shared HyperFrames project. Align reveals and holds with narration; complete [scene review](../../boring-video/references/hyperframes-review-project.md) using the actual content.

The gallery renders opaque 16:9 still images and staged reveals. It is not a HyperFrames composition. Catalog `direction` is production guidance, not a list of implemented effects. Video, audio, camera moves, exits, and other ratios require project implementation and review. The eight-second preview does not set production duration.

## Renderer

Load `patterns.css`, `catalog.js`, and `patterns.js`. Props shallowly override the selected case; replacing an array replaces all its items. Media paths resolve from the hosting page.

```js
const scene = ScenePatterns.render(element, 'metric-scorecard', {
  title: '本次测试结果', source: '项目证据 / 版本',
  columns: ['方案 A', '方案 B'],
  metrics: [{label: '耗时', a: '12', b: '24', unit: '分钟'}]
}, {theme: 'blockframe', time: 4});
scene.setTime(1.5); // local seconds; direct and backward seeking
```

## Reference analysis

Sample the full video, then inspect adjacent states around distinct layouts or changes. Separate packaging from embedded demos and overlays. Record timestamps, frames, observations, and source attribution outside the distributable library. Static frames establish composition; motion claims require adjacent states. Build library examples with independent content and assets.

## Maintain

[catalog.json](../assets/scene-patterns/catalog.json) owns pattern fields, case props, and shared preview settings. After editing it, run `python3 scripts/build_scene_catalog.py` from `to-scenes`; `--check` detects a stale generated `catalog.js`.

Run `node scripts/verify_scene_gallery.cjs` with Playwright installed, or pass its absolute module path. It checks default-case image loading, layout bounds, seeking, and gallery interactions across all themes.

A new pattern is ready when its viewer question, slots, constraints, independent case, theme variants, and gallery entry are present and inspected. Record findings separately from catalog metadata. Production scenes still pass the shared scene-review gate.
