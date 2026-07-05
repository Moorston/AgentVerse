"""Paper metadata extraction using LLM."""

from agentverse.extractor.base import BaseExtractor, ExtractionResult
from agentverse.extractor.llm.client import LLMClient
from agentverse.extractor.llm.prompts import PAPER_EXTRACTION_PROMPT
from agentverse.shared.logging import get_logger

logger = get_logger(__name__)

SYSTEM_PROMPT = """You are an AI research paper analyzer. Extract structured metadata from paper text.
Return valid JSON with these fields:
{
  "title": "paper title",
  "authors": ["author1", "author2"],
  "abstract": "paper abstract",
  "concepts": ["concept1", "concept2"],
  "frameworks": ["framework1"],
  "contribution_type": "method|survey|benchmark|analysis"
}"""


class PaperExtractor(BaseExtractor):
    """Extract paper metadata and concepts from text."""

    def __init__(self, llm_client: LLMClient | None = None) -> None:
        self._client = llm_client or LLMClient()

    async def extract(self, text: str, **kwargs) -> ExtractionResult:
        """Extract structured data from a paper."""
        prompt = PAPER_EXTRACTION_PROMPT.format(text=text)

        try:
            data = await self._client.complete_json(
                prompt=prompt,
                system_prompt=SYSTEM_PROMPT,
            )
        except Exception as exc:
            logger.error("Paper extraction failed", error=str(exc))
            return ExtractionResult(source="paper")

        if not data:
            return ExtractionResult(source="paper")

        # Normalize concept names
        concepts = [c.strip() for c in data.get("concepts", []) if c.strip()]
        frameworks = [f.strip() for f in data.get("frameworks", []) if f.strip()]

        entities = [
            {"type": "paper", "name": data.get("title", ""), "properties": data},
        ]
        for concept in concepts:
            entities.append({"type": "concept", "name": concept, "category": "method"})
        for framework in frameworks:
            entities.append({"type": "framework", "name": framework})

        relationships = []
        for concept in concepts:
            relationships.append({
                "source": data.get("title", ""),
                "target": concept,
                "type": "PROPOSES",
            })

        return ExtractionResult(source="paper", entities=entities, relationships=relationships)