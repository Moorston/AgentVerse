# Development

## Prerequisites

- Python 3.12+
- Node.js 22+
- Docker + Docker Compose

## Setup

```bash
# Clone the repo
git clone https://github.com/your-org/agentverse.git
cd agentverse

# Install Python dependencies
uv sync

# Install web dependencies
cd apps/web && npm install && cd ../..
```

## Start Dev Environment

```bash
# Start databases
docker compose up -d neo4j postgres

# Start API (hot-reload)
cd apps/api && uv run uvicorn agentverse.api.main:app --reload --host 0.0.0.0 --port 8000

# Start Web (in another terminal)
cd apps/web && npm run dev
```

## Run Tests

```bash
# Python tests
uv run pytest

# Web tests
cd apps/web && npm test
```