# Agent-directed narration editing

Implement a file-based protocol: bind source WAV/transcript/script by hash; export stable word IDs and context for the current agent; accept separate recognition corrections and semantic cut decisions; validate version, replacement ranges and overlap; execute using the existing editor; map retained words to output time and export draft subtitles and a local A/B review page. No additional LLM endpoint. Keep originals immutable and require user listening acceptance. Subtitles mapped from ASR are drafts, not fresh acoustic alignment or full listening evidence.

Validate with synthetic WAV tests (stale bindings, replacement preservation, exact sample duration, word/timing mapping), existing narration tests, then the Swarm recording and previous final transcript. Record text-supported edits separately from audio-supported verification. Do not claim complete removal when ASR omitted a restart.
