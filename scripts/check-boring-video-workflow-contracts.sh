#!/usr/bin/env bash
set -euo pipefail

root="$(cd "$(dirname "$0")/.." && pwd)"

require() {
  local pattern="$1"
  local file="$2"
  local message="$3"
  if ! rg --quiet --fixed-strings "$pattern" "$root/$file"; then
    echo "FAIL: $message" >&2
    exit 1
  fi
}

require "production defaults" "skills/boring-video/boring-video/SKILL.md" \
  "the wrapper must resolve reusable project, series, or brand defaults"
require 'Create the workflow `BRIEF.md` at intake' "skills/boring-video/boring-video/SKILL.md" \
  "production defaults must be durable before upstream content stages"
require "real session" "skills/boring-video/to-scenes/references/scene-format.md" \
  "scene contracts must distinguish demonstration truth modes"
require "evidence replay" "skills/boring-video/to-scenes/references/scene-format.md" \
  "scene contracts must include evidence replay"
require "instructional reconstruction" "skills/boring-video/to-scenes/references/scene-format.md" \
  "scene contracts must include instructional reconstruction"
require '`real code`' "skills/boring-video/to-scenes/references/scene-format.md" \
  "scene contracts must label real code"
require "real code excerpt" "skills/boring-video/to-scenes/references/scene-format.md" \
  "scene contracts must label excerpted code"
require "illustrative code" "skills/boring-video/to-scenes/references/scene-format.md" \
  "scene contracts must label illustrative code"
require "serve the narration" "skills/boring-video/to-scenes/SKILL.md" \
  "visual planning must explicitly coordinate with narration"
require "visual state supports the spoken idea" "skills/boring-video/to-storyboard/SKILL.md" \
  "narration coordination must survive into storyboard planning"
require '<user>@<host> <short-path> > ' "skills/boring-video/record-terminal/references/terminal-visual-style.md" \
  "the terminal default must define the visible prompt shape"
require "publication branch" "skills/boring-video/boring-video/SKILL.md" \
  "requested covers and platform materials must enter the formal workflow"
require 'For direct-production work, this wrapper owns the same branch beside `/hyperframes`' "skills/boring-video/boring-video/SKILL.md" \
  "the publication branch must also route direct-production inputs"
require 'Direct-production work remains in `/hyperframes`' "skills/boring-video/boring-video/SKILL.md" \
  "direct-production publishing must not route through content-only to-video"

echo "PASS: boring-video workflow contracts are present"
