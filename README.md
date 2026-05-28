# AgentVerse

> The Open Knowledge Graph for AI Agents, GraphRAG, MCP and Multi-Agent Systems.

AgentVerse is an open-source knowledge infrastructure project for the AI Agent ecosystem.

It combines:

* Knowledge Graphs
* GraphRAG
* Agent Ontology
* Paper Intelligence
* Framework Relationships
* MCP / A2A Protocol Mapping
* Evolution Timeline Analysis

into a unified AI-native knowledge system.

---

# Vision

The AI Agent ecosystem is evolving extremely fast.

New concepts, frameworks, protocols, architectures, and research papers emerge every day:

* ReAct
* Reflexion
* GraphRAG
* MCP
* A2A
* LangGraph
* CrewAI
* AutoGen
* DSPy
* Multi-Agent Systems

However, the knowledge is fragmented across:

* Papers
* GitHub repositories
* Blogs
* Framework docs
* Conference talks
* Social media

AgentVerse aims to build:

> A structured, queryable, evolving knowledge graph for the entire AI Agent ecosystem.

---

# Core Features

## AI Agent Ontology

Structured ontology covering:

* Reasoning
* Planning
* Memory
* Tool Use
* Reflection
* Multi-Agent
* Workflow Runtime
* MCP / A2A
* RAG / GraphRAG
* Prompt Engineering

---

## Knowledge Graph

Powered by Neo4j.

Relationships include:

* PROPOSES
* IMPLEMENTS
* EVOLVES_TO
* RELATED_TO
* DEPENDS_ON
* SUPPORTS
* USED_IN

Example:

```text
ReAct
 ├── proposed_by -> Paper
 ├── implemented_by -> LangGraph
 ├── evolves_to -> Reflexion
 ├── related_to -> Tool Calling
 └── used_in -> Research Agent
```

---

## GraphRAG

Hybrid retrieval combining:

* Vector Search
* Knowledge Graph Traversal
* Relationship-aware Retrieval
* Multi-hop Reasoning

---

## Agent Evolution Timeline

Track how AI Agent architectures evolve:

```text
Chain-of-Thought
    ↓
ReAct
    ↓
Plan-and-Execute
    ↓
Reflexion
    ↓
Graph Agents
    ↓
Multi-Agent Societies
```

---

## Framework Ecosystem Mapping

Visualize relationships between:

* LangChain
* LangGraph
* AutoGen
* CrewAI
* DSPy
* LlamaIndex
* Haystack

and the concepts they implement.

---

## MCP & A2A Protocol Graph

Explore emerging agent communication protocols:

* MCP
* A2A
* OpenAPI
* Function Calling
* Tool Registry
* Agent Runtime

---

# Architecture

```text
                ┌─────────────────────┐
                │ Source Crawlers     │
                └─────────┬───────────┘
                          │
               ┌──────────▼──────────┐
               │ LLM Extractor       │
               └──────────┬──────────┘
                          │
             ┌────────────▼────────────┐
             │ Ontology Normalizer     │
             └────────────┬────────────┘
                          │
               ┌──────────▼───────────┐
               │ Neo4j Knowledge Graph│
               └──────────┬───────────┘
                          │
                ┌─────────▼──────────┐
                │ GraphRAG Engine    │
                └─────────┬──────────┘
                          │
                   ┌──────▼──────┐
                   │ API Gateway │
                   └──────┬──────┘
                          │
                 ┌────────▼────────┐
                 │ Next.js UI      │
                 └─────────────────┘
```

---

# Tech Stack

## Backend

* FastAPI
* Python
* LangGraph
* Neo4j Driver

## Database

* Neo4j
* PostgreSQL + pgvector

## Frontend

* Next.js
* React
* Cytoscape.js
* React Flow

## AI Stack

* OpenAI
* Claude
* DeepSeek
* Embedding Models

---

# Repository Structure

```text
agentverse/
├── apps/
│   ├── api/
│   ├── web/
│   └── worker/
│
├── packages/
│   ├── ontology/
│   ├── graphrag/
│   ├── extractor/
│   ├── crawler/
│   ├── graph-core/
│   └── shared/
│
├── datasets/
├── docs/
├── examples/
├── scripts/
└── docker/
```

---

# Quick Start

## Clone Repository

```bash
git clone https://github.com/your-org/agentverse.git
cd agentverse
```

---

## Start Services

```bash
docker compose up -d
```

---

## Open UI

```text
http://localhost:3000
```

---

# Example Queries

## Query Concept Evolution

```cypher
MATCH path=(c:Concept {name:"ReAct"})
-[:EVOLVES_TO*1..5]->
(next)
RETURN path
```

---

## Query Framework Capabilities

```cypher
MATCH (f:Framework {name:"LangGraph"})
-[:IMPLEMENTS]->(c)
RETURN c.name
```

---

# Roadmap

## Phase 1

* [x] Core Ontology
* [x] Neo4j Schema
* [ ] Paper Extraction
* [ ] Concept Graph

## Phase 2

* [ ] Framework Mapping
* [ ] GraphRAG
* [ ] Relationship Explorer

## Phase 3

* [ ] Agent Evolution Engine
* [ ] Auto Knowledge Extraction
* [ ] Multi-Agent Knowledge Graph

## Phase 4

* [ ] AI Agent Search Engine
* [ ] Agent Recommendation System
* [ ] Research Copilot

---

# Long-term Goals

AgentVerse aims to become:

> The open knowledge operating system for the AI Agent era.

---

# Contributing

We welcome contributions from:

* AI Researchers
* Agent Framework Developers
* GraphRAG Engineers
* Knowledge Graph Experts
* Open Source Contributors

Please read:

```text
docs/CONTRIBUTING.md
```

---

# License

Apache License 2.0

---

# Inspirations

* Neo4j
* LangGraph
* GraphRAG
* LlamaIndex
* Papers With Code
* Wikipedia

---

# Star History

If you find this project useful, please consider giving it a star.

It helps the project grow and reach more contributors.

---

# Community

Coming soon:

* Discord
* Documentation Site
* Public Graph Explorer
* AgentVerse Cloud

---

# Motto

> Understand the evolving intelligence ecosystem.

