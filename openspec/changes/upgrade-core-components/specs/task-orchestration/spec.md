# Spec: Task Orchestration via TaskIQ

## Requirements

### FR-1: Declarative Task Definition
- Tasks are defined with `@broker.task` decorator
- Each task specifies retry policy (`max_retries=3`, `retry_on_error=True`)
- Tasks are pure async functions — no class wrappers needed

### FR-2: Task Chaining
- `crawl_arxiv` → `extract_all` → `index_all` chain must be declarative
- Each completed task triggers the next via `.kiq()`
- A failure in one task must not corrupt the chain state

### FR-3: Retry with Backoff
- Failed tasks retry up to 3 times with exponential backoff (1s, 2s, 4s)
- After max retries, the task is logged as dead (no silent drop)
- The rest of the chain continues if downstream tasks have independent input

### FR-4: Concurrency Control
- Multiple crawl sources (arxiv, github, rss) can run concurrently
- Maximum concurrent LLM calls limited to 5 (via TaskIQ middleware or asyncio.Semaphore)
- Index operations are serialized to avoid Neo4j write contention

### FR-5: Observability
- Each task logs: start, success/failure, duration, retry count
- Structured logging via `structlog` (same as rest of project)

## Acceptance Criteria

- [ ] `crawl_arxiv()` triggers `extract_all()` automatically on success
- [ ] A failed crawl retries 3 times with increasing delay
- [ ] Worker starts with `python -m agentverse.worker.main` (or `taskiq worker`)
- [ ] `MemoryBroker` works with zero external dependencies
- [ ] Replacing `MemoryBroker` with `RedisBroker` requires only import change
