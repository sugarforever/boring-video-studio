---
name: setup-boring-video-skills
description: Use when installing, validating, or repairing the Boring Video planning skill set before its first use.
---

# Setup Boring Video skills

Verify that the complete planning suite and its production dependency are available. This skill validates the toolchain; it does not create a video project.

## Required suite

The following skills must be discoverable by name:

```text
boring-video
artifact-preview
develop-topic
to-article
to-spec-beats
to-narration
to-scenes
to-storyboard
to-video
record-terminal
setup-boring-video-skills
```

Do not require `verysmallwoods-video`; it is a separate standalone workflow.

## Setup

1. Inspect the available skills and, when this repository is present, run `scripts/verify-skills.sh` from its root.
2. Report missing or duplicate skill names. A grouped source path is valid: installation must expose each directory containing `SKILL.md` as a flat skill named by its frontmatter.
3. If suite skills are missing, offer the repository's complete install command from `README.md`. Run an install command only when the user asks you to install or repair the installation.
4. Confirm that the `hyperframes` skill is available, then run `npx hyperframes doctor`. HyperFrames owns production and is a hard dependency for the later stages.
5. Report optional voice support separately. ListenHub is needed only when the user chooses that voice branch.

Setup is complete only when all required suite names are discoverable, HyperFrames is discoverable, and `npx hyperframes doctor` passes. Preserve the diagnostic output when a check fails and give the smallest corrective action; do not claim readiness from file presence alone.
