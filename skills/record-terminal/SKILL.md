---
name: record-terminal
description: Use when a video must show terminal commands, CLI output, TUI behavior, or code being entered on screen.
---

# Record terminal

Build an evidence-backed HTML replay. Run the real commands first, preserve their complete input and output, then reconstruct the terminal or editor at high fidelity for deterministic, legible video playback.

Read [`references/terminal-presentation.md`](references/terminal-presentation.md) before planning or producing the shot. It owns the evidence contract, default dark terminal style, code-entry behavior, and verification.

Use the reference's default style when the user has not chosen another terminal treatment. User-provided brand, shell, font, prompt, or accessibility requirements override the defaults while the evidence and alignment requirements remain in force.

Real screen capture is outside the default workflow. Use it only when the user explicitly requests recorded terminal footage; keep the HTML replay as the ordinary deliverable.
