"use client";

import React, { Suspense, useEffect, useState, useCallback } from "react";
import { useRouter } from "next/navigation";
import type { GraphData } from "@/types/graph";
import { LoadingSkeleton } from "@/components/ui/Loading";
import { UI_TEXT } from "@/lib/i18n";

const GraphCanvas = React.lazy(() => import("@/components/graph/GraphCanvas").then(m => ({ default: m.GraphCanvas })));
const GraphControls = React.lazy(() => import("@/components/graph/GraphControls").then(m => ({ default: m.GraphControls })));

// Demo data for development
const DEMO_DATA: GraphData = {
  nodes: [
    { id: "1", label: "Chain-of-Thought", type: "Concept", properties: { category: "reasoning" } },
    { id: "2", label: "ReAct", type: "Concept", properties: { category: "reasoning" } },
    { id: "3", label: "Reflexion", type: "Concept", properties: { category: "reflection" } },
    { id: "4", label: "Plan-and-Execute", type: "Concept", properties: { category: "planning" } },
    { id: "5", label: "Graph Agents", type: "Concept", properties: { category: "multi_agent" } },
    { id: "6", label: "LangGraph", type: "Framework", properties: { stars: 8000 } },
    { id: "7", label: "CrewAI", type: "Framework", properties: { stars: 15000 } },
    { id: "8", label: "Mem0", type: "MemoryFramework", properties: {} },
    { id: "9", label: "ReAct Paper", type: "Paper", properties: { year: 2022 } },
    { id: "10", label: "MCP", type: "Protocol", properties: {} },
  ],
  edges: [
    { id: "e1", source: "1", target: "2", type: "EVOLVES_TO", properties: {} },
    { id: "e2", source: "2", target: "3", type: "EVOLVES_TO", properties: {} },
    { id: "e3", source: "2", target: "4", type: "EVOLVES_TO", properties: {} },
    { id: "e4", source: "3", target: "5", type: "EVOLVES_TO", properties: {} },
    { id: "e5", source: "9", target: "2", type: "PROPOSES", properties: {} },
    { id: "e6", source: "6", target: "2", type: "IMPLEMENTS", properties: {} },
    { id: "e7", source: "6", target: "3", type: "IMPLEMENTS", properties: {} },
    { id: "e8", source: "7", target: "4", type: "IMPLEMENTS", properties: {} },
  ],
};

export default function GraphExplorer() {
  const router = useRouter();
  const [data, setData] = useState<GraphData>(DEMO_DATA);
  const [loading, setLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const [activeFilter, setActiveFilter] = useState<string[]>([]);
  const [highlightNode, setHighlightNode] = useState<string | undefined>(undefined);

  // Load initial graph data from JSON file
  useEffect(() => {
    let cancelled = false;
    async function loadJsonData() {
      try {
        const res = await fetch("/data/knowledge_graph.json");
        if (res.ok && !cancelled) {
          const json = await res.json();
          if (json.nodes && json.edges) {
            setData(json as GraphData);
          }
        }
      } catch {
        // Keep DEMO_DATA as fallback
      }
    }
    loadJsonData();
    return () => { cancelled = true; };
  }, []);

  // Fetch graph data from API
  const fetchData = useCallback(async (query?: string) => {
    setLoading(true);
    try {
      const url = query
        ? `/api/v1/search?q=${encodeURIComponent(query)}`
        : "/api/v1/concepts?size=50";
      const response = await fetch(url);
      if (response.ok) {
        const result = await response.json();
        // Transform API response to GraphData format
        if (result.results || result.nodes) {
          setData(result as GraphData);
        }
      }
    } catch {
      // Keep current data on error
      console.log("Using existing data");
    } finally {
      setLoading(false);
    }
  }, []);

  // Debounced search
  useEffect(() => {
    const timer = setTimeout(() => {
      if (searchQuery) {
        fetchData(searchQuery);
      }
    }, 500);
    return () => clearTimeout(timer);
  }, [searchQuery, fetchData]);

  const handleNodeClick = useCallback((nodeId: string) => {
    console.log("Node clicked:", nodeId);
    // TODO: Expand neighbors on click
  }, []);

  const handleNodeDoubleClick = useCallback(
    (nodeId: string) => {
      const node = data.nodes.find((n) => n.id === nodeId);
      const name = node?.label || nodeId;
      router.push(`/concept/${encodeURIComponent(name)}`);
    },
    [data.nodes, router],
  );

  // Filter nodes by type (used for info display only; GraphCanvas handles visual filtering)
  const filteredData: GraphData = activeFilter.length > 0
    ? {
        nodes: data.nodes.filter((n) => activeFilter.includes(n.type)),
        edges: data.edges.filter(
          (e) =>
            data.nodes.some((n) => n.id === e.source && activeFilter.includes(n.type)) ||
            data.nodes.some((n) => n.id === e.target && activeFilter.includes(n.type)),
        ),
      }
    : data;

  return (
    <div className="flex h-screen">
      {/* Sidebar */}
      <aside className="w-64 border-r bg-gray-50 flex-shrink-0">
        <div className="p-4 border-b">
          <h2 className="text-lg font-semibold">{UI_TEXT.graphExplorer}</h2>
          <p className="text-xs text-gray-500 mt-1">
            {filteredData.nodes.length} {UI_TEXT.nodes}, {filteredData.edges.length} {UI_TEXT.edges}
          </p>
        </div>
        <Suspense fallback={<LoadingSkeleton rows={5} />}>
          <GraphControls
            onSearch={setSearchQuery}
            onFilter={setActiveFilter}
            activeFilter={activeFilter}
            highlightNode={highlightNode}
            onHighlight={setHighlightNode}
          />
        </Suspense>
      </aside>

      {/* Graph Canvas */}
      <main className="flex-1 relative">
        {loading && (
          <div className="absolute inset-0 bg-white/80 flex items-center justify-center z-10">
            <div className="text-gray-500">{UI_TEXT.loading}</div>
          </div>
        )}
        <Suspense fallback={<LoadingSkeleton rows={3} />}>
          <GraphCanvas
            data={filteredData}
            onNodeClick={handleNodeClick}
            onNodeDoubleClick={handleNodeDoubleClick}
            filterType={activeFilter}
            highlightNode={highlightNode}
            className="w-full h-full"
          />
        </Suspense>
      </main>
    </div>
  );
}