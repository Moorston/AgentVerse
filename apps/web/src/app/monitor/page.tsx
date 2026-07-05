"use client";

import { useEffect, useState } from "react";

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

const STATUS_COLORS: Record<string, string> = {
  ok: "bg-green-500",
  degraded: "bg-yellow-500",
  unavailable: "bg-red-500",
};

export default function MonitorPage() {
  const [health, setHealth] = useState<HealthData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

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
    const interval = setInterval(fetchHealth, 30000); // Refresh every 30s
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <main className="p-8">
        <h1 className="text-3xl font-bold mb-4">System Monitor</h1>
        <p className="text-gray-500">Loading...</p>
      </main>
    );
  }

  return (
    <main className="p-8 max-w-4xl">
      <h1 className="text-3xl font-bold mb-2">System Monitor</h1>
      <p className="text-gray-600 mb-8">Real-time system health and statistics</p>

      {error && (
        <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
          {error}
        </div>
      )}

      {/* Overall Status */}
      <div className="mb-8 p-6 border rounded-xl bg-white">
        <div className="flex items-center gap-3 mb-2">
          <span className={`w-3 h-3 rounded-full ${STATUS_COLORS[health?.status || "unavailable"]}`} />
          <h2 className="text-xl font-semibold">System Status: {health?.status || "Unknown"}</h2>
        </div>
        <p className="text-sm text-gray-500">Version {health?.version || "?"}</p>
      </div>

      {/* Services */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
        {/* Neo4j */}
        <div className="p-6 border rounded-xl bg-white">
          <div className="flex items-center gap-2 mb-4">
            <span className={`w-3 h-3 rounded-full ${STATUS_COLORS[health?.services?.neo4j?.status || "unavailable"]}`} />
            <h3 className="text-lg font-semibold">Neo4j</h3>
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
        </div>

        {/* pgvector */}
        <div className="p-6 border rounded-xl bg-white">
          <div className="flex items-center gap-2 mb-4">
            <span className={`w-3 h-3 rounded-full ${STATUS_COLORS[health?.services?.pgvector?.status || "unavailable"]}`} />
            <h3 className="text-lg font-semibold">pgvector</h3>
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
        </div>
      </div>

      {/* Cache Stats */}
      <div className="p-6 border rounded-xl bg-white">
        <h3 className="text-lg font-semibold mb-4">Cache Statistics</h3>
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
      </div>

      {/* Quick Actions */}
      <div className="mt-8 flex gap-4">
        <a href="/docs" className="px-4 py-2 border rounded-lg text-sm hover:bg-gray-50 transition">
          API Docs
        </a>
        <a href="/api/v1/export/json" className="px-4 py-2 border rounded-lg text-sm hover:bg-gray-50 transition">
          Export JSON
        </a>
        <a href="/api/v1/export/csv" className="px-4 py-2 border rounded-lg text-sm hover:bg-gray-50 transition">
          Export CSV
        </a>
      </div>
    </main>
  );
}