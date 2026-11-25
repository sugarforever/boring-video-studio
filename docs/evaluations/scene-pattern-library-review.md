# Scene-pattern library review

Reviewed on 2026-11-25 using `writing-for-agents` and its `SKILL-MECHANICS.md` reference. Scope: the `to-scenes` routing addition, scene-pattern reference, catalog, and gallery handoff. This is an applied skill review, not a separate GitHub approval.

## Findings resolved

- **Context pointers:** Added an explicit branch for chronology, comparison, evidence, evaluation, closing examples, and reference-video analysis. Kept details behind the reference instead of expanding the main workflow.
- **Single source of truth:** Removed the parallel family/ID table from the reference. `catalog.json` owns record metadata and example props; the generated browser catalog has a freshness check.
- **Contract ownership:** The current main branch already defines matched comparison and grouped-card presets. The new reference defers to those bounds and timing rules and retains the shared HTML scene-review gate. Gallery acceptance remains separate from scene acceptance.
- **Reachability:** Replaced a link to an unrelated uncommitted component-review draft with the committed shared project contract. Checked all new local Markdown links in the isolated checkout.
- **Completion criteria:** Original patterns require explicit viewer questions, inputs, constraints, themes, and inspectable examples. Reference-derived work retains research separately; the distributed gallery contains independent fictional cases and original SVG assets.
- **Co-location:** Moved catalog generation and verification instructions into their own maintenance section, separate from reference-video analysis.

## Validation and limits

The browser verification script checks 20 patterns across four themes, image loading, layout bounds, direct/sequential/backward seeking, filtering, theme selection, blind reveal, and edited copy. The catalog generation check and JavaScript syntax checks pass. Historical case/font inspection is recorded in `docs/research/scene-pattern-examples-review.json`.

The library is an opaque 16:9 design scaffold. Production media, narration, alternate ratios, scene exits, and assembled playback still require the project's normal review. No remaining findings from this writing-for-agents review.
