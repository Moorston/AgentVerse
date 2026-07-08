# Upgrade Core Components

## Summary

Replace three under-engineered core components with purpose-built solutions:
1. **LLMClient → PydanticAI**: typed structured output, built-in retry, connection reuse
2. **Scheduler → TaskIQ**: async-native task orchestration with retry, chaining, concurrency control
3. **HybridSearch → Query Router + Cache**: adaptive fusion weights based on query intent, LRU cache

All three changes are independent and scoped to their respective packages — no cross-package API changes required.

## Motivation

### Current Pain Points

**LLMClient** (`packages/extractor/llm/client.py`):
- Creates a new `AsyncOpenAI` / `AsyncAnthropic` instance on every `complete()` call
- Structured output requires manual `json.loads()` with no retry on parse failure
- No timeout enforcement (documented as 10s/30s but not implemented)
- No rate limiting or circuit breaker

**Scheduler** (`apps/worker/scheduler.py`):
- `asyncio.gather` + infinite loop + bare `except`
- No exponential backoff retry (documented but unimplemented)
- No task chaining — `crawl → extract → index` is hardcoded in task functions
- No concurrency control, dead letter handling, or observability
- Cannot distribute across processes

**HybridSearch** (`packages/graphrag/retrieval/hybrid.py`):
- Fixed 0.6/0.4 vector/graph weight for all query types
- No caching — identical queries hit both Neo4j and pgvector every time
- No query classification — structural queries ("what depends on X?") get the same weights as semantic queries ("what is chain-of-thought?")

### Goals

| Goal | Measure |
|------|---------|
| LLM calls return typed models | `ExtractionResult` via PydanticAI `result_type` |
| LLM calls retry on transient failures | 3 retries with exponential backoff, built into PydanticAI Agent |
| Tasks survive individual failures | TaskIQ retry with backoff, task chain continues |
| Task chains are declarative | `@broker.task` decorators with `.kiq()` chaining |
| Structural queries favor graph search | Query router classifies intent, adjusts weights |
| Repeated queries are cached | LRU cache with TTL eliminates redundant DB hits |

### Non-Goals

- Replacing the four-layer DAG architecture (it's correct)
- Adding a full event bus or message broker (premature for current scale)
- Integrating Dagster/Prefect (overkill for <10 data sources)
- Changing the package dependency structure

## Approach

### Change 1: PydanticAI for LLM extraction

Replace the hand-rolled `LLMClient` with PydanticAI `Agent` instances per extractor type. Each extractor defines a Pydantic `result_type` and delegates retries/JSON parsing to PydanticAI.

**Files modified:**
- `packages/extractor/llm/client.py` → thin wrapper around PydanticAI Agent factory
- `packages/extractor/extractors/paper.py` → use Agent with PaperResult type
- `packages/extractor/extractors/concept.py` → use Agent with ConceptResult type
- `packages/extractor/extractors/relationship.py` → use Agent with RelationshipResult type
- `pyproject.toml` → add `pydantic-ai` dependency

**Files NOT modified:**
- All other packages — extractor's public API (`ExtractionResult`) stays the same

### Change 2: TaskIQ for worker orchestration

Replace the hand-rolled `Scheduler` with TaskIQ broker and task definitions. Tasks become `@broker.task` decorated functions with built-in retry, chaining via `.kiq()`, and concurrency control.

**Files modified:**
- `apps/worker/scheduler.py` → replaced by TaskIQ broker setup
- `apps/worker/main.py` → start TaskIQ worker
- `apps/worker/tasks/crawl.py` → `@broker.task` with retry policy
- `apps/worker/tasks/extract.py` → `@broker.task`, chain from crawl
- `apps/worker/tasks/index.py` → `@broker.task`, chain from extract
- `pyproject.toml` → add `taskiq` dependency

**Files NOT modified:**
- All `packages/` — task functions still call the same package APIs

### Change 3: Query Router + LRU Cache for HybridSearch

Add a lightweight `QueryRouter` that classifies queries as semantic vs structural using pattern matching (no LLM call), and adjusts vector/graph weights accordingly. Add an LRU+TTL cache in front of the hybrid search.

**Files modified:**
- `packages/graphrag/retrieval/hybrid.py` → integrate router and cache
- `packages/graphrag/retrieval/router.py` → new file, query classification

**Files NOT modified:**
- `VectorSearch`, `GraphSearch` — untouched, still called by HybridSearch
- All other packages

## Risks

| Risk | Mitigation |
|------|-----------|
| PydanticAI version instability | Pin to `>=0.2,<1.0`; extraction result types provide a stable contract |
| TaskIQ broker selection | Start with `MemoryBroker` (zero deps); upgrade to Redis broker later |
| Query router misclassification | Rules-based first; wrong classification degrades to current behavior (0.6/0.4), never worse |
| Cache staleness | Short TTL (5 min default), configurable; cache invalidated on reindex |
