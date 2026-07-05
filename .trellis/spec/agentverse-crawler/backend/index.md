# Crawler Package Guidelines

> AgentVerse data acquisition layer conventions

---

## Overview

`agentverse-crawler` collects raw data from external sources. All crawlers inherit `BaseCrawler` and return `CrawlResult`. Crawlers never write to databases — they only return structured data.

---

## Directory Structure

```
packages/crawler/src/agentverse/crawler/
├── base.py              ← BaseCrawler ABC + CrawlResult dataclass
├── rate_limiter.py      ← RateLimiter (configurable requests_per_second)
├── pipeline.py          ← CrawlPipeline (register + run_all)
└── sources/
    ├── arxiv.py         ← ArxivCrawler (REST API, 3 req/s)
    ├── github.py        ← GitHubCrawler (REST API, 5000 req/h)
    ├── web.py           ← WebCrawler (httpx + BeautifulSoup)
    ├── semantic_scholar.py  ← SemanticScholarCrawler
    ├── papers_with_code.py  ← PapersWithCodeCrawler
    ├── rss.py           ← RSSCrawler
    └── awesome_parser.py    ← AwesomeMarkdownParser
```

---

## Design Patterns

### All crawlers inherit BaseCrawler

```python
from agentverse.crawler.base import BaseCrawler, CrawlResult

class ArxivCrawler(BaseCrawler):
    async def crawl(self, max_results: int = 100, since: str = "", **kwargs) -> CrawlResult:
        """Fetch recent papers from ArXiv API."""
        ...
        return CrawlResult(source="arxiv", items=[...])
```

### Use RateLimiter for rate limiting

```python
from agentverse.crawler.rate_limiter import RateLimiter

limiter = RateLimiter(requests_per_second=3)
await limiter.acquire()
response = await client.get(url)
```

### Use CrawlPipeline for orchestration

```python
from agentverse.crawler.pipeline import CrawlPipeline

pipeline = CrawlPipeline()
pipeline.register(ArxivCrawler())
pipeline.register(GitHubCrawler())
results = await pipeline.run_all()
```

---

## Forbidden Patterns

| Pattern | Reason |
|---------|--------|
| Direct database writes | Crawlers only return CrawlResult |
| `requests` library | Must use `httpx.AsyncClient` |
| LLM calls in crawlers | LLM extraction belongs in extractor package |
| Hardcoded API URLs | Pass via Settings or parameters |
| Skipping rate_limiter | Will trigger API 429 errors |

---

## Common Mistakes

1. Forgetting `await limiter.acquire()` → triggers API rate limit
2. XML parsing without namespace handling → arXiv parse failure
3. Incremental crawl without tracking last crawl time → duplicate data
