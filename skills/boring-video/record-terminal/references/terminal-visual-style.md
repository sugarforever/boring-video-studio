# Default terminal visual style

Use this profile when the user or project does not specify a terminal visual
system. It is the skill's classic macOS iTerm-like presentation default, not a
claim about iTerm's factory shell prompt. A fitting registry component may
implement this profile; it does not override the profile. User-provided
terminal, shell, brand, or accessibility requirements may replace it as a
coherent system.

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

Keep the title inside the macOS window bar.

### Default prompt

Use this visible shape when the project supplies no prompt convention:

```text
<user>@<host> <short-path> > <command>
```

Use stable, non-sensitive values appropriate to the project, for example
`alex@mac ~/project > npm test`. Show the user and host, a shortened working
directory (`~` plus the project-relative path), one space, the `>` prompt glyph,
and one trailing space before the command. Omit environment badges, timestamps,
Git status, and decorative prompt segments unless the project requires them.
This presentation default does not authorize changing the command, output, or
causal order established by the captured evidence.

At delivery resolution, inspect prompt alignment, line height, widest commands and output, resolved font families and weights, opaque coverage, and safe areas.
