"""Hybrid retrieval — combines vector search and graph traversal."""

from typing import Any

from agentverse.graphrag.retrieval.vector import VectorSearch
from agentverse.graphrag.retrieval.graph import GraphSearch
from agentverse.shared.logging import get_logger

logger = get_logger(__name__)


class HybridSearch:
    """Combines vector search and graph traversal with fusion ranking."""

    def __init__(self, vector_search: VectorSearch, graph_search: GraphSearch) -> None:
        self._vector_search = vector_search
        self._graph_search = graph_search

    async def search(self, query: str, top_k: int = 10) -> list[dict[str, Any]]:
        """Perform hybrid search combining vector and graph results.

        Args:
            query: Search query text.
            top_k: Maximum results.

        Returns:
            Merged and ranked results.
        """
        vector_results = await self._vector_search.search(query, top_k=top_k)
        graph_results = await self._graph_search.search(query, top_k=top_k)

        return self._merge_and_rank(vector_results, graph_results, top_k)

    def _merge_and_rank(
        self,
        vector_results: list[dict[str, Any]],
        graph_results: list[dict[str, Any]],
        top_k: int,
    ) -> list[dict[str, Any]]:
        """Merge results from both sources and rank by combined score.

        Scoring:
        - Vector results: score from cosine similarity
        - Graph results: score from match_type (exact=1.0, fuzzy=0.7, traversal=0.5)
        - Combined: 0.6 * vector_score + 0.4 * graph_score
        """
        seen: set[str] = set()
        merged: list[dict[str, Any]] = []

        # Index graph results by node name for deduplication
        graph_by_name: dict[str, dict[str, Any]] = {}
        for r in graph_results:
            node = r.get("node", {})
            name = node.get("name", "") if isinstance(node, dict) else ""
            if name:
                graph_by_name[name] = r

        # Add vector results, boosting with graph score if present
        for vr in vector_results:
            node_id = vr.get("node_id", "")
            name = vr.get("name", "")
            if name in seen:
                continue
            seen.add(name)

            vector_score = vr.get("score", 0.5)
            graph_score = graph_by_name.get(name, {}).get("score", 0.0)
            combined_score = 0.6 * vector_score + 0.4 * graph_score

            merged.append({
                **vr,
                "score": combined_score,
                "source": "hybrid" if graph_score > 0 else "vector",
            })

        # Add graph-only results
        for r in graph_results:
            node = r.get("node", {})
            name = node.get("name", "") if isinstance(node, dict) else ""
            if name and name not in seen:
                seen.add(name)
                merged.append({
                    **r,
                    "score": r.get("score", 0.5) * 0.4,
                    "source": "graph",
                })

        # Sort by combined score descending
        merged.sort(key=lambda x: x.get("score", 0), reverse=True)
        logger.info("Hybrid search complete", results=len(merged[:top_k]))
        return merged[:top_k]