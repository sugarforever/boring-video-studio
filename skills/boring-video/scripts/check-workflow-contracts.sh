#!/usr/bin/env bash
set -euo pipefail

suite_root="$(cd "$(dirname "$0")/.." && pwd)"

require() {
  local pattern="$1"
  local file="$2"
  local message="$3"
  if ! rg --quiet --fixed-strings "$pattern" "$suite_root/$file"; then
    echo "FAIL: $message" >&2
    exit 1
  fi
}

require "production defaults" "boring-video/SKILL.md" \
  "the wrapper must resolve reusable project, series, or brand defaults"
require 'Create the workflow `BRIEF.md` at intake' "boring-video/SKILL.md" \
  "production defaults must be durable before upstream content stages"
require "real session" "to-scenes/references/scene-format.md" \
  "scene contracts must distinguish demonstration truth modes"
require "evidence replay" "to-scenes/references/scene-format.md" \
  "scene contracts must include evidence replay"
require "instructional reconstruction" "to-scenes/references/scene-format.md" \
  "scene contracts must include instructional reconstruction"
require '`real code`' "to-scenes/references/scene-format.md" \
  "scene contracts must label real code"
require "real code excerpt" "to-scenes/references/scene-format.md" \
  "scene contracts must label excerpted code"
require "illustrative code" "to-scenes/references/scene-format.md" \
  "scene contracts must label illustrative code"
require "serve the narration" "to-scenes/SKILL.md" \
  "visual planning must explicitly coordinate with narration"
require "visual state supports the spoken idea" "to-storyboard/SKILL.md" \
  "narration coordination must survive into storyboard planning"
require '<user>@<host> <short-path> > ' "record-terminal/references/terminal-visual-style.md" \
  "the terminal default must define the visible prompt shape"
require "publication branch" "boring-video/SKILL.md" \
  "requested covers and platform materials must enter the formal workflow"
require 'For direct-production work, this wrapper owns the same branch beside `/hyperframes`' "boring-video/SKILL.md" \
  "the publication branch must also route direct-production inputs"
require 'Direct-production work remains in `/hyperframes`' "boring-video/SKILL.md" \
  "direct-production publishing must not route through content-only to-video"

echo "PASS: boring-video workflow contracts are present"
