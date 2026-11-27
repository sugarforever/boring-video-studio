# Historical narration holdout — 2026-11-27

## Outcome

Two earlier human-recorded episodes were reprocessed from their selected original WebM recordings: Home Repo (2026-11-23) and T3 Code / ACP (2026-11-24). New audio files and matched old/new listening pages exist. Source recordings and historical products remain unchanged.

The experiment does **not** establish stable one-pass production readiness. The frozen starting implementation failed on raw zero-duration words, rejected valid edits due to breath-gap ambiguity, and could abort subtitle export after completing costly recognition/alignment. General fixes were made and separately tested rather than concealing those first-pass failures. Final audio export completed on both episodes, but listening/text-warning review remains pending and T3's strict subtitle layout still needs attention.

## Source selection and comparability

Root: `/Users/wyang14/github/verysmallwoods/studio/videos/`.

| Episode | Selected raw recording | Historical output compared |
|---|---|---|
| `20261123-home-repo` | `narration/recording-20261123-home-repo/takes/237de0e8e8e94a4b9199e00d806d33d5/original.webm` | `narration/edited-v2/narration.edited.wav` |
| `20261124-t3-code-acp` | `narration/recording-20261124-211500/takes/261ede41d9854dc9a9b041b355324fce/original.webm` | `narration/edited-v2/narration.edited.wav` |

The T3 comparison uses its original-speed edit, not its later 1.1x derivative. Speed-up is not counted as editing improvement.

Each episode's new artifacts are co-located under `narration/agent-edit-holdout-20261127-v1/`. Shared report: `_validation/narration-holdout-20261127/review.html`; metrics/provenance: `summary.json` in that folder. These are local studio assets, not deployed or committed media.

Frozen starting code: `4d0fa895`. New input timing/layout recovery and pause-selection fixes are reported separately below. The same acoustic parameters were used for both episodes; no per-episode threshold tuning or copied historical cut seconds were used to place new cuts. Historical reports were read before selection, so this is not a blind precision/recall benchmark.

## Fresh input processing

Both original WebMs were freshly decoded to mono 48-kHz PCM16, processed with a fixed conservative broadband filter `afftdn=nr=6:nf=-45:tn=1`, then passed through the skill's verified linear loudness normalization and a fresh faster-whisper small ASR run. No prior ASR result was substituted for these fresh full runs. Models were already cached locally; first-time model downloads are not part of timing.

Original clocks were verified by equal frame counts (27,806,400 / 38,640,960 frames) and by comparing the decoded original to the historical uncut normalized source at 100,000 evenly distributed samples. Correlations were 0.9999999909 / 0.9999999860, with linear-fit residual RMS below 0.29 PCM units. This supports a common source clock despite different gain/denoising. Historical and new normalized sources have different hashes; the report does not pretend they are bit-identical.

Pre-gain noise RMS in the source 0.5–1.5-second reference changed from −56.05 to −57.19 dBFS (Home) and −51.14 to −51.62 dBFS (T3). These already quiet references show modest attenuation, not proof of better voice quality. The new filters' effect on voice remains a listening question.

## First-pass failures and general fixes

1. Historical raw ASR contained 4 / 7 zero-duration tokens; the frozen entry point rejected both. Fresh recognition also produced 2 / 5 zero-duration tokens. Shared timed units now preserve every character and original token index, while retaining raw recognition and explicit timing notes.
2. Recognition was successfully saved but initial subtitle layout threw, which previously looked like a failed transcription. Initial layout now has an explicit status artifact; expensive successful ASR is not repeated merely because initial subtitles need alignment/layout review.
3. The frozen edit-only control retained Home's known restart because multiple tiny breath/click gaps competed with a long quiet stretch. It accepted only two of T3's three known whole-phrase edits. The planner now accepts a uniquely dominant sustained quiet region while still rejecting comparable competing candidates. This is a generic dominance rule with a synthetic regression test, not a widened episode-specific time tolerance. All six previous Swarm cut boundaries remained unchanged after the fix.
4. T3's long technical terms cannot always meet the strict 16-character whole-word subtitle policy. A failure after model alignment now writes QC and a review page while retaining measured alignment. The new `resume` command validates bindings and regenerates review/layout without rerunning the model. It does not silently weaken subtitle limits.

First-pass artifacts were retained: `frozen-prepare-probe.json`, `edit-control-*`, `candidate/` and failed alignment data. Final candidates use `candidate-r2/`; Home alignment/review is `aligned-r2/`, T3's resumed alignment/review is `aligned-r3/`.

## Editing results

