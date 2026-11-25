# Audio-review ledger

Use this helper to record the review required by [retakes.md](retakes.md). It reads WAV/JSON without modifying audio. Times always refer to the bound WAV.

## Initialize

```bash
python3 scripts/review_audio.py init \
  --audio /absolute/path/narration.wav \
  --transcript /absolute/path/transcript.raw.json \
  --output /absolute/path/audio-review.json
```

For edited audio, supply both `--edit-report /absolute/path/edit-report.json` and `--previous-review /absolute/path/source-audio-review.json`. The source ledger must bind that edit's source. The helper maps prior candidates/reports into output time, resets their decisions, and adds output ASR hints and join checks. Fully removed intervals map to their output seam. Missing inherited entries fail validation.

Without cuts, keep the current ledger; if explicitly starting another review of the same WAV, pass `--previous-review` to retain its issues. Audio changes require an edit map. Hashes bind the WAV, transcript, edit report and prior ledger; finalize prior records before deriving another version. Changed bound artifacts require regenerating the dependent ledger. Initialization refuses to overwrite a file.

## Record evidence

| Field | Required content |
|---|---|
| `capabilities` | `id`, `kind`, `tool`, `available`, `probe_evidence`. Listening kinds: `audio_model`, `human_listening`; other kinds record available analysis without counting toward speech coverage. |
| `asr_runs` | `engine`, exact `model`/revision and run artifact references. |
| `coverage` | Actual `start`/`end`, capability ID, evidence reference with findings, and checks performed. The JSON example below lists the required checks. |
| `candidates` | Preserve generated/inherited identity and source fields. Add manual discoveries with unique IDs. Context may expand within file bounds; it may not shrink. |
| `user_reports` | Unique `id`, `start`/`end`, `context_start`/`context_end`, description, decision and evidence. Preserve inherited entries. |
| `boundary_checks` | Preserve generated ranges; add source/output comparison findings for opening, ending and joins. |
| `limitations` | Failures, unavailable capabilities and remaining uncertainty. |

Candidate/report decisions start as `pending`. Use `keep` with an observed-wording explanation and evidence. After deciding to cut, record `removed_in_new_version` with the planned cut/version in the source evidence; this remains incomplete until the final version is reviewed. In the final ledger use `removed` only for an inherited interval wholly removed by the edit map, with evidence from its output seam; surviving intervals require `keep`. All decisions require coverage of their context, including at least three seconds on each side, clipped to file bounds.

The helper merges overlapping coverage and reports gaps. Record failures as gaps. Example entry after actual review:

```json
{
  "start": 0,
  "end": 30,
  "capability": "listener-1",
  "evidence": "/absolute/path/listening-notes.md#window-1: findings and disposition IDs",
  "checks": ["sentence_restart", "short_repeat", "partial_word_restart", "self_correction", "mixed_language", "proper_name"]
}
```

## Validate

```bash
python3 scripts/review_audio.py check --review /absolute/path/audio-review.json
```

Preserve the JSON result alongside `REVIEW.md`: exit **0** means recorded evidence passes the structural gate; **2** reports incomplete gates, exact `spoken_audio_gaps` and unresolved items; **1** indicates invalid/stale artifacts. Apply the completion criteria in `retakes.md` before claiming the work is complete.
