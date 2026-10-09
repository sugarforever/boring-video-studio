# Terminal visual style

Use this reference when reconstructing terminal or editor appearance. The default is a high-fidelity macOS iTerm/zsh treatment; user-provided terminal, shell, brand, or accessibility requirements may replace it as a coherent system.

## Frame fidelity

- Give the terminal 90–95% of the frame.
- Preserve whitespace with preformatted layout and keep aligned data in one font run and size.
- Disable ligatures where they alter character widths.
- Prefer intentional path redaction, real wrapping, or horizontal cropping to unreadably small text.
- Keep the terminal surface opaque and avoid added black drop shadows.

## Font contract

Terminal and full-screen TUI surfaces own their font stack independently of the surrounding video:

| Role | Family | Weights |
| --- | --- | --- |
| Commands, Latin code, prompts, output, and tables | `JetBrains Mono` | 400, 700 |
| Chinese glyph fallback inside terminal surfaces | `Noto Sans SC` | 400, 700 |

Use shared terminal tokens:

```css
:root {
  --terminal-font: "JetBrains Mono", "Noto Sans SC", monospace;
}

.terminal-window {
  font-family: var(--terminal-font);
  font-synthesis: none;
}
```

Before review, inspect representative Latin, Chinese, normal, and emphasized runs in the rendered terminal. Confirm both families and every used weight are loaded, Chinese fallback resolves to `Noto Sans SC`, and aligned content retains equal character widths.

## Default macOS iTerm treatment

| Element | Default |
| --- | --- |
| Window | `#101217` opaque background, `#343942` border |
| Title bar | 58 px at 1080p, `#1a1d23` background, `#30343c` 1 px bottom rule |
| Title | `#aeb5bf`, 20 px, weight 400 |
| Window controls | Red, yellow, and green; 14 px at 1080p |
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

Keep the title inside the macOS window bar. Video annotations live visibly outside the terminal window. Application state, working directory, environment verification, and execution results appear through real terminal interaction rather than terminal-internal badges or labels.

At delivery resolution, inspect prompt alignment, line height, widest commands and output, resolved font families and weights, opaque coverage, and safe areas.
