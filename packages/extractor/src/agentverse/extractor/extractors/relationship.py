"""Relationship extraction using LLM."""

from agentverse.extractor.base import BaseExtractor, ExtractionResult
from agentverse.extractor.llm.client import LLMClient
from agentverse.extractor.llm.prompts import RELATIONSHIP_EXTRACTION_PROMPT
from agentverse.extractor.types import ExtractionRequest
from agentverse.shared.logging import get_logger

logger = get_logger(__name__)

VALID_RELATIONSHIP_TYPES = [
    "PROPOSES", "IMPLEMENTS", "EVOLVES_TO", "RELATED_TO",
    "DEPENDS_ON", "SUPPORTS", "USED_IN", "REFERENCES",
    "CITES", "EXTENDS", "INSPIRED_BY",
]

SYSTEM_PROMPT = f"""You are an AI research relationship analyst. Extract relationships between concepts.

STRICT RULES:
1. Valid relationship types: {', '.join(VALID_RELATIONSHIP_TYPES)}
2. source = the method/framework/technique that acts (the one proposing, implementing, or extending)
3. target = the entity being affected, supported, or extended
4. ALL concept names MUST be PascalCase (e.g., ChainOfThought, not chain-of-thought)
5. Do NOT include generic terms as source or target: "LLMs", "AI", "models", "data"
6. Do NOT reverse directions: "A extends B" means source=A, target=B

GOOD: source="ReAct", target="ChainOfThought", type="EXTENDS"
BAD: source="alignment training", target="LLMs", type="SUPPORTS"

Return valid JSON:
{{
  "relationships": [
    {{
      "source": "PascalCaseSourceName",
      "target": "PascalCaseTargetName",
      "type": "one of the valid types above",
      "evidence": "brief evidence from the text"
    }}
  ]
}}"""


class RelationshipExtractor(BaseExtractor):
    """Extract relationships between concepts."""

    def __init__(self, llm_client: LLMClient | None = None) -> None:
        self._client = llm_client or LLMClient()

    async def extract(self, request: ExtractionRequest) -> ExtractionResult:
        """Extract relationships from text."""
        text = request.get("text", "")
        prompt = RELATIONSHIP_EXTRACTION_PROMPT.format(text=text)

        try:
            data = await self._client.complete_json(
                prompt=prompt,
                system_prompt=SYSTEM_PROMPT,
            )
        except Exception as exc:
            logger.error("Relationship extraction failed", error=str(exc))
            return ExtractionResult(source="relationship")

        if not data:
            return ExtractionResult(source="relationship")

        relationships = []
        for rel in data.get("relationships", []):
            source = rel.get("source", "").strip()
            target = rel.get("target", "").strip()
            rel_type = rel.get("type", "RELATED_TO").upper()

            if not source or not target:
                continue
            if rel_type not in VALID_RELATIONSHIP_TYPES:
                rel_type = "RELATED_TO"

            relationships.append({
                "source": source,
                "target": target,
                "type": rel_type,
                "evidence": rel.get("evidence", ""),
            })

        return ExtractionResult(source="relationship", relationships=relationships)