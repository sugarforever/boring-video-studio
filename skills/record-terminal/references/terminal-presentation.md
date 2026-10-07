# Terminal and code presentation

The default treatment is a deterministic, high-fidelity HTML replay in a dark iTerm-inspired terminal. It reconstructs a real execution for video; it does not invent terminal footage. Use another visual treatment when the user asks for one.

## Evidence-first replay

1. Run the commands against the intended code, working directory, data, and environment. Save the complete input and output before designing the frame.
2. Reconcile the replay line by line with that evidence. Preserve command order, prompts, whitespace, wrapping, exit or status results, ANSI meaning, and table shape. For databases, preserve nulls, headers, separators, column widths, and row counts.
3. Record provenance beside the production artifact: execution context, evidence files, transformations, and redactions. Mark reconstructed prompts or chrome explicitly. Redact secrets and machine-specific paths consistently without changing semantic output.
4. Keep the evidence outside the rendered frame unless the storyboard calls for it.

The replay is ready only when every visible command and result is traceable to evidence or disclosed as presentation chrome.

## Frame fidelity

- Give the terminal or editor 90–95% of the frame. Use an actual monospace face for ASCII code, prompts, and tables; add a language-appropriate fallback for glyphs the mono face lacks. Disable ligatures where they can change character widths.
- Preserve whitespace with preformatted layout. Keep aligned data in one font run and at one size. Test the widest command, code line, and table row at delivery resolution.
- Meet the project's accessibility target for foreground, muted text, selection, and cursor contrast. Decorative window controls must not resemble output.
- Prefer intentional path redaction or horizontal cropping to scaling text below readable size.

## Default dark style

Use these defaults when the user has not requested a different shell or visual identity. Adapt sizes proportionally for other delivery resolutions.

| Element | Default |
| --- | --- |
| Window | `#101217` background, `#343942` border |
| Title bar | 58 px at 1080p, `#1a1d23` background, `#30343c` 1 px bottom rule |
| Title | `#aeb5bf`, 20 px, weight 400 |
| Window dots | 14 px, visually subordinate to content |
| Surface | 28 px vertical / 30 px horizontal padding, `#e7e9ed` foreground |
| Font | `"iTerm Monaco", Monaco, "Noto Sans SC", monospace` |
| Text | weight 400, letter spacing 0; 24–29 px at 1080p; line height 1.30–1.42 |
| Command | `#f4f4f5`, weight 400 |
| Muted output | `#a2aab3` |
| Username | `#57e35a` |
| Path | `#6f8cff` |
| Git branch | `#2bd4d4` |
| Prompt glyph | `#df5ac8` |
| Active cursor | `#65e5c2` |

Keep the title inside the title bar. Do not add a persistent vertical name strip. When a frame or evidence label is useful, place a compact label at the lower right, above masks and clipped surfaces, with enough inset to remain inside the delivery safe area.

Use the same window chrome, font stack, weight, spacing, and base palette for simulated `vi` or editor views. Syntax accents default to keyword `#fe90e8`, function `#c0f7fe`, string `#99e885`, comment or line number `#7c8794`, and focused line `rgba(247,203,70,.15)` with a `#f7cb46` inset marker. Show only the code needed for the explanation; use explicit jumps, folds, or omissions instead of shrinking a long file below readable size.

These values are a coherent starting style, not project truth. A user-selected theme may replace them as a set; preserve monospace alignment, readable contrast, safe areas, and terminal/editor consistency.

## Coding animation

Place code at its final coordinates from the first frame. Reveal characters in place so the layout neither slides nor reflows.

- Type line by line. Long passages may use a faster deterministic rate; reserve slower typing for the line the viewer must understand.
- Put the caret immediately after the latest revealed monospace character. It advances with every character and resets to the next line's indentation after a newline.
- Keep completed lines stable. Scrolling is a separate, motivated camera event rather than a side effect of typing.
- Implement animation from composition time, not timers or accumulated DOM state, so seeking and rendering the same timestamp produce the same frame.

## Verification

Inspect snapshots during the first line, within a long line, immediately after a newline, near the final character, and after completion. Confirm caret position, indentation, clipping, wrapping, and absence of horizontal movement or reflow.

Then inspect every terminal state against the saved evidence. At delivery resolution, verify font fallback, weight consistency, prompt alignment, table columns, widest lines, label stacking, masks, and safe areas. Run the production workflow's lint, runtime, layout, motion, and contrast checks. The treatment is complete only when intermediate typing states and final output pass.
