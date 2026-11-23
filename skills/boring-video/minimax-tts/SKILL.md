---
name: minimax-tts
description: Use when generating video narration with MiniMax TTS, choosing a MiniMax voice, or recovering its subtitle download.
---

# MiniMax TTS

Generate narration audio and timed subtitles for the current narration revision. Resolve `scripts/minimax_tts.py` relative to this skill's installed directory. Requires Python 3.10+; uses only the standard library.

## Voice gate

1. In a HyperFrames production workflow, wait for its voice gate and use that gate's narration version. Extract only spoken text into a UTF-8 file; keep beat IDs, Markdown headings and production notes in the planning artifacts.
2. Confirm the account endpoint and model, then use the existing `MINIMAX_API_KEY` environment variable. `MINIMAX_API_BASE` defaults to `https://api.minimax.io`; set it to `https://api.minimaxi.com` for the domestic platform or `https://api-uw.minimax.io` for US West. The base is an origin without `/v1`. Use credentials provisioned for the selected platform; do not assume cross-platform account compatibility.
3. List voices, then use the user's chosen voice or an explicit project default. System, existing cloned and generated voice IDs use the same synthesis path. Creating or cloning voices is outside this skill.

   ```bash
   python3 scripts/minimax_tts.py voices --type all
   ```

4. Synthesize into a new or empty output directory, using an absolute input/output path:

   ```bash
   python3 scripts/minimax_tts.py synthesize \
     /absolute/path/narration.txt /absolute/path/narration/revision-01 \
     --voice-id 'Chinese (Mandarin)_News_Anchor' \
     --model speech-2.8-hd --language Chinese --speed 1
   ```

   The example voice is illustrative; use an ID returned for the account. The default model is `speech-2.8-hd`; `--model` allows other account-supported models. Speed is 0.5–2. The client requests non-streaming MP3, 32 kHz, mono, with sentence-level subtitles. It rejects empty text and inputs of 10,000 characters or more before synthesis. For long scripts, split at coherent paragraph/beat boundaries, retain the same settings and use a separate directory for each part; assemble audio through the production workflow and offset each part's SRT by its actual timeline start. Automatic chunking/merging and asynchronous synthesis are outside this version.
5. Review pronunciation, pauses, subtitle text and timing against the spoken source. MiniMax accepts `<#0.5#>` pause markers and inline pronunciation annotations; keep these synthesis annotations out of display captions. Correct subtitle text without shifting timing unless listening establishes a timing error.
6. Give `narration-full.mp3` and reviewed `narration.srt` to `/media-use`, with the narration revision and selected settings. Keep `response.json` (trace ID, source-text digest, settings and subtitle URL) and `subtitles.json` as production evidence. A changed narration invalidates these outputs and returns to the next voice gate.

Completion requires playable audio and reviewed SRT for the current narration revision, accepted into the selected production workflow. Local tests alone do not establish live API quality.

## Recovery

The CLI checks both HTTP failures and MiniMax's `base_resp.status_code`. It does not automatically retry paid requests. Audio is saved before subtitle retrieval, so a subtitle failure can be recovered without paying for another synthesis:

```bash
python3 scripts/minimax_tts.py subtitles \
  --url '<data.subtitle_file from response.json>' \
  --out-dir /absolute/path/narration/revision-01
```

Downloads use no API authorization header. Inspect saved `subtitles.json` if conversion fails; the converter expects a JSON array of segments containing `text`, `time_begin` and `time_end` in milliseconds. A failed conversion exits nonzero and retains raw data; do not treat a missing SRT as a completed handoff. If a synthesis request times out, investigate its status before making another paid request. Use a new output directory for a new synthesis to preserve earlier audio.

## API references and verification

Verified against official documentation on 2026-11-23:

- [Synchronous TTS](https://platform.minimax.io/docs/api-reference/speech-t2a-http): request options, limits, audio and subtitle outputs.
- [Get Voice](https://platform.minimax.io/docs/api-reference/voice-management-get): account voice categories.
- [International endpoints](https://platform.minimax.io/docs/guides/speech-t2a-websocket#endpoints) and [domestic API](https://platform.minimaxi.com/document/T2A%20V2?key=66719005a427f0c8a5701643).

Run local HTTP contract and artifact tests without credentials or paid API requests:

```bash
python3 -m unittest discover -s tests -v
```
