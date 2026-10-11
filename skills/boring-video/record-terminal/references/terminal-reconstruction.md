# Build and render the terminal replay

Start this sequence only after the runbook and real capture pass the gates in
[`terminal-presentation.md`](terminal-presentation.md).

```text
captured evidence → replay ledger → terminalState(t) → rendered terminal
```

The ledger is the sole source of terminal-visible content. HyperFrames renders
the ledger state at composition time.

## Gate 3: Build the replay ledger

Convert the capture into a chronological replay ledger. This ledger is both the
complete execution checklist and the content model consumed by HyperFrames.
Give every event these fields:

| Field | Requirement |
| --- | --- |
| `id` | Stable event identifier |
| `seq` | Strictly increasing order |
| `cycle` | Parent command or child-application cycle |
| `type` | Observed transition type |
| `evidenceTime` | Monotonic time from capture |
| `presentationStart` | Composition time at which the event begins |
| `presentationDuration` | Reveal interval; `0` for an instantaneous mutation |
| `reveal` | `instant`, `typed-prefix`, `stream-prefix`, or `screen-mutation` |
| `payload` | Decoded text, keystrokes, or a typed mutation object |
| `stream` | `input`, `stdout`, `stderr`, or `terminal-control` when applicable |
| `source` | Capture, source file, or redaction record |

Use typed events whose payload shape determines one screen operation:

- `shell_prompt_initial`
- `input_chunk`
- `input_submitted`
- `output_chunk`
- `screen_mutation`
- `continuation_prompt`
- `program_prompt`
- `child_app_entered`
- `child_app_updated`
- `child_app_exited`
- `command_completed`
- `shell_prompt_returned`

Parse raw PTY bytes before ledger construction. Decoded text becomes text events;
complete ANSI and terminal-control sequences become atomic screen mutations.
Text events carry exact text and an append or overwrite target. Screen mutation
events carry one explicit operation such as move, clear, resize, enter alternate
screen, exit alternate screen, or replace viewport. This discriminated shape
gives the reducer one unambiguous operation per event.

An `output_chunk` may end mid-line. Split chunks at evidenced timing boundaries
or meaningful screen updates. Represent difficult ANSI behavior with explicit
screen mutations or evidenced viewport snapshots.

### Prompt invariant

The ledger begins with one `shell_prompt_initial` event. A continuing command
cycle ends with exactly one `shell_prompt_returned` event after completion and
before the next input begins. `continuation_prompt` and `program_prompt` events
occur inside the owning cycle and never signal shell return.

### Content boundary

Terminal content consists exclusively of replay-ledger events and disclosed
terminal chrome. Titles, explanations, callouts, captions, charts, badges, and
editorial progress labels occupy separate video layers outside the terminal.
A later non-terminal visualization may interpret results while retaining its
link to the captured evidence.

### Reconciliation

Replay the ledger from the beginning and compare it with the capture. Account
for all of these observed properties:

- shell, continuation, and program prompt text;
- whitespace, wrapping, cursor position, and terminal dimensions;
- partial lines, `\n`, `\r`, backspace, ANSI meaning, and screen clears;
- stdout/stderr order and visible interleaving;
- errors, exit status, structured-output shape, tables, nulls, and row counts;
- full-screen buffer, viewport, status line, command area, and exit transition.

Gate passes when replaying all events reproduces the captured final screen and
replaying every prefix reproduces its corresponding intermediate screen. Every
continuing command cycle has exactly one shell-return event.

## Gate 4: Reconstruct in HyperFrames

Before implementing terminal UI, use `hyperframes-registry` to find the current
terminal components. Reuse a fitting component as the visual shell when its
content surface can be driven exclusively by the replay ledger. Otherwise use
the fallback in [`terminal-visual-style.md`](terminal-visual-style.md). When a
full-screen application appears, also apply
[`fullscreen-tui.md`](fullscreen-tui.md).

The content surface is a deterministic reducer over ledger events:

```text
terminalState(t) = reduce(events started at or before t)
```

For an event active at `t`, derive its visible prefix from
`presentationStart`, `presentationDuration`, and `reveal`. An `instant` or
`screen-mutation` event applies atomically at its start. A `typed-prefix` or
`stream-prefix` event exposes the corresponding payload prefix as normalized
progress moves from `0` to `1` across its duration. Prefix boundaries follow
complete grapheme clusters or evidenced capture chunks; they never split an
encoded character or terminal-control sequence.

Commands, output, prompts, cursor state, and scrollback render exclusively from
`terminalState(t)`. Immutable checkpoints may accelerate the reducer when they
produce the same state as folding the ledger from the beginning.

Apply carriage returns, overwrites, cursor operations, wrapping, clears, and
full-screen updates to the modeled screen. The viewport scrolls when the modeled
terminal scrolls.

The content state is commonly one of:

- `idle`: the current shell or in-cycle prompt is visible;
- `typing`: the current evidenced input prefix and caret are visible;
- `submitted`: the complete input is fixed in scrollback;
- `streaming_output`: output and screen mutations are visible through time `t`;
- `child_app`: a full-screen terminal application owns the content area;
- `returned`: the single evidenced shell-return event is visible;
- `exited`: the terminal has closed or handed off to the next scene.

State derives entirely from composition time, so playback and direct seeking
produce identical screens.

## Verification matrix

Inspect the delivered composition at all of these points:

| Seek point | Required result |
| --- | --- |
| Before Enter | Only the current prompt and typed prefix are visible |
| Immediately after Enter | Submitted command is fixed; no future shell prompt exists |
| Each output boundary | Exactly the reached chunks and screen effects are visible |
| Mid-stream | Partial lines and in-place updates match the ledger prefix |
| In-cycle prompt | Continuation or program prompt remains inside its command cycle |
| Command completion | Exit state is correct; shell-return event follows completion |
| Child-app entry/exit | Shell and child application own the surface successively |
| Direct seek | State matches playback without visiting earlier frames |
| Final frame | State matches the fully replayed ledger |

Also verify:

- every terminal-visible character and mutation has ledger or chrome provenance;
- every seek point contains only events reached at that composition time;
- editorial graphics occupy layers outside the terminal;
- every visual-style inspection passes at delivery resolution;
- the production workflow's lint, runtime, layout, motion, and contrast checks
  pass.

Gate passes when every verification row succeeds and the capture, ledger, and
render agree at every inspected boundary.
