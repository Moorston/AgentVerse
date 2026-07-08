"""Tests for crawler source implementations.

Tests at the public seam: crawl() -> CrawlResult.
External HTTP is mocked via respx; behavior is verified through return values.
"""

import pytest
import respx
import httpx

from agentverse.crawler.sources.arxiv import ArxivCrawler, ARXIV_API_URL
from agentverse.crawler.sources.github import GitHubCrawler, GITHUB_API_URL
from agentverse.crawler.sources.semantic_scholar import SemanticScholarCrawler, S2_API_URL
from agentverse.crawler.sources.papers_with_code import PapersWithCodeCrawler, PWC_API_URL
from agentverse.crawler.sources.rss import RSSCrawler


# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------

SAMPLE_GITHUB_REPO = {
    "full_name": "langchain-ai/langgraph",
    "description": "Library for building stateful, multi-actor agent systems",
    "stargazers_count": 12345,
    "forks_count": 1500,
    "open_issues_count": 100,
    "language": "Python",
    "topics": ["agents", "llm", "graph"],
    "created_at": "2023-12-01T00:00:00Z",
    "updated_at": "2024-06-01T00:00:00Z",
    "pushed_at": "2024-06-01T00:00:00Z",
    "license": {"spdx_id": "MIT"},
    "html_url": "https://github.com/langchain-ai/langgraph",
    "homepage": "https://langchain-ai.github.io/langgraph",
}

SAMPLE_GITHUB_SEARCH = {
    "items": [{
        "full_name": "crewaiinc/crewai",
        "description": "Framework for orchestrating role-playing AI agents",
        "stargazers_count": 8000,
        "forks_count": 500,
        "language": "Python",
        "html_url": "https://github.com/crewaiinc/crewai",
    }],
}

SAMPLE_ARXIV_XML = """\
<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <entry>
    <id>http://arxiv.org/abs/2401.00001v1</id>
    <title>Test Paper: AI Agents</title>
    <summary>We present a new framework for AI agents.</summary>
    <published>2024-01-15T00:00:00Z</published>
    <updated>2024-01-20T00:00:00Z</updated>
    <author><name>Alice Author</name></author>
    <author><name>Bob Researcher</name></author>
    <category term="cs.AI"/>
    <category term="cs.LG"/>
  </entry>
  <entry>
    <id>http://arxiv.org/abs/2401.00002v1</id>
    <title>Another Paper: LLM Memory</title>
    <summary>Memory systems for large language models.</summary>
    <published>2024-02-10T00:00:00Z</published>
    <updated>2024-02-15T00:00:00Z</updated>
    <author><name>Charlie Coder</name></author>
    <category term="cs.CL"/>
  </entry>
</feed>
"""

EMPTY_ARXIV_XML = """\
<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
</feed>
"""


# ---------------------------------------------------------------------------
# ArxivCrawler
# ---------------------------------------------------------------------------


