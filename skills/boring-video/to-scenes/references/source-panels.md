# Source panels

Choose the viewer's task, then edit the selected case's `data`:

| Pattern | Use | Additional fields |
|---|---|---|
| `terminal-session` | Command and output in one terminal window | — |
| `code-block` | Explain a code excerpt | `language` |
| `json-data` | Locate a JSON field and value | `focusPath`: array of keys or indices |
| `xml-data` | Locate an XML element and text | `focusTag`: first matching element |
| `vscode-editor` | Show project, active file, and code | `language`, `files`: up to five filenames including the active file |

All use `source`, `fileName`, and a one-based `highlightLine`. Edit source through `data.source`; `copy` changes surrounding labels. Whitespace is preserved and line endings normalize to LF. `code-block` and `vscode-editor` accept `language: javascript | json | xml | shell | text`; other languages use `text`. Coloring does not execute or compile code. JSON must parse; XML must be well formed.

Use the selected pattern’s `validation` budgets; terminal, standalone blocks, and editor panes have different capacities. Use a plain-text code block for an explicitly labeled raw fragment; ellipses in a sidebar are presentation text, not parsed JSON/XML. After changing source, update the highlight and JSON/XML focus to match. Their positions are selected independently.

After user approval, `data.focusPreview` can show a prefix of the derived value ending in `…` or `...`. It is labeled “节选”; full source stays intact. It still passes the sidebar budget and prefix check.

Example JSON data override:

```js
data: {
  source: JSON.stringify({sensor: {moisture: 41}}, null, 2),
  fileName: 'garden.json', highlightLine: 3,
  focusPath: ['sensor', 'moisture']
}
```

`terminal-session` is an annotated transcript; `terminal-evidence` pairs output with a summary. Both previews are illustrative. Use `/record-terminal` for actual terminal execution. The VS Code layout is an editor illustration; use captured footage or a project replay to show real interactions. Retain the truth label and source attribution appropriate to the content.
