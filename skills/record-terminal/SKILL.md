---
name: record-terminal
description: Use when recording terminal command execution for a video; use ttyd to present a real local shell in a browser and capture the page viewport (CDP by default, native window capture as fallback).
---

# Record terminal

Present a real local shell in a browser with `ttyd`, then operate that browser terminal so commands and output appear in the recording. By default, capture the page viewport through the Chrome DevTools Protocol. Native window capture is the fallback.

## When this applies

Use this when the video shows a command **actually executing** — typed input, growing output, progress bars, ANSI color, or an interactive TUI responding to input — or when narration walks through running something.

Do **not** use it when the terminal only needs to *look* like a terminal: static or decorative windows, fake command mockups, conceptual diagrams, or commands that are destructive, secret, or depend on an environment that cannot be safely run. Animate those in HyperFrames instead. When the call is unclear, record: real footage can be trimmed, sped up, or have frames dropped; a mocked terminal does not hold up when a viewer watches it.

## Preflight

1. Resolve the working directory, shell, exact command sequence, target frame, and output paths. Default to the current directory, login shell, and a 16:9 deliverable.
2. Run `command -v ttyd`. When it is missing, tell the user that `ttyd` is required, show the relevant install command (`brew install ttyd` on macOS or the system package manager on Linux), and resume after it becomes available.
3. Choose an unused local port, normally `7681`, and the loopback interface (`lo0` on macOS, `lo` on Linux).
4. Use a disposable or otherwise safe environment for commands that install packages, edit configuration, or mutate state. Keep secrets and unrelated user data out of the terminal, command history, and environment.
5. Separate capture and delivery paths. Use names such as `*-cdp-4k.mp4` or `*-window-raw.mov` for source capture, and `*-clean-1080p.mp4` for the deliverable. Never overwrite an accepted take while recording or transcoding a replacement.

## Start the terminal

Keep `ttyd` in a managed long-running process so its output and lifecycle remain observable:

```bash
ttyd \
  -i lo0 \
  -p 7681 \
  -W -o -q \
  -w /absolute/working/directory \
  -t fontSize=20 \
  -t cursorBlink=true \
  -t 'theme={"background":"#0b0f14","foreground":"#e6edf3","cursor":"#7ee787"}' \
  /bin/zsh -l
```

Adapt the interface and shell to the host. The loopback bind keeps the writable shell local; one-client and exit-on-disconnect options give the recording session a bounded lifetime.

When the shell is started from a scrubbed environment (`env -i ...`), set `LANG=en_US.UTF-8`. Otherwise zsh echoes typed CJK as `<00ad>`-style escapes, even though command output renders correctly. Add `-t disableResizeOverlay=true -t disableLeaveAlert=true` so no size overlay or leave dialog enters the frame.

## Choose the capture path

| | CDP viewport capture (default) | Native window capture |
|---|---|---|
| Frame | Page viewport only; no crop | Chrome window; crop tabs, toolbar, shadow |
| Resolution | Any viewport size; true 3840×2160 text rendering | Bounded by the display, ~3024 px wide on a 14" Retina |
| Pointer, banners, other apps | Cannot appear | Pointer is recorded when it crosses the window; banners must be dismissed |
| Host screen during the take | Free; headless browser, no focus stealing | Window must stay unminimized on its Space; pointer kept away |
| Permissions | None | macOS Screen Recording |
| Limits | Only what the page renders | Also works for native apps and system UI |

Use CDP viewport capture for ttyd shots. Fall back to native window capture only when the shot needs something outside the page.

## CDP viewport capture

`scripts/cdp-record.mjs` drives headless Chromium with `playwright-core`. It loads the ttyd page at the target resolution and runs a JSON step list: `type`, `paste`, `press`, `wait`, `waitText`, `waitNoText`, `screenshot`, `start`, `stop`. Steps before `start` are off-camera setup. `waitText` and `waitNoText` read the xterm.js buffer that ttyd exposes as `window.term`, so each step waits on real terminal state instead of fixed sleeps.

Between `start` and `stop` it runs `Page.startScreencast` with lossless PNG frames, resamples them to a constant frame rate, and pipes them into ffmpeg (`libx264`, CRF 14 by default). The file is complete a moment after `stop`; there is no separate assembly pass.

```bash
npm i playwright-core && npx playwright install chromium   # once
node scripts/cdp-record.mjs shot.json
```

For a 4K master, use a 3840×2160 viewport with the ttyd font around 40 px (~160×45 cells). Headless screencast frames are delivered in CSS pixels, so raise the viewport, not `deviceScaleFactor`. Derive the 1080p deliverable by downscaling the master.

Put setup such as sourcing credentials, starting the TUI, seeding context, and a final `clear` before `start`, so none of it is on camera. The step list is also the take's script: exact inputs, one `press Enter` per submission, and explicit waits on the signal that proves the point.

## Native window capture

Use this path only when the shot needs something CDP cannot see.

1. Open `http://127.0.0.1:<port>/` with the available Chrome browser-control tool. Size the browser so its page viewport has the intended composition and enough terminal rows for the complete output.
2. Verify the visible path and round trip with `printf 'recording-ready\n'; pwd`.
3. Clear the terminal and inspect the entire capture frame. Dismiss browser automation, debugging, permission, download, and password banners. Confirm the terminal is unobstructed.
4. Resolve the native Chrome window identifier before recording. On macOS, capture that window with `screencapture -l <window-id>` or use a recorder with an equivalent window-capture source. A whole-display capture is not a Chrome-window capture.
5. Record a two-second pilot to the raw path. Extract a frame and confirm it shows the intended Chrome window—not Codex or another foreground app—and that the whole terminal viewport is visible. Start the full take only after the pilot passes.

