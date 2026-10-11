# Plan and capture the terminal run

Finish both gates in this document before designing or implementing the
terminal shot. The observed run is the authority for all later work.

## Gate 1: Write the runbook

Understand the entire demonstration. Produce one ordered runbook containing:

- starting working directory, shell, terminal size, and required environment;
- prerequisites and files that must already exist;
- every visible command, keystroke, answer, navigation action, and exit action;
- expected long-running phases and the condition that ends each one;
- the final terminal state and handoff to the next video scene.

Model every shell command as one causal cycle:

```text
shell prompt → typed input → Enter → visible execution → completion → shell prompt
```

The first shell prompt belongs to startup. A later shell prompt belongs to the
completion of the preceding cycle. Continuation prompts, password prompts,
interactive confirmations, and REPL prompts occur inside a cycle and must be
listed separately from the shell's return.

A command may produce no output, fail, stream for a long time, enter a
full-screen application, or terminate the shell. The runbook represents the
observed branch and its stopping condition.

Gate passes when another operator can execute the complete demonstration from
the runbook without inventing a command, input, branch, or stopping condition.

## Gate 2: Capture the real execution

Execute the runbook in the intended project, directory, data, environment, and
shell. Execute every reconstructed terminal run through a PTY and capture the
complete run before writing HyperFrames code.

Retain this core evidence:

- raw PTY bytes and monotonic timing;
- terminal rows and columns;
- commands and interactive keystrokes;
- observed exit status;
- ANSI sequences and every captured terminal-control operation.

Also retain stdout and stderr separately when the execution harness exposes
them without changing PTY behavior. Derive explicit screen mutations or visible
viewport snapshots for carriage returns, backspaces, cursor movement, screen
clears, wrapping, resize events, alternate-screen transitions, and complex
full-screen updates.

Let commands reach their real completion or the runbook's explicit stopping
condition. Capture pauses, partial lines, prompts, warnings, retries, spinners,
progress bars, and stdout/stderr interleaving. For in-place or streamed output,
the timed PTY evidence accompanies the final log.

When execution diverges, revise the runbook to match the observed branch and
capture that revised run from the beginning.

Secrets and machine-specific paths may be redacted after capture. Record each
redaction and preserve the meaning, width-sensitive layout where relevant, and
all surrounding output. Presentation timing may later be compressed or
extended; content and causal order remain fixed.

Gate passes when the captured evidence accounts for every visible state from
the opening shell prompt through the final state.

After this gate passes, read
[`terminal-reconstruction.md`](terminal-reconstruction.md) to build the replay
ledger and HyperFrames reconstruction.
