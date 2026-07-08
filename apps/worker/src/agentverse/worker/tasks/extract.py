"""Extract tasks — dispatches to appropriate extractor via TaskIQ."""

from typing import Any

from agentverse.extractor.types import ExtractionRequest
from agentverse.shared.logging import get_logger
from agentverse.worker.broker import broker

logger = get_logger(__name__)


async def run_extract(text: str, source: str = "paper", **kwargs: Any) -> dict[str, Any]:
    """Execute an extraction task.

    Args:
        text: Text to extract from.
        source: Extractor type (paper, concept, relationship).

    Returns:
        Extraction result as dict with 'entities' and 'relationships'.
    """
    logger.info("Starting extraction", source=source, text_len=len(text))

    if source == "paper":
        from agentverse.extractor.extractors.paper import PaperExtractor
        extractor = PaperExtractor()
    elif source == "concept":
        from agentverse.extractor.extractors.concept import ConceptExtractor
        extractor = ConceptExtractor()
    elif source == "relationship":
        from agentverse.extractor.extractors.relationship import RelationshipExtractor
        extractor = RelationshipExtractor()
    else:
        logger.warning("Unknown extractor source", source=source)
        return {}

    request: ExtractionRequest = {"text": text, **kwargs}
    result = await extractor.extract(request)

    logger.info(
        "Extraction complete",
        source=source,
        entities=len(result.entities),
        relationships=len(result.relationships),
    )
    return {
        "entities": result.entities,
        "relationships": result.relationships,
    }


@broker.task(
    task_name="extract_text",
    retry_on_error=True,
    max_retries=3,
)
async def extract_text(text: str, source: str = "paper") -> dict[str, Any]:
    """TaskIQ task: extract structured data from text.

    Called by crawl tasks after successful crawl, or on-demand.
    Chains into index_text.kiq() on success.
    """
    logger.info("=== TaskIQ: extract_text starting ===", source=source)
    result = await run_extract(text, source=source)
    logger.info("=== TaskIQ: extract_text complete ===", source=source)
    return result
