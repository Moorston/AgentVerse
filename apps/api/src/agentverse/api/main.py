"""FastAPI application entry point with OpenAPI documentation."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from agentverse.api.api.v1.router import api_v1_router
from agentverse.api.core.events import lifespan
from agentverse.api.core.middleware import setup_middleware
from agentverse.api.core.versioning import versioning_middleware


def create_app() -> FastAPI:
    """Application factory with OpenAPI documentation."""
    app = FastAPI(
        title="AgentVerse API",
        version="0.1.0",
        description="""
## The Open Knowledge Graph for AI Agents

AgentVerse API provides access to a structured knowledge graph covering:

* **Concepts** — AI Agent concepts (reasoning, planning, memory, tool use)
* **Frameworks** — Agent development frameworks (LangGraph, CrewAI, AutoGen)
* **Papers** — Academic papers with extracted concepts and relationships
* **GraphRAG** — Hybrid retrieval combining vector search and graph traversal
* **Timeline** — Concept evolution tracking (Chain-of-Thought → ReAct → Reflexion)

### Data Sources
- arXiv (cs.AI, cs.LG, cs.CL)
- Semantic Scholar
- Papers with Code
- GitHub repositories
- RSS feeds

### Architecture
- **Neo4j** — Knowledge graph storage
- **pgvector** — Vector embeddings for semantic search
- **FastAPI** — Async REST API
- **GraphRAG** — Hybrid retrieval engine
        """,
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        openapi_tags=[
            {
                "name": "health",
                "description": "Service health and status checks",
            },
            {
                "name": "concepts",
                "description": "CRUD operations on knowledge graph concepts. Supports pagination, filtering, and neighbor traversal.",
            },
            {
                "name": "search",
                "description": "GraphRAG hybrid search combining vector similarity and graph traversal.",
            },
            {
                "name": "timeline",
                "description": "Concept evolution timeline and connection analysis.",
            },
        ],
    )

    setup_middleware(app)
    app.middleware("http")(versioning_middleware)
    app.include_router(api_v1_router, prefix="/api/v1")

    return app


app = create_app()