Window capture is independent of foreground focus when the recorder locks onto a native window identifier: a window fully covered by another app is still captured. It is not independent of the pointer. `screencapture -v -l` records the mouse cursor whenever it crosses the window's screen region, even under another app. Keep the pointer away from that region during the take, or treat a visible pointer as a reject. Do not minimize the window or move it to another Space. If the available recorder only supports whole-display capture, keep Chrome foreground and treat any app switch as a rejected take.

## Record the full take

1. Start capture to a new path. With CDP, this is the `start` step. With native window capture, write a new `*-window-raw.mov`; on macOS, prefer a fixed-duration `screencapture` invocation and let it end naturally, because an interrupted capture may not produce a valid file.
2. Enter every on-camera command through the browser terminal. Type visibly, character by character, at roughly 100–150 ms per character by default; slow down further when readability calls for it.
3. Before pressing Enter, compare the rendered command with the intended command. Pay special attention to punctuation and shell-significant text such as `npm:@scope/package`, quotes, backslashes, pipes, redirects, and environment assignments. For fragile commands, type stable segments and paste the exact special fragment rather than trusting character-by-character automation.
4. After the full command has been visually verified, wait two seconds before pressing Enter. Apply this to every command, including short commands such as `vi hello.py`, so the audience can read it before execution replaces the prompt.
5. Submit each input exactly once. Interactive TUIs often take a moment to echo a submission; never re-send because the screen looks unchanged, and never wrap the Enter step in a retry. When the app keeps a session log, confirm afterwards that the input appears once. A duplicate submission rejects the take unless the shot can be trimmed before it.
6. Read the rendered output before advancing and leave a short visual beat after meaningful output. Preserve prompts, ANSI color, progress, and interactive TUI behavior as part of the shot.
7. Reject the take after a typo, failed setup step, unexpected prompt, secret exposure, wrong app capture, or obstructed terminal. Preserve it under a `*-reject.*` name only when it is useful for diagnosis; otherwise discard it. Clear or reset the session, then record a new take to a new path.
8. Leave the final state visible for the closing beat and let capture finish cleanly. When the user controls capture, leave the completed Chrome frame visible for handoff.

### Interactive agent and TUI shots

When the shot runs an agent or other TUI inside the terminal (for example a coding-agent CLI demonstrating an extension):

- Seed any required prior context before capture starts, or in a part of the take that will be trimmed, so the on-camera beat starts from the intended state.
- Suppress update notices, changelog banners, and first-run tips through the app's config or environment when it offers a switch; otherwise plan to trim or cover them.
- Decide in advance which on-screen signal proves the point, such as a status-bar value or a dialog, and end the shot shortly after it appears. Do not wait for long model replies, which are nondeterministic and can contradict the demo; for example, an agent without tool access replying "I can't run tests" to a "run the tests" prompt.

### Legibility

Terminal text is read at video size, not at Retina window size. Size the page viewport near the delivery width in CSS pixels, or raise the font size, so body text stays readable after scaling to 1920×1080. When the key signal is small, such as a single status line, note it for a punch-in during editing.

## Crop the page viewport (native window capture)

CDP output is already the page viewport; skip this section for it. Treat the raw Chrome-window recording as source footage. The deliverable contains only the ttyd page viewport: remove tabs, the address bar, bookmarks, window chrome, and borders.

Determine the crop from a frame of the actual take rather than assuming fixed browser offsets. Crop first, then scale proportionally and pad with the terminal background color to the target frame, normally 1920×1080. Never stretch the terminal to force a 16:9 result.

Example shape; replace all dimensions with measurements from the current take:

```bash
ffmpeg -i demo-window-raw.mov \
  -vf "crop=<w>:<h>:<x>:<y>,scale=1920:-2:flags=lanczos,pad=1920:1080:(ow-iw)/2:(oh-ih)/2:color=#0b0f14,fps=30" \
  -c:v libx264 -crf 18 -pix_fmt yuv420p -movflags +faststart -an \
  demo-clean-1080p.mp4
```

## Quality gate

The recording is accepted only after all of these checks pass:

1. Run `ffprobe` and confirm the expected codec, dimensions, frame rate, duration, and audio policy.
2. Decode the entire deliverable with `ffmpeg -v error -i <file> -f null -` and require a clean exit.
3. Extract and visually inspect frames near the beginning, middle, and end, plus a dense pass of about 4 fps around every submission. Sparse samples miss short events such as a duplicate submission or an unwanted reply.
4. In those frames, confirm the captured app is Chrome, no browser toolbar or unrelated app is visible, terminal content is not clipped or stretched, the intended commands and results are present, and no secret or sensitive path is exposed.
5. Keep the raw take until the clean deliverable passes QA. Do not replace an accepted deliverable until its replacement also passes.
6. After acceptance, keep only the accepted `*-window-raw.mov` and its clean deliverable. Remove whole-display and wrong-app rejects from the project, because they can contain unrelated private screen content.

After acceptance, close the page and confirm the managed `ttyd` process has exited.

The session is complete when the correct Chrome window was captured, the delivered video contains only the terminal viewport at the requested aspect ratio, every command and result is accurate and complete, the full file decodes successfully, and beginning/middle/end frames pass visual and sensitive-information review.
