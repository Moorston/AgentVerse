#!/usr/bin/env python3
"""Seed Neo4j with initial AI Agent ecosystem data."""

import asyncio

from agentverse.graph_core.client import GraphClient
from agentverse.graph_core.repository.base import BaseRepository
from agentverse.shared.config import Settings
from agentverse.shared.logging import get_logger

logger = get_logger(__name__)

# Seed concepts: AI Agent evolution chain
SEED_CONCEPTS = [
    # Reasoning chain
    {"name": "Chain-of-Thought", "description": "Step-by-step reasoning prompting technique", "category": "reasoning"},
    {"name": "ReAct", "description": "Reasoning + Acting paradigm combining thought and tool use", "category": "reasoning"},
    {"name": "Reflexion", "description": "Self-reflection and iterative improvement framework", "category": "reflection"},
    {"name": "Plan-and-Execute", "description": "Planning phase followed by execution phase architecture", "category": "planning"},
    {"name": "Graph Agents", "description": "Agent architectures based on graph-structured workflows", "category": "multi_agent"},
    {"name": "Multi-Agent Societies", "description": "Collaborative multi-agent systems with role specialization", "category": "multi_agent"},
    # Memory concepts
    {"name": "Short-term Memory", "description": "Context window and working memory for current task", "category": "memory"},
    {"name": "Long-term Memory", "description": "Persistent memory across sessions and tasks", "category": "memory"},
    {"name": "Episodic Memory", "description": "Memory of specific past experiences and interactions", "category": "memory"},
    {"name": "Semantic Memory", "description": "Factual knowledge and concept relationships", "category": "memory"},
    {"name": "Procedural Memory", "description": "Memory of how to perform tasks and procedures", "category": "memory"},
    {"name": "Graph Memory", "description": "Knowledge graph-based memory structure", "category": "memory"},
    # Tool and protocol concepts
    {"name": "Tool Calling", "description": "Ability to invoke external tools and APIs", "category": "tool_use"},
    {"name": "Function Calling", "description": "Structured function invocation by LLMs", "category": "tool_use"},
    {"name": "MCP", "description": "Model Context Protocol for tool and resource access", "category": "protocol"},
    {"name": "A2A", "description": "Agent-to-Agent communication protocol", "category": "protocol"},
    # RAG concepts
    {"name": "RAG", "description": "Retrieval-Augmented Generation for knowledge grounding", "category": "rag"},
    {"name": "GraphRAG", "description": "Graph-based retrieval combining vector search and graph traversal", "category": "rag"},
    # Workflow concepts
    {"name": "LangGraph", "description": "State machine framework for agent workflows", "category": "workflow"},
    {"name": "CrewAI", "description": "Multi-agent collaboration framework with role-based assignment", "category": "workflow"},
]

# Seed frameworks
SEED_FRAMEWORKS = [
    {"name": "LangGraph", "description": "State machine framework for complex agent workflows", "category": "framework"},
    {"name": "CrewAI", "description": "Multi-agent collaboration framework", "category": "framework"},
    {"name": "AutoGen", "description": "Microsoft multi-agent conversation framework", "category": "framework"},
    {"name": "LlamaIndex", "description": "Data framework for LLM applications with RAG focus", "category": "framework"},
    {"name": "Semantic Kernel", "description": "Microsoft enterprise AI orchestration SDK", "category": "framework"},
    {"name": "Dify", "description": "Open-source LLM app development platform", "category": "framework"},
    {"name": "Mem0", "description": "Production-ready long-term memory for AI agents", "category": "framework"},
    {"name": "Zep", "description": "Temporal memory framework for conversational agents", "category": "framework"},
    {"name": "LangMem", "description": "LangChain native memory components for agents", "category": "framework"},
]

