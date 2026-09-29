---
name: to-narration
description: Use when writing or revising spoken narration from complete, lineage-valid video beats, including scripts that must remain open to later visual direction.
---

# To narration

Turn `BEATS.md` into `NARRATION.md`: the spoken version of the approved article and video structure. This pass changes language for the ear; it does not establish the author's argument for the first time.

## Process

1. Read `BEATS.md`, its approved `content/ARTICLE.md` source, the cited evidence needed for accuracy, and the resolved voice sources recorded by the article. Recompute the article approval digest and beats artifact digest; require them to match the stored article `approved_digest`, beats `source_digest`, and beats `artifact_digest`. Load every applicable writing-style skill or document that is available. Preserve each beat's job, claim, and handoff.
2. Write for the ear: one thought per sentence, concrete subjects and verbs, spoken transitions, and terminology explained at first use. Preserve the author's voice while adapting reading prose into speech.
3. Let visuals carry visible structure, comparison, and transformation. The narration supplies meaning the image cannot communicate alone.
4. Mark paragraph-to-beat boundaries without adding visual instructions. Put unresolved pronunciation or factual questions in an `Open checks` section.
5. Write `NARRATION.md`:

```markdown
---
source: BEATS.md
source_digest: sha256:<BEATS artifact_digest>
content_source: content/ARTICLE.md
content_digest: sha256:<ARTICLE approved_digest>
artifact_digest: sha256:<digest>
status: draft
target_duration: ...
---

## B01 — Title

<a id="b01-p01"></a>
Spoken paragraph.
```

Compute `artifact_digest` as SHA-256 of the complete narration file after removing only the `artifact_digest:` line. Downstream stages must recompute it before use.

6. Give every paragraph a stable `<beat-id>-pNN` anchor. Preserve anchors when rewriting that paragraph; assign a new anchor when inserting one.
7. Read it aloud or estimate at the user's known speaking rate. Revise until every beat fits its budget and the full draft fits the target.

Every material fact, viewpoint, and conclusion must trace through its beat to the approved article. When speech needs content the article does not establish, immediately return `content/ARTICLE.md` to `status: draft` and revise it there; return `content/TOPIC.md` to `draft` too when the change affects a locked topic decision. Renew the approvals defined by those upstream files, update `BEATS.md` to match, and only then use the content in narration. `BEATS.md` has no separate approval state in this workflow.

The draft is complete when it is ready for visual planning, every material sentence traces to both a beat and the approved article, and no later visual has been prematurely prescribed. The selected HyperFrames workflow owns review timing and the voice-ready narration version after handoff.
