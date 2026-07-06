#!/usr/bin/env python3
"""Build an in-memory knowledge graph from multiple sources and export to JSON.

No database required. Collects data from arXiv, GitHub, and Memory frameworks,
extracts concepts via LLM, and exports to datasets/ for frontend consumption.

Usage:
    python scripts/build_knowledge_graph.py                 # Full pipeline
    python scripts/build_knowledge_graph.py --skip-extract   # Skip LLM extraction
    python scripts/build_knowledge_graph.py --max-papers 5   # Limit papers
"""

import argparse
import asyncio
import sys
from pathlib import Path

# Add scripts/ to path so kg/ is importable
sys.path.insert(0, str(Path(__file__).parent))

from kg.graph import KnowledgeGraph
from kg.collector import (
    collect_arxiv,
    collect_github_frameworks,
    collect_memory_frameworks,
    collect_news,
    extract_concepts_from_papers,
    extract_concepts_from_news,
    build_framework_data,
    build_timeline,
    enrich_citations,
    get_last_run,
    merge_into_existing,
    save_last_run,
)
from kg.exporter import export_datasets


async def main() -> None:
    parser = argparse.ArgumentParser(description="Build knowledge graph from multiple sources")
    parser.add_argument("--max-papers", type=int, default=10, help="Max papers to crawl")
    parser.add_argument("--extract-count", type=int, default=5, help="Papers to run LLM extraction on")
    parser.add_argument("--skip-extract", action="store_true", help="Skip LLM extraction")
    parser.add_argument("--skip-citations", action="store_true", help="Skip Semantic Scholar citations")
    parser.add_argument("--incremental", action="store_true", help="Only process new papers since last run")
    args = parser.parse_args()

    graph = KnowledgeGraph()

    print("=" * 60)
    print("  AgentVerse Knowledge Graph Builder")
    print("=" * 60)

    # F1: Multi-source collection
    papers = await collect_arxiv(graph, args.max_papers)
    news_items = await collect_news(graph)
    frameworks = await collect_github_frameworks(graph)
    memory_items = await collect_memory_frameworks(graph)

    # Incremental: filter papers by date, merge existing graph
    if args.incremental:
        last_run = get_last_run()
        merge_into_existing(graph)
        if last_run and papers:
            papers = [p for p in papers if p.get("published_date", "") > last_run]
            print(f"  [Incremental] Processing {len(papers)} new papers since {last_run}")
        else:
            print(f"  [Incremental] Processing {len(papers)} papers (no previous run found)")

    # F1: LLM extraction
    if not args.skip_extract and papers:
        await extract_concepts_from_papers(graph, papers, args.extract_count)

    # F7: News concept extraction
    if not args.skip_extract and news_items:
        await extract_concepts_from_news(graph, news_items, args.extract_count)

    # F3: Framework ecosystem
    framework_data = build_framework_data(graph)

    # F4: Evolution timeline
    timeline = build_timeline(graph)

    # F5: Citation analysis
    papers_data: list[dict] = []
    if not args.skip_citations:
        papers_data = await enrich_citations(graph, papers) or []
    else:
        for node in graph.nodes.values():
            if node.get("type") == "paper":
                papers_data.append({
                    "name": node.get("name", ""),
                    "description": node.get("description", "")[:150],
                    "authors": node.get("authors", []),
                    "published_date": node.get("published_date", ""),
                    "arxiv_id": node.get("arxiv_id", ""),
                    "citation_count": 0,
                })

    # F2+F6: Export
    print(f"\n{'=' * 60}")
    print("  Exporting datasets...")
    print(f"{'=' * 60}")
    export_datasets(graph, framework_data, timeline, papers_data, news_items)

    # Save last run timestamp for incremental mode
    save_last_run()
    print(f"  [Incremental] Saved last_run timestamp")

    # Summary
    stats = graph.stats()
    print(f"\n{'=' * 60}")
    print("  Summary")
    print(f"{'=' * 60}")
    print(f"  Total nodes:      {stats['total_nodes']}")
    print(f"  Total edges:      {stats['total_edges']}")
    print(f"  Node types:       {stats['node_types']}")
    print(f"  Edge types:       {stats['edge_types']}")
    print(f"  Datasets:         5 JSON files in datasets/")
    print()


if __name__ == "__main__":
    asyncio.run(main())
