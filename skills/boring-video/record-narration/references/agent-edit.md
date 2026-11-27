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

Inspect suspicious long word spans and gaps where the script/transcript appears to conceal a restart. If ASR omitted speech, extract small overlapping audio windows and transcribe them separately. Keep those results as ASR evidence, not listening evidence. Build a new source transcript with documented recovered words and source times, then prepare a new bundle; never edit an existing bundle or invent timings. Conflicting recognitions remain unresolved.

**Decisions ready:** all text has been reviewed; each deletion has a reason and a surviving replacement; uncertain passages remain. Save review coverage and unresolved items in the project's review notes. Empty cuts are allowed and do not certify clean speech.

## 3. Execute and listen

```bash
python3 scripts/agent_edit.py apply --review /absolute/path/agent-review-v1 \
  --decisions /absolute/path/decisions.json --output /absolute/path/agent-edit-v1
```

The command validates bindings and ranges, calls the existing PCM editor, and exports the edited WAV, edit mapping, raw/corrected retained words, draft SRT, decision provenance and `review.html` with local before/after WAV excerpts. It never overwrites a result directory or modifies sources. Open `review.html` directly in a browser; excerpts use relative paths.

**Draft exported:** source hashes are unchanged and output duration equals source duration minus cuts. SRT times are mapped ASR times, not fresh alignment; word boundaries are approximate and this first version does not refine them acoustically. Check every join for clipped syllables, clicks and unnatural pauses. After accepting the edit choices, retranscribe the output and use the normal subtitle layout/correction workflow for delivery subtitles.

**Accepted:** follow processing.md to report limitations and obtain explicit acceptance of this version. Output status `awaiting_audio_approval` is a review note only. Successful execution or absence of textual repeats cannot satisfy full speech review.
