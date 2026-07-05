"""API key management endpoints."""

from fastapi import APIRouter, HTTPException, Header

from agentverse.api.core.key_management import (
    generate_api_key,
    revoke_api_key,
    list_api_keys,
)
from agentverse.shared.logging import get_logger

logger = get_logger(__name__)
router = APIRouter()


@router.post("/keys")
async def create_api_key(
    name: str = "",
    role: str = "user",
    authorization: str = Header(default=""),
) -> dict:
    """Generate a new API key."""
    key = generate_api_key(name=name, role=role)
    return {"key": key, "name": name, "role": role}


@router.delete("/keys/{key}")
async def delete_api_key(
    key: str,
    authorization: str = Header(default=""),
) -> dict:
    """Revoke an API key."""
    if revoke_api_key(key):
        return {"status": "revoked"}
    raise HTTPException(status_code=404, detail="Key not found")


@router.get("/keys")
async def get_api_keys(
    authorization: str = Header(default=""),
) -> list[dict]:
    """List all API keys (without exposing the keys themselves)."""
    return list_api_keys()