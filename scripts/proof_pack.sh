#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${BASE_URL:-http://127.0.0.1:8000}"
POSTGRES_PORT="${POSTGRES_PORT:-5433}"
POSTGRES_USER="${POSTGRES_USER:-cdmad}"
POSTGRES_DB="${POSTGRES_DB:-cdmad_vdb}"

echo "=== PROOF PACK ==="
echo ""

echo "--- pwd ---"
pwd
echo ""

echo "--- timestamp (UTC) ---"
date -u '+%Y-%m-%dT%H:%M:%SZ'
echo ""

echo "--- git status ---"
git status --porcelain
echo ""

echo "--- git diff --stat ---"
git diff --stat
echo ""

echo "--- git log (last 10) ---"
git log --oneline -10
echo ""

echo "--- tree (depth 4) ---"
if command -v tree >/dev/null 2>&1; then
  tree -a -L 4 -I '.git|.venv' .
else
  find . -maxdepth 4 -print
fi
echo ""

echo "--- GET /health ---"
curl -sS "${BASE_URL}/health"
echo ""

echo "--- POST /v1/query ---"
curl -sS -X POST "${BASE_URL}/v1/query" \
  -H "Content-Type: application/json" \
  -d '{"query":"evidence beats explanation","k":3}'
echo ""
echo ""

echo "--- docs row count ---"
docker compose exec -T db psql -U "${POSTGRES_USER}" -d "${POSTGRES_DB}" \
  -c "SELECT COUNT(*) FROM docs;"
echo ""

echo "--- tests ---"
echo "no tests yet"
echo ""

echo "=== END PROOF PACK ==="
