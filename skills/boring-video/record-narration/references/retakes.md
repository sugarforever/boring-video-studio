# Retake editing

Before subtitle correction, review the supplied recording and reference script. Speech is the content authority; the script supplies context. Preserve original audio and raw recognition. Discover retries without requiring the author to provide repeated-word lists or timestamps.

## Establish capability and evidence

Test whether an available tool can consume this recording and understand speech; record the actual tool/model or listener, result and evidence. Playback controls alone do not establish agent listening capability.

Create a source ledger using [audio-review.md](audio-review.md). Keep coverage, evidence and decisions there; `REVIEW.md` summarizes its three gates: candidate decisions, cut/export and boundary verification, and full final speech review.

ASR can omit repeated syllables and partial-word restarts. Use it to locate candidates, never to certify clean speech. Same-model reruns are correlated recognition; different recognizers may expose disagreements but still do not count as listening. Script reading, transcript similarity, subtitle checks and signal measurements also contribute no speech-review coverage.

## Discover and decide

Inspect the entire recording in overlapping windows, logging only speech actually analyzed. Check sentence restarts, short word/syllable repeats, half-word restarts, self-corrections, mixed-language speech and proper names. Inspect long word spans and low-confidence tokens with their surrounding phrase. Generated hints prioritize review; neither their presence nor absence establishes an error.

Recheck every user-reported interval even when ASR shows no repeat. Include at least three seconds on each side, extending to the complete phrase. Map times between versions with the edit report. Each report needs an audio-supported disposition; unresolved evidence blocks completion. Author acceptance of an unchanged issue is a scope decision, not a listening result.

Record each candidate's interval, evidence and decision:

- **Retry:** an abandoned attempt has a complete, coherent replacement. Remove only discarded speech; preserve unique content and deliberate emphasis. The last attempt is not automatically preferable.
- **Improvisation:** coherent additions, omissions or changed examples survive; subtitle the actual speech rather than forcing agreement with the script.
- **Intent conflict:** incompatible substantive statements lack a clear spoken correction. Preserve them and ask only for the meaning decision needed to edit.

**Decisions recorded:** every discovered candidate and user report is accounted for; uncertainty stays explicit. This permits supported edits, not a claim of full cleanup.

## Cut and rebuild timing

Locate candidates with raw word times, then measure boundaries in the analyzed mono 48 kHz PCM16 WAV. ASR times are approximate. Place cuts in verified gaps around discarded speech, retaining neighboring attacks/tails, breathing margins and normal pauses. Silence helps place a cut; it does not identify disposable speech.

Write an ordered, nonoverlapping `retake-cuts.json` array in **source seconds**, with a reason per interval:

```json
[{"start": 8.6, "end": 13.7, "reason": "Discard abandoned attempt; preserve complete replacement."}]
```

Times above illustrate the format; measure this recording's boundaries. Apply the cuts into a new directory:

```bash
python3 scripts/edit_audio.py --audio /absolute/path/processed-v1/narration.wav \
  --cuts /absolute/path/retake-cuts.json --output /absolute/path/edited-v2
```

**Export verified:** the edit report identifies the source and planned cuts; decoded duration matches retained source duration. Preserve the source, edit report and source-to-output map.

Transcribe the edited WAV without normalizing its level again:

```bash
/path/to/venv/bin/python scripts/process_audio.py transcribe \
  --audio /absolute/path/edited-v2/narration.edited.wav \
  --output /absolute/path/edited-v2/final --language zh
```

Create its final ledger using the source ledger and edit report. Carried candidates and reports need final-audio dispositions, including confirmation around fully removed passages. Compare retained content, then correct and lay out subtitles from this fresh transcript; source subtitle times are stale. With no cuts, continue using the existing audio, transcript and ledger.

## Verify and report

Inspect the complete final audio for missed retries. Compare source and output around each join and any trimmed opening/ending for clipped speech, clicks and unnatural pauses. Signal continuity is supporting evidence, not a listening result. Preserve a quiet lead-in/tail; the editor fades interior joins only.

**Complete:** final speech-review coverage has real evidence, every candidate/report has a supported disposition, opening/ending/joins are checked, export verification passes, and the final ledger passes validation. The validator checks declarations; it cannot authenticate listening or guarantee detection.

**Incomplete:** use available speech-understanding tools to close gaps before delivery. If capability remains unavailable after probing, finish safe supported edits, retain ambiguous speech and export local previews. Report exact gaps, unresolved items and the capability needed. Label the result “待听审的剪辑草稿” and state that full spoken-error cleanup remains incomplete; the label does not finish that work.