| Episode | Source duration | Historical edited duration | New duration | New applied cut intervals |
|---|---:|---:|---:|---:|
| Home Repo | 579.300 s | 573.600 s | 574.260 s | 1 |
| T3 Code / ACP | 805.020 s | 783.970 s | 781.380 s | 4 |

Home's new cut is 121.190–126.230 s versus historical 120.500–126.200 s. Both remove the abandoned repo-specific-rule explanation and retain the complete replacement. The extra 0.660 s is principally preserved leading room/pause, not evidence of a worse or better semantic edit. Local old/new recognition supports the retained complete sentence; listening remains pending.

T3's final cuts:

| Source range | Decision and evidence |
|---|---|
| 158.450–159.880 s | Remove first `内置`; retain the complete Provider clause. The old project review explicitly recorded this missed repeat, and fresh ASR now preserves both occurrences. |
| 406.730–409.170 s | Remove the repeated second test-result phrase. Fresh full ASR omitted this repetition, but VAD-separated local recognition recovered `修复后通过的两次测试` at 406.730–408.830 s. Keep the earlier phrase attached to `修复前失败`. |
| 470.640–485.840 s | Remove the first ACP Client explanation; preserve the complete repeated paragraph. |
| 556.170–560.740 s | Local recognition separated three RPC openings, not the two shown in the older transcript. The middle window recognized an incomplete `走通過應用2`; the third contains the complete RPC/action/status clause. The current agent classified the first two as abandoned and retained the third. Historical editing had removed only the first attempt. This judgment remains pending listening. |

The first and fourth regions add substantive coverage beyond the historical edit. These are five applied cut intervals across two episodes, not an exhaustive ground-truth recall estimate. Coherent improvisations and clarifications (`或者说`, `提议或建议`) were retained.

All final cut proposals received acoustic quiet-boundary dispositions. Retained interiors, excluding 300 samples (6.25 ms) at joins, had zero mismatches against their own respective pre-edit source: Home new 27,563,280 samples; T3 new 37,503,240 samples. Historical outputs also matched their own sources. This demonstrates absence of unintended signal edits outside joins, not absence of semantic misdeletions.

## Efficiency measurements

| Stage | Home | T3 |
|---|---:|---:|
| Raw decode | 0.79 s | 1.18 s |
| Broadband denoise | 1.05 s | 2.42 s |
| Linear normalization | 13.78 s | 17.85 s |
| Fresh full-source ASR | 157.85 s | 183.99 s |
| Final acoustic plan + cut export + previews | 0.32 s | 0.79 s |
| Final model alignment + layout | 97.63 s | Initial export failed after measured alignment; elapsed timing was not retained on exception |

These are individual desktop wall times with some concurrent jobs, not averages or total agent turnaround times. They exclude source browsing, agent reasoning, diagnostic probes, failed attempts and waiting. T3's completed alignment was resumed without rerunning the model. The missing measurement is not estimated from file timestamps.

Warm historical cut-export replays took 0.26 / 0.54 s; first-draft new export/previews took 0.37 / 0.45 s. Those measurements have different work scopes and do not establish an overall speed-up. Historical full production time and human correction time are unknown. The defensible efficiency gain is safer recovery/reuse of expensive ASR/alignment and less need for ad-hoc timestamp surgery, not a proven faster end-to-end workflow.

## Quality gates and remaining work

Home exports aligned draft subtitles but has 208 timing/token-probability review hints. T3 retains measured alignment with 177 hints and has `subtitle_layout_review_required`; it does not export a falsely compliant SRT. Hint counts are not counts of proven recognition errors or calibrated timing confidence.

Fresh ASR still omitted some unique, uncut spoken content in T3 (for example the model/agent list around 49.9–53.5 s), while the corresponding audio was retained. Thus clean recognition text cannot establish full speech coverage, and supplied-text alignment cannot discover every omitted word. Neither bit identity nor quieter endpoints certifies natural joins or full short-restart cleanup.

Actual semantic listening is unavailable in this tool environment. Final audio status remains review required; no historical audio/video was replaced, no video was rerendered or published, and no merge was performed. The earlier aspiration of reliably obtaining immediately usable audio in one pass has **not** been established by this experiment.

## Verification

Regression tests cover the newly observed input zero-duration handling, immutable raw recognition, durable initial-layout failure status, sustained-pause dominance, continued rejection of comparable pauses, and preservation of alignment when technical-term layout fails. Full narration tests and compilation are run before committing; the completion message records their final result. Source hashes and all recovered-window evidence are retained with the local artifacts.
