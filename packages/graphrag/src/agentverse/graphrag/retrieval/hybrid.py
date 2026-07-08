"""Hybrid retrieval — combines vector search and graph traversal.

Features:
- Adaptive fusion weights via QueryRouter (semantic vs structural queries)
- TTLCache for repeated queries (default 5 min TTL, 256 entries)
"""

from typing import Any

from cachetools import TTLCache

from agentverse.graphrag.retrieval.graph import GraphSearch
from agentverse.graphrag.retrieval.router import FusionWeights, QueryRouter
from agentverse.graphrag.retrieval.vector import VectorSearch
from agentverse.shared.logging import get_logger

logger = get_logger(__name__)


class HybridSearch:
    """Combines vector search and graph traversal with adaptive fusion ranking."""

    def __init__(
        self,
        vector_search: VectorSearch,
        graph_search: GraphSearch,
        router: QueryRouter | None = None,
        cache_maxsize: int = 256,
        cache_ttl: float = 300.0,
    ) -> None:
        self._vector_search = vector_search
        self._graph_search = graph_search
        self._router = router or QueryRouter()
        self._cache: TTLCache[str, list[dict[str, Any]]] = TTLCache(
            maxsize=cache_maxsize, ttl=cache_ttl
        )

    async def search(self, query: str, top_k: int = 10) -> list[dict[str, Any]]:
        """Perform hybrid search combining vector and graph results.

        Args:
            query: Search query text.
            top_k: Maximum results.

        Returns:
            Merged and ranked results.
        """
        # Check cache
        cache_key = f"{query}:{top_k}"
        if cache_key in self._cache:
            logger.info("hybrid_search_cache_hit", query=query[:50])
            return self._cache[cache_key]

        # Classify query and get adaptive weights
        weights = self._router.weights(query)

        # Run both searches concurrently would be ideal, but we keep it
        # sequential for now to avoid asyncio.gather complexity
        vector_results = await self._vector_search.search(query, top_k=top_k)
        graph_results = await self._graph_search.search(query, top_k=top_k)

        results = self._merge_and_rank(vector_results, graph_results, top_k, weights)

        # Cache results
        self._cache[cache_key] = results
        logger.info("hybrid_search_complete", results=len(results), cached=True)

        return results

    def _merge_and_rank(
        self,
        vector_results: list[dict[str, Any]],
        graph_results: list[dict[str, Any]],
        top_k: int,
        weights: FusionWeights | None = None,
    ) -> list[dict[str, Any]]:
        """Merge results from both sources and rank by combined score.

        Args:
            vector_results: Results from vector search.
            graph_results: Results from graph search.
            top_k: Maximum results to return.
            weights: Fusion weights (defaults to balanced 0.6/0.4).
        """
        if weights is None:
            weights = FusionWeights(vector=0.6, graph=0.4)

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
            name = vr.get("name", "")
            if name in seen:
                continue
            seen.add(name)

            vector_score = vr.get("score", 0.5)
            graph_score = graph_by_name.get(name, {}).get("score", 0.0)
            combined_score = weights.vector * vector_score + weights.graph * graph_score

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
                    "score": r.get("score", 0.5) * weights.graph,
                    "source": "graph",
                })

        # Sort by combined score descending
        merged.sort(key=lambda x: x.get("score", 0), reverse=True)
        logger.info("Hybrid search complete", results=len(merged[:top_k]))
        return merged[:top_k]

    def clear_cache(self) -> None:
        """Clear the search cache (e.g., after reindexing)."""
        self._cache.clear()
        logger.info("hybrid_search_cache_cleared")
