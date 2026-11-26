# Narration camera recording implementation plan

**Goal:** Optional synchronized webcam capture during narration, with reviewed camera edits and corner picture-in-picture delivery.

**Architecture:** One MediaRecorder captures microphone and camera into one original AV container. Existing authenticated chunk upload, retry, recovery and handoff remain authoritative. Audio processing decodes this container. A separate FFmpeg exporter trims camera frames using the audio edit report and replaces the camera's audio with the reviewed WAV; optional background video produces picture-in-picture.

**Constraints:** Default remains audio only. No camera access before an explicit user action. Preserve original takes and never overwrite exports. Camera failure stops capture and reports incomplete input. Mirror only the live preview. No dependency added to the recording server. Work from current origin/main in an isolated checkout; do not include pending segmented-recording edits.

## Tasks

- [x] Test and implement video MIME storage, metadata, authenticated playback and handoff; preserve legacy audio sessions.
- [x] Test and implement camera toggle/device selection, live preview, AV playback and single-recorder pause/resume, save retries and interruption recovery.
- [x] Test and implement camera export using validated edit ranges and reviewed audio; optional corner overlay on content video. Reject mismatched duration, missing video and overwrite.
- [x] Document recording, editing, picture-in-picture export and a manual hardware test checklist. Run Python suite and Chrome fake-media integration, review diff, push branch and open PR.

## Review focus

Permission denied must leave no active capture; audio-only operation must remain available. Device disconnect must preserve saved chunks and warn. Camera takes must survive reload and authenticated recovery. Pauses and retake edits must affect both media tracks. Exports must reject incompatible durations rather than silently truncate.

Validation: Python suite, Chrome audio-only and fake-camera integration; multi-cut frame drift regression and delayed AV-start regression. Real hardware/Safari acceptance remains for the user.
