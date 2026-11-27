# Swarm validation — 2026-11-27

Branch: codex/agent-retake-editing. No additional LLM API or model endpoint is used for edit decisions; the current agent wrote word-ID decisions and context-based provisional corrections. Local faster-whisper small remains the ASR dependency.

## Real input

Project: `/Users/wyang14/github/verysmallwoods/studio/videos/20261125-antigravity-swarm/narration/`.

- Original selected recording: `recording-20261126-184500/takes/6cfdbc454dd249ff82c8b0b8239be9a1/original.webm` (unchanged).
- Full-length test input: `cleaned-v8/narration.denoised.wav`; its existing noise report records unchanged sample count and 48 kHz sample rate. No new denoising claimed.
- Initial word evidence: `processed-v7/transcript.raw.json`.
- Prior published subtitle: `edited-v8/final/delivery-v3/subtitles.video.srt`.
- Deliverable: `agent-edit-test-v1/full/result-v2/review.html`, WAV, draft SRT, full raw/corrected retained-word transcript, source bindings, edit mapping and decisions.

## Findings and execution

Four known discarded attempts are reproducible from the full original transcript (283.33–284.79, 396.12–398.36, 419.10–422.78, 488.88–490.02 seconds). These are baseline regressions, not newly found omissions. Cuts use word timestamps and retain intervening pauses, so their durations differ from the old manual cuts.

A further residual was found in the old edited audio around 126–131 seconds: a discarded `创建`, then the complete `创建和发送以后`. The original final transcript showed only one occurrence at 129.10 seconds. Re-recognizing 122–142 seconds still merged the two. Independent short-window inputs (125–128 and 128–132 seconds, same ASR model) recovered both. This is correlated ASR evidence, not independent listening. The recovered first start includes silence and is not precise speech onset.

The recovered transcript and evidence are retained in `agent-edit-test-v1/full/transcript.recovered.json`. Before the first old edit at 283.333 seconds, old-edited/source clocks are identical. The new recovery ends at 131.05 seconds to meet the next original word start (0.01-second timing adjustment recorded in provenance).

Five word-ID cuts produced 575.28 → 564.44 seconds (10.84 removed), exact decoded PCM frame count verified by the existing editor. The draft includes 129 provisional token corrections from script vocabulary/context and retains all raw text; these are not 129 audio-verified recognition corrections.

## Verification and limitations

- 75 narration unit/integration tests passed using the existing record-narration virtual environment; 11 cover the new protocol. System Python initially failed 15 existing tests because jieba was absent; rerunning in the established environment resolved those dependency failures.
- New tests cover stale source/transcript rejection, bundle mismatch, replacement survival, overlap rejection, immutable raw evidence, no-cut mapping, long-gap hints, and a synthetic regression using the real missed-restart time layout.
- `git diff --check` and Python compilation passed.
- No full listening capability was available. Full speech and join quality remain pending. Mapped ASR subtitle timing is a draft; publication requires fresh transcription/alignment and standard subtitle review.
- Long-gap/long-word hints are inspection priorities, not proof of a restart. Local re-recognition is agent-directed, not an automatic semantic listener.
- Recognition corrections do not rewrite alignment. This protocol handles cuts with a retained replacement, not general shortening or filler removal. Source association is checked by the caller; hashes detect changes after binding.
- No existing audio/video, subtitles, or publication was replaced. User listening acceptance remains required.
