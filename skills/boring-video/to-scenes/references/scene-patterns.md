# Scene patterns

Choose a pattern by viewer question in the [gallery](../assets/scene-patterns/gallery.html), then select a style and light/dark mode. Cases use fictional data and original artwork. Replace their content and conclusions with project evidence; `FRAME.md` controls production appearance. Existing [scene presets](scene-presets.md) retain their bounds and timing rules.

## Use

1. Edit `data` for chart values. Use **读取当前文字槽** to edit visible copy; keys remain the template’s original text. Inspect both the hidden and revealed states of blind comparisons.
2. Before scene generation, pass [content preflight](content-preflight.md). Resolve reported issues through its user-confirmation workflow.
3. Copy the selection into the scene record: ID, revision, props, theme, mode, duration, ratio, and background. Preserve the entire `scene-patterns` asset directory with the project. Revision 2 selections require their original implementation; revision 3 changes props and example content.
4. Implement the event in HyperFrames, align reveals and holds with narration, and pass [scene review](../../boring-video/references/hyperframes-review-project.md) with actual content.

All patterns support all four styles in both modes. The gallery provides opaque 1920×1080 scenes with deterministic staged reveals. Its eight-second preview is a design reference; production timing, voice, camera moves, exits, and other ratios require project implementation and review.

## Renderer

Load `patterns.css`, then `catalog.js`, `themes.js`, `layouts.js`, `validation.js`, and `patterns.js` in order.

```js
const scene = ScenePatterns.render(element, 'metric-scorecard', {
  title: '本次测试结果',
  copy: {'同为 100 单': '同为 50 单'},
  data: {metrics: [['总耗时', '分钟', 40, 30]]}
}, {theme: 'blockframe', mode: 'dark', time: 4});
scene.setTime(1.5); // local seconds; direct and backward seeking
```

`title` replaces the marked heading; `copy` replaces exact trimmed text nodes literally, preserving adjacent styled spans. `data` shallowly overrides the selected case; arrays replace all items. Keep chart labels, units, and narrative conclusions consistent with new values. `source` is selection metadata, not a visible citation; add citations through copy or the project layout.

Use the case's fields and item counts as the layout budget. Price pairs require two plans; blind pairs require two nonnegative vote counts with a positive total; test matrices require three values per row and `best: 'min' | 'max'`; temperature charts require twelve two-hour samples within `min`/`max`. Scale maxima are positive, and values stay within their declared scales. Longer copy or extra rows require layout review.

For source tables, demo stages, and presenters, `media.primary: {src, alt}` replaces the illustration with a contained image. Blind comparisons use `media.a` and `media.b`. Paths resolve from the hosting page.

For terminal, code, JSON, XML, or editor layouts, read [source panels](source-panels.md).

## Maintain

Edit `catalog.json`, `themes.js`, and `layouts/*.html`; run `python3 scripts/build_scene_catalog.py` from `to-scenes`. `--check` detects stale generated catalog and layout bundles.

Run `node scripts/verify_scene_gallery.cjs` with Playwright installed, or pass its absolute module path. It checks all style/mode combinations for text bounds, resolved bindings, and deterministic seeking, plus data/reveal/edit interactions. Visually inspect every combination and record findings separately from catalog metadata before accepting a redesign.

For reference analysis, sample the full video and adjacent states around distinct layouts. Keep source timestamps, frames, and attribution outside the distributable library; build independent cases and assets.
