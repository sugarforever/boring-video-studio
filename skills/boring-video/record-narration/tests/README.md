# Recorder development checks

Run from the repository root. Use the processing virtual environment with this skill's requirements installed; FFmpeg/ffprobe must be on PATH.

```bash
python -m unittest discover -s skills/boring-video/record-narration/tests -p 'test_*.py'
node --check skills/boring-video/record-narration/assets/recorder.js
node --check skills/boring-video/record-narration/assets/ui.js
node --check skills/boring-video/record-narration/assets/camera-monitor.js
```

## Chrome integration

Install Playwright outside the repository; the tests use installed Chrome and synthetic media devices. Set `PLAYWRIGHT_MODULE` to its absolute module directory and optionally `NARRATION_PYTHON` to a Python executable. Run:

```bash
RECORDER_ONLY=1 node skills/boring-video/record-narration/tests/browser.cjs
CAMERA_TEST=1 RECORDER_ONLY=1 node skills/boring-video/record-narration/tests/browser.cjs
node skills/boring-video/record-narration/tests/reading.cjs
```

The first two cover audio-only/camera recording, pause removal, playback, save retry, recovery and handoff. The camera branch also checks permission failure, device disconnection and release, dragging, aspect ratios and streaming WebM export. The reading test checks viewport geometry, text/camera layering, preview track continuity, saved preferences and mobile bounds.

`RECORDER_ONLY=1` skips normalization of constant-level fake input; Python tests exercise real FFmpeg normalization separately. Synthetic devices do not validate real hardware, Safari or human lip sync. Recovered partial WebM may emit FFprobe's premature-end warning; dependency deprecation/resource warnings may also appear.

## Manual hardware acceptance

1. Start an audio-only take; verify existing recording/playback/handoff.
2. Enable camera; deny permission, then grant it and retry. Check camera choice, framing and preview orientation.
3. Record speech with visible hand claps at start/end; pause for several seconds, resume, stop. Confirm both device indicators turn off and playback stays aligned.
4. Save two takes, reload, choose a take and submit. Verify its video matches its script and sound. Exercise save retry and recover a partially uploaded take.
5. Disconnect the camera during recording; confirm automatic saving stops both devices and leaves a visible warning before another take.
6. Process the AV container, remove a deliberate retry, export camera and a corner overlay. Review lip sync around the cut and ensure the camera does not cover important content.

