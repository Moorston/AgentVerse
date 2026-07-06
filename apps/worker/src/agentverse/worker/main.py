"""Worker entry point — multi-source automatic knowledge pipeline."""

import asyncio
import signal
from typing import Any

from agentverse.shared.logging import get_logger
from agentverse.worker.config import WorkerSettings
from agentverse.worker.lifecycle import WorkerClients, init_clients, close_clients
from agentverse.worker.scheduler import Scheduler

logger = get_logger(__name__)


# ── Task factories (capture clients in closure) ────────────────────


def make_crawl_arxiv(clients: WorkerClients):
    async def task_crawl_arxiv() -> None:
        from agentverse.worker.tasks.crawl import run_crawl
        logger.info("=== Starting ArXiv crawl task ===")
        items = await run_crawl("arxiv", max_results=100)
        logger.info("ArXiv crawl task complete", items=len(items))
    return task_crawl_arxiv


def make_extract_papers(clients: WorkerClients):
    async def task_extract_papers() -> None:
        from agentverse.worker.tasks.extract import run_extract
        from agentverse.worker.tasks.index import run_index
        logger.info("=== Starting paper extraction task ===")

        # Query unprocessed papers from Neo4j
        try:
            records = await clients.graph.execute(
                "MATCH (p:Paper) WHERE NOT (p)-[:HAS_CONCEPT]->() "
                "RETURN p.id AS id, p.title AS title, p.abstract AS abstract LIMIT 50"
            )
            logger.info("Found unprocessed papers", count=len(records))
        except Exception as exc:
            logger.warning("Could not query unprocessed papers", error=str(exc))
            records = []

        for paper in records:
            abstract = paper.get("abstract", "")
            if not abstract:
                continue
            result = await run_extract(abstract, source="paper")
            await run_index(
                graph_client=clients.graph,
                vector_store=clients.vector_store,
                entities=result.get("entities", []),
                relationships=result.get("relationships", []),
            )

        logger.info("Paper extraction task complete", processed=len(records))
    return task_extract_papers


def make_crawl_github(clients: WorkerClients):
    async def task_crawl_github() -> None:
        from agentverse.worker.tasks.crawl import run_crawl
        logger.info("=== Starting GitHub crawl task ===")
        items = await run_crawl("github")
        logger.info("GitHub crawl task complete", items=len(items))
    return task_crawl_github


def make_crawl_rss(clients: WorkerClients):
    async def task_crawl_rss() -> None:
        from agentverse.worker.tasks.crawl import run_crawl
        logger.info("=== Starting RSS crawl task ===")
        items = await run_crawl("rss")
        logger.info("RSS crawl task complete", items=len(items))
    return task_crawl_rss


def make_index(clients: WorkerClients):
    async def task_index() -> None:
        from agentverse.worker.tasks.index import run_index
        logger.info("=== Starting indexing task ===")
        result = await run_index(graph_client=clients.graph, vector_store=clients.vector_store)
        logger.info("Indexing task complete", result=result)
    return task_index


# ── Main ───────────────────────────────────────────────────────────


async def main() -> None:
    """Main worker loop with task scheduler."""
    settings = WorkerSettings()
    logger.info("Worker starting", environment=settings.environment)

    # Initialize database connections
    clients = await init_clients(settings)

    scheduler = Scheduler()

    # Register tasks with intervals (seconds)
    scheduler.register("crawl_arxiv", make_crawl_arxiv(clients), interval_seconds=86400)      # Daily
    scheduler.register("extract_papers", make_extract_papers(clients), interval_seconds=86400)  # Daily
    scheduler.register("crawl_github", make_crawl_github(clients), interval_seconds=604800)    # Weekly
    scheduler.register("crawl_rss", make_crawl_rss(clients), interval_seconds=86400)           # Daily
    scheduler.register("index", make_index(clients), interval_seconds=3600)                     # Hourly

    logger.info("Scheduler configured", tasks=5, poll_interval=settings.poll_interval)

    try:
        await scheduler.run()
    finally:
        await close_clients(clients)


if __name__ == "__main__":
    asyncio.run(main())
