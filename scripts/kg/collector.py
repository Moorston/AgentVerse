"""Multi-source data collection and extraction for the knowledge graph."""

from typing import Any

from agentverse.crawler.types import CrawlRequest

from kg.graph import KnowledgeGraph, normalize_name


# ── arXiv ───────────────────────────────────────────────────────


async def collect_arxiv(graph: KnowledgeGraph, max_papers: int = 10) -> list[dict]:
    """Collect papers from arXiv and extract concepts via LLM."""
    from agentverse.crawler.sources.arxiv import ArxivCrawler

    print("\n  [arXiv] Crawling papers...")
    crawler = ArxivCrawler()
    result = await crawler.crawl(CrawlRequest(
        max_results=max_papers, categories=["cs.AI", "cs.LG", "cs.CL"],
    ))
    print(f"  [arXiv] Crawled {len(result.items)} papers")

    for err in result.errors:
        print(f"  [arXiv] Error: {err[:80]}")

    # Add paper nodes
    for paper in result.items:
        title = paper.get("title", "")
        if not title:
            continue
        node_id = normalize_name(title)
        graph.add_node(
            node_id,
            type="paper",
            name=title,
            description=paper.get("abstract", "")[:200],
            authors=paper.get("authors", []),
            published_date=paper.get("published_date", ""),
            arxiv_id=paper.get("arxiv_id", ""),
            categories=paper.get("categories", []),
            sources=["arxiv"],
        )

    return result.items


async def extract_concepts_from_papers(
    graph: KnowledgeGraph, papers: list[dict], extract_count: int = 5,
) -> None:
    """Extract concepts and relationships from paper abstracts using LLM."""
    from agentverse.extractor.llm.client import LLMClient
    from agentverse.extractor.extractors.concept import ConceptExtractor
    from agentverse.extractor.extractors.relationship import RelationshipExtractor

    print(f"\n  [Extract] Running LLM extraction on {extract_count} papers...")
    llm = LLMClient()
    ce = ConceptExtractor(llm_client=llm)
    re_ext = RelationshipExtractor(llm_client=llm)

    papers_with_abstract = [p for p in papers if p.get("abstract")]
    extracted = 0

    for paper in papers_with_abstract[:extract_count]:
        title = paper.get("title", "")
        abstract = paper["abstract"]
        paper_id = normalize_name(title)

        try:
            # Extract concepts
            cr = await ce.extract(abstract)
            for c in cr.entities:
                cname = normalize_name(c.get("name", ""))
                if not cname:
                    continue
                graph.add_node(
                    cname,
                    type="concept",
                    name=c.get("name", cname),
                    description=c.get("description", ""),
                    category=c.get("category", ""),
                    sources=["arxiv_extraction"],
                )
                # Paper -> PROPOSES -> Concept
                graph.add_edge(paper_id, cname, "PROPOSES")

            # Extract relationships
            rr = await re_ext.extract(abstract)
            for r in rr.relationships:
                src = normalize_name(r.get("source", ""))
                tgt = normalize_name(r.get("target", ""))
                if src and tgt:
                    graph.add_edge(src, tgt, r.get("type", "RELATED_TO"),
                                   evidence=r.get("evidence", ""))

            extracted += 1
            print(f"    [{extracted}/{extract_count}] {title[:50]}... -> {len(cr.entities)} concepts, {len(rr.relationships)} rels")

        except Exception as exc:
            print(f"    Error extracting {title[:40]}: {exc}")

    print(f"  [Extract] Done: {extracted} papers processed")


# ── GitHub ──────────────────────────────────────────────────────


