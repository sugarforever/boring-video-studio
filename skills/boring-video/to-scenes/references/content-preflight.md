# Content preflight

Before generating a template scene, validate its proposed selection:

```sh
node scripts/validate_scene_selection.cjs selection.json [playwright-module-path]
```

Run from `to-scenes`. The JSON file contains `id`, `revision`, `props`, `theme`, and `mode`. Exit 0 passes; exit 2 returns content issues and proposals; exit 1 indicates a tool or input-file error. Preflight creates no preview. Browser callers use `ScenePatterns.validate(id, props, options)`; `render` also rejects failed selections before changing the host.

For a failed selection:

1. Show each affected field, actual amount, budget, and proposed adjustment. Recommend a choice that preserves the scene’s point: fewer items, multiple scenes, a shorter focus path, a labeled excerpt, or a different layout.
2. Obtain the user’s choice before changing content. Record the approved adjustment in the scene record and save revised display data separately from the original evidence. Proposals are suggestions, not applied edits or approval tokens.
3. Validate the revision. Generate only when `ok` is true; approval alone does not bypass a failed budget. A layout change requires updated project template rules and another validation pass.

Pattern `validation` records in `catalog.json` own the budgets. They cover title/copy width, array counts and labels, source lines and line width, filenames, parsed focus values, and applicable density rules. Display columns count wide characters as two, combining marks as zero, and tabs to the next eight-column stop. Parse, path, index, and numeric-scale checks also apply.

For code, JSON/XML, or terminal excerpts, follow [source panels](source-panels.md) to preserve syntax and mark omitted content.

The gallery separates **校验待用数据** from **确认数据并生成预览**. Rejected drafts retain the last valid preview and cannot be exported. Passing conservative budgets still requires full-size visual review with project fonts and content.
