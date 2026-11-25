# Scene-pattern library review

Applied `writing-for-agents` and `SKILL-MECHANICS.md` on 2026-11-25. Reviewed all PR additions: routing, references, catalog/schema, generated output, renderer/gallery guidance, verification scripts, assets, and font notices. License text and illustrative case copy are content, not workflow instructions.

## Resolved

| Rule | Change |
| --- | --- |
| Context pointers | Replaced repeated purpose lists with one pointer for reusable examples or reference-video analysis. |
| Pruning | Reduced the scene-pattern reference from 823 to 370 words; retained selection, API, production limits, reference provenance, and maintenance. |
| Single source of truth | Catalog owns case props and shared preview settings; renderer fallback cases and repeated per-pattern settings removed. Generated JavaScript remains checked output. |
| Accuracy | Removed unsupported `activeIndex` and catalog `inspectedTimes`; renamed proposed `motion` to production `direction`. Corrected constraints for illustrative media, general pricing, and result states. |
| Contract ownership | Existing presets own bounds/timing; the shared project contract owns scene acceptance. Removed the uncommitted-document dependency. |
| Co-location | Grouped API semantics and maintenance separately; documented shallow overrides and page-relative media paths. |

## Verification

The updated browser check passes all 80 default-case theme variants and gallery interactions. Catalog freshness, JavaScript syntax, local links, and diff whitespace checks pass. Case/font evidence remains in `docs/research/scene-pattern-examples-review.json`.

No remaining findings in this writing review. Opaque 16:9 gallery acceptance does not establish production media, narration, other ratios, or assembled playback acceptance.
