#!/usr/bin/env python3
"""Initialize Neo4j schema — apply constraints and indexes."""

import asyncio

from agentverse.graph_core.client import GraphClient
from agentverse.graph_core.schema.constraints import apply_constraints, CONSTRAINTS
from agentverse.graph_core.schema.indexes import apply_indexes, INDEXES
from agentverse.shared.config import Settings
from agentverse.shared.logging import get_logger

logger = get_logger(__name__)


async def main() -> None:
    """Initialize Neo4j schema."""
    settings = Settings()
    client = GraphClient(settings)

    print(f"Connecting to Neo4j at {settings.neo4j_uri}...")
    await client.connect()

    healthy = await client.health_check()
    if not healthy:
        print("ERROR: Cannot connect to Neo4j. Is it running?")
        print("Start with: docker compose up -d neo4j")
        return

    print("Neo4j connected. Applying schema...")

    # Apply constraints
    print(f"\nApplying {len(CONSTRAINTS)} constraints...")
    await apply_constraints(client)
    for i, cql in enumerate(CONSTRAINTS, 1):
        label = cql.split("FOR (")[1].split(")")[0].split(":")[1] if "FOR (" in cql else "?"
        print(f"  [{i}/{len(CONSTRAINTS)}] Constraint on :{label}")

    # Apply indexes
    print(f"\nApplying {len(INDEXES)} indexes...")
    await apply_indexes(client)
    for i, cql in enumerate(INDEXES, 1):
        label = cql.split("FOR (")[1].split(")")[0].split(":")[1] if "FOR (" in cql else "?"
        print(f"  [{i}/{len(INDEXES)}] Index on :{label}")

    # Verify
    node_count = await client.node_count()
    rel_count = await client.relationship_count()
    print(f"\nSchema applied successfully!")
    print(f"  Nodes: {node_count}")
    print(f"  Relationships: {rel_count}")

    await client.close()


if __name__ == "__main__":
    asyncio.run(main())