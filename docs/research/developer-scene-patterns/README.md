# Developer scene patterns

Five additions: `terminal-session`, `code-block`, `json-data`, `xml-data`, and `vscode-editor`. The library now has 25 patterns and 200 style/mode combinations. Existing `terminal-evidence` remains an output-summary layout.

Each sheet shows Terminal, code, JSON, XML, and VS Code in reading order; the sixth cell is blank. All 40 new variants were visually inspected, with representative frames checked at full size. They extend the existing four-theme design system; these additions were implemented locally.

| Style | Light | Dark |
|---|---|---|
| BlockFrame | [Preview](blockframe-light.jpg) | [Preview](blockframe-dark.jpg) |
| Swiss | [Preview](swiss-minimalism-light.jpg) | [Preview](swiss-minimalism-dark.jpg) |
| Raycast | [Preview](raycast-dark-light.jpg) | [Preview](raycast-dark-dark.jpg) |
| Claude Warm | [Preview](claude-warm-light.jpg) | [Preview](claude-warm-dark.jpg) |

Checks cover all 200 default variants for text/caption bounds and deterministic seeking, plus source round trips, literal markup, invalid JSON/XML, focus paths, line limits, and editor file selection. Source text is excluded from caption replacement. The illustrations run no commands or application code.

Writing-for-agents review kept the source-panel API behind one conditional pointer, placed case data in the catalog, removed cached pattern counts from the guide, and distinguished illustrative panels from real terminal/editor evidence. Real terminal demonstrations retain the `/record-terminal` workflow.
