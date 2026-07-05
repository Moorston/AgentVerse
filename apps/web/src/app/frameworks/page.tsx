"use client";

import { useEffect, useState } from "react";

interface Framework {
  name: string;
  description: string;
  stars: number;
  implements: string[];
}

export default function FrameworksPage() {
  const [frameworks, setFrameworks] = useState<Framework[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const res = await fetch("/api/v1/frameworks/?size=50");
        if (res.ok) {
          const data = await res.json();
          setFrameworks(data);
        }
      } catch {
        console.log("Using demo data");
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  // Demo data
  const demoFrameworks: Framework[] = [
    { name: "LangGraph", description: "State machine framework for complex agent workflows", stars: 8000, implements: ["ReAct", "Plan-and-Execute", "Tool Calling"] },
    { name: "CrewAI", description: "Multi-agent collaboration framework", stars: 15000, implements: ["Multi-Agent Societies", "Role-based Assignment"] },
    { name: "AutoGen", description: "Microsoft multi-agent conversation framework", stars: 25000, implements: ["Multi-Agent Societies", "Human-in-the-loop"] },
    { name: "LlamaIndex", description: "Data framework for LLM applications with RAG focus", stars: 30000, implements: ["RAG", "GraphRAG", "Data Connectors"] },
    { name: "Semantic Kernel", description: "Microsoft enterprise AI orchestration SDK", stars: 20000, implements: ["Enterprise Integration", "Plugin Architecture"] },
    { name: "Dify", description: "Open-source LLM app development platform", stars: 40000, implements: ["Low-code", "Visual Workflow"] },
    { name: "Mem0", description: "Production-ready long-term memory for AI agents", stars: 22000, implements: ["Long-term Memory", "Graph Memory"] },
    { name: "Zep", description: "Temporal memory framework for conversational agents", stars: 3000, implements: ["Episodic Memory", "Temporal Reasoning"] },
    { name: "LangMem", description: "LangChain native memory components", stars: 1500, implements: ["Semantic Memory", "Procedural Memory"] },
  ];

  const items = frameworks.length > 0 ? frameworks : demoFrameworks;

  return (
    <main className="min-h-screen bg-gray-50 p-8">
      <h1 className="text-3xl font-bold mb-2">Framework Ecosystem</h1>
      <p className="text-gray-600 mb-8">AI Agent development frameworks and their capabilities</p>

      {loading && <p className="text-gray-500">Loading...</p>}

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {items.map((fw) => (
          <div key={fw.name} className="border rounded-xl p-6 bg-white hover:shadow-lg transition">
            <div className="flex items-center justify-between mb-3">
              <h2 className="text-xl font-semibold">{fw.name}</h2>
              {fw.stars > 0 && (
                <span className="text-sm text-gray-500">⭐ {fw.stars.toLocaleString()}</span>
              )}
            </div>
            <p className="text-gray-600 text-sm mb-4">{fw.description}</p>
            <div className="flex flex-wrap gap-1">
              {fw.implements.map((impl) => (
                <span
                  key={impl}
                  className="px-2 py-0.5 text-xs bg-blue-50 text-blue-700 rounded"
                >
                  {impl}
                </span>
              ))}
            </div>
          </div>
        ))}
      </div>
    </main>
  );
}