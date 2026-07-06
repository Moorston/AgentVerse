#!/usr/bin/env python3
"""Test extraction pipeline — crawl arXiv → extract → print results.

No database required. Tests LLM extraction quality on real papers.

Usage:
    python scripts/test_extract.py              # 5 papers
    python scripts/test_extract.py --max-papers 3   # 3 papers
"""

import argparse
import asyncio
import json

from agentverse.crawler.sources.arxiv import ArxivCrawler
from agentverse.crawler.types import CrawlRequest
from agentverse.extractor.llm.client import LLMClient
from agentverse.extractor.extractors.paper import PaperExtractor
from agentverse.extractor.extractors.concept import ConceptExtractor
from agentverse.extractor.extractors.relationship import RelationshipExtractor
from agentverse.shared.logging import get_logger

logger = get_logger(__name__)


def print_section(title: str) -> None:
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print(f"{'=' * 60}")


def print_paper_result(idx: int, paper: dict, paper_ext: dict, concepts: list, relationships: list) -> None:
    title = paper.get("title", "Unknown")[:70]
    print(f"\n{'─' * 60}")
    print(f"  Paper {idx}: {title}")
    print(f"{'─' * 60}")

    # Paper metadata
    if paper_ext:
        print(f"  Contribution: {paper_ext.get('contribution_type', '?')}")
        print(f"  Authors: {', '.join(paper_ext.get('authors', [])[:3])}")

    # Concepts
    print(f"\n  Concepts ({len(concepts)}):")
    for c in concepts:
        name = c.get("name", "?")
        cat = c.get("category", "?")
        desc = c.get("description", "")[:60]
        print(f"    ├─ {name:30s} [{cat}]")
        if desc:
            print(f"    │  {desc}")

    # Relationships
    print(f"\n  Relationships ({len(relationships)}):")
    for r in relationships:
        src = r.get("source", "?")[:25]
        tgt = r.get("target", "?")[:25]
        rtype = r.get("type", "?")
        print(f"    ├─ {src} → {rtype} → {tgt}")


async def main() -> None:
    parser = argparse.ArgumentParser(description="Test extraction on arXiv papers")
    parser.add_argument("--max-papers", type=int, default=10, help="Papers to crawl")
    parser.add_argument("--extract-count", type=int, default=5, help="Papers to extract")
    args = parser.parse_args()

    # Step 1: Crawl
    print_section(f"Step 1: Crawling arXiv (max {args.max_papers} papers)")
    crawler = ArxivCrawler()
    result = await crawler.crawl(CrawlRequest(
        max_results=args.max_papers, categories=["cs.AI", "cs.LG", "cs.CL"],
    ))

    print(f"  Crawled: {len(result.items)} papers")
    if result.errors:
        for err in result.errors[:3]:
            print(f"  Error: {err}")

    if not result.items:
        print("  No papers crawled. Exiting.")
        return

    # Filter papers with abstracts
    papers_with_abstract = [p for p in result.items if p.get("abstract")]
    print(f"  Papers with abstract: {len(papers_with_abstract)}")

    if not papers_with_abstract:
        print("  No papers with abstracts. Exiting.")
        return

    # Step 2: Extract
    print_section(f"Step 2: Extracting from {min(args.extract_count, len(papers_with_abstract))} papers")

    llm = LLMClient()
    print(f"  LLM: provider={llm._provider}, model={llm._model}, base_url={llm._base_url or '(default)'}")

    paper_extractor = PaperExtractor(llm_client=llm)
    concept_extractor = ConceptExtractor(llm_client=llm)
    relationship_extractor = RelationshipExtractor(llm_client=llm)

    total_concepts = 0
    total_relationships = 0
    errors = 0

    for i, paper in enumerate(papers_with_abstract[: args.extract_count], 1):
        abstract = paper["abstract"]
        title = paper.get("title", "Unknown")

        print(f"\n  [{i}/{args.extract_count}] Processing: {title[:60]}...")

        try:
            # Paper extraction
            paper_result = await paper_extractor.extract(abstract)
            paper_data = paper_result.entities[0]["properties"] if paper_result.entities else {}

            # Concept extraction
            concept_result = await concept_extractor.extract(abstract)

            # Relationship extraction
            rel_result = await relationship_extractor.extract(abstract)

            concepts = concept_result.entities
            relationships = rel_result.relationships

            total_concepts += len(concepts)
            total_relationships += len(relationships)

            print_paper_result(i, paper, paper_data, concepts, relationships)

        except Exception as exc:
            errors += 1
            print(f"    ERROR: {exc}")

    # Step 3: Summary
    print_section("Summary")
    print(f"  Papers crawled:     {len(result.items)}")
    print(f"  Papers extracted:   {args.extract_count - errors}")
    print(f"  Total concepts:     {total_concepts}")
    print(f"  Total relationships:{total_relationships}")
    print(f"  Errors:             {errors}")
    print()


if __name__ == "__main__":
    asyncio.run(main())
