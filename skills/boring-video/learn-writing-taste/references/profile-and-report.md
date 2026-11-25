# Profile and report

## Proposed changes

| ID | User evidence | Scope | Proposed rule | Reason | Destination |
| --- | --- | --- | --- | --- | --- |
| W01 | Quote or attributable before/after; file/anchor or session/turn | Language, medium, audience | Concrete target behavior | User's reason, or “Reason not stated” | Profile section |

Follow with unresolved questions, conflicts (existing and proposed rule plus evidence), and skipped items with their classifications. Omit empty sections. Include the proposed `AGENTS.md` pointer diff. Invite approval by ID or all items, with answers to unresolved questions. Existing authorization for specific rules can satisfy this gate; elapsed time cannot.

## Profile format

Create sections only for approved rules. Keep the file useful without the original conversation:

```markdown
# Writing taste

Apply rules only within their stated scope. Current explicit user instructions govern the current task; resolve durable conflicts before updating this profile.

## Explanation

### W01 — Concrete subjects

- Scope: Chinese spoken narration for technical explainers.
- Rule: Name the actor and action when explaining a technical change.
- Example: “The worker stores the result” rather than “Persistence is performed.”
- Reason: Not stated.
- Evidence: YYYY-MM-DD, NARRATION.md#b02-p01, user edit: “Persistence is performed” → “The worker stores the result”.
```

This is an illustrative format, not a default preference. Actual entries require attributable user evidence and approval. Use stable IDs when merging or updating a profile; retain relevant source dates and accepted examples. If a source has no stable locator, describe its available session or artifact context accurately rather than inventing a turn ID. Keep before/after excerpts short enough to explain the distinction.
