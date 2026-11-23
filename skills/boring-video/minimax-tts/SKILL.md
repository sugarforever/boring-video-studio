---
name: minimax-tts
description: Use for MiniMax narration, voice selection, or subtitle recovery.
---

# MiniMax TTS

Use `scripts/minimax_tts.py` relative to this skill's installed directory (Python 3.10+, standard library). Read its `--help` for command options. Follow only the requested branch below; voice selection and subtitle recovery can finish independently of synthesis or HyperFrames.

For voice queries and synthesis, use `MINIMAX_API_KEY` from the environment. Select the account's platform through `MINIMAX_API_BASE` (origin without `/v1`): international `https://api.minimax.io` (default), domestic `https://api.minimaxi.com`, or US West `https://api-uw.minimax.io`. Use credentials and voice IDs from that platform.

## Select a voice

1. Query account voices:

   ```bash
   python3 scripts/minimax_tts.py voices --type all
   ```

2. Validate an explicit user choice or project default against the results. Otherwise, shortlist 3–5 voices suited to the narration language and purpose (or all matches if fewer); show each name, description and `voice_id`. Base descriptions on returned metadata, and mark missing details as unknown.
3. When no valid choice or default exists, wait for the user to select a candidate. If none match, report the gap and ask whether to broaden the search. If they request auditions, synthesize the same short excerpt for each requested candidate in separate directories and present the audio before selection.

Voice selection is complete when a valid `voice_id` is confirmed by the user or an explicit project default. Record it with the platform. Continue to full synthesis only when requested; a shortlist or audition alone does not select a voice.

## Generate narration

1. In HyperFrames, use the narration version at its voice gate; for a standalone request, use the supplied script. Extract spoken text into a UTF-8 file, keeping planning IDs and production notes in their source artifacts. Resolve the platform, model and voice before synthesis, using the selection branch when needed.
2. Use absolute input/output paths and a new or empty output directory:

   ```bash
   python3 scripts/minimax_tts.py synthesize \
     /absolute/path/narration.txt /absolute/path/narration/revision-01 \
     --voice-id '<confirmed voice_id>'
   ```

   If the script exceeds the CLI's length limit, follow [long narration](references/long-narration.md) before synthesis.
3. Review pronunciation, pauses and SRT text/timing against the audio and script. Keep synthesis annotations out of display captions; preserve timestamps when correcting text unless listening establishes a timing error.
4. Deliver `narration-full.mp3` and reviewed `narration.srt`, retaining `response.json` and `subtitles.json` as evidence. For HyperFrames, pass the current narration revision and settings through `/media-use`; changed narration returns to the next voice gate with fresh outputs.

Standalone synthesis is complete when playable audio and reviewed SRT are delivered. HyperFrames synthesis additionally requires acceptance into the current production workflow.

## Recover subtitles

Use the existing audio's `response.json` and its `data.subtitle_file` URL:

```bash
python3 scripts/minimax_tts.py subtitles \
  --url '<data.subtitle_file>' \
  --out-dir /absolute/path/narration/revision-01
```

This retries subtitle retrieval without another synthesis charge. If conversion fails, inspect retained `subtitles.json` against the [API subtitle schema](https://platform.minimax.io/docs/api-reference/speech-t2a-http); preserve the existing audio and resolve the subtitle error. If synthesis timed out, establish its outcome before deciding whether another paid request is needed.

Recovery is complete when the restored SRT has been checked against the existing audio and delivered for that same revision. Resume the production workflow only when that was part of the request.