async def collect_github_frameworks(graph: KnowledgeGraph) -> list[dict]:
    """Collect framework data from GitHub."""
    from agentverse.crawler.sources.github import GitHubCrawler

    print("\n  [GitHub] Crawling framework repos...")
    crawler = GitHubCrawler()
    result = await crawler.crawl(CrawlRequest(max_results=15))
    print(f"  [GitHub] Found {len(result.items)} repos")

    for err in result.errors:
        print(f"  [GitHub] Error: {err[:80]}")

    for repo in result.items:
        name = repo.get("name", "")
        if not name:
            continue
        node_id = normalize_name(name)
        graph.add_node(
            node_id,
            type="framework",
            name=name,
            description=repo.get("description", ""),
            github_url=repo.get("html_url", ""),
            stars=repo.get("stargazers_count", 0),
            forks=repo.get("forks_count", 0),
            language=repo.get("language", ""),
            topics=repo.get("topics", []),
            updated_at=repo.get("updated_at", ""),
            sources=["github"],
        )

    return result.items


# ── Memory Frameworks ───────────────────────────────────────────


async def collect_memory_frameworks(graph: KnowledgeGraph) -> list[dict]:
    """Collect memory framework data."""
    from agentverse.crawler.sources.memory_frameworks import MemoryFrameworkCrawler

    print("\n  [Memory] Crawling memory frameworks...")
    crawler = MemoryFrameworkCrawler()
    result = await crawler.crawl()
    print(f"  [Memory] Found {len(result.items)} items")

    for item in result.items:
        name = item.get("name", "")
        if not name:
            continue
        node_id = normalize_name(name)
        itype = item.get("type", "memory_framework")

        graph.add_node(
            node_id,
            type=itype,
            name=name,
            description=item.get("description", ""),
            github_url=item.get("github_url", ""),
            stars=item.get("stars", 0),
            memory_categories=item.get("memory_categories", []),
            sources=["memory_frameworks"],
        )

        # Link memory types to frameworks
        if itype == "memory_type":
            for fw in item.get("frameworks", []):
                fw_id = normalize_name(fw)
                graph.add_edge(fw_id, node_id, "HAS_MEMORY_TYPE")

    return result.items


# ── RSS News ────────────────────────────────────────────────────


async def collect_news(graph: KnowledgeGraph) -> list[dict]:
    """Collect AI news from RSS feeds and link to concepts."""
    from agentverse.crawler.sources.rss import RSSCrawler

    print("\n  [News] Crawling RSS feeds...")
    crawler = RSSCrawler()

    try:
        result = await crawler.crawl()
    except Exception as exc:
        print(f"  [News] Crawl failed: {exc}")
        return []

    print(f"  [News] Found {len(result.items)} news items")

    for err in result.errors:
        print(f"  [News] Error: {err[:80]}")

    news_items = []

    for item in result.items:
        title = item.get("title", "")
        if not title:
            continue
        node_id = normalize_name(title) or f"news_{hash(title) % (10 ** 8)}"
        published = item.get("published_date", "")

        graph.add_node(
            node_id,
            type="news",
            name=title,
            description=item.get("description", "")[:300],
            source=item.get("source", ""),
            url=item.get("url", ""),
            published_date=published,
            sources=["rss"],
        )

        news_items.append({
            "name": title,
            "source": item.get("source", ""),
            "url": item.get("url", ""),
            "date": published,
            "concepts": [],
        })

    return news_items


