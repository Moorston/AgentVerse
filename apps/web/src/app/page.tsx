"use client";

import { useState, useEffect } from "react";
import Link from "next/link";

const FEATURES = [
  {
    title: "Knowledge Graph",
    description: "Explore AI Agent concepts, frameworks, and their relationships",
    href: "/graph",
    icon: "🔮",
    color: "border-blue-200 hover:border-blue-400",
  },
  {
    title: "GraphRAG Search",
    description: "Hybrid retrieval combining vector search and graph traversal",
    href: "/search",
    icon: "🔍",
    color: "border-green-200 hover:border-green-400",
  },
  {
    title: "Framework Ecosystem",
    description: "Map of AI Agent frameworks and their capabilities",
    href: "/frameworks",
    icon: "🧩",
    color: "border-purple-200 hover:border-purple-400",
  },
  {
    title: "Evolution Timeline",
    description: "Track how AI Agent architectures evolve over time",
    href: "/timeline",
    icon: "📈",
    color: "border-orange-200 hover:border-orange-400",
  },
];

const STATS = [
  { value: "13", label: "Node Types", color: "text-blue-600" },
  { value: "24", label: "Relationship Types", color: "text-green-600" },
  { value: "6", label: "Data Sources", color: "text-purple-600" },
  { value: "11", label: "API Endpoints", color: "text-orange-600" },
];

interface GraphNode {
  id: string;
  label: string;
  type: string;
}

interface GraphEdge {
  id: string;
  source: string;
  target: string;
  type: string;
}

export default function Home() {
  const [stats, setStats] = useState(STATS);
  const [statsLoading, setStatsLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    async function loadStats() {
      try {
        const res = await fetch("/data/knowledge_graph.json");
        if (res.ok && !cancelled) {
          const json = await res.json();
          const nodes: GraphNode[] = json.nodes || [];
          const edges: GraphEdge[] = json.edges || [];
          const nodeTypes = new Set(nodes.map((n) => n.type)).size;
          const relTypes = new Set(edges.map((e) => e.type)).size;
          setStats([
            { value: String(nodes.length), label: "Total Nodes", color: "text-blue-600" },
            { value: String(edges.length), label: "Total Edges", color: "text-green-600" },
            { value: String(nodeTypes), label: "Node Types", color: "text-purple-600" },
            { value: String(relTypes), label: "Relationship Types", color: "text-orange-600" },
          ]);
        }
      } catch {
        // Keep hardcoded STATS as fallback
      } finally {
        if (!cancelled) setStatsLoading(false);
      }
    }
    loadStats();
    return () => { cancelled = true; };
  }, []);

  return (
    <main className="min-h-screen bg-gray-50">
      {/* Hero */}
      <section className="flex flex-col items-center justify-center py-20 px-8">
        <h1 className="text-5xl font-bold mb-4 text-center">AgentVerse</h1>
        <p className="text-xl text-gray-600 text-center max-w-2xl mb-2">
          The Open Knowledge Graph for AI Agents
        </p>
        <p className="text-sm text-gray-400 text-center max-w-xl mb-8">
          GraphRAG · MCP · A2A · Multi-Agent Systems
        </p>
        <div className="flex gap-4">
          <Link
            href="/graph"
            className="rounded-lg bg-blue-600 px-6 py-3 text-white hover:bg-blue-700 transition font-medium"
          >
            Explore Graph
          </Link>
          <Link
            href="/search"
            className="rounded-lg bg-green-600 px-6 py-3 text-white hover:bg-green-700 transition font-medium"
          >
            Search
          </Link>
          <a
            href="/docs"
            className="rounded-lg border border-gray-300 px-6 py-3 hover:bg-gray-100 transition font-medium"
          >
            API Docs
          </a>
        </div>
      </section>

      {/* Features Grid */}
      <section className="max-w-5xl mx-auto px-8 pb-16">
        <h2 className="text-2xl font-semibold mb-8 text-center">Core Features</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {FEATURES.map((feature) => (
            <Link
              key={feature.title}
              href={feature.href}
              className={`border-2 rounded-xl p-6 hover:shadow-lg transition bg-white ${feature.color}`}
            >
              <div className="text-3xl mb-3">{feature.icon}</div>
              <h3 className="text-lg font-semibold mb-2">{feature.title}</h3>
              <p className="text-gray-600 text-sm">{feature.description}</p>
            </Link>
          ))}
        </div>
      </section>

      {/* Stats */}
      <section className="max-w-3xl mx-auto px-8 pb-20">
        <div className="grid grid-cols-4 gap-8 text-center">
          {stats.map((stat) => (
            <div key={stat.label}>
              <div className={`text-3xl font-bold ${stat.color}`}>
                {statsLoading ? "..." : stat.value}
              </div>
              <div className="text-sm text-gray-500">{stat.label}</div>
            </div>
          ))}
        </div>
      </section>
    </main>
  );
}