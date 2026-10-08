---
name: artifact-preview
description: Use when an artifact-owning skill requires a durable Markdown file to be presented for user review in a coding agent.
---

# Artifact preview

Present an artifact as a readable, self-contained HTML review surface. The source Markdown remains authoritative. When the owning skill requires rendered evidence, the preview also presents that evidence without pretending prose is pixels or motion.

## Produce the preview

After writing a durable Markdown artifact, or after any later source change once its preview exists:

1. Compute the source file's SHA-256 digest.
2. Create or refresh `<basename>.preview.html` beside the source file.
3. Build a review header containing the artifact title, source path, source status value verbatim when present (otherwise `not declared`), and digest; add a table of contents for multi-section documents.
   - Include the review scope supplied by the owning skill. Use its honest label, such as content-structure review, visual direction board, or animatic review. State what the page validates and distinguish semantic claims from rendered evidence.
4. Render frontmatter as metadata and every Markdown heading section as semantic HTML: headings, paragraphs, lists, tables, code blocks, and safe links. Preserve approval state, open checks, evidence links, stable IDs, and lineage fields that affect review. A raw-source appendix is optional; a `<pre>` dump is not the primary review surface.
   - For a visual direction board, include the owning skill's rendered 16:9 proof states at inspectable size and identify their project revision and scene/state IDs.
   - For an animatic review, provide playback and seeking for the owning skill's timeline plus inspectable start, intermediate, boundary, and end states. Inline the review runtime and media, or package them in the host's supported self-contained representation.
5. Label the page as derived review material.
6. Use one self-contained HTML file with inline CSS and optional inline JavaScript. It must need no server, build step, network request, external font, stylesheet, script, image, or other local file. Rendered images and media may be embedded as `data:` resources.
7. Treat source text as data and escape it before inserting it into HTML.

## Present it

Present the rendered page through the host's native HTML or browser preview when available; opening the HTML source in an editor is not presentation.

- In Codex, open a rendered browser/file preview when the capability exists; otherwise include a clickable Markdown link to the absolute file path in the final response.
- In Claude Code, use its browser or platform file-opening capability when available; otherwise emit the absolute `file://` URI together with the filesystem path.

The presentation branch succeeds only when the opening tool confirms success or the host renders a clickable link or URI. Plain unlinked path text is not presentation.

Presenting a preview never records approval. Only the approval rule in the artifact-owning skill can change status or approval metadata. A later source change makes the preview stale.

A semantic HTML rendering of prose is not a visual prototype, styleframe, motion proof, or animatic. Claim visual or motion review only when the preview contains the owning skill's actual rendered evidence and identifies the source project revision.

## Completion criterion

The preview step is complete when:

- `<basename>.preview.html` exists beside the source;
- its displayed source path and digest match the current Markdown file;
- the frontmatter and every Markdown heading section appear in the semantic review surface;
- every rendered-evidence requirement declared by the owning skill is present, attributable to its current project revision, and directly inspectable or playable;
- a static audit finds no external URL in automatically loaded resources (`src`, stylesheet links, imports, CSS `url()`, or media), no `fetch`, `XMLHttpRequest`, `WebSocket`, or dynamic `import`, and no non-`data:` resource-bearing attribute; safe user-activated anchors may use fragments, relative paths, `http:`, or `https:`;
- it renders without horizontal page overflow at 1280 px when a rendered-preview capability is available; otherwise its CSS provides page wrapping plus local overflow containment for wide tables and code blocks; and
- it has been presented through one successful host branch: rendered preview, browser preview, or supported absolute-path link.
