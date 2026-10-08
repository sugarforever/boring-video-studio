---
name: record-terminal
description: Use when a video must show terminal commands, CLI output, TUI behavior, or code being entered on screen.
---

# Record terminal

Build an evidence-backed HTML replay. Plan and execute one ordered terminal session, preserve its real shell and editor state transitions, then reconstruct them at high fidelity for deterministic, legible video playback.

Read [`references/terminal-presentation.md`](references/terminal-presentation.md) and [`../boring-video/references/hyperframes-review-project.md`](../boring-video/references/hyperframes-review-project.md) before planning or producing the shot. The first owns evidence and code-entry behavior; the second owns the shared project and font contract.

Use the reference's default style when the user has not chosen another terminal treatment. User-provided brand, shell, font, prompt, or accessibility requirements override the defaults while the evidence and alignment requirements remain in force.

Real screen capture is outside the default workflow. Use it only when the user explicitly requests recorded terminal footage; keep the HTML replay as the ordinary deliverable.
