"""Extract task — dispatches to appropriate extractor."""

from typing import Any

from agentverse.shared.logging import get_logger

logger = get_logger(__name__)


async def run_extract(text: str, source: str = "paper", **kwargs) -> dict[str, Any]:
    """Execute an extraction task.

    Args:
        text: Text to extract from.
        source: Extractor type (paper, concept, relationship).

    Returns:
        Extraction result as dict.
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

    result = await extractor.extract(text, **kwargs)

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