class TestArxivCrawler:
    """Tests for ArxivCrawler at the crawl() seam."""

    @pytest.mark.asyncio
    @respx.mock
    async def test_crawl_returns_parsed_papers(self):
        """ArxivCrawler returns structured paper dicts from XML response.

        Mock returns 2 papers then empty feed to stop pagination loop.
        """
        respx.get(ARXIV_API_URL).mock(side_effect=[
            httpx.Response(200, text=SAMPLE_ARXIV_XML),
            httpx.Response(200, text=EMPTY_ARXIV_XML),
        ])

        crawler = ArxivCrawler()
        result = await crawler.crawl({"max_results": 10})

        assert result.source == "arxiv"
        assert len(result.items) == 2
        assert result.errors == []

    @pytest.mark.asyncio
    @respx.mock
    async def test_crawl_extracts_paper_fields(self):
        """Each paper dict contains all expected fields with correct values."""
        respx.get(ARXIV_API_URL).mock(side_effect=[
            httpx.Response(200, text=SAMPLE_ARXIV_XML),
            httpx.Response(200, text=EMPTY_ARXIV_XML),
        ])

        crawler = ArxivCrawler()
        result = await crawler.crawl({"max_results": 10})
        paper = result.items[0]

        assert paper["title"] == "Test Paper: AI Agents"
        assert paper["authors"] == ["Alice Author", "Bob Researcher"]
        assert paper["abstract"] == "We present a new framework for AI agents."
        assert paper["arxiv_id"] == "2401.00001v1"
        assert paper["published_date"] == "2024-01-15"
        assert paper["categories"] == ["cs.AI", "cs.LG"]

    @pytest.mark.asyncio
    @respx.mock
    async def test_crawl_filters_by_since_date(self):
        """Papers published before 'since' date are excluded.

        Only the second paper (2024-02-10) survives the filter.
        Mock returns empty feed on second call to stop pagination.
        """
        respx.get(ARXIV_API_URL).mock(side_effect=[
            httpx.Response(200, text=SAMPLE_ARXIV_XML),
            httpx.Response(200, text=EMPTY_ARXIV_XML),
        ])

        crawler = ArxivCrawler()
        result = await crawler.crawl({"max_results": 10, "since": "2024-01-31"})

        assert len(result.items) == 1
        assert result.items[0]["title"] == "Another Paper: LLM Memory"

    @pytest.mark.asyncio
    @respx.mock
    async def test_crawl_returns_empty_on_no_results(self):
        """Empty feed yields empty items list with no errors."""
        respx.get(ARXIV_API_URL).mock(
            return_value=httpx.Response(200, text=EMPTY_ARXIV_XML)
        )

        crawler = ArxivCrawler()
        result = await crawler.crawl({"max_results": 10})

        assert result.items == []
        assert result.errors == []

    @pytest.mark.asyncio
    @respx.mock
    async def test_crawl_records_http_error(self):
        """HTTP 500 error is captured in CrawlResult.errors, not raised."""
        respx.get(ARXIV_API_URL).mock(
            return_value=httpx.Response(500, text="Internal Server Error")
        )

        crawler = ArxivCrawler()
        result = await crawler.crawl({"max_results": 10})

        assert result.items == []
        assert len(result.errors) == 1
        assert "500" in result.errors[0]

    @pytest.mark.asyncio
    @respx.mock
    async def test_crawl_builds_search_query_with_categories(self):
        """Categories and search_query are combined into the API query string."""
        route = respx.get(ARXIV_API_URL).mock(
            return_value=httpx.Response(200, text=EMPTY_ARXIV_XML)
        )

        crawler = ArxivCrawler()
        await crawler.crawl({
            "max_results": 10,
            "categories": ["cs.AI"],
            "search_query": "agent",
        })

        sent_params = route.calls.last.request.url.params
        assert "cat:cs.AI" in sent_params["search_query"]
        assert "all:agent" in sent_params["search_query"]


# ---------------------------------------------------------------------------
# GitHubCrawler
# ---------------------------------------------------------------------------


class TestGitHubCrawler:
    """Tests for GitHubCrawler at the crawl() seam."""

    @pytest.mark.asyncio
    @respx.mock
    async def test_crawl_returns_repo_metadata(self):
        """GitHubCrawler fetches and returns structured repo data."""
        respx.get(f"{GITHUB_API_URL}/repos/langchain-ai/langgraph").mock(
            return_value=httpx.Response(200, json=SAMPLE_GITHUB_REPO)
        )

        crawler = GitHubCrawler()
        result = await crawler.crawl({"repos": ["langchain-ai/langgraph"]})

        assert result.source == "github"
        assert len(result.items) == 1
        assert result.errors == []

    @pytest.mark.asyncio
    @respx.mock
    async def test_crawl_extracts_repo_fields(self):
        """Each repo dict contains name, stars, description, and other metadata."""
        respx.get(f"{GITHUB_API_URL}/repos/langchain-ai/langgraph").mock(
            return_value=httpx.Response(200, json=SAMPLE_GITHUB_REPO)
        )

        crawler = GitHubCrawler()
        result = await crawler.crawl({"repos": ["langchain-ai/langgraph"]})
        repo = result.items[0]

        assert repo["name"] == "langchain-ai/langgraph"
        assert repo["stars"] == 12345
        assert repo["forks"] == 1500
        assert repo["language"] == "Python"
        assert repo["topics"] == ["agents", "llm", "graph"]
        assert repo["license"] == "MIT"

    @pytest.mark.asyncio
    @respx.mock
    async def test_crawl_sends_auth_header_with_token(self):
        """When a token is provided, Authorization header is sent."""
        route = respx.get(f"{GITHUB_API_URL}/repos/owner/repo").mock(
            return_value=httpx.Response(200, json={
                **SAMPLE_GITHUB_REPO,
                "full_name": "owner/repo",
            })
        )

        crawler = GitHubCrawler(token="ghp_test_token")
        await crawler.crawl({"repos": ["owner/repo"]})

        auth = route.calls.last.request.headers.get("Authorization")
        assert auth == "Bearer ghp_test_token"

    @pytest.mark.asyncio
    @respx.mock
    async def test_crawl_records_error_for_failed_repo(self):
        """A 404 for one repo doesn't abort the entire crawl."""
        respx.get(f"{GITHUB_API_URL}/repos/good/repo").mock(
            return_value=httpx.Response(200, json={
                **SAMPLE_GITHUB_REPO, "full_name": "good/repo"
            })
        )
        respx.get(f"{GITHUB_API_URL}/repos/bad/repo").mock(
            return_value=httpx.Response(404, json={"message": "Not Found"})
        )

        crawler = GitHubCrawler()
        result = await crawler.crawl({"repos": ["good/repo", "bad/repo"]})

        assert len(result.items) == 1
        assert len(result.errors) == 1
        assert "bad/repo" in result.errors[0]

    @pytest.mark.asyncio
    @respx.mock
    async def test_crawl_search_fallback_when_query_provided(self):
        """When no repos match, a search query is used as fallback."""
        respx.get(f"{GITHUB_API_URL}/search/repositories").mock(
            return_value=httpx.Response(200, json=SAMPLE_GITHUB_SEARCH)
        )

        crawler = GitHubCrawler()
        result = await crawler.crawl({"repos": [], "query": "AI agent framework"})

        assert len(result.items) == 1
        assert result.items[0]["name"] == "crewaiinc/crewai"


