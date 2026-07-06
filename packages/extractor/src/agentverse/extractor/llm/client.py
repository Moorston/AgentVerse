"""LLM client factory — supports OpenAI and Claude with structured output."""

import json
from typing import Any

from agentverse.shared.config import Settings
from agentverse.shared.logging import get_logger

logger = get_logger(__name__)


class LLMClient:
    """Unified LLM client supporting OpenAI and Claude."""

    def __init__(self, provider: str = "openai", api_key: str = "", model: str = "", base_url: str = "") -> None:
        self._provider = provider
        self._base_url = base_url

        if not api_key or not model or not base_url:
            settings = Settings()
            self._api_key = api_key or settings.openai_api_key
            self._base_url = base_url or settings.openai_base_url
            self._model = model or settings.openai_model or self._default_model()
        else:
            self._api_key = api_key
            self._model = model or self._default_model()

    def _default_model(self) -> str:
        return "gpt-4o" if self._provider == "openai" else "claude-sonnet-4-20250514"

    async def complete(
        self,
        prompt: str,
        system_prompt: str = "",
        response_format: dict[str, Any] | None = None,
        temperature: float = 0.0,
        max_tokens: int = 2000,
    ) -> str:
        """Send a completion request to the LLM.

        Args:
            prompt: User prompt text.
            system_prompt: System prompt for context.
            response_format: JSON schema for structured output.
            temperature: Sampling temperature (0.0 = deterministic).
            max_tokens: Maximum tokens in response.
        """
        if self._provider == "openai":
            return await self._complete_openai(prompt, system_prompt, response_format, temperature, max_tokens)
        return await self._complete_anthropic(prompt, system_prompt, temperature, max_tokens)

    async def complete_json(
        self,
        prompt: str,
        system_prompt: str = "",
        schema: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Complete and parse JSON response."""
        response_format = {"type": "json_object"}
        if schema:
            response_format["schema"] = schema

        raw = await self.complete(
            prompt=prompt,
            system_prompt=system_prompt,
            response_format=response_format,
            temperature=0.0,
        )
        try:
            return json.loads(raw)
        except json.JSONDecodeError as exc:
            logger.error("Failed to parse LLM JSON response", error=str(exc), raw=raw[:200])
            return {}

    async def _complete_openai(
        self, prompt: str, system_prompt: str, response_format: dict | None, temperature: float, max_tokens: int
    ) -> str:
        """Call OpenAI API."""
        from openai import AsyncOpenAI

        client = AsyncOpenAI(api_key=self._api_key, base_url=self._base_url or None)
        messages: list[dict[str, str]] = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        kwargs: dict[str, Any] = {
            "model": self._model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        if response_format:
            kwargs["response_format"] = response_format

        response = await client.chat.completions.create(**kwargs)
        return response.choices[0].message.content or ""

    async def _complete_anthropic(
        self, prompt: str, system_prompt: str, temperature: float, max_tokens: int
    ) -> str:
        """Call Anthropic API."""
        from anthropic import AsyncAnthropic

        client = AsyncAnthropic(api_key=self._api_key)

        kwargs: dict[str, Any] = {
            "model": self._model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        if system_prompt:
            kwargs["system"] = system_prompt

        response = await client.messages.create(**kwargs)
        return response.content[0].text if response.content else ""