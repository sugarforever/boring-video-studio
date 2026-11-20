---
name: record-narration
description: Record a human voice reading a narration script in a local browser teleprompter, preserve takes, normalize audio, generate timed subtitles, and correct recognition errors against the script. Use for recording your own narration; use record-terminal for terminal footage and to-narration for writing a script.
---

# Record Narration

Turn an existing UTF-8 narration file into human-recorded audio and reviewed subtitles. Run bundled commands from this skill's resolved directory, not an assumed repository checkout. The recorder requires Python 3.10+ and a browser with microphone support. Audio processing requires FFmpeg. Local transcription additionally requires faster-whisper; no cloud API key is needed.

## Start a recording

1. Resolve the user's script and video project. Choose a new session directory, normally `<project>/narration/recording-YYYYMMDD-HHMMSS`. For resuming, reuse the exact session directory: its `script.txt` snapshot is authoritative. Changing the draft does not replace an existing session's snapshot.
2. Start the server as a long-running terminal process:

   ```bash
   python3 scripts/recorder.py --script /absolute/path/NARRATION.md --session /absolute/path/project/narration/recording-20261120-143000 --port 0
   ```

   The command prints and opens a loopback URL with a session access token in its fragment. If automatic opening fails, open that exact URL in the user's browser. A plain rendered HTML preview may block microphone access; use Chrome or Safari on the Mac instead. Never automate microphone consent or record without the user's interaction.
3. Explain briefly: choose a microphone, click start, pause/resume as needed, stop and listen, then select a take and click “使用选中版本，交给 Codex”. Font size, scrolling speed and manual scrolling are independent of recording. V1 records whole takes; another recording creates a new take and preserves previous ones.
4. Leave the service running while the user records. Give the user the browser URL and session path, then let them record and reply “录好了，继续处理”. The page writes `handoff.json` and sets `session.json` status to `ready`; it does not itself send a message to the chat. A later agent can resume from these files without the original server process. Read status when the user resumes; a missing handoff means recording has not been submitted yet.

Audio chunks are written about every two seconds and retained beside the assembled original. After a browser interruption, reopen the same session and use the recovery button for the incomplete take, then listen before selecting it. Recovery includes only successfully saved chunks and may omit the tail. If saving fails while the page is still open, use its original-audio download link. Keep original takes and chunk files until the user has verified the result.

## Process the selected take

Check `ffmpeg` and `ffprobe`. If unavailable, explain how to install FFmpeg (`brew install ffmpeg` on macOS). Recording works without these tools.

For local transcription, use a Python 3.11/3.12 virtual environment outside the skill folder, for example `<project>/.venv-narration`. Install `faster-whisper>=1.1,<2` there when needed. Tell the user that first use downloads model weights; recorded audio stays local. Default multilingual `small` runs on CPU with int8; use a local model directory or another multilingual model if the user requests it. Model download or dependency failure must be reported, not replaced with invented subtitles.

```bash
/path/to/venv/bin/python scripts/process_audio.py prepare \
  --session /absolute/path/session \
  --output /absolute/path/project/narration/processed-v1 \
  --transcribe --model small --language zh
```

`prepare` reads the submitted handoff, retains the original, normalizes loudness using FFmpeg (`I=-16`, `TP=-1.5`, `LRA=11`), and creates mono 48 kHz PCM WAV. It preserves speed and content. Automatic noise reduction, silence cuts and retake selection are outside v1. `--audio /absolute/path/backup.webm` can replace `--session` when recovering a downloaded recording.

If the normalized WAV exists but transcription failed, resume without reprocessing:

```bash
/path/to/venv/bin/python scripts/process_audio.py transcribe \
  --audio /absolute/path/processed-v1/narration.wav \
  --output /absolute/path/processed-v1 --model small --language zh
```

Use `--language auto` for language detection. Transcription produces `transcript.raw.json` with original word timestamps and numbered subtitle cues, and `subtitles.raw.srt`. Existing outputs are protected; use new output directories for another version. Never time subtitles from the script alone.

## Review recognition errors

Read the session's `script.txt` and the raw transcript. Correct clear recognition errors, terminology, names and punctuation. Actual recorded speech determines subtitle content: preserve spoken paraphrases and omissions. List uncertain names, numbers, negations, or substantial differences in `REVIEW.md` with cue IDs and times. Ask for clarification when the script cannot establish what was spoken. Do not claim to have listened if only transcript and measurements were inspected.

Write an explicit `corrections.json` array (empty if no changes):

```json
[{"id": 3, "text": "Use the words actually spoken, correcting recognition errors."}]
```

Apply it with the bundled helper, which preserves cue IDs and timing and retains raw recognition evidence:

```bash
python3 scripts/process_audio.py correct \
  --transcript /absolute/path/processed-v1/transcript.raw.json \
  --corrections /absolute/path/processed-v1/corrections.json \
  --output /absolute/path/processed-v1/reviewed
```

Check cue order, audio duration, subtitle timing and reported differences. Deliver clickable paths to `narration.wav`, `reviewed/subtitles.srt`, `reviewed/transcript.corrected.json`, and `REVIEW.md`. State whether human playback is still needed. Hand these paths and the script snapshot to subsequent video production; do not silently replace a project's existing audio or regenerate human narration with TTS.