async def extract_concepts_from_news(
    graph: KnowledgeGraph, news_items: list[dict], extract_count: int = 5,
) -> None:
    """Extract concepts from news descriptions and link via MENTIONS edges."""
    from agentverse.extractor.llm.client import LLMClient
    from agentverse.extractor.extractors.concept import ConceptExtractor

    items_with_desc = [n for n in news_items if n.get("description")]
    if not items_with_desc:
        print("  [News Extract] No descriptions available")
        return

    print(f"\n  [News Extract] Running LLM extraction on {min(extract_count, len(items_with_desc))} news items...")
    llm = LLMClient()
    ce = ConceptExtractor(llm_client=llm)

    extracted = 0
    for item in items_with_desc[:extract_count]:
        title = item.get("name", "")
        description = item.get("description", "")
        node_id = normalize_name(title) or f"news_{hash(title) % (10 ** 8)}"

        try:
            cr = await ce.extract(description)
            concepts = []
            for c in cr.entities:
                cname = normalize_name(c.get("name", ""))
                if not cname:
                    continue
                graph.add_node(
                    cname,
                    type="concept",
                    name=c.get("name", cname),
                    description=c.get("description", ""),
                    category=c.get("category", ""),
                    sources=["news_extraction"],
                )
                # News -> MENTIONS -> Concept
                graph.add_edge(node_id, cname, "MENTIONS")
                concepts.append(c.get("name", cname))

            # Attach concepts back to the news item for export
            item["concepts"] = concepts
            extracted += 1
            print(f"    [{extracted}/{extract_count}] {title[:50]}... -> {len(cr.entities)} concepts")

        except Exception as exc:
            print(f"    Error extracting {title[:40]}: {exc}")

    print(f"  [News Extract] Done: {extracted} news items processed")


# ── Framework Ecosystem ─────────────────────────────────────────


def build_framework_data(graph: KnowledgeGraph) -> list[dict]:
    """Extract framework data for frontend consumption."""
    frameworks = []
    for node in graph.nodes.values():
        if node.get("type") == "framework":
            # Find concepts this framework implements
            implements = []
            for e in graph.edges:
                if e["source"] == node["id"] and e["type"] == "IMPLEMENTS":
                    implements.append(e["target"])
                elif e["target"] == node["id"] and e["type"] == "IMPLEMENTS":
                    implements.append(e["source"])

            frameworks.append({
                "name": node.get("name", node["id"]),
                "description": node.get("description", ""),
                "github_url": node.get("github_url", ""),
                "stars": node.get("stars", 0),
                "forks": node.get("forks", 0),
                "language": node.get("language", ""),
                "topics": node.get("topics", []),
                "implements": implements,
            })

    # Sort by stars descending
    frameworks.sort(key=lambda f: f.get("stars", 0), reverse=True)
    return frameworks


# ── Concept Evolution Timeline ──────────────────────────────────


def build_timeline(graph: KnowledgeGraph) -> dict[str, Any]:
    """Build concept evolution chains from EVOLVES_TO/EXTENDS/INSPIRED_BY edges."""
    evolution_types = {"EVOLVES_TO", "EXTENDS", "INSPIRED_BY"}

    # Build adjacency for evolution edges
    evolution_graph: dict[str, list[str]] = {}
    for e in graph.edges:
        if e["type"] in evolution_types:
            evolution_graph.setdefault(e["source"], []).append(e["target"])

    # Find chains (DFS from roots -- nodes with no incoming evolution edges)
    has_incoming: set[str] = set()
    for targets in evolution_graph.values():
        has_incoming.update(targets)
    roots = [n for n in evolution_graph if n not in has_incoming]

    chains = []
    visited: set[str] = set()

    def dfs(node: str, path: list[str]) -> None:
        if node in visited:
            return
        visited.add(node)
        path = path + [node]
        if node not in evolution_graph:
            if len(path) > 1:
                chains.append(path)
            return
        for child in evolution_graph[node]:
            dfs(child, path)
        if len(path) > 1 and node not in evolution_graph:
            chains.append(path)

    for root in roots:
        dfs(root, [])

    # Also find any PROPOSES chains (paper -> concept)
    paper_concept_chains = []
    for e in graph.edges:
        if e["type"] == "PROPOSES":
            src_node = graph.nodes.get(e["source"], {})
            tgt_node = graph.nodes.get(e["target"], {})
            if src_node.get("type") == "paper":
                paper_concept_chains.append({
                    "paper": src_node.get("name", e["source"]),
                    "concept": tgt_node.get("name", e["target"]),
                    "category": tgt_node.get("category", ""),
                    "date": src_node.get("published_date", ""),
                })

    # Build timeline entries
    timeline = []
    for chain in chains:
        entries = []
        for node_id in chain:
            node = graph.nodes.get(node_id, {})
            entries.append({
                "name": node.get("name", node_id),
                "type": node.get("type", "concept"),
                "category": node.get("category", ""),
                "description": node.get("description", "")[:100],
            })
        timeline.append({"chain": entries, "length": len(entries)})

    # Sort by chain length descending
    timeline.sort(key=lambda t: t["length"], reverse=True)

    return {
        "evolution_chains": timeline,
        "paper_concept_links": paper_concept_chains,
    }


