# Markdown artifact review

Every planning stage owns one authoritative Markdown file at its canonical path. Update that file in place; do not create version-suffixed copies such as `BEATS-v2.md`, `NARRATION-final.md`, or parallel HTML previews. The canonical path is the current version, Git records history, and the artifact digest records machine-readable lineage.

## Present for review

After creating or changing an artifact:

1. Recompute its digest and propagate any required stale state or source digest changes.
2. Present the Markdown through the host's native file view. In Codex, open the exact `.md` file with `open_in_codex`; otherwise provide a clickable absolute-path link supported by the host.
3. Use the source or diff review surface for line comments. Apply accepted feedback to the same Markdown file and present the refreshed file or diff.

Presentation does not record approval. Only the approval rule in the artifact-owning skill changes approval metadata or advances a gate.

## Rendered evidence

When a planning decision needs pixels or media, keep the decision in Markdown and reference the evidence from it:

- embed inspectable images with Markdown image syntax;
- link audio, video, or a HyperFrames project from the relevant section;
- identify the project revision and scene, frame, state, or timestamp that produced the evidence;
- refresh stale evidence after a source or design change.

Use HyperFrames Studio for playable timeline, motion, transition, and final-look review. A generated Markdown-adjacent HTML player is not a planning artifact.

## Completion criterion

The review handoff is complete when the canonical Markdown exists, its stored digest matches its current contents, every required section and evidence reference is present, and the current file has been presented through a supported host branch.
