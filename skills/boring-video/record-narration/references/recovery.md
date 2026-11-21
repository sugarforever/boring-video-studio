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

## WAV exists but transcription failed

Resume from the final WAV rather than running normalization again:

```bash
/path/to/venv/bin/python scripts/process_audio.py transcribe \
  --audio /absolute/path/processed-v1/narration.wav \
  --output /absolute/path/processed-v1 --language zh
```

The helpers protect existing outputs. For a fresh version, use a new output directory instead of deleting previous results. If raw JSON or SRT already exists from a partial write, preserve it and transcribe into a new directory.

**Recovered:** both nonempty raw transcript cues and the corresponding SRT exist for the final WAV.
