"""Ontology normalizer — converts raw data into ontology instances."""

from agentverse.ontology.concepts.agent import AgentConcept
from agentverse.ontology.concepts.application import ApplicationConcept
from agentverse.ontology.concepts.company import CompanyConcept
from agentverse.ontology.concepts.framework import FrameworkConcept
from agentverse.ontology.concepts.industry_trend import IndustryTrendConcept
from agentverse.ontology.concepts.memory_framework import MemoryFrameworkConcept
from agentverse.ontology.concepts.memory_type import MemoryTypeConcept
from agentverse.ontology.concepts.news import NewsConcept
from agentverse.ontology.concepts.paper import PaperConcept
from agentverse.ontology.concepts.pattern import PatternConcept
from agentverse.ontology.concepts.product import ProductConcept
from agentverse.ontology.concepts.protocol import ProtocolConcept


def normalize_agent(data: dict) -> AgentConcept:
    """Convert raw agent data to an AgentConcept."""
    return AgentConcept(
        name=data.get("name", ""),
        description=data.get("description", ""),
    )


def normalize_framework(data: dict) -> FrameworkConcept:
    """Convert raw framework data to a FrameworkConcept."""
    return FrameworkConcept(
        name=data.get("name", ""),
        description=data.get("description", ""),
    )


def normalize_paper(data: dict) -> PaperConcept:
    """Convert raw paper data to a PaperConcept."""
    return PaperConcept(
        name=data.get("title", ""),
        doi=data.get("doi", ""),
        description=data.get("abstract", ""),
    )


def normalize_protocol(data: dict) -> ProtocolConcept:
    """Convert raw protocol data to a ProtocolConcept."""
    return ProtocolConcept(
        name=data.get("name", ""),
        description=data.get("description", ""),
    )


def normalize_news(data: dict) -> NewsConcept:
    """Convert raw news data to a NewsConcept."""
    return NewsConcept(
        name=data.get("title", ""),
        url=data.get("url", ""),
        source=data.get("source", ""),
        summary=data.get("summary", ""),
    )


def normalize_product(data: dict) -> ProductConcept:
    """Convert raw product data to a ProductConcept."""
    return ProductConcept(
        name=data.get("name", ""),
        company=data.get("company", ""),
        description=data.get("description", ""),
    )


def normalize_company(data: dict) -> CompanyConcept:
    """Convert raw company data to a CompanyConcept."""
    return CompanyConcept(
        name=data.get("name", ""),
        description=data.get("description", ""),
    )


def normalize_memory_type(data: dict) -> MemoryTypeConcept:
    """Convert raw memory type data to a MemoryTypeConcept."""
    return MemoryTypeConcept(
        name=data.get("name", ""),
        description=data.get("description", ""),
        memory_category=data.get("memory_category", ""),
    )


def normalize_memory_framework(data: dict) -> MemoryFrameworkConcept:
    """Convert raw memory framework data to a MemoryFrameworkConcept."""
    return MemoryFrameworkConcept(
        name=data.get("name", ""),
        description=data.get("description", ""),
        github_url=data.get("github_url", ""),
    )


def normalize_application(data: dict) -> ApplicationConcept:
    """Convert raw application data to an ApplicationConcept."""
    return ApplicationConcept(
        name=data.get("name", ""),
        description=data.get("description", ""),
        tech_stack=data.get("tech_stack", ""),
    )


def normalize_pattern(data: dict) -> PatternConcept:
    """Convert raw pattern data to a PatternConcept."""
    return PatternConcept(
        name=data.get("name", ""),
        description=data.get("description", ""),
    )


def normalize_industry_trend(data: dict) -> IndustryTrendConcept:
    """Convert raw trend data to an IndustryTrendConcept."""
    return IndustryTrendConcept(
        name=data.get("name", ""),
        description=data.get("description", ""),
        direction=data.get("direction", ""),
        strength=data.get("strength", ""),
    )