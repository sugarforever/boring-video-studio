# Swarm old/new audio comparison — 2026-11-27

Verdict: the current prototype is a listening/review draft, not a production audio deliverable. Do not promote it as the default cleanup path on the evidence below.

## Method and artifacts

Compared the same denoised source, the prior `edited-v8` narration and `agent-edit-test-v1/full/result-v2` on the original source clock using both edit maps. Both reports bind SHA-256 `60bcd80125bcea76efd98fc594384d3dbdcd050131a65c34cd07070fde7011c8`.

Generated 15 WAV excerpts: source/old/new for each of five candidate contexts, with fresh local faster-whisper small recognition (CPU int8, word timestamps, no VAD filter, condition_on_previous_text=False). Contexts use matching source start/end and each edit's mapping. These outputs remain correlated ASR, not listening evidence. The previous separate 125–128 / 128–132 probes exposed the collapsed restart; broader windows collapsed it again.

Artifacts are outside the repository under:
`/Users/wyang14/github/verysmallwoods/studio/videos/20261125-antigravity-swarm/narration/agent-edit-test-v1/comparison-v1/`

- `review.html`: three-way audio and local ASR for each context.
- `comparison.json`: source hash, exact durations, retained-interior verification, all 15 transcripts, cut-boundary RMS.
- `restored-interval-energy.json`: audio energy in source intervals restored by the new cuts.

## Results

| Source region | Old removal (s) | New removal (s) | Interpretation |
|---|---:|---:|---|
| 125–127.32, abandoned 创建 | 0 | 2.320 | New candidate recovered by split-window ASR; narrow-window evidence, listening still pending |
| 283, 又去创建或 | 1.400 | 1.460 | Nearly the same semantic edit; new end is 56.7 ms later |
| 396, 看看…怎样使 | 4.333 | 2.240 | New version restores about 1.97 s after the ASR end, plus 0.12 s before start |
| 419, 随后要求… | 4.600 | 3.680 | New version restores about 0.95 s after the ASR end |
| 489, 并且反馈… | 1.433 | 1.140 | New version restores 0.38 s at the end and removes an extra 86.7 ms at the start |

Source duration: 575.280 s. Old: 563.513333 s. New: 564.440 s. The new output is 0.926667 s longer despite its extra 2.320 s deletion. The four shared edits remove 3.246667 s less in aggregate.

Signal observations:

- Retained interiors, excluding 300 samples (6.25 ms) at each interval edge, are bit-identical to the source: 0 mismatches out of 27,045,640 old / 27,089,520 new samples. This supports preservation outside edits; it says nothing about semantic correctness or the excluded boundaries.
- The three restored tails at 398.36–400.333, 422.78–423.733 and 490.02–490.40 have RMS −28.22 / −28.03 / −30.96 dBFS. A nearby quiet reference at 127.4–128.5 is −42.85 dBFS. These intervals cannot be described as merely quiet padding. Their identity (speech tail, breath, other sound) remains unverified.
- Source 20-ms RMS at the 419-region cut end: old −53.89 vs new −19.44 dBFS; at the 489-region end: old −50.12 vs new −22.77 dBFS. The new cuts land amid much greater energy. High-energy cuts and fades are not proof of clipped speech, but require listening and acoustic boundary refinement.
- The new 创建 cut ends at a source RMS of −19.60 dBFS. Even the added detection has not established a safe boundary.
- Broad local ASR generally produces semantically similar old/new text. It also hides repeats present in the source. Its apparent cleanliness therefore cannot certify that either cut is clean. In the 并反馈 context both edited versions omit the obvious textual restart, supporting that broad edit only.

## Delivery assessment

Passed: deterministic source binding, original preservation, sample-count/export validation, transcript mapping and structural unit tests (75 narration tests in the implementation turn).

Unmet: acoustic boundary refinement, full final speech listening, reliable omission coverage, fresh final alignment and subtitle layout review, verification of 129 provisional context-based word corrections, and explicit user acceptance.

Five candidates are not a recall benchmark: four are previously known, and the extra one was recovered by agent-directed inspection. No quantitative precision/recall or superiority claim follows.

Next version should preserve reviewed old cut boundaries for the four baseline cases, refine new candidates against measured speech/quiet boundaries rather than applying raw ASR endpoints, regenerate aligned subtitles, and evaluate on independently annotated Chinese restart/emphasis samples. Final listening remains required. A hybrid revision has not been generated or accepted in this comparison.
