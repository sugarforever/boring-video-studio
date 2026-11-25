# Blockframe scene review demo

A 28-second, three-scene example of the scene-stage workflow proposed in [PR #33](https://github.com/sugarforever/boring-video-studio/pull/33). Each scene is actual HyperFrames composition HTML. The review page reads those same files; `index.html` mounts them at 0, 8, and 18 seconds for the assembled video.

## Run the scene review

Requirements: Python 3 and a modern browser. No npm install or service login is needed for the scene review.

```sh
cd demo/scene-blockframe-test
npm run review
```

Open [the review page](http://127.0.0.1:3121/review.html). Without npm, run `python3 -m http.server 3121 --bind 127.0.0.1` from this directory. The page requires HTTP because it loads the compositions with `fetch`; opening the file directly is unsupported. Choose another port if 3121 is occupied.

Select scenes, play/pause, seek or run the whole sequence, and compare the narration text with the actual visuals. Notes stay in browser-local storage; **导出审阅意见** downloads JSON. It does not write source files or approve scenes.

## HyperFrames integration

With Node.js 22+ and HyperFrames browser dependencies available:

```sh
npm run dev
npm run check
```

The commands use HyperFrames 0.9.92. Use the preview URL printed by the CLI; no fixed HyperFrames port is assumed. Agents should use their installed HyperFrames skill's launcher convention instead of these human-operated npm commands.

`viewer.html` is a small review-only host for these three scenes. It mounts each `<template>` into a shadow root, scopes the GSAP operations used by the demo, and seeks the registered timeline. It is not a general replacement for the HyperFrames runtime. HyperFrames owns the assembled preview and export.

## Files and review state

- `INPUT.md`, `BEATS.md`, `NARRATION.md`: synthetic test inputs; no upstream article approval is claimed.
- `compositions/s01.html`: a paper plan becomes an actual scene preview.
- `compositions/s02.html`: six information blocks reduce to one focus.
- `compositions/s03.html`: narration and picture are edited before assembly.
- `SCENES.md`, `review/manifest.json`: scene contracts, source/asset digests, local timing, and pending review decisions.
- `review.html`, `viewer.html`: the scene-review interface and source composition host.
- `frame.md`: official installed BlockFrame design specification.
- `review/check-summary.json`, `REVIEW.md`: measured checks and limitations.

The user explicitly chose visual-only review. Audio and spoken pacing remain pending, and visual acceptance is also pending user review. Structural checks do not approve design. An intentional dense-reading hold and the requested silence may produce craft warnings.

The screenshot below records this run, while live playback uses the current source files. See [third-party notices](THIRD_PARTY_NOTICES.md) for bundled fonts and GSAP.

![Scene states before and after each change](review/contact-sheet.jpg)
