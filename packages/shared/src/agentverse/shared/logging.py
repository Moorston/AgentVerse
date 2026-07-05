"""Structured logging setup using structlog.

Supports two modes:
  - Development: colored, human-readable console output
  - Production: JSON-formatted logs (one JSON object per line)

Controlled by AGENTVERSE_ENV environment variable:
  - "production" / "prod" → JSON renderer
  - anything else (default) → Console renderer
"""

import logging
import os
import sys
from typing import Any

import structlog


_ENV = os.getenv("AGENTVERSE_ENV", "development").lower()
_IS_PROD = _ENV in ("production", "prod")


# ─── Shared processors (run for every log entry) ──────────────────────

_SHARED_PROCESSORS: list[structlog.types.Processor] = [
    structlog.contextvars.merge_contextvars,
    structlog.stdlib.add_log_level,
    structlog.stdlib.add_logger_name,
    structlog.processors.TimeStamper(fmt="iso"),
    structlog.processors.StackInfoRenderer(),
    structlog.processors.UnicodeDecoder(),
]


# ─── Renderer selection ────────────────────────────────────────────────

def _get_renderer() -> structlog.types.Processor:
    """Return the appropriate renderer based on environment."""
    if _IS_PROD:
        return structlog.processors.JSONRenderer(ensure_ascii=False)
    return structlog.dev.ConsoleRenderer(colors=True)


# ─── Configuration ─────────────────────────────────────────────────────

def _configure() -> None:
    """Configure structlog and stdlib logging."""
    renderer = _get_renderer()

    structlog.configure(
        processors=[
            *_SHARED_PROCESSORS,
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    # Configure the stdlib root handler so structlog output actually reaches stderr
    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(
        structlog.stdlib.ProcessorFormatter(
            processors=[
                structlog.stdlib.ProcessorFormatter.remove_processors_meta,
                renderer,
            ],
            foreign_pre_chain=_SHARED_PROCESSORS,
        )
    )
    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.addHandler(handler)
    root_logger.setLevel(logging.DEBUG if not _IS_PROD else logging.INFO)


# Run configuration once at import time
_configure()


# ─── Public API ────────────────────────────────────────────────────────

def get_logger(name: str | None = None) -> structlog.stdlib.BoundLogger:
    """Return a structured logger instance.

    Usage:
        from agentverse.shared.logging import get_logger
        logger = get_logger(__name__)
        logger.info("started", port=8000)
    """
    return structlog.get_logger(name or __name__)



def bind_request_context(**kwargs: Any) -> None:
    """Bind context variables that appear on all subsequent log entries.

    Useful for request-scoped data (request_id, user_id, etc.).

    Usage:
        bind_request_context(request_id="abc-123", user_id="u1")
        logger.info("handling request")  # includes request_id and user_id
    """
    structlog.contextvars.bind_contextvars(**kwargs)



def clear_request_context() -> None:
    """Clear all bound context variables (call at end of request)."""
    structlog.contextvars.clear_contextvars()
