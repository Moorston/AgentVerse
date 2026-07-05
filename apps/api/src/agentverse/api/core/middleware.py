"""CORS, logging, error handling, rate limiting, and request timing middleware."""

import time
import traceback
from typing import Any

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from agentverse.api.core.rate_limiter import get_rate_limiter
from agentverse.shared.exceptions import AgentVerseError, DatabaseError, NotFoundError
from agentverse.shared.logging import get_logger

logger = get_logger(__name__)


def setup_middleware(app: FastAPI) -> None:
    """Configure middleware for the FastAPI app."""

    # CORS — must be first
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Rate limiting + request timing + logging
    @app.middleware("http")
    async def log_and_rate_limit(request: Request, call_next: Any) -> Any:
        """Log every request, enforce rate limits, and measure timing."""
        start = time.monotonic()
        method = request.method
        path = request.url.path

        # Skip rate limiting for docs and health
        if path in ("/docs", "/redoc", "/openapi.json", "/api/v1/health"):
            response = await call_next(request)
            elapsed = (time.monotonic() - start) * 1000
            response.headers["X-Response-Time"] = f"{elapsed:.2f}ms"
            return response

        # Rate limiting
        limiter = get_rate_limiter()
        allowed, rate_headers = limiter.is_allowed(request)
        if not allowed:
            logger.warning("Rate limit exceeded", method=method, path=path)
            return JSONResponse(
                status_code=429,
                content={"error": "Too Many Requests", "detail": "Rate limit exceeded", "status_code": 429},
                headers=rate_headers,
            )

        # Execute request
        try:
            response = await call_next(request)
        except Exception as exc:
            elapsed = (time.monotonic() - start) * 1000
            logger.error(
                "Request failed",
                method=method,
                path=path,
                elapsed_ms=round(elapsed, 2),
                error=str(exc),
            )
            # Return 500 JSON instead of re-raising — exception handlers
            # registered on the app do NOT intercept middleware exceptions.
            return JSONResponse(
                status_code=500,
                content={
                    "error": "Internal Server Error",
                    "detail": "An unexpected error occurred",
                    "status_code": 500,
                },
            )

        elapsed = (time.monotonic() - start) * 1000
        logger.info(
            "Request",
            method=method,
            path=path,
            status=response.status_code,
            elapsed_ms=round(elapsed, 2),
        )

        # Add headers
        response.headers["X-Response-Time"] = f"{elapsed:.2f}ms"
        for key, value in rate_headers.items():
            response.headers[key] = value

        # Security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Content-Security-Policy"] = "default-src 'self'"

        return response

    # Global exception handlers
    @app.exception_handler(NotFoundError)
    async def not_found_handler(request: Request, exc: NotFoundError) -> JSONResponse:
        return JSONResponse(
            status_code=404,
            content={"error": "Not Found", "detail": str(exc), "status_code": 404},
        )

    @app.exception_handler(DatabaseError)
    async def database_error_handler(request: Request, exc: DatabaseError) -> JSONResponse:
        logger.error("Database error", path=request.url.path, error=str(exc))
        return JSONResponse(
            status_code=503,
            content={"error": "Service Unavailable", "detail": "Database connection failed", "status_code": 503},
        )

    @app.exception_handler(AgentVerseError)
    async def agentverse_error_handler(request: Request, exc: AgentVerseError) -> JSONResponse:
        return JSONResponse(
            status_code=400,
            content={"error": "Bad Request", "detail": str(exc), "status_code": 400},
        )

    @app.exception_handler(Exception)
    async def generic_error_handler(request: Request, exc: Exception) -> JSONResponse:
        logger.error(
            "Unhandled exception",
            path=request.url.path,
            error=str(exc),
            traceback=traceback.format_exc()[:500],
        )
        return JSONResponse(
            status_code=500,
            content={"error": "Internal Server Error", "detail": "An unexpected error occurred", "status_code": 500},
        )