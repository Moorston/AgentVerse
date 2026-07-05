"use client";

import { useEffect, useState, useCallback } from "react";
import { GraphCanvas } from "@/components/graph/GraphCanvas";
import { GraphControls } from "@/components/graph/GraphControls";
import type { GraphData } from "@/types/graph";

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
  const [data, setData] = useState<GraphData>(DEMO_DATA);
  const [loading, setLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const [activeFilter, setActiveFilter] = useState("");

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
      // Use demo data on error
      console.log("Using demo data");
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

  // Filter nodes by type
  const filteredData: GraphData = activeFilter
    ? {
        nodes: data.nodes.filter((n) => n.type === activeFilter),
        edges: data.edges.filter(
          (e) =>
            data.nodes.some((n) => n.id === e.source && n.type === activeFilter) ||
            data.nodes.some((n) => n.id === e.target && n.type === activeFilter),
        ),
      }
    : data;

  return (
    <div className="flex h-screen">
      {/* Sidebar */}
      <aside className="w-64 border-r bg-gray-50 flex-shrink-0">
        <div className="p-4 border-b">
          <h2 className="text-lg font-semibold">Graph Explorer</h2>
          <p className="text-xs text-gray-500 mt-1">
            {filteredData.nodes.length} nodes, {filteredData.edges.length} edges
          </p>
        </div>
        <GraphControls
          onSearch={setSearchQuery}
          onFilter={setActiveFilter}
          activeFilter={activeFilter}
        />
      </aside>

      {/* Graph Canvas */}
      <main className="flex-1 relative">
        {loading && (
          <div className="absolute inset-0 bg-white/80 flex items-center justify-center z-10">
            <div className="text-gray-500">Loading graph...</div>
          </div>
        )}
        <GraphCanvas data={filteredData} onNodeClick={handleNodeClick} className="w-full h-full" />
      </main>
    </div>
  );
}