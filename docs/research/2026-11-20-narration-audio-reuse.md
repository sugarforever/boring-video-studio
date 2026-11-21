# Narration recording and processing reuse study

Research snapshot: 2026-11-20. Sources are upstream repositories, licenses, documentation, GitHub repository metadata, and local experiments. Recommendations below are integration judgments; repository popularity alone is not evidence of recording quality.

## Selection

| Project | Upstream evidence and license | Fit for this Skill | Decision |
|---|---|---|---|
| [WaveSurfer.js](https://github.com/katspaugh/wavesurfer.js) | BSD-3-Clause; repository last pushed 2026-11-12; documented Regions, Record, Timeline and Spectrogram plugins | Reusable waveform navigation and precise local selection/playback. A renderer/player, not an audio cleanup or speech-understanding engine | Integrated core + Regions 8.1.0 as local, unchanged assets; retain native recorder's recovery behavior |
| [ffmpeg-normalize](https://github.com/slhck/ffmpeg-normalize) | MIT license text; last pushed 2026-11-17; two-pass EBU normalization and explicit protection against dynamic fallback | Replaces our unsafe one-pass loudnorm command; maintains relative levels instead of independently boosting quiet sections | Integrated pinned 1.45.2; measured linear output required, preserve loudness range and lower target for peak headroom |
| [extendable-media-recorder](https://github.com/chrisguttandin/extendable-media-recorder) + [WAV encoder](https://github.com/chrisguttandin/extendable-media-recorder-wav-encoder) | MIT; recorder last pushed 2026-09-02; MediaRecorder-compatible API with custom WAV encoder | Strong candidate for lossless capture while preserving current control interface | Candidate only. Must test timeslice/chunk headers, pause/resume, interrupted recovery, Safari and sustained memory usage before adoption. Existing compressed chunks can be concatenated; a WAV encoder's chunks must not be assumed to have the same semantics |
| [xiangyuecn/Recorder](https://github.com/xiangyuecn/Recorder) | MIT; last pushed 2026-07-30; documented PCM callbacks, WAV capture, streaming and clearing old buffers | Alternative lossless recorder, especially if mobile support and long-recording memory matter | Candidate only. More capture/state integration than a MediaRecorder-compatible adapter; compare against the WAV encoder on the same browser matrix |
| [AudioMass](https://github.com/pkalogiros/AudioMass) | Original code MIT; bundled libraries retain own licenses, including an LGPL MP3 encoder; last pushed 2026-08-20 | Complete local browser editor with waveform editing/effects; useful reference or optional advanced editor | Do not embed the whole editor in a minimal teleprompter. A separate local review surface may be appropriate if selection/playback proves insufficient |
| [DeepFilterNet](https://github.com/Rikorose/DeepFilterNet) | MIT OR Apache-2.0 for repository code; last pushed 2026-11-06; documented 48 kHz speech enhancement and native/Python options | Offline optional speech denoising while retaining original recording | Candidate only. Validate macOS packaging, model terms, compensated delay, duration and speech artifacts before enabling; compare original/processed excerpts, never infer perceptual quality from noise-level reduction alone |
| [ffmpeg.wasm](https://ffmpegwasm.netlify.app/docs/faq/) | Wrapper MIT; core retains FFmpeg and linked-library terms; upstream FAQ describes native-performance disadvantage and memory constraints | Useful if completely browser-only processing becomes a requirement | Keep installed native FFmpeg for this local-agent workflow; a WASM runtime adds overhead without removing our need for local transcription and file handoff |

GitHub metadata was fetched directly from `https://api.github.com/repos/{owner}/{repository}`. Dates are repository push dates, not a claim that each release or default branch was updated on that date. License judgments above come from the actual license text, not GitHub's `NOASSERTION` classification. Sources:

- [WaveSurfer README/plugins](https://github.com/katspaugh/wavesurfer.js/blob/main/README.md)
- [Normalization modes and fallback prevention](https://github.com/slhck/ffmpeg-normalize/blob/master/docs/usage/normalization-options.md)
- [ffmpeg-normalize license](https://github.com/slhck/ffmpeg-normalize/blob/master/LICENSE.md)
- [AudioMass license and third-party terms](https://github.com/pkalogiros/AudioMass/blob/production/LICENSE)
- [DeepFilterNet usage](https://github.com/Rikorose/DeepFilterNet/blob/main/README.md), [license](https://github.com/Rikorose/DeepFilterNet/blob/main/LICENSE)

## Implemented changes

1. A saved take displays a WaveSurfer waveform. Drag to select a range, inspect its numeric start/end, and play only that range. The assets are served locally under the existing host checks and CSP. No runtime CDN or new recording upload destination is used. Third-party attribution/version/checksums are in the Skill's `THIRD_PARTY_NOTICES.md`.
2. Capture requests mono input with browser auto gain, noise suppression and echo cancellation disabled, to retain a controllable narration source rather than apply undocumented browser processing. The browser's actual supported settings are saved in each new take; this request does not guarantee that hardware or every browser honors each setting. The old chunk-upload and recovery mechanism remains.
3. Processing first decodes/resamples/downmixes to a finite-duration PCM WAV, then calls ffmpeg-normalize. Analysis and export see the same samples. Two-pass linear mode, preserved loudness range and peak-constrained target lowering replace one-pass dynamic loudnorm. Unexpected dynamic output fails before final audio is published. Measured results and dependency version are stored in processing.json.
4. Processing dependencies are installed from the Skill's requirements.txt. The recorder itself remains Python standard-library only, with bundled browser assets. No noise model is silently installed or applied.

## Tests and measurements

### Reproducing the quiet-start failure

A deterministic fixture has three seconds of quiet tone followed by louder audio. The old processor changed the quiet-to-loud relationship by **47.62 dB**, failing the new regression test. The linear replacement passes the test's 0.6 dB tolerance. This test establishes level preservation, not subjective denoising quality.

### Existing human narration

The same submitted original recording was decoded by both pipelines. RMS was measured over 0.5–1.0 seconds (quiet lead-in) and 4.0–5.0 seconds (speech).

| Version | Quiet interval RMS | Speech interval RMS | Change in quiet/speech relationship vs original |
|---|---:|---:|---:|
| Original | -59.30 dBFS | -11.31 dBFS | Reference |
| Old one-pass output | -33.50 dBFS | -14.30 dBFS | +28.80 dB |
| ffmpeg-normalize linear output | -60.95 dBFS | -12.96 dBFS | Approximately 0.00 dB |

Local experimental output: `demo/narration-recorder/reused-tools-v1/narration.wav`; measurements and settings: `comparison.json` and `processing.json` in that directory. These are private, untracked recording artifacts, not bundled with the Skill. This output is an uncut normalization comparison, not a newly approved retake edit or final subtitle delivery.

### Browser verification

Chrome with a synthetic microphone exercised recording, pause/resume, playback, WaveSurfer drag selection, selected-range playback, capture settings, decoded duration, normalization, handoff, upload failure and interrupted recovery. Safari, physical microphones, long recordings and human listening remain outside this automated test. Normalization dependency tests emit upstream resource warnings; no claimed perceptual validation is inferred from their success.

## Remaining quality work

- Use a real WAV recorder comparison before replacing the reliable recovery path. Test PCM integrity and long-session memory in addition to exported file extensions.
- Offer optional DeepFilterNet A/B previews after packaging and delay tests; retain the cleanest intelligible speech, not merely the quietest output.
- Reuse waveform selections to make user-reported short retries precisely addressable. The selected projects do not supply trustworthy short-retake semantic understanding. The Skill's audio-review evidence and draft-status requirements still apply.
- Preserve the simple UI: no full DAW or broad effects rack unless the user needs it.
