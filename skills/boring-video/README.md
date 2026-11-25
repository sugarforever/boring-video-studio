# Boring Video skill set

This directory groups the coordinated Boring Video planning skills. Each child directory containing a `SKILL.md` remains an independently discoverable skill; the source grouping does not namespace or rename it.

`boring-video` is the entry point. `setup-boring-video-skills` validates the complete set and its HyperFrames dependency.

## Writing preferences

[`learn-writing-taste`](learn-writing-taste/SKILL.md) is an optional, user-invoked companion for learning from article and narration edits. Install it separately:

```bash
npx skills add sugarforever/boring-video-studio --skill learn-writing-taste
```

After reviewing a draft, invoke `$learn-writing-taste` in the chat containing your corrections. It proposes reusable rules with evidence, reasons when stated, and scopes such as language, article prose, or spoken narration. Approve all candidates or selected IDs to save them in `WRITING-TASTE.md` (or an existing authoritative profile) and add an `AGENTS.md` loading pointer.

The article and narration stages read the linked profile for future drafts. Source content and approval metadata remain unchanged. Invoke `$learn-writing-taste prune` to review duplicates, conflicting scopes, and obsolete rules before approving maintenance changes.
