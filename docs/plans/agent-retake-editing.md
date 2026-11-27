# Agent-directed narration editing

Implement a file-based protocol: bind source WAV/transcript/script by hash; export stable word IDs and context for the current agent; accept separate recognition corrections and semantic cut decisions; validate version, replacement ranges and overlap; execute using the existing editor; map retained words to output time and export draft subtitles and a local A/B review page. No additional LLM endpoint. Keep originals immutable and require user listening acceptance. Subtitles mapped from ASR are drafts, not fresh acoustic alignment or full listening evidence.

Validate with synthetic WAV tests (stale bindings, replacement preservation, exact sample duration, word/timing mapping), existing narration tests, then the Swarm recording and previous final transcript. Record text-supported edits separately from audio-supported verification. Do not claim complete removal when ASR omitted a restart.

## Second iteration

Add an acoustic planning stage (10-ms adaptive RMS, continuous quiet regions, neighbour protection, unresolved cuts retained), a repeatable local ASR inspection command for suspicious intervals, and a post-edit alignment command using the installed faster-whisper attention aligner and the existing subtitle layout implementation. Preserve raw/corrected text and explicitly distinguish alignment from independent recognition/listening. Validate on the same source, decisions and prior edit map; no new semantic LLM service.
