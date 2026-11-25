# Boring Video Studio

Boring Video Studio is a collection of [Agent Skills](https://agentskills.io) for planning high-quality videos before production.

For content-driven work, the main `boring-video` skill establishes and approves the content before it plans the video:

```text
content/TOPIC.md → content/ARTICLE.md → BEATS.md → NARRATION.md → SCENES.md → STORYBOARD.md
```

Research notes and experiment reports live beside the content contracts under `content/`. Product promos, UI demonstrations, music-led pieces, locked scripts, and other direct-production inputs can bypass the article chain and enter HyperFrames through its own intake.

It then hands the approved plan to [HyperFrames](https://www.hyperframes.dev), which owns video production, review, timing, animation, verification, and rendering. Optional [ListenHub](https://listenhub.ai) and [MiniMax](https://platform.minimax.io) TTS support can provide narration audio and subtitles through the `listenhub-tts` and `minimax-tts` skills, respectively.

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
7. `to-video` hands the complete plan and optional ListenHub or MiniMax narration to the appropriate HyperFrames workflow.

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

## MiniMax narration

Install the optional provider skill:

```bash
npx skills add sugarforever/boring-video-studio --skill minimax-tts
```

Choose MiniMax at the voice gate in `boring-video` or `verysmallwoods-video`,
or invoke `$minimax-tts` directly. Set `MINIMAX_API_KEY` in the environment;
`MINIMAX_API_BASE` selects the international (default), domestic, or US West endpoint.
The bundled Python 3.10+ CLI lists account voices and generates MP3 + sentence-level SRT,
with no extra Python dependencies. It uses native subtitle timestamps and preserves
audio if subtitle retrieval fails. Each synthesis accepts 1–9999 characters;
longer narration requires separate parts and timeline assembly.

See [MiniMax setup, commands and recovery](skills/boring-video/minimax-tts/SKILL.md).
Local tests use a substitute HTTP server and do not call the paid API:

```bash
python3 -m unittest discover -s skills/boring-video/minimax-tts/tests -v
```

## Record your own narration

`record-narration` provides a local browser teleprompter and microphone recorder,
multiple takes, WaveSurfer waveform selection/playback, interruption recovery, and selected-take handoff to the
agent. The agent identifies abandoned retries against the script and applies
reviewed cuts while retaining originals and an edit map. The bundled processing CLI normalizes loudness with ffmpeg-normalize in linear mode, generates
local Whisper subtitles, and applies agent-reviewed recognition corrections
without changing subtitle timing. Original recordings are retained.

```bash
npx skills add sugarforever/boring-video-studio --skill record-narration
```

```text
$record-narration Record my voice reading /absolute/path/NARRATION.md.
```

Run directly from a checkout:

```bash
python3 skills/boring-video/record-narration/scripts/recorder.py \
  --script /absolute/path/NARRATION.md \
  --session /absolute/path/project/narration/session-01 --port 0
```

Recording uses Python 3.10+ and Chrome or Safari. Processing additionally needs
FFmpeg; local transcription uses a Python 3.11/3.12 environment with
`pip install -r skills/boring-video/record-narration/requirements.txt`. Model weights download on first use;
recorded audio stays local. After selecting a take and submitting it in the page,
return to the chat and ask the agent to continue. The workflow preserves speaking speed and intended content;
automatic noise reduction and general pause compression are deferred.

See [the skill](skills/boring-video/record-narration/SKILL.md) for processing and
subtitle correction commands.

Development checks (activate the processing virtual environment first):

```bash
python -m unittest discover -s skills/boring-video/record-narration/tests -v
node --check skills/boring-video/record-narration/assets/recorder.js
```

The optional Chrome integration test uses Playwright and a synthetic microphone;
it covers scrolling, pause/resume, playback, failed uploads, recovery and handoff.
Install Playwright in a temporary directory, then run:

```bash
PLAYWRIGHT_MODULE=/absolute/path/node_modules/playwright \
NARRATION_PYTHON=/absolute/path/venv/bin/python \
  node skills/boring-video/record-narration/tests/browser.cjs
```

## Learn your writing preferences

Install the optional companion with `npx skills add sugarforever/boring-video-studio --skill learn-writing-taste`. After reviewing an article or narration, invoke `/learn-writing-taste` to extract reusable preferences from your corrections. It proposes evidence-backed rules, then saves approved items in `WRITING-TASTE.md` with an `AGENTS.md` loading pointer. `/learn-writing-taste prune` proposes maintenance of an existing profile.
