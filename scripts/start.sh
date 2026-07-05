#!/usr/bin/env bash
# AgentVerse — Comprehensive startup script
# Usage: ./scripts/start.sh [command]
# Commands: all, db, schema, seed, pipeline, api, web, worker

set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PYTHON=".venv/Scripts/python.exe"
CMD="${1:-all}"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

log() { echo -e "${BLUE}[AgentVerse]${NC} $1"; }
ok()  { echo -e "${GREEN}[OK]${NC} $1"; }
warn(){ echo -e "${YELLOW}[WARN]${NC} $1"; }

cd "$PROJECT_ROOT"

# === Functions ===

start_db() {
    log "Starting databases..."
    docker compose up -d neo4j postgres
    log "Waiting for databases to be healthy..."
    sleep 5
    ok "Databases started"
}

init_schema() {
    log "Initializing Neo4j schema..."
    $PYTHON scripts/init_schema.py
    ok "Schema initialized"
}

seed_data() {
    log "Seeding data..."
    $PYTHON scripts/seed_data.py
    ok "Seed data loaded"
}

run_pipeline() {
    local max="${2:-10}"
    log "Running data pipeline (max $max papers)..."
    $PYTHON scripts/run_pipeline.py --max-papers "$max"
    ok "Pipeline complete"
}

start_api() {
    log "Starting API server..."
    cd apps/api
    $PYTHON -m uvicorn agentverse.api.main:app --reload --host 0.0.0.0 --port 8000
}

start_web() {
    log "Starting web frontend..."
    cd apps/web
    npm run dev
}

start_worker() {
    log "Starting worker..."
    $PYTHON -m agentverse.worker.main
}

show_help() {
    echo "AgentVerse Startup Script"
    echo ""
    echo "Usage: ./scripts/start.sh [command]"
    echo ""
    echo "Commands:"
    echo "  all        Start everything (db + schema + seed + api + web)"
    echo "  db         Start Neo4j and PostgreSQL"
    echo "  schema     Initialize Neo4j schema (constraints + indexes)"
    echo "  seed       Load seed data"
    echo "  pipeline   Run data pipeline (crawl + extract + store)"
    echo "  api        Start FastAPI server"
    echo "  web        Start Next.js frontend"
    echo "  worker     Start background worker"
    echo "  help       Show this help"
    echo ""
    echo "Examples:"
    echo "  ./scripts/start.sh all              # Full startup"
    echo "  ./scripts/start.sh db && ./scripts/start.sh schema && ./scripts/start.sh seed"
    echo "  ./scripts/start.sh pipeline 20      # Crawl 20 papers"
}

# === Main ===

case "$CMD" in
    all)
        start_db
        init_schema
        seed_data
        log "Starting API and Web..."
        start_api &
        start_web &
        wait
        ;;
    db)       start_db ;;
    schema)   init_schema ;;
    seed)     seed_data ;;
    pipeline) run_pipeline "$@" ;;
    api)      start_api ;;
    web)      start_web ;;
    worker)   start_worker ;;
    help|-h|--help) show_help ;;
    *)        warn "Unknown command: $CMD"; show_help; exit 1 ;;
esac