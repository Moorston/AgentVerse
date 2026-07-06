"use client";

import { useState, useMemo } from "react";
import { LoadingSkeleton } from "@/components/ui/Loading";
import { FrameworkCard } from "@/components/framework/FrameworkCard";
import { FrameworkModal } from "@/components/framework/FrameworkModal";
import { SimilarFrameworks } from "@/components/framework/SimilarFrameworks";
import { useFrameworks, type Framework } from "@/hooks/useFrameworks";

type SortKey = "stars" | "name" | "language";

export default function FrameworksPage() {
  const { frameworks, loading } = useFrameworks();
  const [sortKey, setSortKey] = useState<SortKey>("stars");
  const [modalFramework, setModalFramework] = useState<Framework | null>(null);

  const sorted = useMemo(() => {
    const items = [...frameworks];
    switch (sortKey) {
      case "stars": items.sort((a, b) => b.stars - a.stars); break;
      case "name": items.sort((a, b) => a.name.localeCompare(b.name)); break;
      case "language": items.sort((a, b) => (a.language || "").localeCompare(b.language || "")); break;
    }
    return items;
  }, [frameworks, sortKey]);

  if (loading) {
    return (
      <main className="min-h-screen bg-gray-50 p-8">
        <h1 className="text-3xl font-bold mb-6">Framework Ecosystem</h1>
        <LoadingSkeleton rows={6} />
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-6xl mx-auto">
        <h1 className="text-3xl font-bold mb-2">Framework Ecosystem</h1>
        <p className="text-gray-600 mb-6">AI Agent development frameworks and their capabilities</p>

        <div className="flex items-center gap-3 mb-8">
          <label className="text-sm font-medium text-gray-600">Sort by:</label>
          <select
            value={sortKey}
            onChange={(e) => setSortKey(e.target.value as SortKey)}
            className="px-3 py-2 border rounded-lg text-sm bg-white focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="stars">Stars (high to low)</option>
            <option value="name">Name (A-Z)</option>
            <option value="language">Language</option>
          </select>
          <span className="text-xs text-gray-400">{sorted.length} frameworks</span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {sorted.map((fw) => (
            <FrameworkCard key={fw.name} framework={fw} onClick={() => setModalFramework(fw)} />
          ))}
        </div>

        <SimilarFrameworks frameworks={frameworks} onFrameworkClick={setModalFramework} />
      </div>

      {modalFramework && (
        <FrameworkModal framework={modalFramework} onClose={() => setModalFramework(null)} />
      )}
    </main>
  );
}