# ── Citation Analysis ───────────────────────────────────────────


async def enrich_citations(graph: KnowledgeGraph, papers: list[dict]) -> list[dict]:
    """Enrich paper nodes with citation data from Semantic Scholar."""
    from agentverse.crawler.sources.semantic_scholar import SemanticScholarCrawler

    arxiv_ids = [p.get("arxiv_id", "").split("v")[0] for p in papers if p.get("arxiv_id")]
    if not arxiv_ids:
        print("  [Citations] No arXiv IDs available")
        return []

    print(f"\n  [Citations] Looking up {len(arxiv_ids)} papers on Semantic Scholar...")
    crawler = SemanticScholarCrawler(requests_per_second=0.5)

    # Try just the first 3 to avoid rate limiting
    result = await crawler.crawl(CrawlRequest(
        arxiv_ids=arxiv_ids[:3], max_results=3,
    ))
    print(f"  [Citations] Found {len(result.items)} papers with citation data")

    for err in result.errors:
        print(f"  [Citations] Error: {err[:80]}")

    for paper in result.items:
        title = paper.get("title", "")
        if not title:
            continue
        node_id = normalize_name(title)
        if node_id in graph.nodes:
            graph.nodes[node_id]["citation_count"] = paper.get("citation_count", 0)
            graph.nodes[node_id]["influential_citation_count"] = paper.get("influential_citation_count", 0)

    # Build papers.json data
    papers_data = []
    for node in graph.nodes.values():
        if node.get("type") == "paper":
            papers_data.append({
                "name": node.get("name", ""),
                "description": node.get("description", "")[:150],
                "authors": node.get("authors", []),
                "published_date": node.get("published_date", ""),
                "arxiv_id": node.get("arxiv_id", ""),
                "citation_count": node.get("citation_count", 0),
                "categories": node.get("categories", []),
            })
    papers_data.sort(key=lambda p: p.get("citation_count", 0), reverse=True)
    return papers_data


# ── Incremental Helpers ─────────────────────────────────────────


def get_last_run() -> str:
    """Read last run timestamp from datasets/.last_run."""
    try:
        with open("datasets/.last_run") as f:
            return f.read().strip()
    except FileNotFoundError:
        return ""


def save_last_run() -> None:
    """Save current timestamp to datasets/.last_run."""
    from datetime import datetime
    with open("datasets/.last_run", "w") as f:
        f.write(datetime.utcnow().strftime("%Y-%m-%d"))


def merge_into_existing(graph: KnowledgeGraph) -> None:
    """Merge in-memory graph into existing datasets/knowledge_graph.json."""
    import json
    import os
    existing_path = "datasets/knowledge_graph.json"
    if os.path.exists(existing_path):
        with open(existing_path) as f:
            existing = json.load(f)
        for n in existing.get("nodes", []):
            node_id = n.pop("id", "")
            if node_id:
                graph.add_node(node_id, **n)
        # Edges are de-duped by add_edge
        for e in existing.get("links", []):
            graph.add_edge(
                e["source"], e["target"], e.get("type", "RELATED_TO"),
                **{k: v for k, v in e.items() if k not in ("source", "target", "type")},
            )
        print(f"  [Merge] Merged {len(existing.get('nodes', []))} existing nodes and {len(existing.get('links', []))} links")
