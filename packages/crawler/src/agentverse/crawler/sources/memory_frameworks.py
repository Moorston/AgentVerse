"""Memory framework crawler — collects data about AI agent memory frameworks.

Crawls GitHub repos and documentation for memory frameworks like Mem0, Zep,
LangMem, Letta, and Cognee to populate the knowledge graph.
"""

from typing import Any

import httpx

from agentverse.crawler.base import BaseCrawler, CrawlResult
from agentverse.crawler.rate_limiter import RateLimiter
from agentverse.crawler.types import CrawlRequest
from agentverse.shared.logging import get_logger

logger = get_logger(__name__)

MEMORY_FRAMEWORKS: list[dict[str, Any]] = [
    {
        "name": "Mem0",
        "description": "Production-ready long-term memory for AI agents. Supports graph memory, personalized memory, and cross-session persistence.",
        "github_url": "https://github.com/mem0ai/mem0",
        "memory_categories": ["long_term", "graph", "personalized"],
    },
    {
        "name": "Zep",
        "description": "Temporal memory framework for conversational agents. Focuses on fact extraction, content summarization, and temporal reasoning.",
        "github_url": "https://github.com/getzep/zep",
        "memory_categories": ["temporal", "episodic", "fact_extraction"],
    },
    {
        "name": "LangMem",
        "description": "LangChain native memory components for agents. Supports event memory, fact/preference memory, and procedural memory with hot-path and background updates.",
        "github_url": "https://github.com/langchain-ai/langmem",
        "memory_categories": ["event", "semantic", "procedural"],
    },
    {
        "name": "Letta",
        "description": "Long-running agent framework with persistent state management. Designed for ultra-long-running agents.",
        "github_url": "https://github.com/letta-ai/letta",
        "memory_categories": ["persistent_state", "long_term"],
    },
    {
        "name": "Cognee",
        "description": "Knowledge graph-based memory. Structures memory as a knowledge graph for complex relationship reasoning.",
        "github_url": "https://github.com/topoteretes/cognee",
        "memory_categories": ["graph", "semantic", "relationship"],
    },
]

MEMORY_TYPES: list[dict[str, Any]] = [
    {
        "name": "Short-term Memory",
        "description": "Context window and working memory for the current task. Limited by model context length.",
        "memory_category": "short_term",
    },
    {
        "name": "Long-term Memory",
        "description": "Persistent memory that survives across sessions and tasks. Stored in external databases.",
        "memory_category": "long_term",
    },
    {
        "name": "Episodic Memory",
        "description": "Memory of specific past experiences and interactions. Records what happened, when, and where.",
        "memory_category": "episodic",
    },
    {
        "name": "Semantic Memory",
        "description": "Factual knowledge and concept relationships. General world knowledge independent of specific episodes.",
        "memory_category": "semantic",
    },
    {
        "name": "Procedural Memory",
        "description": "Memory of how to perform tasks and procedures. Encodes skills and step-by-step processes.",
        "memory_category": "procedural",
    },
    {
        "name": "Graph Memory",
        "description": "Knowledge graph-based memory structure. Stores entities and relationships as an interconnected graph.",
        "memory_category": "graph",
    },
]


class MemoryFrameworkCrawler(BaseCrawler):
    """Crawl memory framework metadata from GitHub and documentation.

    Collects information about memory frameworks, their capabilities,
    and the types of memory they support.
    """

    def __init__(self, requests_per_second: float = 3.0) -> None:
        self._limiter = RateLimiter(requests_per_second=requests_per_second)

    async def crawl(self, request: CrawlRequest | None = None) -> CrawlResult:
        """Fetch memory framework metadata.

        Returns structured data about each memory framework including
        name, description, GitHub URL, and supported memory categories.
        """
        items: list[dict[str, Any]] = []
        errors: list[str] = []

        for framework in MEMORY_FRAMEWORKS:
            await self._limiter.acquire()
            try:
                async with httpx.AsyncClient(timeout=15) as client:
                    # Fetch GitHub API for live stats
                    repo_path = framework["github_url"].replace("https://github.com/", "")
                    response = await client.get(
                        f"https://api.github.com/repos/{repo_path}",
                        headers={"Accept": "application/vnd.github.v3+json"},
                    )

                    stars = 0
                    forks = 0
                    if response.status_code == 200:
                        data = response.json()
                        stars = data.get("stargazers_count", 0)
                        forks = data.get("forks_count", 0)

                    items.append({
                        **framework,
                        "stars": stars,
                        "forks": forks,
                        "type": "memory_framework",
                    })

                    logger.debug("Crawled memory framework", name=framework["name"], stars=stars)

            except Exception as exc:
                # Still include the framework even if GitHub API fails
                items.append({
                    **framework,
                    "stars": 0,
                    "forks": 0,
                    "type": "memory_framework",
                })
                errors.append(f"GitHub API failed for {framework['name']}: {exc}")

        # Also include memory type definitions
        for mem_type in MEMORY_TYPES:
            items.append({
                **mem_type,
                "type": "memory_type",
            })

        logger.info("Memory framework crawl complete", frameworks=len(MEMORY_FRAMEWORKS), types=len(MEMORY_TYPES), errors=len(errors))
        return CrawlResult(source="memory_frameworks", items=items, errors=errors)
