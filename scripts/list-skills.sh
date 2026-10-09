#!/usr/bin/env bash
set -euo pipefail

REPO="$(cd "$(dirname "$0")/.." && pwd)"

find "$REPO/skills" -name SKILL.md -not -path '*/node_modules/*' -print \
  | sed "s|^$REPO/||" \
  | sort
