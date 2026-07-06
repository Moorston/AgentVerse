"""Prometheus-compatible metrics endpoint."""

from fastapi import APIRouter
from fastapi.responses import PlainTextResponse

from agentverse.api.core.metrics import get_metrics_text
from agentverse.shared.logging import get_logger

logger = get_logger(__name__)
router = APIRouter()


@router.get("/metrics", response_class=PlainTextResponse)
async def metrics() -> str:
    """Return Prometheus-compatible metrics.

    Delegates to core.metrics for counter storage and formatting.
    """
    return get_metrics_text()