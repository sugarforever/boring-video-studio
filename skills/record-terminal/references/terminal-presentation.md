# Terminal and code presentation

The default treatment is a deterministic, high-fidelity reconstruction of a real macOS iTerm/zsh session. It reconstructs actual application behavior and execution evidence, not merely an iTerm-looking panel. Use another terminal, shell, or visual treatment when the user asks for one.

Use the shared font contract in [`../../boring-video/references/hyperframes-review-project.md`](../../boring-video/references/hyperframes-review-project.md). This reference adds terminal and editor behavior without duplicating that contract.

## Session plan

Plan one continuous terminal session before designing shots. List each real input or operation in order, the visible state it produces, its evidence source, and how that state exits. Execute the plan step by step and let the replay preserve those state transitions.

When an existing script is inspected and then run, use this causal sequence unless the real workflow requires another editor or command:

1. enter the intended working directory and run any commands needed to establish visible context;
2. run `vi <real-path>` and show the real file contents;
3. perform the planned editor navigation or scrolling so the relevant code becomes visible;
4. run `:q` to return to the same shell session;
5. execute the complete real command, such as `node <real-path>`;
6. show that execution's stdout, stderr, and exit result in their actual order;
7. show the returned zsh prompt before typing the next command.

Represent editor input, navigation, scrolling, shell input, output, and exits as ordered manifest events. A single window may move between shell and editor states, but code, shell commands, and output remain temporally distinct states rather than simultaneous terminal-styled panels.

Model each command cycle as `prompt → typed input → Enter → running/output → returned prompt`. Only content reached by the current cycle is visible. Never initialize a shot with later commands and their results already present.

If the execution result also needs a designed chart, card, diagram, or other visualization, make that a subsequent video element sourced from the captured output or generated file. Keep it outside the terminal replay and preserve its evidence link.

## Evidence-first replay

1. Run the commands against the intended code, working directory, data, and environment. Save the complete command, stdout, stderr, exit code, and any timing evidence before designing the frame.
2. Create an evidence manifest beside the saved streams. For each shell or editor event, record its type, input or operation, source file or execution record, ordering, visible result, exit condition, redactions, and presentation-only chrome. The manifest is the boundary between real shell or source evidence and HyperFrames replay.
3. Reconcile the replay line by line with that evidence. Preserve command order, prompts, whitespace, wrapping, exit or status results, ANSI meaning, and table shape. For databases, preserve nulls, headers, separators, column widths, and row counts.
4. Redact secrets and machine-specific paths consistently without changing semantic output. Keep execution context such as the captured working directory in the manifest; when the frame needs to prove it, run and show `pwd` instead of adding a synthetic `cwd:` label.
5. Prove secret presence with a real non-disclosing command appropriate to the variable, such as `echo "OPENAI_API_KEY is ${OPENAI_API_KEY:+set}"`; never render the value. Show its real output rather than a synthetic status badge.
6. Keep the evidence and manifest outside the rendered frame unless the storyboard calls for them.

The replay is ready only when every visible editor state, navigation step, command, stdout line, stderr line, and exit result is traceable through the ordered manifest to real evidence or explicitly disclosed as presentation chrome.

## Real command pipelines

Run multi-command demonstrations exactly as a shell user would, one prompt cycle at a time. Preserve quoting, redirection, pipes, variable expansion, tool output, and failures from the tested commands.

For an image request that embeds a local file, use this planning pattern:

```sh
IMAGE_PATH=/real/path/to/image.png
IMAGE_DATA=$(base64 < "$IMAGE_PATH" | tr -d '\n')
jq --arg image_url "data:image/png;base64,$IMAGE_DATA" \
  '.input[0].content[0].image_url = $image_url' request.json > request.with-image.json
curl <real-options-and-endpoint> --data-binary @request.with-image.json > response.json
jq . response.json
```

Resolve every placeholder before execution. Adapt the request shape, MIME type, endpoint, and options to the real API and source files. Only the resulting tested commands may enter the evidence manifest or replay; do not replace them with shortened pseudo-commands. Display a formatted API response as the real `jq` text/JSON output in the terminal. Any cards, dashboards, tables, or image layouts derived from that response belong to a later non-terminal scene and retain a link to the response evidence.

## Application state machine

Treat shell and full-screen Vim as mutually exclusive application states:

