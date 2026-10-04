---
name: to-spec-beats
description: Use when an approved content article needs to be reorganized into the factual and narrative architecture for a narrated video.
---

# To spec beats

Turn an approved `content/ARTICLE.md` into `BEATS.md`: the video's factual and narrative spine. The article owns what the work says; this pass decides what the viewer learns when. Later passes decide spoken wording and visuals.

## Process

1. Read `content/ARTICLE.md`, `content/TOPIC.md` when it exists, and the evidence needed to preserve their boundaries. Recompute each approved file's SHA-256 after removing only its `approved_digest:` line; continue only when the stored digest matches the current file and the article has `status: approved`. When a user brings a complete article from outside this workflow, first place or adapt it as `content/ARTICLE.md` using the external-source contract from `/boring-video`; a separate topic contract is not required retroactively.
2. Inherit the audience, thesis, and scope from the approved article and topic contract when present. Define only the audience's prior knowledge, desired change in understanding, target duration, and the video's selection from the approved scope.
3. Build the reverse-iceberg arc: hook in viewer language, value or answer by beat two, then evidence, mechanism, implications, and close. Reorder, compress, or omit article material for the medium while preserving meaning and boundaries.
4. Give every beat one cognitive job. Split beats that require two independent realizations; remove beats whose job does not trace to the approved thesis.
5. Write `BEATS.md` beside `content/` using this shape:

```markdown
---
source: content/ARTICLE.md
source_digest: sha256:<ARTICLE approved_digest>
artifact_digest: sha256:<digest>
audience: ...
thesis: ...
viewer_shift: ... → ...
target_duration: ...
---

## B01 — Title
- job: What changes in the viewer's understanding
- claim: The factual statement this beat establishes
- source: Article heading or passage that establishes it
- evidence: Source or experiment already selected by the article
- setup: Prior beat knowledge this depends on
- handoff: Question or tension passed forward
- duration: Rough narration budget

Notes needed to write this beat accurately.
```

Compute `artifact_digest` as SHA-256 of the complete beats file after removing only the `artifact_digest:` line. Any later stage must recompute it rather than trust the stored value.

6. Audit the complete file: every material claim and viewpoint traces to the approved article, every dependency points backward, the thesis lands by beat two, and the duration budgets fit the target.

When the video structure exposes a missing fact, viewpoint, argument step, or conclusion, return it to `content/ARTICLE.md`. If resolving it changes a locked topic decision, return `content/TOPIC.md` to `draft` as well. Renew the required approvals, then propagate the change forward. Do not patch a content gap inside `BEATS.md`.

Beat IDs are stable interfaces. Preserve them through revisions and assign a new ID when inserting a beat.

**REQUIRED SUB-SKILL:** Use `artifact-preview` for `BEATS.md` before declaring it complete and after every later source change.

`BEATS.md` is complete when another writer can draft the narration without inventing content, every beat is a medium-specific arrangement of the approved article rather than a new argument, and the `artifact-preview` completion criterion is satisfied for `BEATS.preview.html`.
