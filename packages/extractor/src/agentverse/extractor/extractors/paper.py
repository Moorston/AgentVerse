"""Paper metadata extraction using LLM."""

from agentverse.extractor.base import BaseExtractor, ExtractionResult
from agentverse.extractor.llm.client import LLMClient
from agentverse.extractor.llm.prompts import PAPER_EXTRACTION_PROMPT
from agentverse.extractor.types import ExtractionRequest
from agentverse.shared.logging import get_logger

logger = get_logger(__name__)

SYSTEM_PROMPT = """You are an AI research paper analyzer. Extract structured metadata from paper text.

STRICT RULES:
1. ALL concept and framework names MUST be PascalCase (e.g., ChainOfThought, not chain-of-thought)
2. Do NOT include generic terms: "LLMs", "AI", "models", "data", "safety", "performance"
3. ONLY extract specific techniques, methods, frameworks, or architectures
4. Each concept MUST have a category

Valid categories: reasoning, planning, memory, tool_use, reflection, multi_agent, workflow, protocol, rag, prompt_engineering

Return valid JSON with these fields:
{
  "title": "paper title",
  "authors": ["author1", "author2"],
  "abstract": "paper abstract",
  "concepts": [
    {"name": "PascalCaseName", "category": "one of the valid categories"}
  ],
  "frameworks": ["FrameworkName"],
  "contribution_type": "method|survey|benchmark|analysis|system"
}"""


class PaperExtractor(BaseExtractor):
    """Extract paper metadata and concepts from text."""

    def __init__(self, llm_client: LLMClient | None = None) -> None:
        self._client = llm_client or LLMClient()

    async def extract(self, request: ExtractionRequest) -> ExtractionResult:
        """Extract structured data from a paper."""
        text = request.get("text", "")
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

        # Normalize concept names — handle both string and object formats
        raw_concepts = data.get("concepts", [])
        concepts: list[dict[str, str]] = []
        for c in raw_concepts:
            if isinstance(c, dict):
                name = c.get("name", "").strip()
                cat = c.get("category", "method")
            else:
                name = str(c).strip()
                cat = "method"
            if name:
                concepts.append({"name": name, "category": cat})

        frameworks = [f.strip() for f in data.get("frameworks", []) if isinstance(f, str) and f.strip()]

        entities = [
            {"type": "paper", "name": data.get("title", ""), "properties": data},
        ]
        for concept in concepts:
            entities.append({"type": "concept", "name": concept["name"], "category": concept["category"]})
        for framework in frameworks:
            entities.append({"type": "framework", "name": framework})

        relationships = []
        for concept in concepts:
            relationships.append({
                "source": data.get("title", ""),
                "target": concept["name"],
                "type": "PROPOSES",
            })

        return ExtractionResult(source="paper", entities=entities, relationships=relationships)