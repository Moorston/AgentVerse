"""LLM client factory — creates PydanticAI Agents for typed extraction."""

from typing import TypeVar

from pydantic import BaseModel
from pydantic_ai import Agent

from agentverse.shared.config import Settings
from agentverse.shared.logging import get_logger

logger = get_logger(__name__)

T = TypeVar("T", bound=BaseModel)


class LLMClient:
    """Factory for creating PydanticAI Agent instances.

    Centralises provider selection and default configuration.
    Individual extractors own their ``result_type`` and prompt logic.
    """

    def __init__(self, settings: Settings | None = None) -> None:
        self._settings = settings or Settings()

    def get_agent(
        self,
        result_type: type[T],
        system_prompt: str,
        retries: int = 3,
    ) -> Agent[None, T]:
        """Create a PydanticAI Agent with the configured provider.

        Args:
            result_type: Pydantic model for structured output.
            system_prompt: System prompt for the agent.
            retries: Number of retries on transient failures.

        Returns:
            Configured PydanticAI Agent instance.
        """
        model = self._resolve_model()
        logger.info("Creating agent", model=model, result_type=result_type.__name__)
        return Agent(
            model,
            result_type=result_type,
            system_prompt=system_prompt,
            retries=retries,
        )

    def _resolve_model(self) -> str:
        """Select model string based on available API keys."""
        if self._settings.openai_api_key:
            return f"openai:{self._settings.openai_model}"
        if self._settings.anthropic_api_key:
            return f"anthropic:{self._settings.anthropic_model}"
        # Default to OpenAI (will fail at runtime if no key, but keeps import safe)
        return f"openai:{self._settings.openai_model}"


# ---------------------------------------------------------------------------
# Backward-compatible alias for tests and external callers
# ---------------------------------------------------------------------------


def create_client(
    provider: str = "openai",
    api_key: str = "",
    model: str = "",
    base_url: str = "",
) -> LLMClient:
    """Create an LLMClient with optional overrides.

    Kept for backward compatibility. Prefer ``LLMClient(settings=...)``.
    """
    settings = Settings()
    if api_key:
        if provider == "openai":
            settings = settings.model_copy(update={"openai_api_key": api_key})
        else:
            settings = settings.model_copy(update={"anthropic_api_key": api_key})
    if model:
        if provider == "openai":
            settings = settings.model_copy(update={"openai_model": model})
        else:
            settings = settings.model_copy(update={"anthropic_model": model})
    return LLMClient(settings=settings)