# Seed relationships
SEED_RELATIONSHIPS = [
    # Evolution chain
    {"from_label": "Concept", "from_name": "Chain-of-Thought", "to_label": "Concept", "to_name": "ReAct", "type": "EVOLVES_TO"},
    {"from_label": "Concept", "from_name": "ReAct", "to_label": "Concept", "to_name": "Reflexion", "type": "EVOLVES_TO"},
    {"from_label": "Concept", "from_name": "ReAct", "to_label": "Concept", "to_name": "Plan-and-Execute", "type": "EVOLVES_TO"},
    {"from_label": "Concept", "from_name": "Reflexion", "to_label": "Concept", "to_name": "Graph Agents", "type": "EVOLVES_TO"},
    {"from_label": "Concept", "from_name": "Graph Agents", "to_label": "Concept", "to_name": "Multi-Agent Societies", "type": "EVOLVES_TO"},
    # Framework implementations
    {"from_label": "Concept", "from_name": "LangGraph", "to_label": "Concept", "to_name": "ReAct", "type": "IMPLEMENTS"},
    {"from_label": "Concept", "from_name": "LangGraph", "to_label": "Concept", "to_name": "Plan-and-Execute", "type": "IMPLEMENTS"},
    {"from_label": "Concept", "from_name": "CrewAI", "to_label": "Concept", "to_name": "Multi-Agent Societies", "type": "IMPLEMENTS"},
    {"from_label": "Concept", "from_name": "AutoGen", "to_label": "Concept", "to_name": "Multi-Agent Societies", "type": "IMPLEMENTS"},
    {"from_label": "Concept", "from_name": "LlamaIndex", "to_label": "Concept", "to_name": "RAG", "type": "IMPLEMENTS"},
    {"from_label": "Concept", "from_name": "Mem0", "to_label": "Concept", "to_name": "Long-term Memory", "type": "IMPLEMENTS"},
    {"from_label": "Concept", "from_name": "Mem0", "to_label": "Concept", "to_name": "Graph Memory", "type": "IMPLEMENTS"},
    {"from_label": "Concept", "from_name": "Zep", "to_label": "Concept", "to_name": "Episodic Memory", "type": "IMPLEMENTS"},
    {"from_label": "Concept", "from_name": "LangMem", "to_label": "Concept", "to_name": "Semantic Memory", "type": "IMPLEMENTS"},
    # Tool relationships
    {"from_label": "Concept", "from_name": "ReAct", "to_label": "Concept", "to_name": "Tool Calling", "type": "RELATED_TO"},
    {"from_label": "Concept", "from_name": "MCP", "to_label": "Concept", "to_name": "Tool Calling", "type": "RELATED_TO"},
    {"from_label": "Concept", "from_name": "A2A", "to_label": "Concept", "to_name": "Multi-Agent Societies", "type": "RELATED_TO"},
    # RAG relationships
    {"from_label": "Concept", "from_name": "GraphRAG", "to_label": "Concept", "to_name": "RAG", "type": "EXTENDS"},
    {"from_label": "Concept", "from_name": "GraphRAG", "to_label": "Concept", "to_name": "Graph Memory", "type": "RELATED_TO"},
    # Memory relationships
    {"from_label": "Concept", "from_name": "Graph Memory", "to_label": "Concept", "to_name": "Semantic Memory", "type": "RELATED_TO"},
    {"from_label": "Concept", "from_name": "Episodic Memory", "to_label": "Concept", "to_name": "Short-term Memory", "type": "RELATED_TO"},
    {"from_label": "Concept", "from_name": "Long-term Memory", "to_label": "Concept", "to_name": "Semantic Memory", "type": "RELATED_TO"},
    {"from_label": "Concept", "from_name": "Long-term Memory", "to_label": "Concept", "to_name": "Procedural Memory", "type": "RELATED_TO"},
]


async def main() -> None:
    """Seed Neo4j with initial data."""
    settings = Settings()
    client = GraphClient(settings)

    print(f"Connecting to Neo4j at {settings.neo4j_uri}...")
    await client.connect()

    if not await client.health_check():
        print("ERROR: Cannot connect to Neo4j. Run: docker compose up -d neo4j")
        return

    repo = BaseRepository(client)

    # Seed concepts
    print(f"\nCreating {len(SEED_CONCEPTS)} concepts...")
    for i, concept in enumerate(SEED_CONCEPTS, 1):
        await repo.create_node(["Concept"], concept)
        print(f"  [{i}/{len(SEED_CONCEPTS)}] {concept['name']}")

    # Seed frameworks
    print(f"\nCreating {len(SEED_FRAMEWORKS)} frameworks...")
    for i, fw in enumerate(SEED_FRAMEWORKS, 1):
        await repo.create_node(["Framework"], fw)
        print(f"  [{i}/{len(SEED_FRAMEWORKS)}] {fw['name']}")

    # Seed relationships
    print(f"\nCreating {len(SEED_RELATIONSHIPS)} relationships...")
    for i, rel in enumerate(SEED_RELATIONSHIPS, 1):
        await repo.create_relationship(
            rel["from_label"], rel["from_name"],
            rel["to_label"], rel["to_name"],
            rel["type"],
        )
        print(f"  [{i}/{len(SEED_RELATIONSHIPS)}] {rel['from_name']} --{rel['type']}--> {rel['to_name']}")

    # Verify
    node_count = await client.node_count()
    rel_count = await client.relationship_count()
    print(f"\nSeed complete!")
    print(f"  Total nodes: {node_count}")
    print(f"  Total relationships: {rel_count}")

    await client.close()


if __name__ == "__main__":
    asyncio.run(main())