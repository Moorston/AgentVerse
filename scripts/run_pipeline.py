#!/usr/bin/env python3
"""End-to-end data pipeline — crawl → extract → normalize → store.

Usage:
    python scripts/run_pipeline.py              # Full pipeline (arXiv + extract + store)
    python scripts/run_pipeline.py --crawl-only # Only crawl
    python scripts/run_pipeline.py --dry-run    # Preview without writing to DB
"""

import argparse
import asyncio
from typing import Any

from agentverse.crawler.sources.arxiv import ArxivCrawler
from agentverse.extractor.extractors.paper import PaperExtractor
from agentverse.extractor.extractors.concept import ConceptExtractor
from agentverse.extractor.extractors.relationship import RelationshipExtractor
from agentverse.graph_core.client import GraphClient
from agentverse.graph_core.repository.base import BaseRepository
from agentverse.ontology.concepts.paper import PaperConcept
from agentverse.ontology.concepts.agent import AgentConcept
from agentverse.ontology.concepts.framework import FrameworkConcept
from agentverse.ontology.normalizer import normalize_paper, normalize_agent, normalize_framework
from agentverse.shared.config import Settings
from agentverse.shared.logging import get_logger

logger = get_logger(__name__)


async def run_pipeline(
    max_papers: int = 10,
    dry_run: bool = False,
    crawl_only: bool = False,
) -> dict[str, Any]:
    """Run the full data pipeline.

    Args:
        max_papers: Maximum papers to process.
        dry_run: If True, don't write to database.
        crawl_only: If True, only crawl without extraction.
    """
    stats = {"crawled": 0, "extracted": 0, "stored": 0, "errors": 0}

    # Step 1: Crawl
    print(f"\n{'='*50}")
    print(f"Step 1: Crawling arXiv (max {max_papers} papers)...")
    print(f"{'='*50}")
    crawler = ArxivCrawler()
    crawl_result = await crawler.crawl(max_results=max_papers, categories=["cs.AI", "cs.LG", "cs.CL"])

    stats["crawled"] = len(crawl_result.items)
    print(f"  Crawled: {stats['crawled']} papers")
    if crawl_result.errors:
        print(f"  Errors: {len(crawl_result.errors)}")
        for err in crawl_result.errors[:3]:
            print(f"    - {err}")

    if crawl_only or not crawl_result.items:
        return stats

    # Step 2: Extract
    print(f"\n{'='*50}")
    print(f"Step 2: Extracting concepts from {len(crawl_result.items)} papers...")
    print(f"{'='*50}")
    paper_extractor = PaperExtractor()
    concept_extractor = ConceptExtractor()
    relationship_extractor = RelationshipExtractor()

    all_concepts: list[dict[str, Any]] = []
    all_relationships: list[dict[str, Any]] = []

    for i, paper in enumerate(crawl_result.items[:5], 1):  # Limit to 5 for demo
        title = paper.get("title", "Unknown")
        abstract = paper.get("abstract", "")
        print(f"  [{i}/5] Extracting: {title[:60]}...")

        if not abstract:
            print(f"    Skipped (no abstract)")
            continue

        try:
            # Extract concepts
            concept_result = await concept_extractor.extract(abstract)
            all_concepts.extend(concept_result.entities)

            # Extract relationships
            rel_result = await relationship_extractor.extract(abstract)
            all_relationships.extend(rel_result.relationships)

            stats["extracted"] += 1
            print(f"    Concepts: {len(concept_result.entities)}, Relations: {len(rel_result.relationships)}")
        except Exception as exc:
            stats["errors"] += 1
            print(f"    Error: {exc}")

    print(f"\n  Total extracted: {stats['extracted']} papers")
    print(f"  Total concepts: {len(all_concepts)}")
    print(f"  Total relationships: {len(all_relationships)}")

    # Step 3: Normalize and Store
    if dry_run:
        print(f"\n{'='*50}")
        print(f"Step 3: DRY RUN — would store:")
        print(f"{'='*50}")
        print(f"  Papers: {stats['crawled']}")
        print(f"  Concepts: {len(all_concepts)}")
        print(f"  Relationships: {len(all_relationships)}")
        return stats

    print(f"\n{'='*50}")
    print(f"Step 3: Storing in Neo4j...")
    print(f"{'='*50}")

    settings = Settings()
    client = GraphClient(settings)
    await client.connect()

    if not await client.health_check():
        print("  ERROR: Neo4j not available. Skipping storage.")
        return stats

    repo = BaseRepository(client)

    # Store papers
    for paper in crawl_result.items:
        normalized = normalize_paper(paper)
        await repo.create_node(normalized.labels, normalized.properties)
        stats["stored"] += 1

    # Store concepts
    for concept in all_concepts:
        name = concept.get("name", "")
        if not name:
            continue
        await repo.create_node(
            ["Concept"],
            {"name": name, "description": concept.get("description", ""), "category": concept.get("category", "")},
        )
        stats["stored"] += 1

    # Store relationships
    for rel in all_relationships:
        source = rel.get("source", "")
        target = rel.get("target", "")
        rel_type = rel.get("type", "RELATED_TO")
        if source and target:
            await repo.create_relationship("Concept", source, "Concept", target, rel_type)

    node_count = await client.node_count()
    rel_count = await client.relationship_count()
    print(f"  Stored successfully!")
    print(f"  Total nodes: {node_count}")
    print(f"  Total relationships: {rel_count}")

    await client.close()
    return stats


async def main() -> None:
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="AgentVerse data pipeline")
    parser.add_argument("--max-papers", type=int, default=10, help="Max papers to crawl")
    parser.add_argument("--crawl-only", action="store_true", help="Only crawl, no extraction")
    parser.add_argument("--dry-run", action="store_true", help="Preview without writing to DB")
    args = parser.parse_args()

    print("AgentVerse Data Pipeline")
    print(f"  Max papers: {args.max_papers}")
    print(f"  Crawl only: {args.crawl_only}")
    print(f"  Dry run: {args.dry_run}")

    stats = await run_pipeline(
        max_papers=args.max_papers,
        dry_run=args.dry_run,
        crawl_only=args.crawl_only,
    )

    print(f"\n{'='*50}")
    print(f"Pipeline Summary:")
    print(f"{'='*50}")
    print(f"  Crawled:    {stats['crawled']}")
    print(f"  Extracted:  {stats['extracted']}")
    print(f"  Stored:     {stats['stored']}")
    print(f"  Errors:     {stats['errors']}")


if __name__ == "__main__":
    asyncio.run(main())