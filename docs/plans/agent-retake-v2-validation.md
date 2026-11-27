# Acoustic planning and review pipeline — Swarm validation, 2026-11-27

## Implementation

Current branch: `codex/agent-retake-editing`. No independent semantic LLM service was added. The current agent still decides what speech to remove, from preserved source evidence and the reference script.

- `audio_evidence.py`: adaptive 10-ms RMS, continuous quiet runs, <=40-ms click bridging, neighbour-constrained boundaries, ambiguity/contrast rejection, attention/DTW alignment and zero-duration shared-unit handling.
- `agent_edit.py apply`: acoustic planning is the default; unresolved cuts stay in the audio; source edits are bound to word IDs and input hashes; boundary evidence, mapping intersections and review tasks are exported. Raw word edges require an explicit diagnostic mode.
- `narration_review.py inspect`: packaged Silero ONNX VAD isolates speech near suspicious ASR gaps/spans, then faster-whisper recognizes each window separately. Scope, unprocessed windows and engine versions are recorded. The current agent reviews these results; the tool never silently patches the transcript.
- `narration_review.py align`: supplied retained text is re-timed against the actual edited WAV using the installed faster-whisper attention aligner, with shorter groups separated at natural gaps. This is not phoneme CTC alignment or independent listening. Existing `process_audio.word_cues` generates the single-line SRT.
- `compare_audio_edits.py`: identical-source check, retained-interior sample comparison, boundary energy and matched listening excerpts across source, old production audio, first draft and new candidate.

The implementation draws on the pause-search/room-tone approach in MakeMyClip/editor `src/timeline/pauses.ts`, neighbouring-word constraints in Developh/resolve-cut `cut_list.py`, and the separate recognition/alignment stages used by WhisperX. The acoustic algorithm is an original, conservative NumPy implementation rather than copying an entire editor or adding its LLM client. RMS alone can confuse quiet speech and room tone, so results require listening. The known same-recording evidence is not a general quality benchmark.

## Inputs and reproducible artifacts

Project narration root:
`/Users/wyang14/github/verysmallwoods/studio/videos/20261125-antigravity-swarm/narration/`

All versions use the existing `cleaned-v8/narration.denoised.wav`, SHA-256 `60bcd80125bcea76efd98fc594384d3dbdcd050131a65c34cd07070fde7011c8`, 48-kHz mono PCM16. Original recorder WebM, source WAV and previous products were not modified. Noise reduction is inherited from the recorded prior stage, not newly claimed.

Artifacts are under `agent-edit-test-v2/`:

- Controlled same-five-decision comparison: `result-final/` and `comparison/` (earlier identical acoustic audio `result-c/` is bound in that comparison).
- Original final transcript inspection: `old-final-input/`, `inspection-vad/`. In source seconds of the old edited audio, 120–135 s inspection isolated `创建` at 126.666–127.638 s. The full transcript had collapsed it into the next sentence.
- Fresh full recognition of the five-cut output: `fresh-asr/transcript.raw.json`. This is recognition, not forced alignment and not independent listening.
- New finding inspection: `inspection-target/`, source scope 515–524 s. It separately recognized `目標明確` at 517.578–518.438 and `目標名稱不明確實` at 519.210–520.550 s. This explains the original 1.70-s span assigned to `称`. The current agent judged the first phrase an abandoned restart based on the coherent replacement and script context.
- Six-cut recovered source evidence and decisions: `six-cuts/transcript.recovered.json`, `six-cuts/input/`, `six-cuts/decisions.json`. Traditional ASR characters remain raw; simplified/contextual corrections are separately recorded and remain provisional.
- Latest audio and cut evidence: `six-cuts/result/`.
- Latest re-aligned subtitles and review page: `six-cuts/alignment/`.
- Four-way, six-location comparison (24 excerpts): `comparison-final/review.html` and `comparison-final/comparison.json`.
- Independent recognition of the sixth final context: `six-cuts/target-final-asr/`; `target-final-reference.json` binds source/output clock windows. The first five regions are unchanged from the five-cut audio; only the sixth source interval was removed afterward.

Commands from the skill root use the existing virtual environment `/Users/wyang14/.cache/record-narration/venv/bin/python`. The reference `agent-edit.md` documents each CLI. For example:

```bash
python scripts/agent_edit.py apply --review <six-cuts/input> --decisions <six-cuts/decisions.json> --output <new-result>
python scripts/narration_review.py align --result <new-result> --output <new-alignment>
python scripts/compare_audio_edits.py --baseline <edited-v8/edit-report.json> --previous <first-draft/edit-report.json> --candidate <new-result/edit-report.json> --output <new-comparison>
```

