# Terminal replay contract

Reconstruct an executed terminal session as a deterministic, evidence-backed application state machine. The replay presents what actually happened in the terminal; it does not invent execution or flatten a session into a static terminal-shaped composition.

Read conditional references only when their branch applies:

- For the default macOS iTerm/zsh appearance or another terminal theme, read [`terminal-visual-style.md`](terminal-visual-style.md).
- When the session enters Vim, `less`, `man`, a database client, or another full-screen terminal application, read [`fullscreen-tui.md`](fullscreen-tui.md).

## Ordered session

Plan one continuous terminal session before designing shots. For every real input or operation, record the visible state it produces, its evidence source, and how that state exits. Execute the plan step by step before building the replay.

Model each shell command as:

```text
returned prompt → typed input → Enter → running or streamed output → returned prompt
```

At any timestamp, show only the events already reached by that cycle. A later command or result becomes visible only after the preceding command has completed and the next prompt has returned.

When execution results also need a designed chart, card, diagram, image, or other visualization, create a subsequent non-terminal video element sourced from the captured output or generated file. Preserve its evidence link.

## Evidence manifest

Run commands against the intended code, working directory, data, and environment. Save the complete command, stdout, stderr, exit code, and any execution timing evidence before designing the frame.

For each shell, editor, or TUI event, record:

- event type and observed order;
- input, keystroke, navigation, or operation;
- source file or execution record;
- visible result and exit condition;
- redactions and presentation-only chrome;
- evidence timing when available;
- presentation start, reveal duration, and hold duration.

Evidence timing records what happened; presentation timing controls how long the video types, reveals, or holds that evidence. Editing presentation timing never changes command order, output content, or exit status.

Reconcile the replay line by line with the manifest. Preserve prompts, whitespace, wrapping, ANSI meaning, stdout/stderr order, exit results, and structured-output shape. Preserve database nulls, headers, separators, column widths, and row counts.

For multi-command pipelines, preserve tested variable assignments, quoting, redirection, pipes, expansion, tool errors, and prompt returns. Keep structured responses as their actual text or formatted JSON inside the terminal. A designed interpretation belongs to the subsequent non-terminal element described above.

Redact secrets and machine-specific paths consistently without changing semantic output. Keep captured working-directory evidence in the manifest; when the frame needs to prove it, run and show `pwd`. Prove secret presence with a real non-disclosing command appropriate to the environment, such as `echo "OPENAI_API_KEY is ${OPENAI_API_KEY:+set}"`, and show its actual output.

## Seek-safe state model

Represent the session with the smallest state set its real applications require. The common states are:

- `idle`: the current prompt is visible;
- `typing`: the current input prefix and caret are derived from composition time;
- `submitted`: the complete input is fixed in scrollback;
- `streaming_output`: evidenced output is visible through the current timestamp;
- `child_app`: a full-screen terminal application owns the content area;
- `returned`: the child application or command has ended and the shell prompt is visible again;
- `exited`: the terminal has left cleanly or handed off to the next scene.

Assign every manifest event a start and end time. Derive the active state, visible scrollback, typed prefix, cursor, child-application viewport, and output prefix directly from the current composition timestamp. Seeking to a timestamp reproduces the complete state without replaying earlier events, timers, mutable terminal history, or DOM side effects.

The terminal surface is opaque. When it replaces an earlier title or explanation, end or hide those layers before entry, or cover them with the terminal's complete background throughout the overlap.

## Code presentation

When the story depicts active authoring, place code at its final coordinates and reveal characters in place at a fast deterministic rate. Derive the revealed substring and caret from composition time. Keep completed lines stable; make scrolling a separate motivated event.

When an existing file is opened for inspection, display its real contents directly through the selected editor or TUI. Extracted spans, folds, or omissions may hide unrelated code but preserve the fields, endpoints, and logic being explained.

## Completion criterion

The replay is complete only when:

- every visible character and state traces to real input, source, stdout, stderr, exit evidence, or disclosed presentation chrome;
- every command cycle includes submission, evidenced output or completion, and the returned prompt;
- full-screen child applications and the shell occupy mutually exclusive states;
- direct seeking to event starts, midpoints, exits, and command boundaries reproduces the correct state without future-event leakage;
- designed result visualizations remain separate from terminal output and retain evidence lineage;
- the terminal fully covers intended background layers and fits its longest lines at delivery resolution;
- resolved fonts, weights, monospace alignment, wrapping, contrast, masks, and safe areas pass inspection; and
- the production workflow's lint, runtime, layout, motion, and contrast checks pass.
