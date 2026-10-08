# Terminal and code presentation

The default treatment is a deterministic, high-fidelity HTML replay in a dark iTerm-inspired terminal. It reconstructs a real execution for video; it does not invent terminal footage. Use another visual treatment when the user asks for one.

Use the shared font contract in [`../../boring-video/references/hyperframes-review-project.md`](../../boring-video/references/hyperframes-review-project.md). This reference adds terminal and editor behavior without duplicating that contract.

## Session plan

Plan one continuous terminal session before designing shots. List each real input or operation in order, the visible state it produces, its evidence source, and how that state exits. Execute the plan step by step and let the replay preserve those state transitions.

When an existing script is inspected and then run, use this causal sequence unless the real workflow requires another editor or command:

1. enter the intended working directory and run any commands needed to establish visible context;
2. run `vi <real-path>` and show the real file contents;
3. perform the planned editor navigation or scrolling so the relevant code becomes visible;
4. run `:q` to return to the same shell session;
5. execute the complete real command, such as `node <real-path>`;
6. show that execution's stdout, stderr, and exit result in their actual order.

Represent editor input, navigation, scrolling, shell input, output, and exits as ordered manifest events. A single window may move between shell and editor states, but code, shell commands, and output remain temporally distinct states rather than simultaneous terminal-styled panels.

If the execution result also needs a designed chart, card, diagram, or other visualization, make that a subsequent video element sourced from the captured output or generated file. Keep it outside the terminal replay and preserve its evidence link.

## Evidence-first replay

1. Run the commands against the intended code, working directory, data, and environment. Save the complete command, stdout, stderr, exit code, and any timing evidence before designing the frame.
2. Create an evidence manifest beside the saved streams. For each shell or editor event, record its type, input or operation, source file or execution record, ordering, visible result, exit condition, redactions, and presentation-only chrome. The manifest is the boundary between real shell or source evidence and HyperFrames replay.
3. Reconcile the replay line by line with that evidence. Preserve command order, prompts, whitespace, wrapping, exit or status results, ANSI meaning, and table shape. For databases, preserve nulls, headers, separators, column widths, and row counts.
4. Redact secrets and machine-specific paths consistently without changing semantic output. Keep execution context such as the captured working directory in the manifest; when the frame needs to prove it, run and show `pwd` instead of adding a synthetic `cwd:` label.
5. Prove secret presence with a real non-disclosing command appropriate to the variable, such as `echo "OPENAI_API_KEY is ${OPENAI_API_KEY:+set}"`; never render the value. Show its real output rather than a synthetic status badge.
6. Keep the evidence and manifest outside the rendered frame unless the storyboard calls for them.

The replay is ready only when every visible editor state, navigation step, command, stdout line, stderr line, and exit result is traceable through the ordered manifest to real evidence or explicitly disclosed as presentation chrome.

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
| Font | `"JetBrains Mono", "Noto Sans SC", monospace` |
| Text | weight 400, letter spacing 0; 24–29 px at 1080p; line height 1.30–1.42 |
| Command | `#f4f4f5`, weight 400 |
| Muted output | `#a2aab3` |
| Username | `#57e35a` |
| Path | `#6f8cff` |
| Git branch | `#2bd4d4` |
| Prompt glyph | `#df5ac8` |
| Active cursor | `#65e5c2` |

Keep the title inside the title bar. Do not add a persistent vertical name strip. When a frame or evidence label is useful, place a compact label at the lower right, above masks and clipped surfaces, with enough inset to remain inside the delivery safe area.

Use the same window chrome, font stack, weight, spacing, and base palette for simulated `vi` or editor views. Syntax accents default to keyword `#fe90e8`, function `#c0f7fe`, string `#99e885`, comment or line number `#7c8794`, and focused line `rgba(247,203,70,.15)` with a `#f7cb46` inset marker. Show only the code needed for the explanation; use explicit jumps, folds, or omissions instead of shrinking a long file below readable size. Keep an Explorer or file tree subordinate and ensure the active filename remains readable.

These values are a coherent starting style, not project truth. A user-selected theme may replace them as a set; preserve monospace alignment, readable contrast, safe areas, and terminal/editor consistency.

## Coding animation

Place code at its final coordinates from the first frame. Reveal characters in place so the layout neither slides nor reflows.

- When a script will be executed later, show the real source first and preserve the causal order: inspect code, then execute it, then show its result. Extract only relevant spans; folds or ellipses may hide unrelated code but must not alter fields, endpoints, or logic.
- Use fast character-by-character typing only when the story depicts active authoring. An existing file opened for inspection appears directly or loads quickly without pretending it is being retyped.
- Type continuously across lines at a deterministic rate; do not slide completed lines horizontally into place. Reserve slower typing for the characters the viewer must understand.
- Put the caret immediately after the latest revealed monospace character. It advances with every character and resets to the next line's indentation after a newline.
- Keep completed lines stable. Scrolling is a separate, motivated camera event rather than a side effect of typing.
- Implement animation from composition time, not timers or accumulated DOM state, so seeking and rendering the same timestamp produce the same frame.

## Verification

Inspect snapshots during the first line, within a long line, immediately after a newline, near the final character, and after completion. Confirm caret position, indentation, clipping, wrapping, and absence of horizontal movement or reflow.

Then inspect every terminal state against the evidence manifest. At delivery resolution, verify the shared font contract, resolved font families and weights, prompt alignment, table columns, widest lines, label stacking, masks, and safe areas. Run the production workflow's lint, runtime, layout, motion, and contrast checks. The treatment is complete only when intermediate typing states, final output, and evidence traceability pass.
