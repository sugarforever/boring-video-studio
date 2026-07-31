#!/usr/bin/env bash
# listenhub-speakers.sh — 列出 ListenHub 音色(speakers),供选音色
#
# 选好的 speakerId 作为 listenhub-tts.sh 的第 3 个参数传入。
#
# 用法:
#   LISTENHUB_API_KEY=...  scripts/listenhub-speakers.sh [zh|en] [--json]
#     默认 zh;--json 打原始 JSON(给 agent 解析),否则打可读音色表
#
# 端点:GET /v1/speakers/list?language=<lang>   (Authorization: Bearer $LISTENHUB_API_KEY)
# 依赖:curl · python3(srt_helper.py 同目录)
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LH_BASE="${LISTENHUB_API_BASE:-https://api.marswave.ai/openapi/v1}"
LANG_FILTER="${1:-zh}"
AS_JSON=0
[ "${2:-}" = "--json" ] && AS_JSON=1
[ "${1:-}" = "--json" ] && { AS_JSON=1; LANG_FILTER="zh"; }

command -v curl >/dev/null || { echo "need curl" >&2; exit 1; }
command -v python3 >/dev/null || { echo "need python3" >&2; exit 1; }
: "${LISTENHUB_API_KEY:?set LISTENHUB_API_KEY (https://listenhub.ai/settings/api-keys)}"

RESP="$(mktemp -t lh-spk)"; trap 'rm -f "$RESP"' EXIT
code=$(curl -sS -w '%{http_code}' -o "$RESP" \
  "$LH_BASE/speakers/list?language=$LANG_FILTER" \
  -H "Authorization: Bearer $LISTENHUB_API_KEY")
[ "$code" = "200" ] || { echo "speakers list failed (HTTP $code):" >&2; head -c 600 "$RESP" >&2; echo >&2; exit 1; }

if [ "$AS_JSON" = "1" ]; then
  cat "$RESP"
else
  python3 "$HERE/srt_helper.py" speakers "$RESP"
fi
