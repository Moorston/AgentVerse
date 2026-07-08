"""GraphRAG search endpoint -- with caching and hybrid retrieval."""

from fastapi import APIRouter, Depends, Query

from agentverse.api.core.cache import query_cache
from agentverse.api.core.context import AppContext, get_context
from agentverse.api.models.response import SearchResponse
from agentverse.shared.logging import get_logger

logger = get_logger(__name__)
router = APIRouter()


@router.get("/", response_model=SearchResponse)
async def search(
    q: str = Query("", description="Search query"),
    top_k: int = Query(10, ge=1, le=100),
    strategy: str = Query("hybrid", description="Search strategy: graph, vector, hybrid"),
    ctx: AppContext = Depends(get_context),
) -> SearchResponse:
    """Search the knowledge graph using GraphRAG.

    Strategies:
    - **graph**: Multi-hop graph traversal via Neo4j
    - **vector**: Semantic similarity via pgvector embeddings
    - **hybrid**: Combined vector + graph with fusion ranking

    Results are cached for 5 minutes.
    """
    if not q:
        return SearchResponse(query=q, results=[])

    # Check cache
    cache_key = f"search:{q}:{top_k}:{strategy}"
    cached = query_cache.get(cache_key)
    if cached is not None:
        logger.info("Cache hit", query=q)
        return SearchResponse(query=q, results=cached)

    try:
        engine = await ctx.get_engine()
        results = await engine.query(q, top_k=top_k, strategy=strategy)
        logger.info("GraphRAG search complete", query=q, strategy=strategy, results=len(results))

        # Cache results
        query_cache.set(cache_key, results)
        return SearchResponse(query=q, results=results)
    except Exception as exc:
        logger.error("GraphRAG search failed", query=q, error=str(exc))
        return await _fallback_search(q, top_k, ctx)


async def _fallback_search(q: str, top_k: int, ctx: AppContext) -> SearchResponse:
    """Fallback search using simple Neo4j queries."""
    try:
        repo = await ctx.get_repository()
        results = await repo.execute_raw(
            """
            MATCH (n)
            WHERE n.name CONTAINS $q OR n.description CONTAINS $q
            RETURN n.name AS name, n.description AS description, labels(n) AS types
            LIMIT $limit
            """,
            {"q": q, "limit": top_k},
        )
        search_results = [
            {
                "name": r["name"],
                "description": r.get("description", ""),
                "type": r["types"][0] if r["types"] else "Unknown",
                "score": 0.5,
                "match": "fallback",
            }
            for r in results
        ]
        return SearchResponse(query=q, results=search_results)
    except Exception as exc:
        logger.warning("Fallback search also failed", error=str(exc))
        return SearchResponse(query=q, results=[])
