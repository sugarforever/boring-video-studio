---
name: develop-topic
description: Use when a content-driven video has a candidate topic but still needs research, experiments, a defensible thesis, or user-approved scope before an article or video beats can be written.
---

# Develop topic

Turn a candidate topic into an approved content contract. The work is ready for writing only when the argument, evidence, and boundaries no longer need to be invented downstream.

## Scope

Start from one candidate topic or a small, naturally bounded set. When several nearby directions remain, compare them lightly for audience value, novelty, verifiability, demonstrability, author fit, and overclaiming risk; ask the user to choose before deep research. Open-ended trend scanning and maintaining an idea backlog stay outside this skill.

## Evidence workspace

Create a `content/` directory in the video project:

```text
content/
|-- RESEARCH.md
|-- TOPIC.md
`-- experiments/
```

Use `RESEARCH.md` for sourced facts, interpretations, disagreements, unknowns, rejected directions, and links to primary material. Keep collection separate from editorial selection.

Treat a claim as material when it affects whether the subject works, matters to the audience, differs from an alternative, can be demonstrated, or remains valid within the stated scope. Support it with a source or experiment strong enough for that exact claim; label weaker evidence `provisional` rather than silently stretching it.

When a claim needs runnable evidence, perform the smallest experiment that can settle it and write `content/experiments/<name>.md` with the question, method, samples, environment, command, results, limitations, and conclusions the result supports. Keep code and raw data in the project that owns them; record their paths and Git revision instead of copying them into the video project.

## Content contract

Write `content/TOPIC.md`:

```markdown
---
status: draft
audience: ...
core_question: ...
thesis: ...
scope: ...
voice:
  language: ...
  skills: []
  documents: []
  unavailable: []
  status: resolved | assumed
---

# Working title

## Reader promise

## Argument

### A01 - Claim
- role: Why this claim exists in the argument
- claim: The exact proposition
- evidence: Links to RESEARCH.md headings or experiment reports
- confidence: established | provisional
- boundary: What the evidence does not establish

## Out of scope

## Open questions

## Alternate titles
```

Resolve voice sources in this order: explicit user direction, project or brand guidance, an available writing-style skill matching the language and content type, visible user preferences, writing samples, then a clear explanatory default. Record the sources actually used and persist requested but unavailable sources under `voice.unavailable`; do not assume unavailable memory or a hidden profile.

## Approval gate

Present the working title, thesis, scope, argument, key evidence, boundaries, and material open questions for review. A title may keep changing, but audience, thesis, scope, argument, evidence, and conclusion boundaries are locked decisions.

Only explicit user approval changes the frontmatter to:

```yaml
status: approved
approved_at: YYYY-MM-DD
approved_digest: sha256:<digest>
```

The digest is SHA-256 of the complete file after removing only the `approved_digest:` line. Recompute it before trusting approval. A mismatch makes the approval stale and returns the file to `draft`. After a verified non-material title or copy edit, the digest may be refreshed without renewed approval; propagate the new digest to every dependent artifact.

Until then, keep all writing inside `RESEARCH.md`, experiment reports, and the draft `TOPIC.md`. Do not create `ARTICLE.md` or `BEATS.md`; a request to move quickly or permission to choose a thesis does not substitute for approval of the resulting contract.

A later material change to a locked decision returns `TOPIC.md` to `draft` and makes downstream article approval stale. Copy edits, examples, and title changes that preserve meaning do not revoke approval.

The topic is complete when `TOPIC.md` is approved, every material claim points to sufficient evidence, remaining open questions are non-blocking and visible, and an article writer can draft without inventing facts, experiments, author position, argument, or scope.
