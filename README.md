# Boring Video Studio

Agent skills for turning a topic, article, or script into a reviewed video with [HyperFrames](https://www.hyperframes.dev).

## 1. Copy and paste to your agent

**Install** - paste this into an agent that supports skills:

```text
Install the Boring Video core skills in this project:

npx skills add sugarforever/boring-video-studio --skill setup-boring-video-skills boring-video develop-topic to-article to-spec-beats to-narration to-scenes to-storyboard to-video record-terminal

Ensure the separate hyperframes skill and its production dependencies are available.
Run setup-boring-video-skills, including npx hyperframes doctor.
Report any missing dependencies; confirm readiness only when verification passes.
```

For installation across projects, add `--global` to the command. Optional skills below can be installed with `npx skills add sugarforever/boring-video-studio --skill <name>`.

**Create a video** - replace the brackets and paste:

```text
Use boring-video to make a [duration] video about [topic or source path].
Language: [language]. Audience: [audience]. Voice: [recording, TTS, or none].
Develop and review the content, finish and review the scenes, then assemble the video.
Ask me to approve the content and scene reviews before proceeding. Export the final MP4.
```

**Continue or revise**:

```text
Use boring-video to continue the project at [project path].
Requested change: [change, or "continue from the last approved stage"].
Check the existing approvals and source versions, then resume at the affected stage.
```

## 2. User guide

Start with **boring-video**. It coordinates research, writing, narration, scenes, and final assembly. You supply the topic or material, audience, duration, and preferences; the agent asks for missing choices and presents work for review. In Codex, invoke it as `$boring-video`; other agents can use the skill name in natural language.

```text
topic → article → beats → narration → finished scenes → assembly plan → video
```

Scenes are reviewed as playable HTML with narration before assembly. The storyboard plans scene order, cuts, and boundary transitions; final production joins those approved scenes and checks the complete film.

An article you approve as the content master can start at beats. Existing projects resume after approval and source-version checks. Locked scripts, promos, and UI demos can go directly to HyperFrames. Request covers, platform copy, or other publishing outputs when needed.

### Skills at a glance

| Skill | Purpose |
| --- | --- |
| [boring-video](skills/boring-video/boring-video/SKILL.md) | Coordinate the workflow and choose where to start or resume. |
| [setup-boring-video-skills](skills/boring-video/setup-boring-video-skills/SKILL.md) | Verify the installed suite and HyperFrames environment. |
| [develop-topic](skills/boring-video/develop-topic/SKILL.md) | Research evidence and agree on the thesis and scope. |
| [to-article](skills/boring-video/to-article/SKILL.md) | Write the complete article that establishes the content. |
| [to-spec-beats](skills/boring-video/to-spec-beats/SKILL.md) | Organize the approved article into the video's narrative beats. |
| [to-narration](skills/boring-video/to-narration/SKILL.md) | Write the spoken script from those beats. |
| [to-scenes](skills/boring-video/to-scenes/SKILL.md) | Build and review finished scenes, including internal motion and narration. |
| [to-storyboard](skills/boring-video/to-storyboard/SKILL.md) | Plan scene placement, cuts, and boundary transitions. |
| [to-video](skills/boring-video/to-video/SKILL.md) | Assemble scenes, master audio, review playback, and export. |
| [record-terminal](skills/boring-video/record-terminal/SKILL.md) | Capture terminal, CLI, code-entry, and TUI demonstrations. |
| [record-narration](skills/boring-video/record-narration/SKILL.md) *(optional)* | Record voice and optional synchronized webcam with a teleprompter; review takes and prepare audio/subtitles. |
| [minimax-tts](skills/boring-video/minimax-tts/SKILL.md) *(optional)* | Generate MiniMax narration and subtitles; requires API credentials. |
| [learn-writing-taste](skills/boring-video/learn-writing-taste/SKILL.md) *(optional)* | Save writing preferences from your corrections after you approve them. |
| [verysmallwoods-video](skills/verysmallwoods-video/SKILL.md) *(optional)* | Run the VerySmallWoods workflow for video, covers, platform copy, blog, and social posts. |

Use an individual skill when its inputs are ready. Follow its linked instructions for dependencies and detailed commands. HyperFrames is required for production and is installed separately; paid voice services require their own credentials.

For webcam framing, reading layouts and synchronized exports, see the [camera workflow](skills/boring-video/record-narration/references/camera.md).
