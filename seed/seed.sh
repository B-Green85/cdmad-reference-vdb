#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${BASE_URL:-http://127.0.0.1:8000}"
CHUNKS_FILE="$(dirname "$0")/chunks.json"

if [ ! -f "$CHUNKS_FILE" ]; then
  echo "ERROR: $CHUNKS_FILE not found" >&2
  exit 1
fi

COUNT=$(python3 -c "import json,sys; print(len(json.load(open(sys.argv[1]))))" "$CHUNKS_FILE")
echo "Seeding $COUNT chunks from $CHUNKS_FILE ..."

SUCCESS=0
for i in $(seq 0 $(( COUNT - 1 ))); do
  CHUNK=$(python3 -c "
import json, sys
chunks = json.load(open(sys.argv[1]))
print(json.dumps(chunks[int(sys.argv[2])]))
" "$CHUNKS_FILE" "$i")

  ID=$(echo "$CHUNK" | python3 -c "import json,sys; print(json.load(sys.stdin)['id'])")

  HTTP_CODE=$(curl -sS -o /dev/null -w "%{http_code}" \
    -X POST "${BASE_URL}/v1/docs/upsert" \
    -H "Content-Type: application/json" \
    -d "$CHUNK")

  if [ "$HTTP_CODE" -ne 200 ]; then
    echo "FAIL [$HTTP_CODE]: $ID" >&2
    exit 1
  fi

  echo "  ok: $ID"
  SUCCESS=$(( SUCCESS + 1 ))
done

echo "Done. $SUCCESS/$COUNT chunks seeded."
