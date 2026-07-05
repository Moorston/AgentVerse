"use client";

import { useState, useCallback } from "react";

interface SearchResult {
  name: string;
  description: string;
  type: string;
  score: number;
  match: string;
}

export default function SearchPage() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<SearchResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [strategy, setStrategy] = useState("graph");

  const handleSearch = useCallback(async () => {
    if (!query.trim()) return;
    setLoading(true);
    setError("");
    try {
      const res = await fetch(
        `/api/v1/search/?q=${encodeURIComponent(query)}&strategy=${strategy}&top_k=20`,
      );
      if (res.ok) {
        const data = await res.json();
        setResults(data.results || []);
      } else {
        setError(`API error: ${res.status}`);
      }
    } catch {
      setError("Failed to connect to API");
    } finally {
      setLoading(false);
    }
  }, [query, strategy]);

  return (
    <main className="min-h-screen bg-gray-50 p-8">
      <h1 className="text-3xl font-bold mb-6">GraphRAG Search</h1>

      <div className="flex gap-4 mb-8">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleSearch()}
          placeholder="Search concepts, frameworks, papers..."
          className="flex-1 px-4 py-3 border rounded-lg text-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          disabled={loading}
        />
        <select
          value={strategy}
          onChange={(e) => setStrategy(e.target.value)}
          className="px-4 py-3 border rounded-lg"
          disabled={loading}
        >
          <option value="graph">Graph Search</option>
          <option value="vector">Vector Search</option>
          <option value="hybrid">Hybrid</option>
        </select>
        <button
          onClick={handleSearch}
          disabled={loading}
          className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition"
        >
          {loading ? "Searching..." : "Search"}
        </button>
      </div>

      {error && (
        <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
          {error}
        </div>
      )}

      {loading ? (
        <div className="space-y-4">
          {[1, 2, 3].map((i) => (
            <div key={i} className="animate-pulse border rounded-lg p-4 bg-white">
              <div className="h-4 bg-gray-200 rounded w-1/3 mb-3" />
              <div className="h-3 bg-gray-100 rounded w-2/3" />
            </div>
          ))}
        </div>
      ) : (
        <div className="space-y-4">
          {results.map((r, i) => (
            <div key={i} className="border rounded-lg p-4 bg-white hover:shadow-md transition">
              <div className="flex items-center gap-2 mb-2">
                <span className="text-xs px-2 py-0.5 bg-gray-100 rounded">{r.type}</span>
                <span className="text-xs text-gray-400">score: {r.score.toFixed(2)}</span>
              </div>
              <h3 className="text-lg font-semibold mb-1">{r.name}</h3>
              <p className="text-gray-600 text-sm">{r.description}</p>
            </div>
          ))}
          {results.length === 0 && query && !error && (
            <p className="text-gray-500">No results found for &quot;{query}&quot;</p>
          )}
        </div>
      )}
    </main>
  );
}