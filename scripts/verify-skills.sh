#!/usr/bin/env bash
set -euo pipefail

REPO="$(cd "$(dirname "$0")/.." && pwd)"
EXPECTED=(
  artifact-preview
  boring-video
  develop-topic
  record-terminal
  setup-boring-video-skills
  to-article
  to-narration
  to-scenes
  to-spec-beats
  to-storyboard
  to-video
  verysmallwoods-video
)

mapfile_compat() {
  while IFS= read -r line; do
    SKILL_FILES+=("$line")
  done
}

SKILL_FILES=()
mapfile_compat < <(find "$REPO/skills" -name SKILL.md -not -path '*/node_modules/*' | sort)

NAMES=()
PATHS=()
failed=0
for skill_file in "${SKILL_FILES[@]}"; do
  name="$(sed -n 's/^name:[[:space:]]*//p' "$skill_file" | head -n 1)"
  if [ -z "$name" ]; then
    echo "error: missing name in ${skill_file#$REPO/}" >&2
    failed=1
    continue
  fi
  for i in "${!NAMES[@]}"; do
    if [ "${NAMES[$i]}" = "$name" ]; then
      echo "error: duplicate skill name '$name' in ${PATHS[$i]} and ${skill_file#$REPO/}" >&2
      failed=1
    fi
  done
  NAMES+=("$name")
  PATHS+=("${skill_file#$REPO/}")
done

for name in "${EXPECTED[@]}"; do
  found=0
  for actual in "${NAMES[@]}"; do
    if [ "$actual" = "$name" ]; then
      found=1
      break
    fi
  done
  if [ "$found" -eq 0 ]; then
    echo "error: expected skill '$name' is missing" >&2
    failed=1
  fi
done

if [ "$failed" -ne 0 ]; then
  exit 1
fi

echo "verified ${#SKILL_FILES[@]} skills"
