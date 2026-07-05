"""Tests for graph-core client (mocked)."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest


@pytest.mark.asyncio
async def test_graph_client_init():
    """GraphClient should initialize without connecting."""
    from agentverse.graph_core.client import GraphClient
    client = GraphClient()
    assert client._driver is None


@pytest.mark.asyncio
async def test_graph_client_health_check_no_driver():
    """health_check should return False when not connected."""
    from agentverse.graph_core.client import GraphClient
    client = GraphClient()
    result = await client.health_check()
    assert result is False


@pytest.mark.asyncio
async def test_graph_client_session_raises():
    """session() should raise when not connected."""
    from agentverse.graph_core.client import GraphClient
    client = GraphClient()
    with pytest.raises(RuntimeError, match="not connected"):
        client.session()
