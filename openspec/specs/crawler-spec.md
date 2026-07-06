# Crawler System Specification

## Purpose
The crawler system collects raw data from external sources (arXiv, GitHub, RSS feeds, Semantic Scholar, Papers with Code, Awesome repositories).

## Architecture
```
BaseCrawler (ABC)
├── ArxivCrawler      — arXiv REST API (3 req/s)
├── GitHubCrawler     — GitHub REST API (5000 req/h)
├── SemanticScholarCrawler — Semantic Scholar API
├── PapersWithCodeCrawler  — Papers with Code API
├── RSSCrawler        — RSS 2.0 + Atom feeds
└── AwesomeMarkdownParser  — Git clone + MD link extraction
```

## Data Flow
```
External Source → BaseCrawler.crawl() → CrawlResult → Pipeline
```

## Constraints
1. All crawlers MUST inherit BaseCrawler
2. All HTTP calls MUST use httpx.AsyncClient (no requests)
3. All crawlers MUST use RateLimiter
4. Crawlers MUST NOT write to database (only return CrawlResult)
5. Crawlers MUST NOT call LLM
6. Worker `run_crawl()` SHALL dispatch all documented sources (arxiv, github, rss, semantic_scholar)
7. `run_crawl()` SHALL catch exceptions from crawler instantiation and crawl execution, returning empty list on failure
8. ArXiv API endpoint SHALL use HTTPS (`https://export.arxiv.org/api/query`)

## CrawlResult Schema
```python
@dataclass
class CrawlResult:
    source: str           # "arxiv" | "github" | "rss" | "semantic_scholar" | "papers_with_code" | "awesome"
    items: list[dict]     # List of structured data dicts
    errors: list[str]     # Error messages
```

## Test Criteria
- [ ] Each crawler returns CrawlResult with correct source
- [ ] RateLimiter prevents exceeding API limits
- [ ] Incremental crawl skips already-crawled items
- [ ] Error handling captures failures without crashing