SAMPLE_S2_PAPER = {
    "paperId": "abc123",
    "title": "Attention Is All You Need",
    "abstract": "The dominant sequence transduction models...",
    "authors": [{"name": "Ashish Vaswani"}, {"name": "Noam Shazeer"}],
    "year": 2017,
    "citationCount": 90000,
    "influentialCitationCount": 15000,
    "externalIds": {"ArXiv": "1706.03762"},
    "references": [{"paperId": "ref1"}, {"paperId": "ref2"}],
}

SAMPLE_S2_SEARCH = {
    "data": [{
        "paperId": "def456",
        "title": "ReAct: Synergizing Reasoning and Acting",
        "abstract": "LLMs augmented with reasoning and acting...",
        "authors": [{"name": "Shunyu Yao"}],
        "year": 2022,
        "citationCount": 2000,
    }],
}


class TestSemanticScholarCrawler:
    """Tests for SemanticScholarCrawler at the crawl() seam."""

    @pytest.mark.asyncio
    @respx.mock
    async def test_crawl_fetches_by_arxiv_id(self):
        """SemanticScholarCrawler looks up papers by arXiv ID."""
        respx.get(f"{S2_API_URL}/paper/ARXIV:1706.03762").mock(
            return_value=httpx.Response(200, json=SAMPLE_S2_PAPER)
        )

        crawler = SemanticScholarCrawler()
        result = await crawler.crawl({"arxiv_ids": ["1706.03762"]})

        assert result.source == "semantic_scholar"
        assert len(result.items) == 1
        assert result.items[0]["title"] == "Attention Is All You Need"
        assert result.items[0]["citation_count"] == 90000
        assert result.items[0]["arxiv_id"] == "1706.03762"

    @pytest.mark.asyncio
    @respx.mock
    async def test_crawl_searches_by_query(self):
        """SemanticScholarCrawler searches papers by keyword."""
        respx.get(f"{S2_API_URL}/paper/search").mock(
            return_value=httpx.Response(200, json=SAMPLE_S2_SEARCH)
        )

        crawler = SemanticScholarCrawler()
        result = await crawler.crawl({"query": "ReAct agent"})

        assert len(result.items) == 1
        assert result.items[0]["title"] == "ReAct: Synergizing Reasoning and Acting"

    @pytest.mark.asyncio
    @respx.mock
    async def test_crawl_handles_404_for_missing_paper(self):
        """A 404 for an arXiv ID is silently skipped, not recorded as error."""
        respx.get(f"{S2_API_URL}/paper/ARXIV:0000.00000").mock(
            return_value=httpx.Response(404, json={"message": "Paper not found"})
        )

        crawler = SemanticScholarCrawler()
        result = await crawler.crawl({"arxiv_ids": ["0000.00000"]})

        assert result.items == []
        assert result.errors == []

    @pytest.mark.asyncio
    @respx.mock
    async def test_crawl_sends_api_key_header(self):
        """When api_key is provided, x-api-key header is sent."""
        route = respx.get(f"{S2_API_URL}/paper/ARXIV:1706.03762").mock(
            return_value=httpx.Response(200, json=SAMPLE_S2_PAPER)
        )

        crawler = SemanticScholarCrawler(api_key="s2_test_key")
        await crawler.crawl({"arxiv_ids": ["1706.03762"]})

        assert route.calls.last.request.headers["x-api-key"] == "s2_test_key"

    @pytest.mark.asyncio
    @respx.mock
    async def test_crawl_records_http_error(self):
        """HTTP 500 is captured in errors, not raised."""
        respx.get(f"{S2_API_URL}/paper/search").mock(
            return_value=httpx.Response(500, text="Server Error")
        )

        crawler = SemanticScholarCrawler()
        result = await crawler.crawl({"query": "test"})

        assert result.items == []
        assert len(result.errors) == 1


