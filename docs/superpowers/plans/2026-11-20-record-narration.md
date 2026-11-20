# Record Narration v1 Implementation Plan

**Goal:** Record a supplied narration script in a local teleprompter, preserve takes, and hand final audio and timed subtitles to the agent.

**Architecture:** A dependency-free Python loopback server serves a static recorder and stores numbered audio chunks and session metadata. A separate CLI uses FFmpeg for loudness normalization and optional faster-whisper for local transcription. The agent corrects recognized text against the immutable script snapshot while preserving actual speech and final-audio timing.

**Scope:** Continuous recording with pause/resume, microphone selection, input meter, timer, adjustable teleprompter, multiple takes, playback, selected-take handoff. Preserve original audio. Save chunks during recording; recover interrupted takes. No automatic semantic cuts, denoising, or speed changes in v1.

**Files:** `skills/boring-video/record-narration/{SKILL.md,scripts/recorder.py,scripts/process_audio.py,assets/index.html,assets/recorder.js,tests/test_recorder.py,tests/test_process_audio.py}`; usage in root README.

## Tasks

- [x] Write failing storage/HTTP tests: script snapshot, chunk idempotency, interrupted recovery, selection, ready handoff, origin/auth checks, isolation from arbitrary paths.
- [x] Implement loopback service and recorder UI. Persist each chunk, serialize uploads, retain download fallback, stop tracks on completion. Hand off only finalized selected takes.
- [x] Write failing processing tests: timestamp rounding, subtitle corrections, malformed input, output isolation, real FFmpeg normalization.
- [x] Implement processing CLI: normalize to mono 48 kHz WAV, optional local transcription to JSON/SRT, guarded correction application, explicit dependency failures.
- [x] Document skill invocation, dependency installation, human recording boundary, wait/resume, correction rules and downstream handoff.
- [x] Run Python tests, JavaScript syntax and skill validation; exercise browser recording with synthetic microphone if browser automation is available. Report live-microphone and model-download limitations honestly.

## Validation evidence

- 12 Python tests passed, including real FFmpeg conversion and HTTP storage/auth flows.
- Chrome integration passed with a synthetic microphone: default-speed auto-scroll,
  pause/resume, decoded WAV duration, playback, selected-take handoff, upload failure
  followed by reload and recovery, and script text escaping.
- Local faster-whisper tiny transcribed English and Chinese speech samples; the default small model also completed a Chinese transcription;
  text-correction CLI generated reviewed JSON/SRT without changing timing.
- JavaScript syntax and skill frontmatter validation passed.
- Independent review found and resolved fractional scrolling and upload-gap recovery bugs.
- Human microphone quality and Safari recording remain to be verified by live use.
