"use client";

import { useState, useCallback } from "react";
import type { SearchResult as GSearchResult } from "@/lib/search";
import { useGraphSearch } from "@/hooks/useGraphSearch";
import { SearchTabs } from "@/components/search/SearchTabs";
import { SearchResults } from "@/components/search/SearchResults";
import { TrendingSidebar } from "@/components/search/TrendingSidebar";
import { UI_TEXT } from "@/lib/i18n";

export default function SearchPage() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<GSearchResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [strategy, setStrategy] = useState("graph");
  const [searchMode, setSearchMode] = useState<"api" | "local">("api");

  const { searchLocal, trending } = useGraphSearch();

  const handleSearch = useCallback(async () => {
    if (!query.trim()) return;

    if (searchMode === "local") {
      setLoading(true);
      setError("");
      await new Promise((r) => setTimeout(r, 150));
      const localResults = searchLocal(query);
      setResults(localResults);
      setLoading(false);
      if (localResults.length === 0) setError(UI_TEXT.noLocalMatches);
      return;
    }

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
        const localResults = searchLocal(query);
        setResults(localResults);
        if (localResults.length === 0) setError(`API error: ${res.status}. No local matches found.`);
      }
    } catch {
      const localResults = searchLocal(query);
      setResults(localResults);
      if (localResults.length === 0) setError("Failed to connect to API and no local matches found.");
    } finally {
      setLoading(false);
    }
  }, [query, strategy, searchLocal, searchMode]);

  return (
    <main className="min-h-screen bg-gray-50 p-8">
      <h1 className="text-3xl font-bold mb-6">{UI_TEXT.graphRagSearch}</h1>

      <SearchTabs
        activeTab={searchMode}
        onTabChange={setSearchMode}
        strategy={strategy}
        onStrategyChange={setStrategy}
        loading={loading}
      />

      <div className="flex gap-8">
        <div className="flex-1 min-w-0">
          <div className="flex gap-4 mb-8">
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleSearch()}
              placeholder={UI_TEXT.searchConceptsFrameworksPapers}
              className="flex-1 px-4 py-3 border rounded-lg text-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              disabled={loading}
            />
            <button
              onClick={handleSearch}
              disabled={loading}
              className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition"
            >
              {loading ? UI_TEXT.searching : UI_TEXT.search}
            </button>
          </div>

          {error && (
            <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
              {error}
            </div>
          )}

          {searchMode === "local" && (
            <p className="text-xs text-gray-400 mb-4">
              Local search uses MemoryGraphRAG to score results by name match (1.0),
              description match (0.7), and neighbor proximity (0.5).
            </p>
          )}

          <SearchResults results={results} loading={loading} error={error} query={query} />
        </div>

        <TrendingSidebar trending={trending} />
      </div>
    </main>
  );
}
