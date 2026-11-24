# Low-level background suppression

Use this branch when the user requests quieter pauses or reports low-level room noise or distant conversation. Keep the default preparation path for recordings that do not need this treatment. This is an optional soft downward expander using [FFmpeg agate](https://ffmpeg.org/ffmpeg-filters.html#agate), not a learned denoiser or target-speaker extractor. It reduces all sufficiently quiet audio, including quiet speech; it cannot distinguish a distant speaker from the narrator by identity or remove overlapping voices reliably.

## Prepare a review candidate

```bash
/path/to/venv/bin/python scripts/process_audio.py prepare \
  --audio /absolute/path/original-recording.mp3 \
  --output /absolute/path/background-candidate-v1 \
  --suppress-background
```

Use `--session` instead of `--audio` for a submitted recorder take. Finish the background review before transcription and retake decisions; transcribe the selected candidate afterward with `transcribe`. Retain the original recording and script association. Each attempt uses a new output directory.

The helper decodes to mono 48 kHz PCM16, suppresses low-level audio, then performs the existing uniform-gain normalization. `prepare --help` exposes the input threshold. The preset uses a soft knee, finite attenuation floor and attack/release smoothing, rather than deleting samples or muting all pauses. The input threshold depends on microphone gain: use measured background and quiet-narration levels to choose a candidate. A higher threshold affects more audio; a lower threshold preserves more quiet speech. If there is no usable level separation, retain the original or evaluate another approach rather than raising the threshold until speech disappears.

Outputs:

- `narration.before-suppression.wav`: decoded reference, without suppression or normalization.
- `narration.suppressed.wav`: suppressed candidate, before normalization; compare this with the reference at the same playback volume.
- `narration.wav`: normalized candidate for downstream processing if accepted.
- `processing.json`: original source hash, filter settings, reference paths, normalization report and `background_suppression.review_status: pending`.

Original files remain untouched. `denoise: false` refers to the absence of spectral/model denoising; `background_suppression` separately describes the level-based processing. No model weights or new packages are needed.

## Review and choose

Compare matching excerpts around background-only intervals, speech onsets, quiet narration, breaths and word endings. Include intervals where background conversation overlaps the narrator. Measure attenuation on the unnormalized pair; waveform levels and ASR agreement alone cannot prove voice preservation. Record the candidate parameters, inspected intervals, evidence, accepted or rejected outcome and chosen downstream audio in `REVIEW.md`. A rejection uses a new preparation without suppression, or the already retained unprocessed path; keep rejected candidates as provenance.

**Accepted for processing:** sample count/rate/channels match the decoded reference; actual listening or an audio-understanding tool supports reduced unwanted sound without unacceptable loss of narrator content. Missing listening capability leaves the candidate pending: export A/B previews and state that limitation, retaining the original for continued work. Technical success and file creation leave `processing.json` pending; `REVIEW.md` is the authority for the review decision. Do not claim parity with a commercial editor or speaker separation from level changes alone.

This preset was motivated by one aligned original/editor comparison whose strongest changes occurred in low-level intervals. That observation supports a baseline experiment, not a universal inference about the editor's algorithm or a guarantee for other rooms and microphones.
