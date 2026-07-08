"""Concept extraction using PydanticAI."""

from pydantic_ai import Agent

from agentverse.extractor.base import BaseExtractor, ExtractionResult
from agentverse.extractor.llm.client import LLMClient
from agentverse.extractor.llm.prompts import CONCEPT_EXTRACTION_PROMPT
from agentverse.extractor.types import ConceptResult, ExtractionRequest
from agentverse.shared.logging import get_logger

logger = get_logger(__name__)

SYSTEM_PROMPT = """You are an AI Agent domain expert. Extract key concepts from the text.

STRICT RULES:
1. ALL concept names MUST be PascalCase (e.g., ChainOfThought, Not chain-of-thought)
2. Do NOT extract generic terms: "LLMs", "AI", "models", "data", "safety", "performance", "results"
3. ONLY extract specific techniques, methods, frameworks, architectures, or well-known patterns
4. Each concept MUST have a one-sentence description and a category

Valid categories: reasoning, planning, memory, tool_use, reflection, multi_agent, workflow, protocol, rag, prompt_engineering

GOOD examples: ChainOfThought, ReAct, Reflexion, ToolCalling, GraphRAG, ReWOO, PlanAndExecute
BAD examples: LLMs, artificial intelligence, machine learning, large language model, the model, our method"""


class ConceptExtractor(BaseExtractor):
    """Extract AI Agent concepts from text."""

    def __init__(
        self,
        llm_client: LLMClient | None = None,
        agent: Agent[None, ConceptResult] | None = None,
    ) -> None:
        if agent is not None:
            self._agent = agent
        else:
            client = llm_client or LLMClient()
            self._agent = client.get_agent(
                result_type=ConceptResult,
                system_prompt=SYSTEM_PROMPT,
            )

    async def extract(self, request: ExtractionRequest) -> ExtractionResult:
        """Extract concepts and their relationships from text."""
        text = request.get("text", "")
        prompt = CONCEPT_EXTRACTION_PROMPT.format(text=text)

        try:
            result = await self._agent.run(prompt)
            data = result.data
        except Exception as exc:
            logger.error("Concept extraction failed", error=str(exc))
            return ExtractionResult(source="concept")

        if not data or not data.concepts:
            return ExtractionResult(source="concept")

        entities = []
        for concept in data.concepts:
            name = concept.name.strip()
            if not name:
                continue
            entities.append({
                "type": "concept",
                "name": name,
                "description": concept.description,
                "category": concept.category,
            })

        # Extract related_to relationships between co-occurring concepts
        relationships = []
        concept_names = [e["name"] for e in entities]
        for i, name_a in enumerate(concept_names):
            for name_b in concept_names[i + 1:]:
                relationships.append({
                    "source": name_a,
                    "target": name_b,
                    "type": "RELATED_TO",
                })

        return ExtractionResult(source="concept", entities=entities, relationships=relationships)
