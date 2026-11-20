---
name: record-narration
description: Record your own narration from a script using a local browser teleprompter, or resume a recording session through retake editing, audio normalization and script-assisted subtitle correction.
---

# Record Narration

Produce human-recorded narration and reviewed, timed subtitles from an existing UTF-8 script. Resolve bundled paths relative to this skill's directory; run the commands below there with absolute project paths. Treat recorded speech as the content authority and the script as context for recognition and progression. Preserve original takes, coherent improvisation and speaking speed. Remove abandoned retries when a complete replacement is identifiable. Denoising, general pause compression and TTS are outside this workflow.

## 1. Establish the session

Resolve the script and project directory from the request. For a new recording, choose `<project>/narration/recording-YYYYMMDD-HHMMSS`. For a continuation, locate the previously supplied session path before creating anything new. Its `script.txt` snapshot is the recording's reference even if the original draft has changed.

**Ready to proceed:** the script and session path are known, and a continuation uses the existing session rather than a replacement.

## 2. Open the recorder and let the user record

Start a long-running process and retain its process handle:

```bash
python3 scripts/recorder.py --script /absolute/path/NARRATION.md \
  --session /absolute/path/project/narration/recording-YYYYMMDD-HHMMSS --port 0
```

Give the user the printed browser URL, including its token fragment, and the session path. Ask them to choose a microphone, start recording, stop and listen, then select a take and click “使用选中版本，交给 Codex”. They can pause/resume or record another whole take. After saving, they can drag across the waveform and play that selection to inspect short retries. Microphone permission and recording controls belong to the user.

Leave the service running and yield the chat while they record. Explain that they must return and say “录好了，继续处理”; the page saves a handoff file but does not send a chat message. If opening, saving or recording fails, read [recovery.md](references/recovery.md).

**Recording submitted:** after the user resumes, `session.json` has status `ready`, its selected take is complete, and `handoff.json` names that same take and an existing audio file. Otherwise report the current state and help them finish selecting/submitting; a verbal “done” alone is insufficient. Once submitted, processing can continue without the recorder service.

## 3. Prepare audio and transcribe

Use an existing compatible environment when available. Recording needs Python 3.10+; processing needs `ffmpeg` and `ffprobe`, plus this skill’s `requirements.txt` installed in a Python 3.11/3.12 virtual environment outside the skill directory. If dependencies are missing, or only part of processing succeeded, read [recovery.md](references/recovery.md).

Tell the user that first use may download model weights; audio processing and transcription run locally. Choose the spoken language (`zh` for Chinese, `auto` when uncertain) and a new output directory:

```bash
/path/to/venv/bin/python scripts/process_audio.py prepare \
  --session /absolute/path/session --output /absolute/path/processed-v1 \
  --transcribe --language zh
```

This uses ffmpeg-normalize to measure and apply a uniform gain, then transcribes `narration.wav`. Preserve the loudness report: peak headroom can require a quieter target. A dynamic fallback stops export rather than amplifying quiet passages separately. Normalization preserves relative levels; it does not remove noise. Use `scripts/process_audio.py --help` and its subcommand help for alternate inputs or model settings.

**Ready for editing:** the WAV is decodable and has positive duration; `transcript.raw.json` contains nonempty timed cues, and `subtitles.raw.srt` exists. Retain raw outputs. A failed transcription is unfinished work, even if audio normalization succeeded.

## 4. Resolve retakes before correcting subtitles

For every continuous narration take, read [retakes.md](references/retakes.md) and perform its review before correcting recognition text, including when the transcript appears fluent. This reference defines evidence, review coverage and handling of unavailable audio understanding. Preserve the uncorrected transcript as evidence throughout editing.

**Editing stage complete:** `REVIEW.md` accounts for review coverage, candidate decisions and every user-reported interval under the reference's criteria. Applied cuts have an edit report and the resulting audio has a fresh transcript. Unresolved alternatives remain in the audio and are identified for review. With no cuts, reuse step 3's audio and transcript. Correction below always uses the transcript of the final audio.

## 5. Correct recognition against the script

Read the complete script snapshot and final transcript. Correct recognition errors and punctuation using audio evidence and context; preserve intelligible spoken wording, including off-script additions, omissions and changed examples. A difference from the script alone is not a recognition error. Apply the author-intent and capability rules in the retake reference to unresolved passages, and record their IDs, times and disposition in `REVIEW.md`.

Write `corrections.json` as an array of changed cue IDs and replacement text; use `[]` if no changes are needed. For example, when cue 3 clearly misrecognized the spoken product name:

```json
[{"id": 3, "text": "然后交给 Codex 处理。"}]
```

Apply the reviewed changes:

```bash
python3 scripts/process_audio.py correct \
  --transcript /absolute/path/processed-v1/transcript.raw.json \
  --corrections /absolute/path/processed-v1/corrections.json \
  --output /absolute/path/processed-v1/reviewed
```

**Correction complete:** every cue has been considered; reviewed cue IDs and times match the raw cues, all text changes have evidence, and unresolved differences are documented. The corrected JSON's `segments` contain reviewed text; its `words` retain raw recognition evidence. Downstream subtitles must use the reviewed segments or exported SRT.

## 6. Verify and hand off

Read the exported subtitles and check increasing, nonoverlapping cue times within the final WAV's duration, allowing only millisecond rounding at the end. If adjacent cues split a word, merge them in a separate delivery export using existing outer cue boundaries; retain source cue IDs and raw word times. Record subtitle checks in `REVIEW.md` alongside the audio review defined in the retake reference.

Deliver clickable absolute paths to the final WAV, final subtitle SRT and corresponding transcript JSON, script snapshot and review notes; include the edit report when cuts were made. If cues were merged, link the delivery exports and retain the reviewed originals as provenance. Keep original takes and chunks available. Pass these artifacts to the next production step; replacing an existing project's audio requires the user's requested scope to cover that change.

**Delivery complete:** audio and subtitles are usable together, and the delivery carries the audio-review status defined in the retake reference. Pending audio review is stated in the final response as well as the review notes.
