# Design: Upgrade Core Components

## Overview

Three independent component upgrades. Each follows the same pattern: replace a hand-rolled component with a purpose-built library, preserve the existing public API, minimize blast radius.

---

## 1. PydanticAI for LLM Extraction

### Current State

```
extractor/llm/client.py
  LLMClient
    .complete(prompt, system_prompt, response_format) → str
    .complete_json(prompt, system_prompt, schema) → dict
    ._complete_openai(...)   # creates AsyncOpenAI every call
    ._complete_anthropic(...) # creates AsyncAnthropic every call
```

### Target State

```
extractor/llm/client.py
  LLMClient (thin factory)
    .get_agent(result_type, system_prompt) → Agent[T]
    .supports(provider) → bool

extractor/extractors/paper.py
  PaperExtractor
    uses Agent[PaperResult] for extraction
```

### Design Decision: Keep LLMClient as a factory

PydanticAI `Agent` instances are cheap to create but carry config (model, system prompt, retries). A thin factory in `LLMClient` centralizes provider selection and config, while individual extractors own their `result_type` and prompt logic.

```python
# New LLMClient
class LLMClient:
    def __init__(self, settings: Settings):
        self._settings = settings

    def get_agent(
        self,
        result_type: type[T],
        system_prompt: str,
        retries: int = 3,
    ) -> Agent[T]:
        model = self._resolve_model()
        return Agent(
            model,
            result_type=result_type,
            system_prompt=system_prompt,
            retries=retries,
        )

    def _resolve_model(self) -> str:
        if self._settings.openai_api_key:
            return f"openai:{self._settings.openai_model}"
        return f"anthropic:{self._settings.anthropic_model}"
```

### Extraction Result Types (Pydantic models)

```python
# Each extractor defines its own result_type
class PaperResult(BaseModel):
    title: str
    authors: list[str]
    abstract: str
    published_date: str
    categories: list[str]

class ConceptResult(BaseModel):
    concepts: list[ExtractedConcept]

class ExtractedConcept(BaseModel):
    name: str
    description: str
    category: str

class RelationshipResult(BaseModel):
    relationships: list[ExtractedRelationship]

class ExtractedRelationship(BaseModel):
    source: str
    target: str
    type: str  # constrained to RelationshipType values
    description: str
```

### Migration Path

1. Add `pydantic-ai` to `packages/extractor/pyproject.toml`
2. Add result type models to `packages/extractor/types.py`
3. Rewrite `LLMClient` as Agent factory
4. Update each extractor to use `Agent[T]` instead of `complete_json()`
5. Keep `ExtractionResult` as the public output — internal only changes

---

## 2. TaskIQ for Worker Orchestration

### Current State

```
worker/scheduler.py
  Scheduler
    .register(name, task, interval_seconds)
    .run()  # asyncio.gather of infinite loops

worker/main.py
  scheduler.register("crawl", run_crawl, 3600)
  scheduler.register("extract", run_extract, 3600)
  await scheduler.run()
```

### Target State

```
worker/broker.py       # TaskIQ broker configuration
  broker = MemoryBroker()  # or RedisBroker in production

worker/tasks/
  crawl.py              # @broker.task with schedule
  extract.py            # @broker.task, called by crawl
  index.py              # @broker.task, called by extract

worker/main.py          # starts TaskIQ worker
```

### Design Decision: MemoryBroker first, Redis later

TaskIQ's `MemoryBroker` requires zero external dependencies and runs in-process. It supports all the features we need (retry, chaining, events). When the system needs distributed workers, switching to `RedisBroker` is a one-line change.

### Task Chain Design

```
┌─────────────────────────────────────────────────────┐
│  Scheduler (cron or interval trigger)                │
│                                                     │
│  crawl_arxiv() ──────┐                              │
│  crawl_github() ─────┤                              │
│  crawl_rss() ────────┼──→ extract_all.kiq(results)  │
│  crawl_semantic() ───┘                              │
│                                                     │
│  extract_all(items) ──→ index_all.kiq(concepts)     │
│                                                     │
│  index_all(concepts)  (terminal)                     │
└─────────────────────────────────────────────────────┘
```