- `shell_idle`: prompt visible, no future input or output;
- `shell_typing`: the current command prefix and caret derived from composition time;
- `shell_running`: submitted command fixed in scrollback while evidenced output reveals in order;
- `vim_view`: Vim occupies the terminal content area with the real file, status area, cursor, and viewport;
- `vim_navigation`: the same Vim buffer at an evidenced or planned scroll/jump position;
- `vim_command`: `:q` appears in Vim's command line;
- `shell_return`: Vim is gone and the shell prompt has returned;
- `session_exit`: the terminal leaves cleanly or hands off to the next scene.

Assign every manifest event a start and end time. Derive the active state, visible scrollback, Vim viewport, typed prefix, cursor, and output prefix directly from the current composition timestamp. Randomly seeking to a timestamp must reproduce the complete state without replaying earlier events, timers, mutable terminal history, or DOM side effects.

The terminal surface is opaque. When it replaces an earlier title or explanation, end or hide those layers before the terminal enters, or cover them with the terminal's complete background for the entire overlap. No underlying copy may remain visible through or around an unintended gap.

## Frame fidelity

- Give the terminal or editor 90–95% of the frame. Use an actual monospace face for ASCII code, prompts, and tables; add a language-appropriate fallback for glyphs the mono face lacks. Disable ligatures where they can change character widths.
- Preserve whitespace with preformatted layout. Keep aligned data in one font run and at one size. Test the widest command, code line, and table row at delivery resolution.
- Meet the project's accessibility target for foreground, muted text, selection, and cursor contrast. Decorative window controls must not resemble output.
- Prefer intentional path redaction or horizontal cropping to scaling text below readable size.

## Default dark style

Use these defaults when the user has not requested a different shell or visual identity. Adapt sizes proportionally for other delivery resolutions.

| Element | Default |
| --- | --- |
| Window | `#101217` opaque background, `#343942` border, no added black drop shadow |
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

Keep the title inside the macOS window bar with the red, yellow, and green controls. Do not add a persistent vertical name strip, editor-state badge, `cwd:` label, verification badge, or other chrome that a real iTerm/Vim session would not show. When a video annotation is required, keep it visibly outside the terminal window so it cannot be mistaken for application UI.

Inside `vi`, preserve the same outer iTerm chrome while Vim takes over the complete terminal content area. Reconstruct the real buffer, viewport, cursor, command line, and status area; do not add an Explorer panel or a separate editor frame. Syntax accents default to keyword `#fe90e8`, function `#c0f7fe`, string `#99e885`, comment or line number `#7c8794`, and focused line `rgba(247,203,70,.15)` with a `#f7cb46` inset marker. Show relevant code through real Vim navigation or scrolling rather than shrinking it below readable size.

These values are a coherent starting style, not project truth. A user-selected theme may replace them as a set; preserve monospace alignment, readable contrast, safe areas, and terminal/editor consistency.

## Coding animation

Place code at its final coordinates from the first frame. Reveal characters in place so the layout neither slides nor reflows.

- When a script will be executed later, show the real source first and preserve the causal order: inspect code, then execute it, then show its result. Extract only relevant spans; folds or ellipses may hide unrelated code but must not alter fields, endpoints, or logic.
- Use fast character-by-character typing only when the story depicts active authoring. An existing file opened for inspection appears directly or loads quickly without pretending it is being retyped.
- Type continuously across lines at a deterministic rate; do not slide completed lines horizontally into place. Reserve slower typing for the characters the viewer must understand.
- Put the caret immediately after the latest revealed monospace character. It advances with every character and resets to the next line's indentation after a newline.
- Keep completed lines stable. Scrolling is a separate, motivated camera event rather than a side effect of typing.
- Implement animation from composition time, not timers or accumulated DOM state, so seeking and rendering the same timestamp produce the same frame.

## Static fake-terminal failure mode

Reject a composition that shows a code panel, a command, and its completed output simultaneously before those actions occur. Also reject terminal-internal result cards, status badges, dashboard widgets, horizontal code-line fly-ins, or a decorative editor pasted above shell output. The valid reconstruction shows one real application state at a time and reaches later states only through the manifest's ordered actions.

## Verification

Inspect snapshots during the first line, within a long line, immediately after a newline, near the final character, and after completion. Confirm caret position, indentation, clipping, wrapping, and absence of horizontal movement or reflow.

Then inspect every terminal state against the evidence manifest. At delivery resolution, verify the shared font contract, resolved JetBrains Mono and Noto Sans SC fallback, prompt alignment, line height, table columns, widest lines, opaque coverage, masks, and safe areas. Seek directly into every shell/Vim transition and command midpoint. Run the production workflow's lint, runtime, layout, motion, and contrast checks. The treatment is complete only when random-seek states, intermediate typing states, final output, and evidence traceability pass.
