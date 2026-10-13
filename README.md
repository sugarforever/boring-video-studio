# Boring Video Studio

Boring Video Studio is a collection of [Agent Skills](https://agentskills.io) for planning high-quality videos before production.

For content-driven work, the main `boring-video` skill establishes and approves the content before it plans the video:

```text
content/TOPIC.md → content/ARTICLE.md → BEATS.md → NARRATION.md → SCENES.md → STORYBOARD.md
```

Research notes and experiment reports live beside the content contracts under `content/`. Product promos, UI demonstrations, music-led pieces, locked scripts, and other direct-production inputs can bypass the article chain and enter HyperFrames through its own intake.

It then hands the approved plan to [HyperFrames](https://www.hyperframes.dev), which owns video production, review, timing, animation, verification, and rendering. Optional [ListenHub](https://listenhub.ai) TTS support can provide narration audio and subtitles through the `listenhub-tts` skill.

The existing `verysmallwoods-video` skill remains available as the complete VerySmallWoods publishing workflow for videos, covers, platform copy, blog posts, and social posts.

## Installation

Install `boring-video`, its planning stages, and the setup verifier:

```bash
npx skills add sugarforever/boring-video-studio \
  --skill setup-boring-video-skills boring-video develop-topic to-article to-spec-beats to-narration to-scenes to-storyboard to-video record-terminal
```

Add `--global` to make the skills available across projects:

```bash
npx skills add sugarforever/boring-video-studio --global \
  --skill setup-boring-video-skills boring-video develop-topic to-article to-spec-beats to-narration to-scenes to-storyboard to-video record-terminal
```

The repository groups these coordinated skills under `skills/boring-video/`, but installation exposes their existing names as a flat skill set. `verysmallwoods-video` stays at `skills/verysmallwoods-video/` and can be installed independently.

After installation, invoke `$setup-boring-video-skills` once to verify the complete set and run the HyperFrames environment check.

Video production requires HyperFrames and its local dependencies. Check the environment with:

```bash
npx hyperframes doctor
```

## Usage

Invoke `$boring-video` with a topic or source document:

```text
$boring-video Turn this article into a planned eight-minute faceless explainer.
```

For a content-driven video, the skill asks for any missing production choices and runs the planning chain:

1. `develop-topic` researches the topic, records experiments, and obtains approval for the thesis, argument, evidence, and boundaries.
2. `to-article` writes the platform-independent content master and obtains article approval.
3. `to-spec-beats` reorganizes the approved article into the video's learning progression.
4. `to-narration` writes the spoken draft without adding new content.
5. `to-scenes` designs visual events, worlds, action, and continuity.
6. `to-storyboard` translates the scenes into buildable shots.
7. `to-video` hands the complete plan and optional ListenHub narration to the appropriate HyperFrames workflow.

Every planning stage maintains one authoritative Markdown artifact at a stable path. Codex opens that file directly for reading and uses the source or diff review surface for line comments; Git holds its history. Rendered images and media remain evidence referenced from Markdown, while HyperFrames Studio owns playable timeline and motion review.

An existing complete article can start at `to-spec-beats` after the user explicitly confirms it as the content master. Later artifacts are resumable only when their lineage traces to that approved article.

You can also invoke an individual stage when you already have its input:

Install an individual stage together with the Skills it invokes. For example, add `record-terminal` when the storyboard contains terminal, CLI, database, or TUI shots:

```bash
npx skills add sugarforever/boring-video-studio --skill record-terminal to-storyboard
```

```text
$to-storyboard Turn SCENES.md into a HyperFrames storyboard.
```
