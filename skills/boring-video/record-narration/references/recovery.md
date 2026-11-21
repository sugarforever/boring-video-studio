# Recording and processing recovery

Use the matching branch below; continue the main workflow once its completion condition is satisfied.

## Recorder cannot open or access the microphone

Open the exact printed URL in Chrome or Safari on the user's Mac. An embedded HTML preview may block microphone access. Let the user grant permission. If the original process ended, restart `scripts/recorder.py` with the existing session's `script.txt` as `--script` and the same `--session`; use the newly printed URL because restarting changes the access token.

**Recovered:** the page displays the session's script and the user can start recording.

## Browser interrupted or saving failed

While the page is still open, use its original-audio download link if automatic saving fails. After an interruption, reopen the same session and use the incomplete take's recovery button. Recovery joins only successfully saved chunks and may omit the tail. Have the user listen before selecting and submitting the recovered take. Preserve the original takes and chunks.

For a downloaded backup, run `prepare --audio /absolute/path/backup.webm` instead of `--session`; retain the session's script snapshot for correction. Confirm the user chose this backup before processing it.

**Recovered:** the user has selected a playable saved take or backup. For an ordinary session, submission must still satisfy the main workflow's handoff checks.

## Missing dependencies

Install FFmpeg on macOS with `brew install ffmpeg` when Homebrew is available. For transcription, create or reuse a project virtual environment:

```bash
python3.11 -m venv /absolute/path/project/.venv-narration
/absolute/path/project/.venv-narration/bin/python -m pip install -r /absolute/path/skill/requirements.txt
```

Python 3.12 is also suitable. If installation or model download fails, report the actual failure and retain any completed audio. A local model directory can be passed with `--model` when network downloads are unavailable.

**Recovered:** the selected interpreter imports `faster_whisper`, `ffmpeg_normalize` and `jieba`, and `ffmpeg` and `ffprobe` are available to the processing command.

## Recognition saved but subtitle export failed

Inspect `transcript.raw.json` and the reported error first. This file is saved before SRT export, retaining original ASR segments and word timings. Keep it unchanged. For invalid cue times, create an aligned version using the final audio and record the changed intervals and evidence. Continue correction from that version once its cues are valid. If raw cues are usable but the initial limited export failed, use `delivery` on the saved raw or aligned JSON to recover a limited subtitle draft in a new directory; record that output as the initial draft. Follow [subtitles.md](subtitles.md) for layout failures rather than starting a new recognition run.

**Recovered:** raw evidence remains available, repaired cue times have supporting evidence, and a usable SRT corresponds to the transcript used for correction. With no available alignment capability, retain the evidence and report the specific pending intervals.

## WAV exists but recognition did not finish

When no saved transcript exists, resume from the final WAV rather than running normalization again:

```bash
/path/to/venv/bin/python scripts/process_audio.py transcribe \
  --audio /absolute/path/processed-v1/narration.wav \
  --output /absolute/path/processed-v1 --language zh
```

The helpers protect existing outputs. Preserve partial results and use a new output directory for another recognition attempt.

**Recovered:** a nonempty original ASR transcript and corresponding raw SRT exist for the final WAV. Final delivery segmentation remains a later step.