Directories must be new. Local recognition evidence is scoped; the two targeted inspection runs do not constitute exhaustive all-window listening.

## Controlled results

| Version | Cut count | Duration, seconds | Removed, seconds |
|---|---:|---:|---:|
| Denoised source | 0 | 575.280 | 0 |
| Prior production narration | 4 | 563.513333 | 11.766667 |
| First word-edge draft | 5 | 564.440 | 10.840 |
| Acoustic draft, same five decisions | 5 | 559.640 | 15.640 |
| Acoustic draft, additional discovered restart | 6 | 558.078 | 17.202 |

The five-decision control changes only cut placement, not semantic selections. The sixth finding is reported separately, rather than attributing its benefit to boundary refinement.

| Source cut | First-draft endpoints | Acoustic endpoints | Acoustic source RMS at start/end, dBFS (20 ms) |
|---|---|---|---|
| 创建 | 125.000–127.320 | 125.000–129.150 | −42.48 / −47.79 |
| 又去创建或 | 283.330–284.790 | 283.520–284.610 | −45.16 / −54.59 |
| 看看…怎样使 | 396.120–398.360 | 396.120–400.470 | −47.60 / −48.51 |
| 随后要求… | 419.100–422.780 | 419.270–423.850 | −46.14 / −45.61 |
| 并且反馈… | 488.880–490.020 | 489.060–490.530 | −51.32 / −50.64 |
| 目标明确 | absent | 517.578–519.140 | −52.64 / −59.19 |

Previous problematic first-draft ends measured −19.60, −22.42, −19.44 and −22.77 dBFS. New cuts are in sustained quiet runs rather than merely fading raw word endpoints. Measured quiet is supporting evidence, not a claim about phoneme completeness or listening quality.

Retained interior identity (excluding 300 samples / 6.25 ms at interval edges): old 27,045,640 samples, first draft 27,089,520 samples, new six-cut audio 26,783,544 samples; zero mismatches for all. Decoded output frame counts agree with retained edit maps.

## Alignment and recognition results

The six-cut output was actually re-aligned in 52 local windows. Result: 1,942 timed tokens, no invalid/overlapping/zero-duration units, no zero-duration coalescing needed, 3 long-span warnings and 126 low alignment-conditioned token-probability hints. The latter are not calibrated timing confidence or 126 proven errors. Long-span words remain flagged at output 144.56–145.88 (`要`), 376.59–378.51 (`会`) and 482.05–484.11 (`自`).

The initial coarse alignment experiment had 3 zero-duration units; shorter, pause-separated windows eliminated these rather than silently deleting text. The generic coalescing safeguard is unit-tested and retains raw measurements if needed on other inputs.

Corrected text is not overwritten by fresh ASR. The initial decision file had 129 provisional word corrections; the six-cut file has 135 including traditional-to-simplified target phrase changes. Audio evidence for every contextual correction remains unverified.

Fresh full ASR of the five-cut output recognized complete replacements at all five edited contexts and exposed the sixth restart. This supports targeted review, not an exhaustive no-restart claim. The final sixth-context recognition and its source-clock evidence are retained separately.

## Tests and readiness

84 narration tests passed in the existing Python 3.11 processing environment. Tests include missed-tail boundary extension, no-quiet rejection, competing-pause ambiguity, kept-word protection, retained-sample mismatch detection, word-ID/version binding, zero-duration text preservation and bounded alignment/inspection windows. Python compilation and `git diff --check` passed. The environment emits jieba's existing pkg_resources deprecation warning; it does not fail export or tests.

Status remains `alignment_review_required` / `draft_review_required`. No publication, existing product replacement, downstream video rendering or merging was performed. Remaining gates: dispositions for timing/text warnings, term correction verification, complete semantic listening and explicit acceptance of the delivered version. The current tool environment has ASR/alignment/signal tools but no independent semantic audio-listening capability. This is a materially improved testable draft, not automatically certified production audio.

## PR review follow-up

Independent standards/spec review identified and closed a conflicting subtitle-authority instruction, an unsafe search inside the previous kept word, and missing trailing-gap inspection. Final wording is reconciled against edited audio under retakes.md; start boundaries now protect the previous kept word's end, and trailing gaps use the existing inspection threshold. Two regression tests reproduced the runtime failures before the fix. Recomputing Swarm's six, Home's one and T3's four saved boundaries produced identical results. The concise agent reference also distinguishes layout retry from correction and CLI hash requirements from manual common-clock comparison.
