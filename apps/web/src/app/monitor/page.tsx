"use client";

import { useEffect, useState } from "react";
import { Card } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Badge } from "@/components/ui/Badge";
import { UI_TEXT } from "@/lib/i18n";
import { NodeTypeChart } from "@/components/monitor/NodeTypeChart";
import { EdgeTypeChart } from "@/components/monitor/EdgeTypeChart";
import { ConceptRanking } from "@/components/monitor/ConceptRanking";
import { PaperTimeline } from "@/components/monitor/PaperTimeline";

interface HealthData {
  status: string;
  version: string;
  services: {
    neo4j?: { status: string; nodes?: number; relationships?: number; error?: string };
    pgvector?: { status: string; embeddings?: number; error?: string };
  };
  cache: {
    query_cache?: { size: number; max_size: number; ttl_seconds: number };
    concept_cache?: { size: number; max_size: number; ttl_seconds: number };
  };
}

interface KGraphNode {
  id: string;
  type: string;
  name: string;
  published_date?: string;
  category?: string;
}

interface KGraphLink {
  source: string;
  target: string;
  type: string;
}

interface KGraphStats {
  totalNodes: number;
  totalEdges: number;
  nodeTypeDistribution: Record<string, number>;
  edgeTypeDistribution: Record<string, number>;
}

const STATUS_COLORS: Record<string, string> = {
  ok: "bg-green-500",
  degraded: "bg-yellow-500",
  unavailable: "bg-red-500",
};

