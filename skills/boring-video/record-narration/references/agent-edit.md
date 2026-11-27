# Agent-directed edit draft

Use this branch to generate a testable narration cleanup from a word-level transcript and reference script, using the current agent's reasoning rather than a second LLM API. It produces a listening draft; the retake review and user acceptance gates still apply.

## 1. Export bound evidence

Use a mono 48 kHz PCM16 WAV and a transcript aligned to that same timeline. A denoised derivative may reuse timings only when its sample count is unchanged. Check the source association: hashes detect later changes, not a wrong initial pairing.

```bash
python3 scripts/agent_edit.py prepare --audio /absolute/path/narration.wav \
  --transcript /absolute/path/transcript.raw.json --script /absolute/path/script.txt \
  --output /absolute/path/agent-review-v1
```

**Ready:** `agent-input.md` lists every raw word with a stable ID and source time; `bundle.json` binds the source, transcript and reference script. Each rerun uses a new directory.

## 2. Current agent writes decisions

Read the full exported input. Reference the script for terms and intended progression while preserving actual speech, improvisations, repetitions and abandoned fragments. A text discrepancy alone does not prove an ASR error. Record contextual corrections as provisional until audio evidence supports them.

Copy `decisions.template.json` to a separate decision file. Keep `bundle_id`. Recognition corrections are `{id, text, reason}` on existing words, preserving `raw_text`. They change display text, never timing or the raw evidence. A correction must retain nonempty text; deletion belongs in a cut decision.

Each cut uses inclusive source word IDs:

```json
{
  "first": "w000010", "last": "w000016",
  "replacement_first": "w000017", "replacement_last": "w000026",
  "reason": "Abandoned opening; the complete replacement follows."
}
```

Review every candidate against the raw words and context. Supply the complete kept replacement, not just its first repeated word. Keep intentional emphasis and unique information. This version supports retries with a retained replacement; unrelated shortening, filler removal and general pause compression are outside this protocol. Cuts must be ordered and disjoint, and all referenced replacements must survive every cut.

Run the suspicious-window inspection command before deciding that an ASR gap is silent:

```bash
/path/to/venv/bin/python scripts/narration_review.py inspect \
  --review /absolute/path/agent-review-v1 --output /absolute/path/inspection-v1
```

It uses the Silero ONNX VAD bundled with faster-whisper to isolate speech near long gaps/spans, then separately transcribes those windows with the local ASR. `--start` / `--end` constrain source seconds; `--max-windows` limits work (default 24). The result records its scope and every unprocessed window: a bounded run is partial evidence. Review results against the original transcript and reference script. Repeated ASR is correlated, not listening. Build a new source transcript with documented recovered words and their observed source times, then prepare a new bundle; never edit an existing bundle or invent times. Conflicts remain unresolved. This inspection proposes evidence, not automatic transcript patches or deletion decisions.

**Decisions ready:** all text has been reviewed; each deletion has a reason and a surviving replacement; uncertain passages remain. Save review coverage and unresolved items in the project's review notes. Empty cuts are allowed and do not certify clean speech.

## 3. Plan acoustic boundaries and execute

```bash
/path/to/venv/bin/python scripts/agent_edit.py apply \
  --review /absolute/path/agent-review-v1 --decisions /absolute/path/decisions.json \
  --output /absolute/path/agent-edit-v1
```

The default acoustic planner uses adaptive local 10-ms RMS, continuous quiet runs and neighbouring kept-word constraints. It moves ASR boundaries into quiet regions while retaining room tone. A sustained sound or competing candidate pauses leaves that cut unresolved and its speech intact. `boundary-report.json` records proposed/resolved times, measured threshold and quiet regions. These checks support a candidate boundary, not proof of no clipped phoneme. Quiet speech can resemble room tone.

`--boundary-mode word` reproduces the original raw-word timing for diagnostics only and creates pending boundary tasks. It cannot establish acoustic acceptance.

The command exports edited PCM audio, sample-accurate time mapping, retained raw/corrected words, mapped draft SRT, source bindings, `review-tasks.json` and `review.html` with relative-path A/B WAV excerpts. Intersections between acoustic cuts and old word times are marked for realignment. Each version uses a new directory; sources remain untouched.

**Draft exported:** exact retained duration passes; every proposal has a boundary disposition; unresolved edits remain in the audio and `draft_review_required` stays explicit. Correction tasks, full listening and user acceptance remain pending. Inspect all joins and retained neighbours.

## 4. Re-align and validate subtitles

```bash
/path/to/venv/bin/python scripts/narration_review.py align \
  --result /absolute/path/agent-edit-v1 --output /absolute/path/alignment-v1
```

This recomputes the supplied retained text's timings against the actual edited audio in local windows using the installed faster-whisper attention/DTW aligner. It uses neither an extra LLM endpoint nor a phoneme CTC model. Raw alignment, engine versions, input hashes, window text and warnings are retained. Attention alignment is not independent recognition or proof of word correctness; local probabilities are not calibrated timing confidence.

For display only, zero-duration tokens can share a neighbouring timed unit, preserving every character without inventing individual timestamps. Raw measurements and coalescing notes remain available. Invalid timing blocks SRT export. Structurally valid results use the existing `process_audio.word_cues` single-line layout, and warnings keep the subtitles at review-draft status. `alignment_review_required` / `draft_review_required` remain incomplete stages; an exported SRT alone does not clear them.

Transcribe the final edited WAV separately with the normal `process_audio.py transcribe` command to check retained wording and possible residual restarts. Compare it with the planned retained text; recognition disagreement triggers local inspection, not silent replacement of corrected text. Source recognizer reruns cannot prove full cleanup.

**Alignment reviewed:** all structural errors are resolved, all timing/text warnings have evidence-backed dispositions, layout passes and all input bindings remain current. Full final speech listening and user acceptance are separate gates.

## 5. Compare versions and obtain acceptance

```bash
/path/to/venv/bin/python scripts/compare_audio_edits.py \
  --baseline /absolute/path/old/edit-report.json \
  --previous /absolute/path/previous-draft/edit-report.json \
  --candidate /absolute/path/agent-edit-v1/edit-report.json \
  --output /absolute/path/comparison-v1
```

The comparison requires identical unchanged source audio. It verifies retained PCM interiors excluding the 6.25-ms join margins, measures source energy around actual cuts and exports matching source/old/previous/candidate listening windows. The `--previous` version is optional. Anchors inside another version's removed region fail explicitly; resolve the overlapping comparison scope rather than claiming a matched comparison.

**Accepted:** report unresolved issues, provisional text corrections, alignment/layout and listening coverage under processing.md. Obtain explicit acceptance of the delivered version before downstream production. Draft generation, quiet endpoints, identical retained samples, clean ASR and passing tests alone never establish production readiness.
