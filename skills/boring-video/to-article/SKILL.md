---
name: to-article
description: Use when an approved content topic, research bundle, and evidence need to become a complete platform-independent article before video beats or publication adaptation.
---

# To article

Turn an approved `content/TOPIC.md` into `content/ARTICLE.md`: the readable content master for both the eventual blog post and the video plan.

## Preconditions

Read `content/TOPIC.md`, `content/RESEARCH.md`, every cited experiment report, and the source material needed to verify the selected evidence. Continue only when `TOPIC.md` has `status: approved`.

Return to `/develop-topic` when writing exposes a missing material claim, contradictory evidence, an unsupported conclusion, or a needed change to the approved audience, thesis, scope, argument, evidence, or conclusion boundaries. Immediately return `TOPIC.md` to `status: draft`, resolve the gap there, and renew topic approval before drafting from it. Adding evidence that changes the confidence, boundary, or interpretation is material; adding an equivalent source without changing the contract is not.

## Voice

Resolve the article voice from the approved topic. Before drafting, inspect the available skills for a writing-style skill matching the output language and content type, then load every applicable user, project, or brand style source named in `voice.skills` or `voice.documents`.

If no reliable source exists for a publication-grade article, ask one compact question for the desired voice or a sample. When the user delegates that choice, or the article is explicitly an internal draft, use a clear explanatory default and record `voice.status: assumed`. Record unavailable named sources under `voice.unavailable`; they are not evidence that their rules were applied. An unavailable source does not block drafting when another available source resolves the voice.

## Draft

Write a complete, platform-independent article. It must stand alone for a reader, preserve the approved argument and boundaries, distinguish fact from interpretation, and cite the original sources behind material claims. Use headings, links, tables, or notes when they help reading; site-specific SEO fields, publishing components, and platform paths belong to a later publishing adaptation.

Write `content/ARTICLE.md` with this frontmatter:

```yaml
---
source: content/TOPIC.md
source_digest: sha256:<TOPIC approved_digest>
status: draft
voice:
  language: ...
  skills: []
  documents: []
  unavailable: []
  status: resolved | assumed
---
```

The article may improve the working title, prose, examples, and section order. It may compress or explain approved claims, but every material fact, viewpoint, and conclusion must trace to the approved topic and its evidence. New content goes upstream first.

## Approval gate

Present the complete article for review. Only explicit user approval changes its frontmatter to:

```yaml
status: approved
approved_at: YYYY-MM-DD
approved_digest: sha256:<digest>
```

Compute `approved_digest` as SHA-256 of the complete file after removing only the `approved_digest:` line. Before drafting or approving, recompute the topic digest and require it to match both `TOPIC.md`'s `approved_digest` and this article's `source_digest`. A mismatch makes the relevant approval or dependent draft stale. A verified non-material edit may refresh and propagate digests without renewed approval.

Until then, do not create `BEATS.md`. A request to continue production does not substitute for approval of the article itself.

A material revision to `TOPIC.md` returns the article to `draft`. A material revision to an approved article also returns it to `draft`; copy edits, title changes, and examples that preserve the approved meaning do not.

**REQUIRED SUB-SKILL:** Use `artifact-preview` for `content/ARTICLE.md` whenever it is ready for review and after every later source change.

The article is complete when it is approved, reads independently, every material statement traces to the approved content contract and sufficient evidence, a video planner can reorganize it without inventing facts, viewpoints, argument, or scope, and the `artifact-preview` completion criterion is satisfied for `content/ARTICLE.preview.html`.