### Retry Policy

```python
@broker.task(
    retry_on_error=True,
    max_retries=3,
    # TaskIQ doesn't have built-in backoff, implement via custom middleware
)
async def crawl_arxiv():
    ...
```

TaskIQ supports event hooks for custom backoff:

```python
@broker.on_error
async def backoff_handler(task_id, error, retries):
    await asyncio.sleep(2 ** retries)  # exponential backoff
```

### Migration Path

1. Add `taskiq` to `apps/worker/pyproject.toml`
2. Create `apps/worker/src/agentverse/worker/broker.py` with MemoryBroker
3. Rewrite task functions as `@broker.task` decorated
4. Add task chaining: crawl → extract → index
5. Rewrite `main.py` to start TaskIQ worker
6. Delete `scheduler.py`

---

## 3. Query Router + Cache for HybridSearch

### Current State

```
hybrid.py
  HybridSearch
    .search(query, top_k)
      vector_results = vector_search.search(query, top_k)
      graph_results = graph_search.search(query, top_k)
      return _merge_and_rank(vector_results, graph_results, top_k)
        # hardcoded: 0.6 * vector + 0.4 * graph
```

### Target State

```
router.py (new)
  QueryRouter
    .classify(query) → QueryType
    .weights(query_type) → (vector_weight, graph_weight)

hybrid.py
  HybridSearch
    .search(query, top_k)
      query_type = router.classify(query)
      weights = router.weights(query_type)
      # check cache first
      # run searches with adjusted weights
      # cache results
```

### Query Classification Strategy

Rule-based pattern matching — no LLM call, zero latency overhead:

```
STRUCTURAL signals (→ graph-dominant 0.3/0.7):
  - "depend", "implement", "extend", "evolve"
  - "what uses X", "what is related to X"
  - "which framework supports X"
  - Questions about relationships, hierarchies

SEMANTIC signals (→ vector-dominant 0.8/0.2):
  - "what is X", "explain X", "how does X work"
  - Conceptual questions, definitions
  - Abstract comparisons

DEFAULT (→ balanced 0.6/0.4):
  - Ambiguous queries fall back to current behavior
```

### Cache Design

```python
from functools import lru_cache
from cachetools import TTLCache

class HybridSearch:
    def __init__(self, ...):
        self._cache = TTLCache(maxsize=256, ttl=300)  # 5 min TTL

    async def search(self, query: str, top_k: int = 10) -> list[dict]:
        cache_key = f"{query}:{top_k}"
        if cache_key in self._cache:
            return self._cache[cache_key]

        results = await self._search_impl(query, top_k)
        self._cache[cache_key] = results
        return results
```

### Migration Path

1. Create `packages/graphrag/retrieval/router.py` with QueryRouter
2. Modify `HybridSearch.__init__` to accept QueryRouter
3. Modify `_merge_and_rank` to accept dynamic weights
4. Add TTLCache
5. Add `cachetools` to `packages/graphrag/pyproject.toml`

---

## Cross-Cutting Concerns

### Dependency Graph (unchanged)

```
shared → graph-core → ontology, graphrag
                   → crawler → extractor
                        → api, worker
```

No new inter-package dependencies are introduced. PydanticAI is contained within `extractor`. TaskIQ is contained within `worker`. QueryRouter is contained within `graphrag`.

### Testing Strategy

| Component | Test Approach |
|-----------|--------------|
| PydanticAI LLMClient | Mock the Agent, verify result_type contract |
| TaskIQ tasks | TaskIQ has `TestBroker` for in-process testing |
| QueryRouter | Unit test classification patterns |
| HybridSearch+Cache | Test cache hit/miss, TTL expiry |
