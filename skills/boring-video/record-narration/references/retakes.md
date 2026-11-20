# Retake editing

Use after the first transcription when the speaker restarts or repeats a passage. The agent identifies retries from the complete script and transcript; the helper executes reviewed cut times, not semantic detection.

## Decide what survives

Map each attempt to a script passage. Record its source start/end, recognized words, completeness and keep/remove decision. A partial sentence followed by another attempt that restates it and continues is strong retry evidence. Repeated terminology across different passages, deliberate emphasis and legitimate recaps are not retries.

Prefer an attempt that contains the intended meaning without a false start. Preserve recorded paraphrases. The final attempt is a useful candidate, not a rule: numbers, negations and names can change between attempts. When transcript and script cannot distinguish a correction from a meaning change, retain alternatives and ask a targeted question rather than silently discarding one. Choose naturalness only from audio evidence; transcript alone establishes completeness, not vocal quality.

**Decisions complete:** every suspected retry has an explicit outcome and a reason; unique intended content remains in its original order.

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

Normalize and transcribe the edited audio in a new directory:

```bash
/path/to/venv/bin/python scripts/process_audio.py prepare \
  --audio /absolute/path/edited-v2/narration.edited.wav \
  --output /absolute/path/edited-v2/final --transcribe --language zh
```

Continue recognition correction against this new transcript. Source subtitle times become stale after a cut; replacing text in the old SRT does not retime it. Use the edit map when referring back to original attempts in the review notes.

Inspect the new transcript for the discarded restart and for missing retained content. Export a short join preview if playback review is needed. Report durations before/after, what was removed and why, and which joins require human listening. Preserve raw recognition, source audio and edit report so a disputed choice can be revised.

**Ready for subtitle review:** the final audio is decodable, its transcript follows the retained script progression, and uncertainty about words or join quality is stated explicitly.
