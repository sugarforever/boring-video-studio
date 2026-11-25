---
name: learn-writing-taste
description: Learn reusable writing preferences from your article and narration edits, and save approved rules for future drafts.
disable-model-invocation: true
---

# Learn writing taste

Turn the user's article and narration corrections into durable writing rules. The output is a project writing profile and an `AGENTS.md` pointer; the source articles, scripts, and their approval metadata stay untouched.

Adapted from [Emil Kowalski's learn-taste](https://github.com/emilkowalski/skills/tree/main/skills/learn-taste): collect evidence, generalize narrowly, propose rules, then persist approved items.

## 1. Collect evidence

Read the available current conversation in order, the article or narration versions it refers to, and any existing writing profile or applicable style instructions. Include earlier sessions only when the user names them and their transcripts are accessible. State coverage gaps; ask for missing evidence only when needed to resolve a candidate.

Capture each explicit correction, attributable user edit, repeated nudge, rejection, or confirmed non-obvious choice. Record the exact quote or before/after excerpt, source location, language, medium, and any reason the user gave. For repeated nudges, capture the accepted endpoint.

A diff proves a change, not its author. Treat edits of uncertain authorship as questions. Agent suggestions, silence, and approval of an entire draft are insufficient evidence of an individual preference.

Done when every available correction has evidence and attribution, or is marked unresolved.

## 2. Filter and generalize

Ask whether the correction would help a fresh agent write a different article or script for this user. Classify every item:

- **Reusable:** a supported preference about voice, phrasing, explanation, structure, examples, or how the author frames claims.
- **Local:** a title, fact correction, audience requirement, or topic/argument boundary specific to this piece. Keep it in the content workflow; this skill only reports it.
- **Covered:** an existing rule already captures it. If that rule failed, propose sharpening its wording instead of duplicating it.
- **Conflict:** the correction contradicts an existing rule within the same scope. Present both with their evidence and ask which should apply.
- **Unresolved:** authorship, meaning, scope, or acceptance is unclear.

A boundary correction can support a reusable rule only when the user expresses a broader principle or confirms the proposed generalization. Preserve the distinction between article prose and spoken narration, and between languages, audiences, projects, and publication formats. Start at the narrowest reusable scope supported by the evidence; use cross-project scope only when the user explicitly requests it and names its destination.

Write a concrete target behavior at the strength the user expressed. Include a short before/after example when it disambiguates the rule. Use the user's stated reason; when absent, record “Reason not stated.” Offer an inferred reason only as a labeled question, and persist it only after confirmation. Style preferences operate within factual evidence and approved topic boundaries.

Done when every correction has a classification and every candidate has evidence, scope, actionable wording, and a reason status.

## 3. Propose the profile changes

Default to `WRITING-TASTE.md` at the project root. Reuse an existing authoritative writing profile when one exists. Read applicable `AGENTS.md` files and their linked style sources before choosing the destination; preserve their unrelated instructions. Show a proposed diff covering rules and the loading pointer, using the format in [Profile and report](references/profile-and-report.md).

Self-test each rule against the original correction and a different writing task: would a fresh agent reproduce the accepted choice, and would the scope keep it from overgeneralizing? Rewrite candidates that fail either test.

Present candidates, conflicts, unresolved questions, and skipped items with reasons. Stop for approval unless the user already authorized persisting these specific rules and their scope. A request to invoke this skill authorizes extraction and proposal; it does not approve inferred preferences. If there is no supported reusable preference, report that and finish without creating files.

## 4. Persist and verify

Write only approved candidates. Reconcile conflicts first; preserve unrelated profile entries. Add or update one pointer in the applicable project `AGENTS.md`, creating that file if necessary:

> Before drafting, revising, or reviewing articles or narration, read `WRITING-TASTE.md` and apply the rules matching the language, medium, and audience.

Use the actual relative profile path. Keep the rules in the profile rather than copying them into `AGENTS.md` or suite skills. For a user-selected destination outside the project, verify the project pointer resolves to it and report the portability limit. Store only the minimal evidence excerpt needed; omit unrelated personal or sensitive transcript material.

Verify that the pointer resolves, each changed rule traces to approved user evidence, scopes and exceptions remain intact, and there are no duplicate or unresolved conflicting rules. Show the resulting diff and state what changed. Completion means the approved profile is readable by the next agent through its pointer; it does not imply any article or narration was revised or approved.

## Prune

`/learn-writing-taste prune` reads the existing profile and proposes duplicate merges, scope corrections, conflict resolutions, and removal of unsupported or obsolete rules. Use the same proposal and approval flow; retain evidence for surviving rules.
