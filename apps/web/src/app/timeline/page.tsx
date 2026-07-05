"use client";

import { useState, useCallback } from "react";

interface TimelineNode {
  name: string;
  description: string;
  category: string;
}

const EVOLUTION_CHAIN: TimelineNode[] = [
  { name: "Chain-of-Thought", description: "Step-by-step reasoning prompting", category: "reasoning" },
  { name: "ReAct", description: "Reasoning + Acting paradigm", category: "reasoning" },
  { name: "Plan-and-Execute", description: "Planning then execution architecture", category: "planning" },
  { name: "Reflexion", description: "Self-reflection and iterative improvement", category: "reflection" },
  { name: "Graph Agents", description: "Graph-structured agent workflows", category: "multi_agent" },
  { name: "Multi-Agent Societies", description: "Collaborative multi-agent systems", category: "multi_agent" },
];

const MEMORY_EVOLUTION: TimelineNode[] = [
  { name: "Short-term Memory", description: "Context window working memory", category: "memory" },
  { name: "Long-term Memory", description: "Persistent cross-session memory", category: "memory" },
  { name: "Episodic Memory", description: "Experience-based memory", category: "memory" },
  { name: "Semantic Memory", description: "Factual knowledge memory", category: "memory" },
  { name: "Graph Memory", description: "Knowledge graph-based memory", category: "memory" },
];

const CATEGORY_COLORS: Record<string, string> = {
  reasoning: "bg-blue-500",
  planning: "bg-green-500",
  reflection: "bg-purple-500",
  multi_agent: "bg-orange-500",
  memory: "bg-pink-500",
};

export default function TimelinePage() {
  const [activeChain, setActiveChain] = useState<"agent" | "memory">("agent");

  const chain = activeChain === "agent" ? EVOLUTION_CHAIN : MEMORY_EVOLUTION;

  return (
    <main className="min-h-screen bg-gray-50 p-8">
      <h1 className="text-3xl font-bold mb-2">Evolution Timeline</h1>
      <p className="text-gray-600 mb-8">Track how AI Agent architectures evolve over time</p>

      {/* Chain Selector */}
      <div className="flex gap-4 mb-8">
        <button
          onClick={() => setActiveChain("agent")}
          className={`px-4 py-2 rounded-lg ${
            activeChain === "agent" ? "bg-blue-600 text-white" : "bg-gray-100"
          }`}
        >
          Agent Evolution
        </button>
        <button
          onClick={() => setActiveChain("memory")}
          className={`px-4 py-2 rounded-lg ${
            activeChain === "memory" ? "bg-blue-600 text-white" : "bg-gray-100"
          }`}
        >
          Memory Evolution
        </button>
      </div>

      {/* Timeline */}
      <div className="relative">
        {/* Vertical line */}
        <div className="absolute left-6 top-0 bottom-0 w-0.5 bg-gray-300" />

        <div className="space-y-8">
          {chain.map((node, i) => (
            <div key={node.name} className="relative flex items-start gap-6">
              {/* Dot */}
              <div
                className={`w-12 h-12 rounded-full ${CATEGORY_COLORS[node.category] || "bg-gray-500"} flex items-center justify-center text-white font-bold text-lg z-10`}
              >
                {i + 1}
              </div>

              {/* Content */}
              <div className="flex-1 border rounded-lg p-4 bg-white hover:shadow-md transition">
                <h3 className="text-lg font-semibold mb-1">{node.name}</h3>
                <p className="text-gray-600 text-sm">{node.description}</p>
                <span className="inline-block mt-2 px-2 py-0.5 text-xs bg-gray-100 rounded">
                  {node.category}
                </span>
              </div>

              {/* Arrow */}
              {i < chain.length - 1 && (
                <div className="absolute left-6 bottom-0 translate-y-full text-gray-400 text-2xl">
                  ↓
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </main>
  );
}