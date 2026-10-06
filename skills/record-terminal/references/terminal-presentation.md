# Terminal and code presentation

Use one of two treatments. Both must preserve what actually happened; they differ in how the event reaches the frame.

## Choose the treatment

Choose **real capture** when live behavior is evidence: an interactive TUI, shell completion, ANSI/progress behavior, latency, mouse interaction, or a failure whose timing matters. Return to `record-terminal/SKILL.md` and capture the real shell through `ttyd`.

Choose **HTML replay** when the audience needs a controlled, legible explanation of commands, output, or code entry and the interaction itself is not the claim. Replay is a reconstruction from evidence, not invented terminal footage.

If one sequence needs both, separate the shots: preserve the live interaction in real capture and use replay for readable excerpts.

## Evidence-first replay

1. Run the commands against the intended code, working directory, data, and environment. Save the complete input and output before designing the frame.
2. Reconcile the replay line by line with that evidence. Preserve command order, prompts, whitespace, wrapping, exit or status results, ANSI meaning, and table shape. For databases, preserve nulls, headers, separators, column widths, and row counts.
3. Record provenance beside the production artifact: execution context, evidence files, transformations, and redactions. Mark reconstructed prompts or chrome explicitly. Redact secrets and machine-specific paths consistently without changing semantic output.
4. Keep the evidence outside the rendered frame unless the storyboard calls for it.

The replay is ready only when every visible command and result is traceable to evidence or disclosed as presentation chrome.

## Frame fidelity

- Give the terminal or editor most of the frame. Use an actual monospace face for ASCII code, prompts, and tables; add a language-appropriate fallback for glyphs the mono face lacks. Disable ligatures where they can change character widths.
- Preserve whitespace with preformatted layout. Keep aligned data in one font run and at one size. Test the widest command, code line, and table row at delivery resolution.
- Meet the project's accessibility target for foreground, muted text, selection, and cursor contrast. Decorative window controls must not resemble output.
- Prefer intentional path redaction or horizontal cropping to scaling text below readable size.

## Coding animation

Place code at its final coordinates from the first frame. Reveal characters in place so the layout neither slides nor reflows.

- Type line by line. Long passages may use a faster deterministic rate; reserve slower typing for the line the viewer must understand.
- Put the caret immediately after the latest revealed monospace character. It advances with every character and resets to the next line's indentation after a newline.
- Keep completed lines stable. Scrolling is a separate, motivated camera event rather than a side effect of typing.
- Implement animation from composition time, not timers or accumulated DOM state, so seeking and rendering the same timestamp produce the same frame.

## Verification

Inspect snapshots during the first line, within a long line, immediately after a newline, near the final character, and after completion. Confirm caret position, indentation, clipping, wrapping, and absence of horizontal movement or reflow.

Then inspect every terminal state against the saved evidence and run the production workflow's lint, runtime, layout, motion, and contrast checks. The treatment is complete only when intermediate typing states and final output pass.
