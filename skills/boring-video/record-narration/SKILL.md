---
name: record-narration
description: Record your own narration from a script using a local browser teleprompter, or resume a recording session through retake editing, audio normalization and script-assisted subtitle correction.
---

# Record Narration

Produce human-recorded narration and reviewed, timed subtitles from an existing UTF-8 script. Resolve bundled paths relative to this skill's directory; run the commands below there with absolute project paths. Treat recorded speech as the content authority and the script as context for recognition and progression. Preserve original takes, coherent improvisation and speaking speed. Remove abandoned retries when a complete replacement is identifiable. General pause compression and TTS are outside this workflow; optional low-level background suppression is defined in step 3.

## 1. Establish the session

Resolve the script and project directory from the request. For a new recording, choose `<project>/narration/recording-YYYYMMDD-HHMMSS`. For a continuation, including draft revisions and repeated recording, reuse the previously supplied session path. The session's `script.txt` is the current draft; each take retains its own script snapshot. Set the recording’s reference script once: for a submitted session take, use its script path in `handoff.json`; for directly imported audio, use the supplied matching script, or the backup take’s snapshot as defined in [recovery.md](references/recovery.md). Use that reference for retake review, correction and delivery.

**Ready to proceed:** the script and session path are known, and a continuation uses the existing session rather than a replacement.

## 2. Open the recorder and let the user record

Start a long-running process and retain its process handle:

```bash
python3 scripts/recorder.py --script /absolute/path/NARRATION.md \
  --session /absolute/path/project/narration/recording-YYYYMMDD-HHMMSS
```

Rerunning this command for the same session reuses its running service and URL without opening another tab. When the user revises the draft, run the same command with `--update-script`; the existing page picks up the new text while idle. Finish or recover incomplete takes before updating; for unrecoverable takes, follow [recovery.md](references/recovery.md). Keep the session directory and `recorder-server.json` private; the latter contains the local access token. If the service has stopped, restart it on the same port. An occupied port is an error to resolve, rather than a reason to silently select a new port.

**Recorder ready:** the service is reachable for the intended session. After a draft update, verify that the existing page displays the requested text and previous takes retain their script snapshots. If the page cannot be inspected, report the display check as pending rather than claiming the new draft is visible.

Give the user the printed browser URL, including its token fragment, and the session path. Ask them to choose a microphone, start recording, stop and listen, then select a take and click “使用选中版本，交给 Codex”. They can pause/resume or record another whole take. After saving, they can drag across the waveform and play that selection to inspect short retries. Microphone permission and recording controls belong to the user.

Leave the service running and yield the chat while they record. Explain that they must return and say “录好了，继续处理”; the page saves a handoff file but does not send a chat message. If opening, saving or recording fails, read [recovery.md](references/recovery.md).

**Recording submitted:** after the user resumes, `session.json` has status `ready`, its selected take is complete, and `handoff.json` names that same take and an existing audio file. Otherwise report the current state and help them finish selecting/submitting; a verbal “done” alone is insufficient. Once submitted, processing can continue without the recorder service.

## 3. Prepare audio and transcribe

Use an existing compatible environment when available. Recording needs Python 3.10+; processing needs `ffmpeg` and `ffprobe`, plus this skill’s `requirements.txt` installed in a Python 3.11/3.12 virtual environment outside the skill directory. If dependencies are missing, or only part of processing succeeded, read [recovery.md](references/recovery.md).

When the user requests noise reduction or reports background voices, read [background.md](references/background.md) before preparation. It defines optional low-level suppression, reference exports and a listening gate; it does not promise separation of overlapping speakers.

Tell the user that first use may download model weights; audio processing and transcription run locally. Choose the spoken language (`zh` for Chinese, `auto` when uncertain) and a new output directory:

```bash
/path/to/venv/bin/python scripts/process_audio.py prepare \
  --session /absolute/path/session --output /absolute/path/processed-v1 \
  --transcribe --language zh
```

This uses ffmpeg-normalize to measure and apply a uniform gain, then transcribes `narration.wav`. Preserve the loudness report: peak headroom can require a quieter target. A dynamic fallback stops export rather than amplifying quiet passages separately. Normalization preserves relative levels; it does not remove noise. Optional background suppression is a separate preceding stage with its own review gate. Use `scripts/process_audio.py --help` and its subcommand help for alternate inputs or model settings.

**Recognition saved:** `transcript.raw.json` preserves the ASR's original segments and word timings before SRT export. Raw cues may exceed delivery limits; `transcript.initial.json` and `subtitles.initial.srt` apply the selected limits immediately after recognition. **Ready for editing:** the WAV is decodable with positive duration, raw cues are nonempty and usable for locating speech, and both raw and initial SRT exports exist. If export fails after recognition is saved, follow the saved-transcript branch in [recovery.md](references/recovery.md); retain the evidence and repair its timing rather than repeating successful recognition. Final subtitle layout is a separate gate in step 6.

## 4. Resolve retakes before correcting subtitles

Before subtitle correction, follow [retakes.md](references/retakes.md), even when transcription is fluent. Preserve raw recognition as evidence.

**Supported edits exported:** cuts have an edit report and a fresh transcript; without cuts, reuse step 3's artifacts. The audio-review ledger accounts for candidates, user reports and remaining gaps; `REVIEW.md` summarizes its status. Correct only the final audio's transcript.

## 5. Correct recognition against the script

Read the reference script established in step 1 and the complete final transcript. Correct recognition errors and punctuation using audio evidence and context; preserve intelligible spoken wording, including off-script additions, omissions and changed examples. A difference from the script alone is not a recognition error. Apply the author-intent and capability rules in the retake reference to unresolved passages, and record their IDs, times and disposition in `REVIEW.md`.

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

Read [subtitles.md](references/subtitles.md) and generate delivery subtitles from the corrected transcript. This required pass defines the single-line policy, natural boundary review, reading-speed checks and timing provenance. Follow its acceptance criteria before claiming subtitle delivery is complete. Record its results in `REVIEW.md` alongside the audio review defined in the retake reference.

Deliver clickable absolute paths to the final WAV, final subtitle SRT and corresponding transcript JSON, script snapshot and review notes; include the edit report when cuts were made. If cues were merged, link the delivery exports and retain the reviewed originals as provenance. Keep original takes and chunks available. Pass these artifacts to the next production step; replacing an existing project's audio requires the user's requested scope to cover that change.

**Delivery status:** report the audio-review result under the retake reference's completion criteria alongside subtitle verification. Unfinished speech review remains incomplete work in both `REVIEW.md` and the final response.
