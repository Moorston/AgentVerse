"""Export knowledge graph datasets to JSON files."""

import json
import shutil
from pathlib import Path
from typing import Any

from kg.graph import KnowledgeGraph


def export_datasets(
    graph: KnowledgeGraph,
    frameworks: list[dict[str, Any]],
    timeline: dict[str, Any],
    papers: list[dict[str, Any]],
    news: list[dict[str, Any]],
) -> None:
    """Export all datasets to JSON files."""
    datasets_dir = Path("datasets")
    datasets_dir.mkdir(exist_ok=True)

    # knowledge_graph.json (D3 format)
    d3_data = graph.to_d3()
    with open(datasets_dir / "knowledge_graph.json", "w", encoding="utf-8") as f:
        json.dump(d3_data, f, indent=2, ensure_ascii=False, default=str)
    print(f"  [Export] knowledge_graph.json: {len(d3_data['nodes'])} nodes, {len(d3_data['links'])} links")

    # frameworks.json
    with open(datasets_dir / "frameworks.json", "w", encoding="utf-8") as f:
        json.dump(frameworks, f, indent=2, ensure_ascii=False, default=str)
    print(f"  [Export] frameworks.json: {len(frameworks)} frameworks")

    # timeline.json
    with open(datasets_dir / "timeline.json", "w", encoding="utf-8") as f:
        json.dump(timeline, f, indent=2, ensure_ascii=False, default=str)
    chains_count = len(timeline.get("evolution_chains", []))
    links_count = len(timeline.get("paper_concept_links", []))
    print(f"  [Export] timeline.json: {chains_count} chains, {links_count} paper-concept links")

    # papers.json
    with open(datasets_dir / "papers.json", "w", encoding="utf-8") as f:
        json.dump(papers, f, indent=2, ensure_ascii=False, default=str)
    print(f"  [Export] papers.json: {len(papers)} papers")

    # news.json
    with open(datasets_dir / "news.json", "w", encoding="utf-8") as f:
        json.dump(news, f, indent=2, ensure_ascii=False, default=str)
    print(f"  [Export] news.json: {len(news)} news items")

    # Copy to frontend public directory
    frontend_data = Path("apps/web/public/data")
    frontend_data.mkdir(parents=True, exist_ok=True)
    for fname in ["knowledge_graph.json", "frameworks.json", "timeline.json", "papers.json", "news.json"]:
        src = datasets_dir / fname
        if src.exists():
            shutil.copy2(src, frontend_data / fname)
    print(f"  [Export] Copied to apps/web/public/data/")