export default function MonitorPage() {
  const [health, setHealth] = useState<HealthData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [graphStats, setGraphStats] = useState<KGraphStats | null>(null);
  const [graphStatsLoading, setGraphStatsLoading] = useState(true);
  const [graphNodes, setGraphNodes] = useState<KGraphNode[]>([]);
  const [graphLinks, setGraphLinks] = useState<KGraphLink[]>([]);

  // Fetch health data
  useEffect(() => {
    async function fetchHealth() {
      try {
        const res = await fetch("/api/v1/health");
        if (res.ok) {
          const data = await res.json();
          setHealth(data);
        } else {
          setError("Failed to fetch health data");
        }
      } catch (err) {
        setError("API not available");
      } finally {
        setLoading(false);
      }
    }
    fetchHealth();
    const interval = setInterval(fetchHealth, 30000);
    return () => clearInterval(interval);
  }, []);

  // Fetch knowledge graph stats
  useEffect(() => {
    let cancelled = false;
    async function loadGraphStats() {
      try {
        const res = await fetch("/data/knowledge_graph.json");
        if (res.ok && !cancelled) {
          const json = await res.json();
          const nodes: KGraphNode[] = json.nodes || [];
          const links: KGraphLink[] = json.links || json.edges || [];

          if (!cancelled) {
            setGraphNodes(nodes);
            setGraphLinks(links);
          }

          const nodeDist: Record<string, number> = {};
          for (const n of nodes) {
            nodeDist[n.type] = (nodeDist[n.type] || 0) + 1;
          }

          const edgeDist: Record<string, number> = {};
          for (const l of links) {
            edgeDist[l.type] = (edgeDist[l.type] || 0) + 1;
          }

          setGraphStats({
            totalNodes: nodes.length,
            totalEdges: links.length,
            nodeTypeDistribution: nodeDist,
            edgeTypeDistribution: edgeDist,
          });
        }
      } catch {
        // Keep null
      } finally {
        if (!cancelled) setGraphStatsLoading(false);
      }
    }
    loadGraphStats();
    return () => { cancelled = true; };
  }, []);

  // Download functions
  const downloadJSON = async () => {
    try {
      const res = await fetch("/data/knowledge_graph.json");
      if (!res.ok) return;
      const data = await res.json();
      const blob = new Blob([JSON.stringify(data, null, 2)], { type: "application/json" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "knowledge_graph.json";
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } catch {
      console.error("Failed to download JSON");
    }
  };

  const downloadCSV = async (type: "nodes" | "edges") => {
    try {
      const res = await fetch("/data/knowledge_graph.json");
      if (!res.ok) return;
      const json = await res.json();
      const items = json.nodes || json.links || json.edges || [];
      const target = type === "nodes" ? json.nodes || [] : json.links || json.edges || [];

      if (target.length === 0) return;

      const headers = Object.keys(target[0]);
      const csvRows = [headers.join(",")];
      for (const item of target) {
        const row = headers.map((h) => {
          const val = item[h];
          if (val === undefined || val === null) return "";
          const str = String(val);
          // Escape quotes and wrap in quotes if contains comma
          return str.includes(",") || str.includes('"') || str.includes("\n")
            ? `"${str.replace(/"/g, '""')}"`
            : str;
        });
        csvRows.push(row.join(","));
      }

      const csv = csvRows.join("\n");
      const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `knowledge_graph_${type}.csv`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } catch {
      console.error(`Failed to download CSV (${type})`);
    }
  };

  if (loading && graphStatsLoading) {
    return (
      <main className="min-h-screen bg-gray-50 p-8">
        <h1 className="text-3xl font-bold mb-4">{UI_TEXT.systemMonitor}</h1>
        <p className="text-gray-500">{UI_TEXT.loading}</p>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-4xl">
        <h1 className="text-3xl font-bold mb-2">{UI_TEXT.systemMonitor}</h1>
        <p className="text-gray-600 mb-8">{UI_TEXT.realtimeHealth}</p>

        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
            {error}
          </div>
        )}

        {/* Overall Status */}
        <Card title={`${UI_TEXT.systemStatus}: ${health?.status || "Unknown"}`} className="mb-8">
          <div className="flex items-center gap-3 mb-2">
            <span className={`w-3 h-3 rounded-full ${STATUS_COLORS[health?.status || "unavailable"]}`} />
            <p className="text-sm text-gray-500">Version {health?.version || "?"}</p>
          </div>
        </Card>

        {/* Services */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
          {/* Neo4j */}
          <Card title="Neo4j">
            <div className="flex items-center gap-2 mb-4">
              <span className={`w-3 h-3 rounded-full ${STATUS_COLORS[health?.services?.neo4j?.status || "unavailable"]}`} />
            </div>
            {health?.services?.neo4j?.status === "ok" ? (
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-500">Nodes</span>
                  <span className="font-mono font-bold">{health.services.neo4j.nodes?.toLocaleString()}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-500">Relationships</span>
                  <span className="font-mono font-bold">{health.services.neo4j.relationships?.toLocaleString()}</span>
                </div>
              </div>
            ) : (
              <p className="text-sm text-gray-500">{health?.services?.neo4j?.error || "Unavailable"}</p>
            )}
          </Card>

          {/* pgvector */}
          <Card title="pgvector">
            <div className="flex items-center gap-2 mb-4">
              <span className={`w-3 h-3 rounded-full ${STATUS_COLORS[health?.services?.pgvector?.status || "unavailable"]}`} />
            </div>
            {health?.services?.pgvector?.status === "ok" ? (
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-500">Embeddings</span>
                  <span className="font-mono font-bold">{health.services.pgvector.embeddings?.toLocaleString()}</span>
                </div>
              </div>
            ) : (
              <p className="text-sm text-gray-500">{health?.services?.pgvector?.error || "Unavailable"}</p>
            )}
          </Card>
        </div>

        {/* Knowledge Graph Stats */}
        <Card title={UI_TEXT.knowledgeGraph} className="mb-8">
          {graphStatsLoading ? (
            <p className="text-sm text-gray-500">{UI_TEXT.loadingStats}</p>
          ) : graphStats ? (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Node Stats */}
              <div>
                <p className="text-sm font-medium text-gray-500 mb-3">
                  {UI_TEXT.nodes}: <span className="font-bold text-gray-800">{graphStats.totalNodes}</span>
                </p>
                <div className="space-y-1 text-sm">
                  {Object.entries(graphStats.nodeTypeDistribution).map(([type, count]) => (
                    <div key={type} className="flex justify-between">
                      <Badge>{type}</Badge>
                      <span className="font-mono font-bold">{count}</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Edge Stats */}
              <div>
                <p className="text-sm font-medium text-gray-500 mb-3">
                  {UI_TEXT.edges}: <span className="font-bold text-gray-800">{graphStats.totalEdges}</span>
                </p>
                <div className="space-y-1 text-sm">
                  {Object.entries(graphStats.edgeTypeDistribution).map(([type, count]) => (
                    <div key={type} className="flex justify-between">
                      <Badge variant="info">{type}</Badge>
                      <span className="font-mono font-bold">{count}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          ) : (
            <p className="text-sm text-gray-500">Knowledge graph file not available.</p>
          )}
        </Card>

        {/* Node Type Distribution Chart */}
        {graphNodes.length > 0 && (
          <Card title={UI_TEXT.nodeTypes} className="mb-8">
            <NodeTypeChart nodes={graphNodes} />
          </Card>
        )}

        {/* Edge Type Distribution Chart */}
        {graphLinks.length > 0 && (
          <Card title={UI_TEXT.edgeTypes} className="mb-8">
            <EdgeTypeChart links={graphLinks} />
          </Card>
        )}

        {/* Concept Ranking */}
        {graphNodes.length > 0 && graphLinks.length > 0 && (
          <Card title="Top Concepts by Paper Count" className="mb-8">
            <ConceptRanking nodes={graphNodes} links={graphLinks} />
          </Card>
        )}

        {/* Paper Timeline */}
        {graphNodes.length > 0 && (
          <Card title={UI_TEXT.paperTimeline} className="mb-8">
            <PaperTimeline nodes={graphNodes} />
          </Card>
        )}

        {/* Cache Stats */}
        <Card title={UI_TEXT.cacheStatistics} className="mb-8">
          <div className="grid grid-cols-2 gap-6">
            <div>
              <h4 className="text-sm font-medium text-gray-500 mb-2">Query Cache</h4>
              <div className="space-y-1 text-sm">
                <div className="flex justify-between">
                  <span>Size</span>
                  <span className="font-mono">{health?.cache?.query_cache?.size || 0}</span>
                </div>
                <div className="flex justify-between">
                  <span>Max Size</span>
                  <span className="font-mono">{health?.cache?.query_cache?.max_size || 0}</span>
                </div>
                <div className="flex justify-between">
                  <span>TTL</span>
                  <span className="font-mono">{health?.cache?.query_cache?.ttl_seconds || 0}s</span>
                </div>
              </div>
            </div>
            <div>
              <h4 className="text-sm font-medium text-gray-500 mb-2">Concept Cache</h4>
              <div className="space-y-1 text-sm">
                <div className="flex justify-between">
                  <span>Size</span>
                  <span className="font-mono">{health?.cache?.concept_cache?.size || 0}</span>
                </div>
                <div className="flex justify-between">
                  <span>Max Size</span>
                  <span className="font-mono">{health?.cache?.concept_cache?.max_size || 0}</span>
                </div>
                <div className="flex justify-between">
                  <span>TTL</span>
                  <span className="font-mono">{health?.cache?.concept_cache?.ttl_seconds || 0}s</span>
                </div>
              </div>
            </div>
          </div>
        </Card>

        {/* Download Actions */}
        <Card title={UI_TEXT.dataExport}>
          <div className="flex flex-wrap gap-3">
            <Button onClick={downloadJSON}>Download JSON (full graph)</Button>
            <Button onClick={() => downloadCSV("nodes")} variant="secondary">Download Nodes CSV</Button>
            <Button onClick={() => downloadCSV("edges")} variant="secondary">Download Edges CSV</Button>
          </div>
          <p className="text-xs text-gray-400 mt-3">
            Exports are generated client-side from the knowledge graph JSON file.
          </p>
        </Card>

        {/* Quick Links */}
        <div className="mt-8 flex gap-4">
          <a
            href="/docs"
            className="px-4 py-2 border rounded-lg text-sm hover:bg-gray-50 transition"
          >
            {UI_TEXT.apiDocs}
          </a>
        </div>
      </div>
    </main>
  );
}