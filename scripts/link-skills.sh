#!/usr/bin/env bash
set -euo pipefail

# Maintainer convenience: expose recursively grouped source skills as a flat
# set of symlinks in Agent Skills-compatible local directories.
REPO="$(cd "$(dirname "$0")/.." && pwd)"
DESTS=("$HOME/.claude/skills" "$HOME/.agents/skills")

"$REPO/scripts/verify-skills.sh"

while IFS= read -r -d '' skill_md; do
  src="$(dirname "$skill_md")"
  name="$(sed -n 's/^name:[[:space:]]*//p' "$skill_md" | head -n 1)"

  for dest in "${DESTS[@]}"; do
    mkdir -p "$dest"
    target="$dest/$name"

    if [ -e "$target" ] && [ ! -L "$target" ]; then
      echo "error: refusing to replace non-symlink $target" >&2
      exit 1
    fi

    ln -sfn "$src" "$target"
    echo "linked $name -> $src ($dest)"
  done
done < <(find "$REPO/skills" -name SKILL.md -not -path '*/node_modules/*' -print0)
