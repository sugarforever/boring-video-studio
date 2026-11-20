# Retake editing

Review every continuous narration take after the first transcription. The agent makes editing decisions; the helper only executes cut times.

## Evidence and coverage

Discover available tools for spoken-audio analysis and establish whether they can actually analyze the recording, such as through an audio-capable model or human listening. Locating retries and their boundaries is agent work; proceed from the supplied audio and original script without requiring author-provided word lists or timestamps. Playback, waveform inspection and another speech-to-text pass are different capabilities; report which was used.

The recording establishes what the author said; the script provides topic and terminology context, the original transcript locates candidates, and acoustic measurements help place boundaries. Speech recognition can omit or merge repeated syllables and partial-word restarts. Treat fluent transcription as a candidate-generation result, not evidence that its corresponding audio is free of retries. Preserve raw recognition until editing decisions are recorded.

In `REVIEW.md`, record the source audio path and duration, inspected time ranges, method and evidence for each range, and the remaining coverage gaps. Check whole-sentence restarts, short repeated words or syllables, abandoned word openings, immediate self-corrections, and restarts after a pause. Preserve deliberate emphasis and legitimate repetition.

Inspect every user-reported interval with its surrounding speech, even when recognition shows no repeat. Record the reported issue, local evidence and disposition. If a report identifies final-output time, use the edit map to locate the source interval. A report is resolved only by a supported keep/remove decision or a specific unresolved issue with its evidence and capability gap, not by a clean transcript.

When spoken-audio analysis is unavailable, continue safe, supported edits and export timestamped local previews for uncertain passages. Report the missing capability rather than asking the author to locate repeated syllables as a workaround. Retain ambiguous audio; report uninspected ranges without inventing listening results. Repeated transcription may add evidence but does not close an audio-review coverage gap.

## Decide what survives

Map each candidate to the spoken narrative; use the script passage where one exists. Off-script speech still needs the same review. Record source start/end, recognized words, completeness, available audio evidence and a keep/remove/pending decision. A partial sentence followed by a replacement that repeats its beginning and continues is strong retry evidence. Check short retries locally even when both attempts were collapsed into one recognized word.

Classify the candidate by how the speech progresses:

- **Retry:** an abandoned attempt is replaced by another rendering of the same thought. Keep the complete, coherent attempt and remove only the discarded speech, preserving unique content.
- **Improvisation:** the author adds an explanation, changes an example or wording, or omits scripted material while continuing coherently. Retain it and subtitle the actual speech; closeness to the script does not rank an attempt higher.
- **Intent conflict:** incompatible substantive statements remain without a clear spoken correction. Preserve the alternatives and flag the specific meaning decision. Ask the author only when their intended claim is needed to decide the edit, rather than to identify which syllable was repeated.

Explicit self-corrections can change a name, number or negation; retain the corrected expression when the speech makes that replacement clear. The last attempt is not automatically preferred, and vocal naturalness requires audio evidence.

**Decisions recorded:** each candidate and user report has a disposition, evidence and source interval; unique intended content stays in order, and inspected versus uninspected coverage is explicit. This permits a draft export, not a claim that all retries are removed.

## Place and execute cuts

Use word times from the analyzed source WAV's raw transcript. Put boundaries in gaps around the abandoned attempt; preserve the preceding and following word's full attack/tail and a short breathing margin. Waveform or FFmpeg `silencedetect` can corroborate gaps; silence alone does not establish that speech is disposable. Retain normal pauses outside the retry.

Write `retake-cuts.json` as an ordered, nonoverlapping array in **source seconds**, with a reason per interval. Example: a discarded attempt occupies 9.02–12.56 seconds and the replacement speech begins near 13.92; gaps around these words permit:

```json
[{"start": 8.6, "end": 13.7, "reason": "Discard abandoned first attempt; retain the complete replacement."}]
```

These are illustrative times, not defaults. Apply only the current recording's measured boundaries:

```bash
python3 scripts/edit_audio.py --audio /absolute/path/processed-v1/narration.wav \
  --cuts /absolute/path/retake-cuts.json --output /absolute/path/edited-v2
```

The source must be the mono 48 kHz PCM16 WAV used for the transcript. The helper preserves it, applies brief join fades without overlapping speech, and writes `narration.edited.wav` plus `edit-report.json` with the source hash, cuts and source-to-output map. A new output directory preserves prior versions.

**Export complete:** the edit report matches the chosen source and every planned cut; decoded output duration equals retained source duration.

## Rebuild final timing

Transcribe the edited audio in a new directory. The analyzed source was already loudness-normalized; preserve its level instead of automatically normalizing it a second time:

```bash
/path/to/venv/bin/python scripts/process_audio.py transcribe \
  --audio /absolute/path/edited-v2/narration.edited.wav \
  --output /absolute/path/edited-v2/final --language zh
```

Continue recognition correction against this new transcript. Source subtitle times become stale after a cut; replacing text in the old SRT does not retime it. Use the edit map when referring back to original attempts in the review notes.

Compare the new transcript with retained content and check subtitle timing against the edited audio. Preserve raw recognition, source audio and the edit report so a disputed choice can be revised.

## Audio acceptance

Review each join with enough surrounding speech to assess missing attacks/tails, clicks and unnatural pauses. Inspect the complete final audio for missed retries, including intervals previously transcribed fluently. Add these results to the existing coverage record, distinguishing audio understanding from signal measurements.

**Reviewed delivery:** the final audio has complete spoken-audio review coverage, every join has been checked, and reported issues are resolved. State the reviewing method rather than claiming perfect detection.

**Draft pending audio review:** spoken-audio coverage is incomplete, a join remains unchecked, or an issue is unresolved. Deliver the supported edits with local previews and exact pending ranges; label the result “待听审的剪辑草稿” in the user-facing response. Subtitle correctness and successful technical checks alone do not upgrade that status.
