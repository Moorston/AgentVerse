# syntax=docker/dockerfile:1
FROM python:3.12-slim AS builder

WORKDIR /app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copy dependency files first (for layer caching)
COPY pyproject.toml uv.lock* ./
COPY packages/shared/pyproject.toml packages/shared/
COPY packages/graph-core/pyproject.toml packages/graph-core/
COPY packages/ontology/pyproject.toml packages/ontology/
COPY packages/crawler/pyproject.toml packages/crawler/
COPY packages/extractor/pyproject.toml packages/extractor/
COPY packages/graphrag/pyproject.toml packages/graphrag/
COPY apps/worker/pyproject.toml apps/worker/

# Install dependencies
RUN uv sync --frozen --no-dev --project apps/worker 2>/dev/null || uv sync --project apps/worker

# Copy source code
COPY packages/shared/src packages/shared/src
COPY packages/graph-core/src packages/graph-core/src
COPY packages/ontology/src packages/ontology/src
COPY packages/crawler/src packages/crawler/src
COPY packages/extractor/src packages/extractor/src
COPY packages/graphrag/src packages/graphrag/src
COPY apps/worker/src apps/worker/src

# Runtime stage
FROM python:3.12-slim
WORKDIR /app
COPY --from=builder /app /app
CMD ["python", "-m", "agentverse.worker.main"]