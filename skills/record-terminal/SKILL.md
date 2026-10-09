---
name: record-terminal
description: Use when a video must show terminal commands, CLI output, full-screen terminal applications, or code entered inside a terminal session.
---

# Record terminal

Build an evidence-backed replay of a real terminal application. Plan and execute one ordered shell/editor session, preserve every prompt, input, full-screen state, output, and return transition, then reconstruct that state machine at high fidelity for deterministic, legible video playback.

Read [`references/terminal-presentation.md`](references/terminal-presentation.md) before planning or producing the shot. It owns the core replay contract and routes to the skill's visual and full-screen TUI references.

Use the reference's default style when the user has not chosen another terminal treatment. User-provided brand, shell, font, prompt, or accessibility requirements override the defaults while the evidence and alignment requirements remain in force.

Real screen capture is outside the default workflow. Use it only when the user explicitly requests recorded terminal footage; keep the evidence-backed reconstruction as the ordinary deliverable.
