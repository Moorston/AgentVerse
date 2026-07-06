"""FastAPI dependency injection -- delegates to AppContext."""

from __future__ import annotations

from fastapi import Request

from agentverse.api.core.context import AppContext, get_context
from agentverse.graph_core.client import GraphClient
from agentverse.graph_core.repository.base import BaseRepository
from agentverse.graphrag.engine import GraphRAGEngine
from agentverse.shared.config import Settings
from agentverse.shared.logging import get_logger

logger = get_logger(__name__)


def get_settings() -> Settings:
    """Return application settings."""
    return Settings()


async def get_graph_client(request: Request) -> GraphClient:
    """Return a connected GraphClient via AppContext."""
    ctx: AppContext = request.app.state.context
    return await ctx.get_client()


async def get_repository(request: Request) -> BaseRepository:
    """Return a BaseRepository via AppContext."""
    ctx: AppContext = request.app.state.context
    return await ctx.get_repository()


async def get_graphrag_engine(request: Request) -> GraphRAGEngine:
    """Return a GraphRAGEngine via AppContext."""
    ctx: AppContext = request.app.state.context
    return await ctx.get_engine()


async def close_connections() -> None:
    """Close all database connections (no-op when context manages lifecycle)."""
    logger.info("close_connections called -- lifecycle is managed by AppContext")