SAMPLE_PWC_RESPONSE = {
    "results": [{
        "id": "attention-is-all-you-need",
        "title": "Attention Is All You Need",
        "abstract": "The dominant sequence transduction models...",
        "url_pdf": "https://arxiv.org/pdf/1706.03762",
        "published": "2017-06-12",
        "authors": "Vaswani et al.",
        "proceeding": "NeurIPS 2017",
    }],
}

SAMPLE_RSS_XML = """\
<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>arXiv cs.AI</title>
    <item>
      <title>New AI Agent Framework</title>
      <link>https://arxiv.org/abs/2401.12345</link>
      <description>A novel framework for building AI agents.</description>
      <pubDate>Mon, 15 Jan 2024 00:00:00 GMT</pubDate>
    </item>
    <item>
      <title>Memory-Augmented LLMs</title>
      <link>https://arxiv.org/abs/2401.12346</link>
      <description>Adding persistent memory to language models.</description>
      <pubDate>Fri, 10 Feb 2024 00:00:00 GMT</pubDate>
    </item>
  </channel>
</rss>
"""


class TestPapersWithCodeCrawler:
    """Tests for PapersWithCodeCrawler at the crawl() seam."""

    @pytest.mark.asyncio
    @respx.mock
    async def test_crawl_returns_papers(self):
        """PapersWithCodeCrawler returns structured paper data."""
        respx.get(f"{PWC_API_URL}/papers/").mock(
            return_value=httpx.Response(200, json=SAMPLE_PWC_RESPONSE)
        )

        crawler = PapersWithCodeCrawler()
        result = await crawler.crawl({"query": "attention", "max_results": 10})

        assert result.source == "papers_with_code"
        assert len(result.items) == 1
        assert result.items[0]["title"] == "Attention Is All You Need"
        assert result.items[0]["proceeding"] == "NeurIPS 2017"

    @pytest.mark.asyncio
    @respx.mock
    async def test_crawl_records_http_error(self):
        """HTTP error is captured in errors, not raised."""
        respx.get(f"{PWC_API_URL}/papers/").mock(
            return_value=httpx.Response(503, text="Service Unavailable")
        )

        crawler = PapersWithCodeCrawler()
        result = await crawler.crawl({"query": "test"})

        assert result.items == []
        assert len(result.errors) == 1


class TestRSSCrawler:
    """Tests for RSSCrawler at the crawl() seam."""

    @pytest.mark.asyncio
    @respx.mock
    async def test_crawl_parses_rss_feed(self):
        """RSSCrawler parses RSS 2.0 items into structured news dicts."""
        respx.get("https://rss.arxiv.org/rss/cs.AI").mock(
            return_value=httpx.Response(200, text=SAMPLE_RSS_XML)
        )

        crawler = RSSCrawler()
        result = await crawler.crawl({
            "feeds": {"arxiv_ai": "https://rss.arxiv.org/rss/cs.AI"},
        })

        assert result.source == "rss"
        assert len(result.items) == 2
        assert result.items[0]["title"] == "New AI Agent Framework"

    @pytest.mark.asyncio
    @respx.mock
    async def test_crawl_extracts_rss_fields(self):
        """Each RSS item has title, url, summary, source, and published_at."""
        respx.get("https://rss.arxiv.org/rss/cs.AI").mock(
            return_value=httpx.Response(200, text=SAMPLE_RSS_XML)
        )

        crawler = RSSCrawler()
        result = await crawler.crawl({
            "feeds": {"arxiv_ai": "https://rss.arxiv.org/rss/cs.AI"},
        })
        item = result.items[0]

        assert item["title"] == "New AI Agent Framework"
        assert item["url"] == "https://arxiv.org/abs/2401.12345"
        assert item["source"] == "arxiv_ai"
        assert item["published_at"] == "2024-01-15"

    @pytest.mark.asyncio
    @respx.mock
    async def test_crawl_filters_by_since_date(self):
        """Items published before 'since' are excluded."""
        respx.get("https://rss.arxiv.org/rss/cs.AI").mock(
            return_value=httpx.Response(200, text=SAMPLE_RSS_XML)
        )

        crawler = RSSCrawler()
        result = await crawler.crawl({
            "feeds": {"arxiv_ai": "https://rss.arxiv.org/rss/cs.AI"},
            "since": "2024-01-31",
        })

        assert len(result.items) == 1
        assert result.items[0]["title"] == "Memory-Augmented LLMs"

    @pytest.mark.asyncio
    @respx.mock
    async def test_crawl_records_http_error(self):
        """HTTP error is captured in errors, not raised."""
        respx.get("https://rss.arxiv.org/rss/cs.AI").mock(
            return_value=httpx.Response(404, text="Not Found")
        )

        crawler = RSSCrawler()
        result = await crawler.crawl({
            "feeds": {"arxiv_ai": "https://rss.arxiv.org/rss/cs.AI"},
        })

        assert result.items == []
        assert len(result.errors) == 1

