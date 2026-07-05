"""GitHub Awesome repository Markdown parser — extracts papers and resources from MD files."""

import re
from typing import Any
from pathlib import Path

from agentverse.crawler.base import BaseCrawler, CrawlResult
from agentverse.shared.logging import get_logger

logger = get_logger(__name__)

# Markdown link pattern: [text](url)
MD_LINK_PATTERN = re.compile(r'\[([^\]]+)\]\(([^)]+)\)')
# GitHub repo pattern: owner/repo
GITHUB_REPO_PATTERN = re.compile(r'github\.com/([^/]+/[^/]+)')
# arXiv pattern: arxiv.org/abs/XXXX.XXXXX
ARXIV_PATTERN = re.compile(r'arxiv\.org/abs/(\d+\.\d+)')


class AwesomeMarkdownParser(BaseCrawler):
    """Parse GitHub Awesome repository Markdown files for papers and resources."""

    async def crawl(
        self,
        repo: str = "",
        readme_path: str = "README.md",
        **kwargs: Any,
    ) -> CrawlResult:
        """Parse a local Awesome repository's README.

        Args:
            repo: Repository name (for labeling).
            readme_path: Path to the README.md file.
        """
        items: list[dict[str, Any]] = []
        errors: list[str] = []

        try:
            path = Path(readme_path)
            if not path.exists():
                errors.append(f"File not found: {readme_path}")
                return CrawlResult(source="awesome", items=items, errors=errors)

            content = path.read_text(encoding="utf-8")
            items = self._parse_markdown(content, repo=repo)
        except Exception as exc:
            errors.append(f"Error parsing {readme_path}: {exc}")

        logger.info("Awesome parse complete", repo=repo, items=len(items), errors=len(errors))
        return CrawlResult(source="awesome", items=items, errors=errors)

    def _parse_markdown(self, content: str, repo: str = "") -> list[dict[str, Any]]:
        """Parse Markdown content and extract structured resources."""
        items: list[dict[str, Any]] = []
        current_section = ""

        for line in content.split("\n"):
            # Track current section
            if line.startswith("#"):
                current_section = line.lstrip("#").strip()
                continue

            # Extract links
            links = MD_LINK_PATTERN.findall(line)
            if not links:
                continue

            for text, url in links:
                item = self._extract_item(text, url, section=current_section, repo=repo)
                if item:
                    items.append(item)

        return items

    def _extract_item(self, text: str, url: str, section: str = "", repo: str = "") -> dict[str, Any] | None:
        """Extract a structured item from a Markdown link."""
        item_type = "unknown"
        arxiv_id = ""

        # Detect type from URL
        if "arxiv.org" in url:
            item_type = "paper"
            match = ARXIV_PATTERN.search(url)
            if match:
                arxiv_id = match.group(1)
        elif "github.com" in url:
            match = GITHUB_REPO_PATTERN.search(url)
            if match:
                item_type = "repository"
            else:
                item_type = "resource"
        elif any(ext in url for ext in [".pdf", ".html"]):
            item_type = "paper"
        else:
            item_type = "resource"

        return {
            "name": text.strip(),
            "url": url,
            "type": item_type,
            "section": section,
            "source_repo": repo,
            "arxiv_id": arxiv_id,
        }


def parse_local_readme(path: str, repo: str = "") -> list[dict[str, Any]]:
    """Convenience function to parse a local README.md file."""
    parser = AwesomeMarkdownParser()
    # Use sync approach for local files
    import asyncio
    result = asyncio.get_event_loop().run_until_complete(
        parser.crawl(repo=repo, readme_path=path)
    )
    return result.items