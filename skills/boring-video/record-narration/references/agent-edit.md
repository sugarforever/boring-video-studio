# Agent-directed narration editing

Use the current agent to review timed words and the reference script, then execute its decisions locally. Speech-review requirements remain in [retakes.md](retakes.md); reporting and user acceptance remain in [processing.md](processing.md). Report audio readiness separately from subtitle readiness.

## 1. Bind the input

Use a mono 48-kHz PCM16 WAV and its matching word-level transcript. A denoised derivative can reuse timings only when its sample count and timeline are unchanged.

```bash
/path/to/venv/bin/python scripts/agent_edit.py prepare \
  --audio /absolute/path/narration.wav --transcript /absolute/path/transcript.raw.json \
  --script /absolute/path/script.txt --output /absolute/path/agent-review-v1
```

**Ready:** verify the audio/transcript association, then read `agent-input.md`. `bundle.json` binds the inputs by hash; word IDs are stable within that bundle. Zero-duration tokens retain their text and original indices in shared timed units. Use a new output directory for each revision.

## 2. Review and write decisions

Review the complete raw wording, using the script for context. Preserve coherent improvisation and deliberate emphasis. Copy `decisions.template.json`, retaining `bundle_id`:

- `corrections`: `{id, text, reason}`; nonempty recognition corrections preserve `raw_text` and timing. Mark context-only corrections provisional until audio evidence supports them.
- `cuts`: ordered, disjoint ranges with a complete surviving replacement. IDs are inclusive:

```json
{
  "first": "w000010", "last": "w000016",
  "replacement_first": "w000017", "replacement_last": "w000026",
  "reason": "Abandoned opening; retain the complete replacement."
}
```

For suspicious ASR gaps or long word spans, run:

```bash
/path/to/venv/bin/python scripts/narration_review.py inspect \
  --review /absolute/path/agent-review-v1 --output /absolute/path/inspection-v1
```

The command uses local VAD and ASR to produce evidence. Check its scope and `unprocessed_windows`; finish or explicitly account for uncovered candidates. Recovered words require observed source times and a new transcript/bundle. Preserve conflicting evidence for review.

**Decisions ready:** every proposed deletion has a reason and a retained replacement; uncertain speech remains. This branch handles abandoned retries, preserving unique content and normal pauses.

## 3. Execute acoustic cuts

```bash
/path/to/venv/bin/python scripts/agent_edit.py apply \
  --review /absolute/path/agent-review-v1 --decisions /absolute/path/decisions.json \
  --output /absolute/path/agent-edit-v1
```

The planner seeks quiet boundaries constrained by kept neighbours. Ambiguous cuts remain unapplied. Review `boundary-report.json`, `review-tasks.json` and `review.html`; the latter provides A/B clips. `--boundary-mode word` is an unverified diagnostic mode.

**Draft exported:** duration matches retained source samples and every proposal has a disposition. Check joins and neighbouring speech. Mapped word times and context-only corrections remain provisional; sources and edit mappings are retained.

## 4. Align and check subtitles

```bash
/path/to/venv/bin/python scripts/narration_review.py align \
  --result /absolute/path/agent-edit-v1 --output /absolute/path/alignment-v1
```

This re-times the retained text against the edited WAV using local attention/DTW alignment, then applies the existing subtitle layout. Read `QC.json`: timing, probability and layout warnings require dispositions. Shared timed units preserve zero-duration text without inventing individual boundaries.

To regenerate QC/review files from saved alignment without rerunning the model:

```bash
/path/to/venv/bin/python scripts/narration_review.py resume \
  --alignment /absolute/path/alignment-v1/transcript.aligned.json \
  --result /absolute/path/agent-edit-v1 --output /absolute/path/resumed-review
```

Separately transcribe the edited WAV with `process_audio.py transcribe`; reconcile wording under [retakes.md](retakes.md). Re-align any changed wording.

Resume retries the same layout; unresolved errors remain pending. Changed wording returns to `align` rather than overwriting saved evidence.

**Subtitles ready for delivery review:** bindings are current, timing/layout errors are resolved and warnings have evidence-backed dispositions. A subtitle failure leaves the WAV available for audio review.

## 5. Compare and hand off

For versions derived from the same unchanged source, use `compare_audio_edits.py --help` to generate matched listening excerpts and retained-sample checks. This CLI requires identical source hashes; different denoising/gain sources need manual comparison after verifying a common timeline.

Deliver the WAV, review page and reports, identifying unresolved audio and subtitle tasks separately. Apply the speech-review and acceptance gates linked above before downstream production.
