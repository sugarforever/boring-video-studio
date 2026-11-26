# Scene design revision 3 review

2026-11-26 · 20 patterns × four styles × light/dark = 160 combinations.

Claude Design produced the new compositions, original community/gardening cases, artwork, and theme tokens. The repository port uses local DOM rendering and bundled OFL fonts, without the design editor runtime. No reference-video content is included in the distributed library.

The sheets below contain all patterns, alphabetically by ID, read left to right. All eight sheets were visually inspected for hierarchy, focal color, composition, readable labels, and mode consistency. Complex charts and blind comparisons were also inspected at full frame size. Subdued backgrounds support saturated focal elements; Swiss keeps a single red accent, while Warm retains its parchment/coffee palette.

| Style | Light | Dark |
|---|---|---|
| BlockFrame | [20 scenes](blockframe-light.jpg) | [20 scenes](blockframe-dark.jpg) |
| Swiss | [20 scenes](swiss-minimalism-light.jpg) | [20 scenes](swiss-minimalism-dark.jpg) |
| Raycast | [20 scenes](raycast-dark-light.jpg) | [20 scenes](raycast-dark-dark.jpg) |
| Claude Warm | [20 scenes](claude-warm-light.jpg) | [20 scenes](claude-warm-dark.jpg) |

Port review corrected stale vote percentages/totals, elapsed totals, temperature endpoints, matrix scale labels, order-count scales, price break-even labels, and metric bars for increases. Price-card spacing and terminal whitespace were corrected to preserve the bottom 160px caption area. The light BlockFrame orange was slightly darkened for large-text contrast. Poster artwork retains its own palette across modes.

Verification: `verify_scene_gallery.cjs` passes all 160 combinations for text bounds including the caption reserve, resolved bindings, and deterministic seeking, plus changed-data labels, blind reveal, invalid scales, mode switching, and copy/title editing. `verify_scene_modes.cjs`, generated-bundle checks, and `git diff --check` pass. Automated text contrast checks found no failures outside poster text drawn over a separate dark backing shape; that text was checked visually.

Writing-for-agents review: revised only the on-demand scene-pattern reference, documented the revision-3 API and media slots, removed obsolete props, retained production review requirements, and kept case fields in the catalog as the source of truth. No blocking documentation issue remains after these corrections.

These checks cover the bundled 16:9 cases. Replaced copy, media, and data still require project scene review; the preview is not a completed HyperFrames composition.
