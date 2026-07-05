"""GitHub repository crawler — fetches repo metadata via GitHub REST API."""

from typing import Any

import httpx

from agentverse.crawler.base import BaseCrawler, CrawlResult
from agentverse.crawler.rate_limiter import RateLimiter
from agentverse.shared.logging import get_logger

logger = get_logger(__name__)

GITHUB_API_URL = "https://api.github.com"

# Target AI Agent frameworks
DEFAULT_REPOS = [
    "langchain-ai/langgraph",
    "crewaiinc/crewai",
    "microsoft/autogen",
    "run-llama/llama_index",
    "microsoft/semantic-kernel",
    "langgenius/dify",
    "openai/swarm",
    "mem0ai/mem0",
    "getzep/zep",
    "langchain-ai/langmem",
    "letta-ai/letta",
    "topoteretes/cognee",
]


class GitHubCrawler(BaseCrawler):
    """Crawl GitHub for AI Agent framework repositories."""

    def __init__(self, token: str = "", requests_per_second: float = 5.0) -> None:
        self._token = token
        self._limiter = RateLimiter(requests_per_second=requests_per_second)

    async def crawl(
        self,
        repos: list[str] | None = None,
        query: str = "",
        **kwargs: Any,
    ) -> CrawlResult:
        """Fetch repository metadata from GitHub API.

        Args:
            repos: List of "owner/repo" strings (default: DEFAULT_REPOS).
            query: GitHub search query (used if repos is empty).
        """
        target_repos = repos or DEFAULT_REPOS
        items: list[dict[str, Any]] = []
        errors: list[str] = []

        headers = {"Accept": "application/vnd.github.v3+json"}
        if self._token:
            headers["Authorization"] = f"Bearer {self._token}"

        for repo in target_repos:
            await self._limiter.acquire()
            try:
                item = await self._fetch_repo(repo, headers)
                if item:
                    items.append(item)
            except Exception as exc:
                errors.append(f"Error fetching {repo}: {exc}")

        # Also search if query provided
        if query and not items:
            await self._limiter.acquire()
            try:
                search_items = await self._search_repos(query, headers)
                items.extend(search_items)
            except Exception as exc:
                errors.append(f"Error searching: {exc}")

        logger.info("GitHub crawl complete", repos=len(items), errors=len(errors))
        return CrawlResult(source="github", items=items, errors=errors)

    async def _fetch_repo(self, repo: str, headers: dict[str, str]) -> dict[str, Any] | None:
        """Fetch metadata for a single repository."""
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(f"{GITHUB_API_URL}/repos/{repo}", headers=headers)
            response.raise_for_status()
            data = response.json()

            return {
                "name": data.get("full_name", ""),
                "description": data.get("description", ""),
                "stars": data.get("stargazers_count", 0),
                "forks": data.get("forks_count", 0),
                "open_issues": data.get("open_issues_count", 0),
                "language": data.get("language", ""),
                "topics": data.get("topics", []),
                "created_at": data.get("created_at", ""),
                "updated_at": data.get("updated_at", ""),
                "pushed_at": data.get("pushed_at", ""),
                "license": data.get("license", {}).get("spdx_id", "") if data.get("license") else "",
                "url": data.get("html_url", ""),
                "homepage": data.get("homepage", ""),
            }

    async def _search_repos(self, query: str, headers: dict[str, str]) -> list[dict[str, Any]]:
        """Search GitHub repositories."""
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(
                f"{GITHUB_API_URL}/search/repositories",
                headers=headers,
                params={"q": query, "sort": "stars", "per_page": 10},
            )
            response.raise_for_status()
            data = response.json()

            items = []
            for repo in data.get("items", []):
                items.append({
                    "name": repo.get("full_name", ""),
                    "description": repo.get("description", ""),
                    "stars": repo.get("stargazers_count", 0),
                    "forks": repo.get("forks_count", 0),
                    "language": repo.get("language", ""),
                    "url": repo.get("html_url", ""),
                })
            return items