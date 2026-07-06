import type { Framework } from "@/hooks/useFrameworks";

export const DEMO_FRAMEWORKS: Framework[] = [
  {
    name: "langchain-ai/langgraph",
    description: "State machine framework for complex agent workflows",
    stars: 8000,
    language: "Python",
    implements: ["ReAct", "Plan-and-Execute", "Tool Calling"],
  },
  {
    name: "crewAIInc/crewAI",
    description: "Multi-agent collaboration framework",
    stars: 15000,
    language: "Python",
    implements: ["Multi-Agent Societies", "Role-based Assignment"],
  },
  {
    name: "microsoft/autogen",
    description: "Microsoft multi-agent conversation framework",
    stars: 25000,
    language: "Python",
    implements: ["Multi-Agent Societies", "Human-in-the-loop"],
  },
  {
    name: "run-llama/llama_index",
    description: "Data framework for LLM applications with RAG focus",
    stars: 30000,
    language: "Python",
    implements: ["RAG", "GraphRAG", "Data Connectors"],
  },
  {
    name: "microsoft/semantic-kernel",
    description: "Microsoft enterprise AI orchestration SDK",
    stars: 20000,
    language: "C#",
    implements: ["Enterprise Integration", "Plugin Architecture"],
  },
  {
    name: "langgenius/dify",
    description: "Open-source LLM app development platform",
    stars: 40000,
    language: "Python",
    implements: ["Low-code", "Visual Workflow"],
  },
  {
    name: "mem0ai/mem0",
    description: "Production-ready long-term memory for AI agents",
    stars: 22000,
    language: "Python",
    implements: ["Long-term Memory", "Graph Memory"],
  },
  {
    name: "getzep/zep",
    description: "Temporal memory framework for conversational agents",
    stars: 3000,
    language: "Go",
    implements: ["Episodic Memory", "Temporal Reasoning"],
  },
  {
    name: "langchain-ai/langmem",
    description: "LangChain native memory components",
    stars: 1500,
    language: "Python",
    implements: ["Semantic Memory", "Procedural Memory"],
  },
];
