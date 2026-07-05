"""Pytest configuration and fixtures for API tests."""

from typing import Any
from unittest.mock import AsyncMock

import pytest
from fastapi import FastAPI

from agentverse.api.core.dependencies import get_repository
from agentverse.graph_core.models.query import Query
from agentverse.shared.logging import get_logger

logger = get_logger(__name__)


class MockRepository:
    """In-memory mock repository that doesn't require Neo4j."""

    def __init__(self) -> None:
        self._nodes: dict[str, dict[str, Any]] = {}
        self._queries: list[Query] = []

    async def run(self, query: Query) -> list[dict[str, Any]]:
        """Execute a mock query."""
        self._queries.append(query)
        stmt = query.statement.lower()

        # Health check
        if "return 1" in stmt or "return count" in stmt:
            return [{"total": 0}]

        # MATCH ... RETURN
        if "match" in stmt and "return" in stmt:
            return []

        return []

    async def create_node(self, labels: list[str], properties: dict[str, Any]) -> dict[str, Any]:
        """Create a mock node."""
        name = properties.get("name", "")
        self._nodes[name] = {"labels": labels, "properties": properties}
        return {"n": {"name": name, "labels": labels, **properties}}

    async def find_node(self, label: str, name: str) -> dict[str, Any] | None:
        """Find a mock node."""
        return self._nodes.get(name)

    async def find_nodes_by_label(self, label: str, limit: int = 100, offset: int = 0) -> list[dict[str, Any]]:
        """Find mock nodes by label."""
        return list(self._nodes.values())[offset:offset + limit]

    async def create_relationship(
        self, from_label: str, from_name: str, to_label: str, to_name: str,
        rel_type: str, properties: dict[str, Any] | None = None,
    ) -> bool:
        """Create a mock relationship."""
        return True

    async def delete_node(self, label: str, name: str) -> bool:
        """Delete a mock node."""
        return self._nodes.pop(name, None) is not None

    async def get_neighbors(self, label: str, name: str, depth: int = 1) -> dict[str, Any]:
        """Get mock neighbors."""
        return {"nodes": [], "relationships": []}

    async def execute(self, cql: str, parameters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        """Execute a mock Cypher query."""
        return await self.run(Query(cql, parameters or {}))


@pytest.fixture
def mock_repo() -> MockRepository:
    """Return a fresh MockRepository instance."""
    return MockRepository()


@pytest.fixture
def app_with_mock(mock_repo: MockRepository) -> FastAPI:
    """Return FastAPI app with mocked Neo4j dependency."""
    from agentverse.api.main import app

    async def _get_mock_repo() -> MockRepository:
        return mock_repo

    app.dependency_overrides[get_repository] = _get_mock_repo
    yield app
    app.dependency_overrides.clear()