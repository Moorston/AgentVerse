"""Paper metadata extraction using PydanticAI."""

from pydantic_ai import Agent

from agentverse.extractor.base import BaseExtractor, ExtractionResult
from agentverse.extractor.llm.client import LLMClient
from agentverse.extractor.llm.prompts import PAPER_EXTRACTION_PROMPT
from agentverse.extractor.types import ExtractionRequest, PaperResult
from agentverse.shared.logging import get_logger

logger = get_logger(__name__)

SYSTEM_PROMPT = """You are an AI research paper analyzer. Extract structured metadata from paper text.

STRICT RULES:
1. ALL concept and framework names MUST be PascalCase (e.g., ChainOfThought, not chain-of-thought)
2. Do NOT include generic terms: "LLMs", "AI", "models", "data", "safety", "performance"
3. ONLY extract specific techniques, methods, frameworks, or architectures
4. Each concept MUST have a category

Valid categories: reasoning, planning, memory, tool_use, reflection, multi_agent, workflow, protocol, rag, prompt_engineering"""


class PaperExtractor(BaseExtractor):
    """Extract paper metadata and concepts from text."""

    def __init__(
        self,
        llm_client: LLMClient | None = None,
        agent: Agent[None, PaperResult] | None = None,
    ) -> None:
        if agent is not None:
            self._agent = agent
        else:
            client = llm_client or LLMClient()
            self._agent = client.get_agent(
                result_type=PaperResult,
                system_prompt=SYSTEM_PROMPT,
            )

    async def extract(self, request: ExtractionRequest) -> ExtractionResult:
        """Extract structured data from a paper."""
        text = request.get("text", "")
        prompt = PAPER_EXTRACTION_PROMPT.format(text=text)

        try:
            result = await self._agent.run(prompt)
            data = result.data
        except Exception as exc:
            logger.error("Paper extraction failed", error=str(exc))
            return ExtractionResult(source="paper")

        if not data or not data.title:
            return ExtractionResult(source="paper")

        # Build entities
        entities: list[dict[str, str]] = [
            {"type": "paper", "name": data.title, "properties": data.model_dump_json()},
        ]
        for concept in data.concepts:
            name = concept.name.strip()
            if name:
                entities.append({
                    "type": "concept",
                    "name": name,
                    "category": concept.category,
                })
        for framework in data.frameworks:
            fw = framework.strip()
            if fw:
                entities.append({"type": "framework", "name": fw})

        # Build PROPOSES relationships
        relationships = []
        for concept in data.concepts:
            name = concept.name.strip()
            if name:
                relationships.append({
                    "source": data.title,
                    "target": name,
                    "type": "PROPOSES",
                })

        return ExtractionResult(source="paper", entities=entities, relationships=relationships)
