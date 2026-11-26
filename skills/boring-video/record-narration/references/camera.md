# Camera recording and picture-in-picture delivery

Read this branch when the user requests webcam capture, when `handoff.json` has `video`, or when editing/delivering a camera take.

## Capture

In the recorder menu, enable “同步录制摄像头” and select the camera. Recording starts only when the user clicks “开始录音” and grants microphone/camera permissions. Drag the live monitor by its picture to reposition it; the focused picture also supports arrow keys. The ratio selector offers 16:9, 4:3, 1:1 and 9:16 with centered preview cropping. Position and preview ratio are remembered in this browser and clamped within the visible area above recording controls when resized. The live monitor is mirrored for framing; original recording dimensions and orientation remain intact. Default capture requests 1280×720 at 30 fps; `capture` records the actual dimensions/rate. Camera device labels may appear only after the first permission grant; stop, choose the newly labeled camera, and record another take if necessary.

One recorder owns both tracks, so pause/resume, chunk retries and interruption recovery share a timeline. Stop releases both devices. If permission is denied, resolve the browser permission or disable camera to record audio only. A disconnected device stops capture and warns that the saved portion needs review. Recovery preserves only the contiguous chunks saved before interruption; inspect both picture and sound, especially the tail.

**Capture submitted:** the selected take is complete and `handoff.json` contains existing `audio` and `video` paths for that take. Both paths intentionally name the same original AV container; `process_audio.py prepare --session ...` decodes its audio to the normal WAV workflow. Retain the original container and chunks. Audio-only sessions keep their existing handoff schema.

## Editing and export

Complete audio review, normalization, retake cuts and subtitles through the main skill. Use `edit_audio.py`'s `edit-report.json` from the same original take to apply every retake cut to the picture. Supply the matching final reviewed WAV as the export's audio. Without cuts, omit `--edit-report`; normalization and optional background suppression preserve duration. Chain all cuts into one report against the original timeline; a report against an already edited intermediate is insufficient.

Export a standalone camera clip:

```bash
python3 scripts/export_camera.py \
  --video /absolute/session/takes/TAKE/original.webm \
  --audio /absolute/edited/narration.edited.wav \
  --edit-report /absolute/edited/edit-report.json \
  --output /absolute/delivery/author.mp4
```

Use `--aspect 1:1` (or `16:9`, `4:3`, `9:16`) to center-crop the exported camera to the chosen ratio. The default `--aspect source` retains original framing. Preview position/ratio are local viewing preferences, independent of the exported composition: explicitly choose the export ratio and corner.

For picture-in-picture, add `--background /absolute/content.mp4 --corner bottom-left`. The content video must already follow the final narration timeline and cover its duration. The exporter uses only the reviewed WAV as sound and trims delivery to its duration. Choose `top-left`, `top-right`, `bottom-left` or `bottom-right`; `--width .25` sets the window width relative to the content frame and `--margin 24` sets the inset. Inspect the result for obscured text/subtitles and agree the placement with the user's intended composition. Outputs are H.264/AAC MP4 and require FFmpeg/ffprobe. Use a fresh output path. If the window exceeds either content dimension (especially with portrait footage), reduce `--width` or `--margin`.

The exporter checks source/edit/audio durations (0.2 s tolerance for browser container and frame rounding), validates ordered cuts, and leaves originals intact. Duration checks cannot prove take identity: verify `handoff.json`, the processing source and the edit report all refer to the same take. Video cuts are frame-quantized; manually inspect lips at the beginning, after pause/resume, each cut and near the end. Report untested hardware/browser compatibility explicitly.

**Camera delivery:** link the original AV container, exported author clip or composed video, final WAV/subtitles and edit report. Confirm picture and sound remain aligned at the reviewed points. Until that review is done, mark camera sync review pending rather than declaring delivery verified.

## Manual hardware acceptance

1. Start an audio-only take; verify existing recording/playback/handoff.
2. Enable camera; deny permission, then grant it and retry. Check camera choice, framing and preview orientation.
3. Record speech with visible hand claps at start/end; pause for several seconds, resume, stop. Confirm both device indicators turn off and playback stays aligned.
4. Save two takes, reload, choose a take and submit. Verify its video matches its script and sound. Exercise save retry and recover a partially uploaded take.
5. Disconnect the camera during recording; confirm the warning remains after saved-part recovery.
6. Process the AV container, remove a deliberate retry, export camera and a corner overlay. Review lip sync around the cut and ensure the camera does not cover important content.

## Automated development checks

Run the recorder Python suite in the processing environment and syntax-check `assets/recorder.js`. The optional `tests/browser.cjs` uses installed Chrome via Playwright:

```bash
CAMERA_TEST=1 RECORDER_ONLY=1 \
PLAYWRIGHT_MODULE=/absolute/path/node_modules/playwright \
  node tests/browser.cjs
```

Omit `CAMERA_TEST` to run the audio-only regression. Simulated devices test recording, pause removal, waveform/video playback, save retry, reload recovery, handoff, permission-denial handling, device-disconnect handling and release. `RECORDER_ONLY=1` skips normalization of the constant-level fake input; Python tests separately cover normalization. It does not validate real hardware, Safari or human lip sync.
