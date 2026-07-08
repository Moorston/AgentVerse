"""Index task — writes extracted data to Neo4j and pgvector via TaskIQ."""

from typing import Any

from agentverse.graph_core.client import GraphClient
from agentverse.shared.config import Settings
from agentverse.shared.logging import get_logger
from agentverse.worker.broker import broker

logger = get_logger(__name__)


async def run_index(
    graph_client: GraphClient | None = None,
    vector_store: Any | None = None,
    entities: list[dict[str, Any]] | None = None,
    relationships: list[dict[str, Any]] | None = None,
) -> dict[str, int]:
    """Execute an indexing task — write entities and relationships to Neo4j.

    Args:
        graph_client: Connected GraphClient for Neo4j writes.
        vector_store: Connected PgVectorStore for embedding writes.
        entities: List of entity dicts with type, name, properties.
        relationships: List of relationship dicts with source, target, type.

    Returns:
        Counts of indexed items.
    """
    entities = entities or []
    relationships = relationships or []

    logger.info("Starting indexing", entities=len(entities), relationships=len(relationships))

    entity_count = 0
    rel_count = 0

    if not graph_client:
        logger.warning("No GraphClient provided — skipping Neo4j writes")
        return {"entities_indexed": 0, "relationships_indexed": 0}

    # Write entities to Neo4j
    for entity in entities:
        entity_type = entity.get("type", "Concept")
        name = entity.get("name", "")
        props = entity.get("properties", {})
        if not name:
            logger.warning("Skipping entity with no name", entity=entity)
            continue

        try:
            cql = f"MERGE (n:{entity_type} {{name: $name}}) SET n += $props RETURN n"
            await graph_client.execute(cql, {"name": name, "props": props})
            entity_count += 1
            logger.debug("Indexed entity", type=entity_type, name=name)
        except Exception as exc:
            logger.error("Failed to index entity", name=name, error=str(exc))

    # Write relationships to Neo4j
    for rel in relationships:
        source = rel.get("source", "")
        target = rel.get("target", "")
        rel_type = rel.get("type", "RELATED_TO")
        if not source or not target:
            logger.warning("Skipping relationship with missing source/target", rel=rel)
            continue

        try:
            cql = (
                f"MATCH (a {{name: $source}}), (b {{name: $target}}) "
                f"MERGE (a)-[r:{rel_type}]->(b) RETURN r"
            )
            await graph_client.execute(cql, {"source": source, "target": target})
            rel_count += 1
            logger.debug("Indexed relationship", source=source, target=target, type=rel_type)
        except Exception as exc:
            logger.error("Failed to index relationship", source=source, target=target, error=str(exc))

    logger.info("Indexing complete", entities=entity_count, relationships=rel_count)
    return {"entities_indexed": entity_count, "relationships_indexed": rel_count}


@broker.task(
    task_name="index_text",
    retry_on_error=True,
    max_retries=3,
)
async def index_text(extraction_result: dict[str, Any]) -> dict[str, int]:
    """TaskIQ task: index extraction results into Neo4j.

    Called by extract_text after successful extraction.
    Initializes its own GraphClient since TaskIQ tasks are standalone.
    """
    logger.info("=== TaskIQ: index_text starting ===")

    settings = Settings()
    graph_client = GraphClient(settings)
    try:
        await graph_client.connect()
        result = await run_index(
            graph_client=graph_client,
            entities=extraction_result.get("entities", []),
            relationships=extraction_result.get("relationships", []),
        )
        logger.info("=== TaskIQ: index_text complete ===", result=result)
        return result
    finally:
        await graph_client.close()
