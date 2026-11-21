# Subtitle segmentation

Run after recognition correction, using the final audio's transcript. Recognition saves the ASR's original segments and also exports length-limited `transcript.initial.json` / `subtitles.initial.srt`. Correct the raw transcript for stable cue IDs, then regenerate the delivery layout from the reviewed text. ASR words can be single Chinese characters or partial English words; those boundaries alone are insufficient for subtitles.

## Export

```bash
/path/to/venv/bin/python scripts/process_audio.py delivery \
  --transcript /absolute/path/final/reviewed/transcript.corrected.json \
  --output /absolute/path/final/delivery
```

The helper reuses Jieba lexical boundaries and the existing ASR word times. It prioritizes sentence punctuation, clause punctuation and word gaps. It preserves source segment boundaries that coincide with complete lexical units, splitting overlong clauses within the character and duration limits shown by `delivery --help`. This prevents global regrouping from merging neighboring short clauses and then cutting them in less natural places. Source boundaries inside a complete word yield to word integrity. The same limits are available on `transcribe` and `prepare --transcribe`; they constrain subtitle export after decoding, not the recognizer’s linguistic sentence length. These defaults are a narration layout choice, not a universal subtitle standard; choose tighter limits for narrower video layouts.

Reviewed text supplies punctuation and actual spoken wording. Original `words` supply timing; `source_segments`, source cue IDs and source word indices preserve provenance. Replacements share the corresponding original word span, while added punctuation stays with its preceding word. English cue joins recover spacing from the original timed word boundary, so a split word rejoins without an inserted space. An unmappable boundary stops export; resolve it from the audio or corrected alignment and record the decision. This is text-to-timing projection, not a new acoustic alignment: listen around wording corrections and large replacements to verify their timing.

If a complete timed word cannot fit a limit, export stops with a diagnostic. Obtain finer audio alignment or make an evidenced boundary adjustment; preserve the entire word rather than inventing equally spaced character timestamps. Keep every previous export.

## Acceptance

Read all delivery cues and their neighboring cues. Check that:

- Text matches the reviewed spoken wording; only whitespace at cue edges changes.
- Each cue respects the selected character and duration limits, and begins/ends at recorded word spans.
- Cues use natural phrase boundaries where available, with complete words and punctuation attached to the phrase it closes. Inspect names, terminology, numbers with units and very short cues explicitly; dictionary segmentation does not establish semantic completeness.
- Times increase without overlap and stay inside the final audio duration, allowing millisecond rounding. Gaps corresponding to real pauses remain gaps.
- Correction spans and disputed boundaries have audio evidence or an explicit pending status. Existing audio-review gaps remain pending after resegmentation.

If a dictionary splits a specialist expression, merge the affected cues only when the result still fits both limits; otherwise choose another phrase boundary using the retained word times. Save any manual adjustment as a new delivery version with its source mapping. Hand off `delivery/subtitles.srt` and `delivery/transcript.delivery.json` together.

**Layout verified:** every cue passes the text, character-count, duration and time-order checks, and delivery links point to the same export version. **Boundary review complete:** each phrase boundary and correction span has a supported decision; pending intervals and missing evidence remain explicitly listed in `REVIEW.md` and the user-facing delivery status. Technical layout success does not resolve pending audio review.

## Reused experience

[stable-ts regrouping](https://github.com/jianfch/stable-ts#regrouping-words) combines gap, punctuation and length rules; its repository is archived, so this workflow borrows the approach without adding its inference stack. [WhisperX](https://github.com/m-bain/whisperX/blob/main/whisperx/__main__.py) exposes subtitle width/count limits. [Jieba](https://github.com/fxsjy/jieba) provides Chinese segmentation and token offsets and is used directly as an MIT-licensed dependency. No code from stable-ts or WhisperX is copied.
