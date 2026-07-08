"""WebSocket endpoint for real-time graph updates."""

import asyncio
import json
from typing import Any

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query

from agentverse.api.core.key_management import validate_api_key
from agentverse.shared.logging import get_logger

from agentverse.shared.logging import get_logger

logger = get_logger(__name__)
router = APIRouter()


class ConnectionManager:
    """Manage WebSocket connections."""

    def __init__(self) -> None:
        self._connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket) -> None:
        """Accept a new WebSocket connection."""
        await websocket.accept()
        self._connections.append(websocket)
        logger.info("WebSocket connected", total=len(self._connections))

    def disconnect(self, websocket: WebSocket) -> None:
        """Remove a disconnected WebSocket safely."""
        try:
            self._connections.remove(websocket)
            logger.info("WebSocket disconnected", total=len(self._connections))
        except ValueError:
            logger.warning("WebSocket disconnect: connection not found")

    async def broadcast(self, message: dict[str, Any]) -> None:
        """Broadcast a message to all connected clients."""
        data = json.dumps(message)
        disconnected: list[WebSocket] = []
        for conn in self._connections:
            try:
                await conn.send_text(data)
            except Exception:
                disconnected.append(conn)
        for conn in disconnected:
            self._connections.remove(conn)


# Global connection manager
manager = ConnectionManager()


@router.websocket("/ws/graph")
async def graph_websocket(
    websocket: WebSocket,
    token: str = Query(""),
) -> None:
    """WebSocket endpoint for real-time graph updates.

    Requires a valid API key as ``token`` query parameter.
    Messages sent to client:
    - {"type": "node_created", "data": {...}}
    - {"type": "node_deleted", "data": {...}}
    - {"type": "relationship_created", "data": {...}}
    - {"type": "stats_update", "data": {"nodes": N, "relationships": M}}

    Messages received from client:
    - {"type": "subscribe", "labels": ["Concept", "Framework"]}
    - {"type": "ping"}
    """
    # Authenticate before accepting
    if not token:
        await websocket.close(code=4001, reason="Missing authentication token")
        return
    valid, _ = validate_api_key(token)
    if not valid:
        await websocket.close(code=4001, reason="Invalid authentication token")
        return

    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
                msg_type = message.get("type", "")

                if msg_type == "ping":
                    await websocket.send_text(json.dumps({"type": "pong"}))
                elif msg_type == "subscribe":
                    labels = message.get("labels", [])
                    await websocket.send_text(json.dumps({
                        "type": "subscribed",
                        "labels": labels,
                    }))
                    logger.info("WebSocket subscribed", labels=labels)
            except json.JSONDecodeError:
                await websocket.send_text(json.dumps({"type": "error", "message": "Invalid JSON"}))
    except WebSocketDisconnect:
        manager.disconnect(websocket)


async def notify_node_created(name: str, label: str) -> None:
    """Notify all clients of a new node."""
    await manager.broadcast({
        "type": "node_created",
        "data": {"name": name, "label": label},
    })


async def notify_stats_update(nodes: int, relationships: int) -> None:
    """Notify all clients of updated stats."""
    await manager.broadcast({
        "type": "stats_update",
        "data": {"nodes": nodes, "relationships": relationships},
    })