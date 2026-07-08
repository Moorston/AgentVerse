"""Query router — classifies search queries and selects fusion weights.

Rule-based pattern matching, no LLM call, < 1ms latency.
"""

import re
from dataclasses import dataclass
from typing import ClassVar

from agentverse.shared.logging import get_logger

logger = get_logger(__name__)


@dataclass(frozen=True)
class FusionWeights:
    """Vector and graph weights for hybrid search fusion."""

    vector: float
    graph: float


class QueryRouter:
    """Classify queries as semantic, structural, or default.

    Structural queries (about relationships, dependencies, evolution)
    are routed to graph-dominant weights. Semantic queries (about
    definitions, explanations) are routed to vector-dominant weights.
    """

    # Patterns that indicate structural queries
    STRUCTURAL_PATTERNS: ClassVar[list[re.Pattern[str]]] = [
        re.compile(p, re.IGNORECASE)
        for p in [
            r"\bdepend(s|encies|ency)?\b",
            r"\bimplement(s|ed|ation)?\b",
            r"\bextend(s|ed|ion)?\b",
            r"\bevolv(e|es|ed|ution)\b",
            r"\brelat(ed|ions|ionship)\b",
            r"which\s+\w+\s+(use|support|depend)",
            r"what\s+\w+\s+(use|support|depend)",
            r"\b(use|uses|used)\s+by\b",
            r"\bsupport(s|ed)?\b",
            r"\bbuilt\s+(on|with|using)\b",
            r"\bbased\s+on\b",
            r"(child|parent|sub|super)\s*(class|type|concept)",
            r"\bconnect(ed|ion|ions)\s+to\b",
            r"\b(graph|tree|hierarchy)\b",
            r"(from|to|between)\s+\w+\s+(and|to)\s+\w+",
        ]
    ]

    # Patterns that indicate semantic queries
    SEMANTIC_PATTERNS: ClassVar[list[re.Pattern[str]]] = [
        re.compile(p, re.IGNORECASE)
        for p in [
            r"^what\s+is\b",
            r"^explain\b",
            r"^how\s+does\b",
            r"^how\s+to\b",
            r"^describe\b",
            r"^define\b",
            r"^meaning\s+of\b",
            r"^concept\s+of\b",
            r"overview",
            r"introduction",
            r"tutorial",
            r"guide",
        ]
    ]

    # Default weights
    WEIGHTS: ClassVar[dict[str, FusionWeights]] = {
        "semantic": FusionWeights(vector=0.8, graph=0.2),
        "structural": FusionWeights(vector=0.3, graph=0.7),
        "default": FusionWeights(vector=0.6, graph=0.4),
    }

    def classify(self, query: str) -> str:
        """Classify query intent.

        Args:
            query: Search query text.

        Returns:
            One of: "semantic", "structural", "default".
        """
        query_stripped = query.strip()
        if not query_stripped:
            return "default"

        # Check structural patterns first (more specific)
        structural_score = sum(
            1 for p in self.STRUCTURAL_PATTERNS if p.search(query_stripped)
        )
        semantic_score = sum(
            1 for p in self.SEMANTIC_PATTERNS if p.search(query_stripped)
        )

        if structural_score > 0 and structural_score >= semantic_score:
            logger.debug("query_classified", query=query_stripped[:50], type="structural")
            return "structural"
        if semantic_score > 0:
            logger.debug("query_classified", query=query_stripped[:50], type="semantic")
            return "default"  # Default weights already lean semantic (0.6/0.4)

        return "default"

    def weights(self, query: str) -> FusionWeights:
        """Get fusion weights for a query.

        Args:
            query: Search query text.

        Returns:
            FusionWeights with vector and graph components.
        """
        query_type = self.classify(query)
        return self.WEIGHTS[query_type]
