"""Extraction pipeline orchestration."""

from agentverse.extractor.base import ExtractionResult


class ExtractionPipeline:
    """Orchestrate multiple extractors."""

    def __init__(self) -> None:
        self._extractors: list = []

    def register(self, extractor) -> None:
        """Register an extractor."""
        self._extractors.append(extractor)

    async def run_all(self, text: str, **kwargs) -> list[ExtractionResult]:
        """Run all registered extractors."""
        results: list[ExtractionResult] = []
        for extractor in self._extractors:
            result = await extractor.extract(text, **kwargs)
            results.append(result)
        return results