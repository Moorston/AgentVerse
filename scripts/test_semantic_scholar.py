#!/usr/bin/env python3
"""Test Semantic Scholar crawler — fetch citations and references.

No database required. Tests citation network data quality.

Usage:
    python scripts/test_semantic_scholar.py               # Search mode
    python scripts/test_semantic_scholar.py --query "ReAct agent"
    python scripts/test_semantic_scholar.py --arxiv-ids 2210.03629 2303.11366
"""

import argparse
import asyncio

from agentverse.crawler.sources.arxiv import ArxivCrawler
from agentverse.crawler.sources.semantic_scholar import SemanticScholarCrawler
from agentverse.crawler.types import CrawlRequest
from agentverse.extractor.llm.client import LLMClient
from agentverse.extractor.extractors.concept import ConceptExtractor
from agentverse.extractor.extractors.relationship import RelationshipExtractor


def print_section(title: str) -> None:
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print(f"{'=' * 60}")


def print_paper(paper: dict, idx: int) -> None:
    title = paper.get("title", "?")[:65]
    citations = paper.get("citation_count", 0)
    year = paper.get("year", "?")
    authors = ", ".join(paper.get("authors", [])[:3])
    arxiv_id = paper.get("arxiv_id", "")

    print(f"\n  {'─' * 55}")
    print(f"  [{idx}] {title}")
    print(f"      Year: {year}  |  Citations: {citations}  |  arXiv: {arxiv_id}")
    print(f"      Authors: {authors}")

    abstract = paper.get("abstract", "")
    if abstract:
        print(f"      Abstract: {abstract[:120]}...")


async def main() -> None:
    parser = argparse.ArgumentParser(description="Test Semantic Scholar crawler")
    parser.add_argument("--query", type=str, default="", help="Search query")
    parser.add_argument("--arxiv-ids", nargs="*", default=[], help="arXiv IDs to look up")
    parser.add_argument("--max-results", type=int, default=10, help="Max results")
    parser.add_argument("--extract", action="store_true", help="Also run LLM extraction")
    args = parser.parse_args()

    # Step 0: Get arXiv IDs from recent papers if none provided
    arxiv_ids = args.arxiv_ids
    if not arxiv_ids and not args.query:
        print_section("Step 0: Getting arXiv IDs from recent papers")
        arxiv = ArxivCrawler()
        arxiv_result = await arxiv.crawl(CrawlRequest(
            max_results=5, categories=["cs.AI", "cs.LG"],
        ))
        arxiv_ids = [p.get("arxiv_id", "") for p in arxiv_result.items if p.get("arxiv_id")]
        print(f"  Found {len(arxiv_ids)} arXiv IDs: {arxiv_ids[:3]}...")

    # Step 1: Crawl Semantic Scholar
    print_section(f"Step 1: Semantic Scholar (query='{args.query or '(arxiv IDs)'}')")
    crawler = SemanticScholarCrawler()
    result = await crawler.crawl(CrawlRequest(
        query=args.query,
        arxiv_ids=arxiv_ids if arxiv_ids else None,
        max_results=args.max_results,
    ))

    print(f"  Papers found: {len(result.items)}")
    if result.errors:
        for err in result.errors[:3]:
            print(f"  Error: {err}")

    if not result.items:
        print("  No papers found. Exiting.")
        return

    # Sort by citation count
    result.items.sort(key=lambda p: p.get("citation_count", 0), reverse=True)

    # Print papers
    for i, paper in enumerate(result.items, 1):
        print_paper(paper, i)

    # Step 2: Citation analysis
    print_section("Step 2: Citation Analysis")
    total_citations = sum(p.get("citation_count", 0) for p in result.items)
    max_cite_paper = max(result.items, key=lambda p: p.get("citation_count", 0))
    print(f"  Total citations across {len(result.items)} papers: {total_citations}")
    print(f"  Most cited: {max_cite_paper.get('title', '?')[:50]} ({max_cite_paper.get('citation_count', 0)} citations)")

    # Step 3: LLM extraction (optional)
    if args.extract:
        print_section("Step 3: LLM Extraction on top papers")
        llm = LLMClient()
        ce = ConceptExtractor(llm_client=llm)
        re = RelationshipExtractor(llm_client=llm)

        for i, paper in enumerate(result.items[:3], 1):
            abstract = paper.get("abstract", "")
            if not abstract:
                continue
            title = paper.get("title", "?")[:50]
            print(f"\n  [{i}] {title}")

            cr = await ce.extract(abstract)
            rr = await re.extract(abstract)

            print(f"      Concepts ({len(cr.entities)}):")
            for c in cr.entities:
                print(f"        {c['name']:30s} [{c.get('category', '?')}]")
            print(f"      Relationships ({len(rr.relationships)}):")
            for r in rr.relationships:
                print(f"        {r['source'][:20]} → {r['type']} → {r['target'][:20]}")

    # Summary
    print_section("Summary")
    print(f"  Source:         Semantic Scholar")
    print(f"  Papers:         {len(result.items)}")
    print(f"  Total citations:{total_citations}")
    print(f"  Errors:         {len(result.errors)}")
    print()


if __name__ == "__main__":
    asyncio.run(main())
