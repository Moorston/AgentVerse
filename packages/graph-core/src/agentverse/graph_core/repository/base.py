"""Generic CRUD repository for Neo4j."""

from typing import Any

from agentverse.graph_core.client import GraphClient
from agentverse.graph_core.models.query import Query
from agentverse.shared.logging import get_logger

logger = get_logger(__name__)


class BaseRepository:
    """Base repository with common CRUD operations."""

    def __init__(self, client: GraphClient) -> None:
        self._client = client

    async def _run(self, query: Query) -> list[dict[str, Any]]:
        """Execute a Cypher query and return records."""
        async with self._client.session() as session:
            result = await session.run(query.statement, query.parameters)
            return [record.data() for record in await result.fetch()]

    async def execute_raw(self, cql: str, params: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        """Execute raw Cypher. Use business methods when possible."""
        return await self._run(Query(cql, params or {}))

    async def create_node(self, labels: list[str], properties: dict[str, Any]) -> dict[str, Any]:
        """Create a node with given labels and properties using MERGE to avoid duplicates."""
        label_str = ":".join(labels)
        props_str = ", ".join(f"{k}: ${k}" for k in properties)
        cql = f"MERGE (n:{label_str} {{{props_str}}}) RETURN n"
        results = await self._run(Query(cql, properties))
        return results[0] if results else {}

    async def find_node(self, label: str, name: str) -> dict[str, Any] | None:
        """Find a node by label and name property."""
        cql = f"MATCH (n:{label} {{name: $name}}) RETURN n"
        results = await self._run(Query(cql, {"name": name}))
        return results[0] if results else None

    async def find_nodes_by_label(self, label: str, limit: int = 100, offset: int = 0) -> list[dict[str, Any]]:
        """Find nodes by label with pagination."""
        cql = f"MATCH (n:{label}) RETURN n SKIP $offset LIMIT $limit"
        return await self._run(Query(cql, {"offset": offset, "limit": limit}))

    async def create_relationship(
        self,
        from_label: str,
        from_name: str,
        to_label: str,
        to_name: str,
        rel_type: str,
        properties: dict[str, Any] | None = None,
    ) -> bool:
        """Create a relationship between two existing nodes."""
        props_str = ""
        params: dict[str, Any] = {
            "from_name": from_name,
            "to_name": to_name,
        }
        if properties:
            props_str = " {" + ", ".join(f"{k}: ${k}" for k in properties) + "}"
            params.update(properties)

        cql = f"""
        MATCH (a:{from_label} {{name: $from_name}})
        MATCH (b:{to_label} {{name: $to_name}})
        MERGE (a)-[r:{rel_type}{props_str}]->(b)
        RETURN r
        """
        results = await self._run(Query(cql, params))
        return len(results) > 0

    async def get_neighbors(self, label: str, name: str, depth: int = 1) -> dict[str, Any]:
        """Get a node and its N-hop neighbors as a subgraph."""
        cql = f"""
        MATCH path = (n:{label} {{name: $name}})-[*1..{depth}]-(m)
        RETURN nodes(path) AS nodes, relationships(path) AS rels
        LIMIT 100
        """
        results = await self._run(Query(cql, {"name": name}))
        return {
            "nodes": [r["nodes"] for r in results],
            "relationships": [r["rels"] for r in results],
        }

    async def find_by_name(self, label: str, name: str) -> dict[str, Any] | None:
        """Find a single node by label and name."""
        cql = f"MATCH (n:{label} {{name: $name}}) RETURN n"
        results = await self._run(Query(cql, {"name": name}))
        return results[0] if results else None

    async def delete_by_name(self, label: str, name: str) -> bool:
        """Delete a node by label and name."""
        cql = f"MATCH (n:{label} {{name: $name}}) DETACH DELETE n"
        await self._run(Query(cql, {"name": name}))
        return True

    async def delete_node(self, label: str, name: str) -> bool:
        """Delete a node and all its relationships."""
        cql = f"MATCH (n:{label} {{name: $name}}) DETACH DELETE n"
        await self._run(Query(cql, {"name": name}))
        return True