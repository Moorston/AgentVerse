"""Worker entry point — multi-source automatic knowledge pipeline."""

import asyncio
import time
from typing import Any

from agentverse.shared.logging import get_logger
from agentverse.worker.config import WorkerSettings
from agentverse.worker.scheduler import Scheduler

logger = get_logger(__name__)


async def task_crawl_arxiv() -> None:
    """Daily ArXiv paper crawl."""
    from agentverse.worker.tasks.crawl import run_crawl
    logger.info("=== Starting ArXiv crawl task ===")
    items = await run_crawl("arxiv", max_results=100)
    logger.info("ArXiv crawl task complete", items=len(items))


async def task_extract_papers() -> None:
    """Extract concepts from crawled papers.

    Reads unprocessed papers from the database (or in-memory queue),
    runs concept extraction, and passes results to the indexing pipeline.
    """
    from agentverse.worker.tasks.extract import run_extract
    from agentverse.worker.tasks.index import run_index
    logger.info("=== Starting paper extraction task ===")

    # TODO: Read from Neo4j query for unprocessed papers
    # For now, demonstrates the pipeline structure
    # In production: query Neo4j for papers without HAS_CONCEPT relationship
    # papers = await graph_client.execute(
    #     "MATCH (p:Paper) WHERE NOT (p)-[:HAS_CONCEPT]->() RETURN p LIMIT 50"
    # )

    # For each paper, extract concepts and index them
    # for paper in papers:
    #     result = await run_extract(paper["abstract"], source="paper")
    #     await run_index(entities=result.get("entities", []), relationships=result.get("relationships", []))

    logger.info("Paper extraction task complete (no unprocessed papers in queue)")


async def task_crawl_github() -> None:
    """Weekly GitHub framework update."""
    from agentverse.worker.tasks.crawl import run_crawl
    logger.info("=== Starting GitHub crawl task ===")
    items = await run_crawl("github")
    logger.info("GitHub crawl task complete", items=len(items))


async def task_crawl_rss() -> None:
    """Daily RSS news crawl."""
    from agentverse.worker.tasks.crawl import run_crawl
    logger.info("=== Starting RSS crawl task ===")
    items = await run_crawl("rss")
    logger.info("RSS crawl task complete", items=len(items))


async def task_index() -> None:
    """Update GraphRAG index."""
    from agentverse.worker.tasks.index import run_index
    logger.info("=== Starting indexing task ===")
    result = await run_index()
    logger.info("Indexing task complete", result=result)


async def main() -> None:
    """Main worker loop with task scheduler."""
    settings = WorkerSettings()
    logger.info("Worker starting", environment=settings.environment)

    scheduler = Scheduler()

    # Register tasks with intervals (seconds)
    scheduler.register("crawl_arxiv", task_crawl_arxiv, interval_seconds=86400)     # Daily
    scheduler.register("extract_papers", task_extract_papers, interval_seconds=86400) # Daily
    scheduler.register("crawl_github", task_crawl_github, interval_seconds=604800)   # Weekly
    scheduler.register("crawl_rss", task_crawl_rss, interval_seconds=86400)          # Daily
    scheduler.register("index", task_index, interval_seconds=3600)                    # Hourly

    logger.info(
        "Scheduler configured",
        tasks=5,
        poll_interval=settings.poll_interval,
    )

    await scheduler.run()


if __name__ == "__main__":
    asyncio.run(main())
