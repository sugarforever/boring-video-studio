# Webcam narration

## Capture and reading

Enable “同步录制摄像头” in the recorder menu and select a device. The user starts capture and grants microphone/camera permission. Device labels may appear only after the first grant; stop and choose the labeled device if needed. One recorder captures both tracks, so pause, resume, saving and recovery share a timeline. Stop releases both devices. For interrupted takes, inspect the recovered picture and sound, especially the tail.

The default “靠近镜头” view keeps roughly three lines near the top-center lens position. Adjust “栏宽” to reduce horizontal eye movement, or turn this view off for the full script. Font, manual scrolling, auto-scroll and pause behavior apply to both views.

The preview supports dragging, keyboard arrows when focused, and a ratio selector. “摄像头居中” aligns it beneath the laptop lens. “文字置顶” places it under readable, translucent text; turn that option off temporarily to reposition the preview or reach controls covered by text. The recording-bar camera icon hides/reveals the preview while capture continues on the same tracks.

These reading and preview preferences are saved locally. They change neither the original footage nor the exported composition. Only the live preview is mirrored; the original keeps its camera orientation and dimensions.

**Submitted:** satisfy the main skill's submission gate, then verify that `handoff.json` also contains an existing `video` path for the selected take. Its `audio` and `video` intentionally name the same original AV container. `process_audio.py prepare --session ...` extracts its audio through the normal workflow. Preserve the container and chunks.

## Synchronized export

Complete the main skill's audio and subtitle review first. Match the handoff, processing source and edit-report source to the same take; matching durations alone cannot prove identity. Use the final reviewed WAV as export audio.

When retakes were cut, supply `edit_audio.py`'s `edit-report.json` in the original take's time coordinates. Combine repeated edits into one original-timeline cut plan; a report against an already edited intermediate cannot drive the original camera. Without cuts, omit `--edit-report`; normalization and background suppression preserve timing.

```bash
python3 scripts/export_camera.py \
  --video /absolute/session/takes/TAKE/original.webm \
  --audio /absolute/edited/narration.edited.wav \
  --edit-report /absolute/edited/edit-report.json \
  --output /absolute/delivery/author.mp4
```

For picture-in-picture, add `--background /absolute/content.mp4 --corner bottom-left`. The content video must already follow the reviewed narration timeline and cover its duration. Export uses the reviewed WAV as sound, discards background/original sound and ends with the narration.

Choose framing independently of the preview: `--aspect 1:1` center-crops the camera; the default retains source framing. Consult `--help` for the other ratios, corners, width and inset controls. Use a fresh output path. If the window exceeds the content bounds, reduce its width or inset. Export requires FFmpeg/ffprobe and produces H.264/AAC MP4.

**Delivered:** inspect lip sync at the beginning, after pause/resume, around every cut and near the end; frame/duration checks alone are insufficient. Check that the overlay leaves important content and subtitles visible. Link the original AV container, camera/composed export, final audio/subtitles and any edit report. Keep sync review pending for any unchecked sync point. Report untested hardware/browser combinations separately in the review notes.
