#!/usr/bin/env bash
set -euo pipefail

echo "==> Starting databases..."
docker compose up -d neo4j postgres

echo "==> Starting API..."
uv run uvicorn agentverse.api.main:app --reload --host 0.0.0.0 --port 8000 &
API_PID=$!

echo "==> Starting Web..."
cd apps/web && npm run dev &
WEB_PID=$!

trap "kill $API_PID $WEB_PID 2>/dev/null" EXIT
wait