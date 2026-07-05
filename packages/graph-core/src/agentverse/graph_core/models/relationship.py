"""Relationship type enum and helpers."""

from enum import Enum


class RelationshipType(str, Enum):
    """Standard relationship types used across AgentVerse."""

    # Original 8 relationships
    PROPOSES = "PROPOSES"           # Paper -> Concept
    IMPLEMENTS = "IMPLEMENTS"       # Framework -> Concept
    EVOLVES_TO = "EVOLVES_TO"       # Concept -> Concept
    RELATED_TO = "RELATED_TO"       # * -> *
    DEPENDS_ON = "DEPENDS_ON"       # Framework -> Framework
    SUPPORTS = "SUPPORTS"           # Framework -> Concept
    USED_IN = "USED_IN"             # Concept -> Application
    REFERENCES = "REFERENCES"       # Paper -> Paper

    # New 16 relationships (Phase 1-3)
    CITES = "CITES"                           # Paper -> Paper
    EXTENDS = "EXTENDS"                       # Paper -> Paper
    INSPIRED_BY = "INSPIRED_BY"               # Concept -> Concept
    AUTHORED_BY = "AUTHORED_BY"               # Paper -> Author
    IMPLEMENTED_BY = "IMPLEMENTED_BY"         # Concept -> Framework
    ACHIEVES_SOTA = "ACHIEVES_SOTA"           # Paper -> Benchmark
    ANNOUNCED_BY = "ANNOUNCED_BY"             # News -> Company
    INVESTED_IN = "INVESTED_IN"               # Company -> Company
    COLLABORATES_WITH = "COLLABORATES_WITH"   # Framework -> Framework
    INTEGRATES_WITH = "INTEGRATES_WITH"       # Framework -> Framework
    SUPPORTS_PATTERN = "SUPPORTS_PATTERN"     # Framework -> Pattern
    IMPLEMENTS_MEMORY = "IMPLEMENTS_MEMORY"   # MemoryFramework -> MemoryType
    BENCHMARKED_ON = "BENCHMARKED_ON"         # MemoryFramework -> MemoryBenchmark
    FEATURED_IN_WEEK = "FEATURED_IN_WEEK"     # Paper -> TimePeriod
    TRENDING_IN = "TRENDING_IN"               # Paper -> TimePeriod
    UPDATED_TO = "UPDATED_TO"                 # Framework -> Version