#!/usr/bin/env bash
# AgentVerse Docker Setup Script
set -euo pipefail

GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

log() { echo -e "${GREEN}[AgentVerse]${NC} $1"; }
err() { echo -e "${RED}[Error]${NC} $1"; }

# Check Docker
if ! command -v docker &>/dev/null; then
    err "Docker is not installed."
    echo "Please install Docker Desktop: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check Docker Compose
if ! docker compose version &>/dev/null; then
    err "Docker Compose not available."
    exit 1
fi

log "Starting databases..."
docker compose up -d neo4j postgres

log "Waiting for databases to be healthy..."
sleep 10

# Check Neo4j
if docker compose exec neo4j cypher-shell -u neo4j -p agentverse_dev "RETURN 1" &>/dev/null; then
    log "Neo4j is ready"
else
    err "Neo4j not ready yet, waiting 10 more seconds..."
    sleep 10
fi

# Check PostgreSQL
if docker compose exec postgres pg_isready -U agentverse &>/dev/null; then
    log "PostgreSQL is ready"
else
    err "PostgreSQL not ready yet, waiting 10 more seconds..."
    sleep 10
fi

log "Initializing schema..."
uv run python scripts/init_schema.py

log "Seeding data..."
uv run python scripts/seed_data.py

log "Setup complete!"
echo ""
echo "Next steps:"
echo "  uv run python scripts/build_knowledge_graph.py"
echo "  cd apps/api && uv run uvicorn agentverse.api.main:app --reload"
echo "  cd apps/web && npm run dev"
