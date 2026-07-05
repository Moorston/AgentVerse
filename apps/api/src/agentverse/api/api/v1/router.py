"""v1 API router aggregator."""

from fastapi import APIRouter

from agentverse.api.api.v1.health import router as health_router
from agentverse.api.api.v1.concepts import router as concepts_router
from agentverse.api.api.v1.search import router as search_router
from agentverse.api.api.v1.timeline import router as timeline_router
from agentverse.api.api.v1.frameworks import router as frameworks_router
from agentverse.api.api.v1.export import router as export_router
from agentverse.api.api.v1.batch import router as batch_router
from agentverse.api.api.v1.metrics import router as metrics_router
from agentverse.api.api.v1.keys import router as keys_router
from agentverse.api.api.v1.websocket import router as ws_router

api_v1_router = APIRouter()

api_v1_router.include_router(health_router, tags=["health"])
api_v1_router.include_router(concepts_router, prefix="/concepts", tags=["concepts"])
api_v1_router.include_router(search_router, prefix="/search", tags=["search"])
api_v1_router.include_router(timeline_router, prefix="/concepts", tags=["timeline"])
api_v1_router.include_router(frameworks_router, prefix="/frameworks", tags=["frameworks"])
api_v1_router.include_router(export_router, prefix="/export", tags=["export"])
api_v1_router.include_router(batch_router, prefix="/batch", tags=["batch"])
api_v1_router.include_router(metrics_router, tags=["metrics"])
api_v1_router.include_router(keys_router, prefix="/keys", tags=["keys"])
api_v1_router.include_router(ws_router, tags=["websocket"])