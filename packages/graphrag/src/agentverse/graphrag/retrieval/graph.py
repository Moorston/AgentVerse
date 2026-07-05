"""Graph traversal search via Neo4j."""

from typing import Any

from agentverse.graph_core.client import GraphClient
from agentverse.shared.logging import get_logger

logger = get_logger(__name__)


class GraphSearch:
    """Knowledge graph traversal search."""

    def __init__(self, client: GraphClient) -> None:
        self._client = client

    async def search(self, query: str, top_k: int = 10, max_depth: int = 3) -> list[dict[str, Any]]:
        """Traverse the knowledge graph to find relevant nodes.

        Strategy:
        1. Exact match on node name
        2. Fuzzy match on name/description
        3. Multi-hop traversal from matched nodes

        Args:
            query: Search query text.
            top_k: Maximum results.
            max_depth: Maximum traversal depth.

        Returns:
            List of results with node data, path, and relevance score.
        """
        results: list[dict[str, Any]] = []

        # Strategy 1: Exact name match
        exact = await self._client.execute(
            """
            MATCH (n)
            WHERE n.name = $query
            OPTIONAL MATCH (n)-[r]-(m)
            RETURN n, collect({rel: type(r), node: m.name, labels: labels(m)}) AS connections
            LIMIT $limit
            """,
            {"query": query, "limit": top_k},
        )
        for record in exact:
            results.append({
                "node": record["n"],
                "connections": record["connections"],
                "match_type": "exact",
                "score": 1.0,
            })

        # Strategy 2: Fuzzy match (CONTAINS)
        if len(results) < top_k:
            fuzzy = await self._client.execute(
                """
                MATCH (n)
                WHERE n.name CONTAINS $query OR n.description CONTAINS $query
                AND n.name <> $query
                OPTIONAL MATCH (n)-[r]-(m)
                RETURN n, collect({rel: type(r), node: m.name, labels: labels(m)}) AS connections
                LIMIT $limit
                """,
                {"query": query, "limit": top_k - len(results)},
            )
            for record in fuzzy:
                results.append({
                    "node": record["n"],
                    "connections": record["connections"],
                    "match_type": "fuzzy",
                    "score": 0.7,
                })

        # Strategy 3: Multi-hop traversal from top results
        if results and len(results) < top_k:
            top_node = results[0]["node"]
            node_name = top_node.get("name", "")
            if node_name:
                neighbors = await self._client.execute(
                    f"""
                    MATCH path = (n {{name: $name}})-[*1..{max_depth}]-(m)
                    RETURN nodes(path) AS path_nodes, relationships(path) AS path_rels
                    LIMIT $limit
                    """,
                    {"name": node_name, "limit": top_k - len(results)},
                )
                for record in neighbors:
                    results.append({
                        "path_nodes": record["path_nodes"],
                        "path_rels": record["path_rels"],
                        "match_type": "traversal",
                        "score": 0.5,
                    })

        logger.info("Graph search complete", query=query, results=len(results))
        return results[:top_k]