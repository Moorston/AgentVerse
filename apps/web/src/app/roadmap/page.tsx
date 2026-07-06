"use client";

import { PhaseCard } from "@/components/roadmap/PhaseCard";
import type { ModuleStatus } from "@/components/roadmap/ModuleItem";

interface Module {
  name: string;
  status: ModuleStatus;
  description: string;
}

interface Phase {
  name: string;
  description: string;
  modules: Module[];
}

// Roadmap data derived from docs/EXECUTION_PLAN.md and docs/BUSINESS_MODULES.md
// Structured for easy migration to JSON/API loading later
const ROADMAP_PHASES: Phase[] = [
  {
    name: "Phase 0 — Toolchain & Standards",
    description: "Set up development tooling, change templates, and requirements clarification.",
    modules: [
      {
        name: "Trellis Specs Configuration",
        status: "completed" as ModuleStatus,
        description: "Configure Trellis specs for each workspace package so AI coding assistants auto-inject project context.",
      },
      {
        name: "OpenSpec Change Templates",
        status: "completed" as ModuleStatus,
        description: "Set up OpenSpec change process templates for proposal-to-archival lifecycle management.",
      },
      {
        name: "grill-me Requirements Clarification",
        status: "planned" as ModuleStatus,
        description: "Use grill-me skill to clarify core module requirements for crawler, extractor, retrieval, and API.",
      },
    ],
  },
  {
    name: "Phase 1 — Data Pipeline",
    description: "Build the foundational data layer: database schema, paper crawling, LLM extraction, and ontology normalization.",
    modules: [
      {
        name: "Neo4j Schema Initialization",
        status: "in_progress" as ModuleStatus,
        description: "Establish database constraints and indexes for 13 node types to ensure data consistency.",
      },
      {
        name: "ArXiv Paper Crawling",
        status: "in_progress" as ModuleStatus,
        description: "Automatically fetch AI Agent papers from arXiv REST API (cs.AI, cs.LG, cs.CL) with incremental crawling.",
      },
      {
        name: "LLM Concept Extraction Engine",
        status: "planned" as ModuleStatus,
        description: "Extract core concepts and relationships from paper abstracts using GPT-4o / Claude Sonnet.",
      },
      {
        name: "Ontology Normalization & Storage",
        status: "planned" as ModuleStatus,
        description: "Standardize crawled and extracted data into ontology instances and write to Neo4j.",
      },
    ],
  },
  {
    name: "Phase 2 — Retrieval & Services",
    description: "Implement hybrid retrieval, REST APIs, framework mapping, and memory framework data collection.",
    modules: [
      {
        name: "GraphRAG Hybrid Retrieval",
        status: "in_progress" as ModuleStatus,
        description: "Implement vector search + graph traversal + hybrid ranking for the GraphRAG engine using pgvector and Neo4j.",
      },
      {
        name: "Concept Browser API",
        status: "planned" as ModuleStatus,
        description: "REST API for concept CRUD and graph traversal queries with pagination and depth filtering.",
      },
      {
        name: "Framework Ecosystem Mapping",
        status: "planned" as ModuleStatus,
        description: "Crawl 9 major AI Agent frameworks from GitHub and build framework-to-concept capability maps.",
      },
      {
        name: "Memory Framework Data Collection",
        status: "planned" as ModuleStatus,
        description: "Collect memory framework data from 5+ Awesome repositories and build a memory-focused knowledge subgraph.",
      },
    ],
  },
  {
    name: "Phase 3 — Frontend & Automation",
    description: "Build interactive web visualizations, automated pipelines, and news ingestion.",
    modules: [
      {
        name: "Web Knowledge Graph Visualization",
        status: "planned" as ModuleStatus,
        description: "Interactive browser-based knowledge graph using Cytoscape.js with node expansion, search, and category filtering.",
      },
      {
        name: "Multi-Source Auto Knowledge Pipeline",
        status: "in_progress" as ModuleStatus,
        description: "Scheduled automation: crawl, extract, store, and index on a recurring basis with failure retry and task chaining.",
      },
      {
        name: "Industry News RSS Pipeline",
        status: "in_progress" as ModuleStatus,
        description: "Automated RSS ingestion from 7+ AI news sources with LLM-based concept extraction from articles.",
      },
      {
        name: "Agent Evolution Timeline",
        status: "planned" as ModuleStatus,
        description: "Track concept evolution paths such as Chain-of-Thought to ReAct to Reflexion with forward/backward traversal.",
      },
    ],
  },
  {
    name: "Phase 4 — Advanced Intelligence",
    description: "High-level features that require significant data accumulation across the knowledge graph.",
    modules: [
      {
        name: "AI Agent Search Engine",
        status: "planned" as ModuleStatus,
        description: "Natural language queries mapped to multi-hop graph retrieval with structured answers. Requires 1000+ graph nodes.",
      },
      {
        name: "Agent Recommendation System",
        status: "planned" as ModuleStatus,
        description: "Recommend framework combinations based on project requirements and framework capability matrices.",
      },
      {
        name: "Research Copilot",
        status: "planned" as ModuleStatus,
        description: "Academic assistant: concept explanation, frontier tracking, and literature review generation from the full knowledge base.",
      },
    ],
  },
];

export default function RoadmapPage() {
  return (
    <main className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold mb-2">AgentVerse Roadmap</h1>
        <p className="text-gray-600 mb-8">
          Development phases from toolchain setup through advanced AI features.
          {ROADMAP_PHASES.reduce(
            (acc, phase) => acc + phase.modules.filter((m) => m.status === "completed").length,
            0
          )}{" "}
          of{" "}
          {ROADMAP_PHASES.reduce((acc, phase) => acc + phase.modules.length, 0)}{" "}
          modules completed.
        </p>

        <div className="space-y-2">
          {ROADMAP_PHASES.map((phase) => (
            <PhaseCard key={phase.name} phase={phase} />
          ))}
        </div>
      </div>
    </main>
  );
}
