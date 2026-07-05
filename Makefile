.PHONY: help install dev test lint format typecheck clean docker-up docker-down schema seed pipeline

help: ## Show available commands
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install all dependencies (Python + Node)
	uv sync
	cd apps/web && npm install

dev: ## Start development environment (db + api + web)
	docker compose up -d neo4j postgres
	@echo "Starting API..." && cd apps/api && uv run uvicorn agentverse.api.main:app --reload --host 0.0.0.0 --port 8000 &
	@echo "Starting Web..." && cd apps/web && npm run dev &
	@echo "Press Ctrl+C to stop all"; wait

schema: ## Initialize Neo4j schema (constraints + indexes)
	uv run python scripts/init_schema.py

seed: ## Load seed data into Neo4j
	uv run python scripts/seed_data.py

pipeline: ## Run data pipeline (crawl arXiv + extract + store)
	uv run python scripts/run_pipeline.py --max-papers 10

pipeline-dry: ## Run data pipeline in dry-run mode (no DB writes)
	uv run python scripts/run_pipeline.py --max-papers 5 --dry-run

test: ## Run all Python tests
	uv run python -m pytest packages/shared/tests/ packages/graph-core/tests/ packages/ontology/tests/ packages/crawler/tests/ packages/extractor/tests/ apps/api/tests/ -v

test-unit: ## Run unit tests only (no DB required)
	@PYTHONPATH="packages/shared/src:packages/graph-core/src:packages/ontology/src:packages/crawler/src:packages/extractor/src" uv run python -c "
	from agentverse.shared.config import Settings; s = Settings(); assert s.neo4j_uri == 'bolt://localhost:7687'; print('shared: OK')
	from agentverse.graph_core.models.relationship import RelationshipType; assert len(RelationshipType) == 24; print('graph-core: OK')
	from agentverse.ontology.concepts.agent import AgentConcept; assert 'Agent' in AgentConcept(name='T', description='d').labels; print('ontology: OK')
	from agentverse.crawler.base import CrawlResult; assert CrawlResult(source='t').items == []; print('crawler: OK')
	from agentverse.extractor.base import ExtractionResult; assert ExtractionResult(source='t').entities == []; print('extractor: OK')
	print('ALL UNIT TESTS PASSED')
	"

test-api: ## Run API tests
	uv run python -m pytest apps/api/tests/ -v

lint: ## Run linters
	uv run ruff check .
	uv run ruff format --check .

format: ## Format code
	uv run ruff format .
	uv run ruff check --fix .

typecheck: ## Run type checking
	uv run mypy

clean: ## Clean build artifacts
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".next" -exec rm -rf {} + 2>/dev/null || true
	rm -rf dist/ build/ .coverage htmlcov/ .mypy_cache/ .ruff_cache/

docker-up: ## Start all services with Docker Compose
	docker compose up -d --build

docker-down: ## Stop all services
	docker compose down

db-start: ## Start databases only
	docker compose up -d neo4j postgres

db-stop: ## Stop databases
	docker compose stop neo4j postgres

api: ## Start API server only
	cd apps/api && uv run uvicorn agentverse.api.main:app --reload --host 0.0.0.0 --port 8000

web: ## Start web frontend only
	cd apps/web && npm run dev

worker: ## Start background worker
	uv run python -m agentverse.worker.main