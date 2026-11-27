# Recording handoff processing

## Reduce noise before editing

On handoff, tell the user that processing will reduce noise, remove abandoned retakes and deliver a listening version with a report. Keep original takes/chunks and script snapshots unchanged. Use a new output directory for each revision, retaining source-to-output mappings.

Inspect background-only and spoken intervals to choose and execute noise reduction before normalization and retake cuts. For steady broadband noise, a starting candidate is:

```bash
ffmpeg -i /absolute/path/original.wav -af "afftdn=nr=10:nf=-40" /absolute/path/new-version/denoised.wav
```

Create the new directory first. Tune the filter to the actual recording; for tonal hum, measure its frequency and use targeted notch filtering. Record the executed command and parameters. Normalization applies gain; the optional expander in [background.md](background.md) attenuates quiet intervals. Neither alone establishes noise removal during speech.

Compare matching source/candidate excerpts at comparable playback levels, covering background, quiet speech, onsets and endings. Record residual noise and voice damage using actual listening or an audio-understanding tool. If processing or listening is unavailable, export available A/B previews and mark the stage incomplete. Retain ambiguous speech and report the capability gap.

**Noise stage complete:** an actual noise-reduction operation has run, its source/output and parameters are recorded, and listening evidence supports the selected candidate. Continue with preparation using that candidate as `--audio`, then follow the skill's retake review and subtitle steps.

## Report and obtain acceptance

Write the processing report in `REVIEW.md` and summarize it in chat:

- Original and processed version paths, noise diagnosis, executed treatment and comparison evidence.
- Removed retake intervals, reasons and total removed duration; before/after duration and loudness.
- Speech and join review results, unresolved issues and listening limitations.

Link the original, processed listening file and matching A/B excerpts. Ask the user to listen and confirm that noise reduction and retake editing meet expectations. Record `awaiting_audio_approval` in `REVIEW.md` as a workflow status, then yield. This is a review-note status, not a recorder or CLI state.

**Accepted for production:** the user explicitly accepts the delivered version and `REVIEW.md` records that version and confirmation. Until then, downstream scenes, storyboard, video assembly, rendering and publishing remain gated. Recorder submission and earlier instructions to continue authorize processing only. For requested revisions, rebuild from retained sources in a new version, update the report and obtain acceptance of that version. Acceptance does not replace the skill's technical and speech-review completion criteria.
