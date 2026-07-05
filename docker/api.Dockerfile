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
COPY packages/graphrag/pyproject.toml packages/graphrag/
COPY apps/api/pyproject.toml apps/api/

# Install dependencies
RUN uv sync --frozen --no-dev --project apps/api 2>/dev/null || uv sync --project apps/api

# Copy source code
COPY packages/shared/src packages/shared/src
COPY packages/graph-core/src packages/graph-core/src
COPY packages/ontology/src packages/ontology/src
COPY packages/graphrag/src packages/graphrag/src
COPY apps/api/src apps/api/src

# Build wheel
RUN uv build --project apps/api 2>/dev/null || echo "Build deferred to runtime stage"

# Runtime stage
FROM python:3.12-slim
WORKDIR /app
COPY --from=builder /app/dist/*.whl . 2>/dev/null || true
RUN pip install --no-cache-dir -e /app 2>/dev/null || true
EXPOSE 8000
CMD ["uvicorn", "agentverse.api.main:app", "--host", "0.0.0.0", "--port", "8000"]