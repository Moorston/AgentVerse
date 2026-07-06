"use client";

import { useState, useMemo } from "react";
import { Card } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { LoadingSkeleton } from "@/components/ui/Loading";
import { ErrorBanner } from "@/components/ui/ErrorBanner";
import { useFetch } from "@/hooks/useFetch";
import { compareConcepts } from "@/lib/compare";
import { parseGraphData } from "@/lib/types/graph";
import type { KGraphData } from "@/lib/types/graph";

function ConceptSelector({
  label,
  concepts,
  value,
  onChange,
}: {
  label: string;
  concepts: string[];
  value: string;
  onChange: (val: string) => void;
}) {
  const [input, setInput] = useState("");
  const [showSuggestions, setShowSuggestions] = useState(false);

  const filtered = useMemo(() => {
    if (!input.trim()) return concepts.slice(0, 10);
    const lower = input.toLowerCase();
    return concepts.filter((c) => c.toLowerCase().includes(lower)).slice(0, 10);
  }, [concepts, input]);

  return (
    <div className="relative">
      <label className="block text-sm font-medium text-gray-700 mb-1">{label}</label>
      <input
        type="text"
        value={input || value}
        onChange={(e) => {
          setInput(e.target.value);
          setShowSuggestions(true);
          onChange("");
        }}
        onFocus={() => setShowSuggestions(true)}
        onBlur={() => setTimeout(() => setShowSuggestions(false), 200)}
        placeholder="Type to search concepts..."
        className="w-full px-3 py-2 border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
      />
      {showSuggestions && filtered.length > 0 && (
        <div className="absolute z-10 w-full bg-white border rounded-lg shadow-md mt-1 max-h-48 overflow-y-auto">
          {filtered.map((concept) => (
            <button
              key={concept}
              onMouseDown={() => {
                setInput(concept);
                onChange(concept);
                setShowSuggestions(false);
              }}
              className="w-full text-left px-3 py-2 text-sm hover:bg-gray-50 transition"
            >
              {concept}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}

function SectionList({ title, items }: { title: string; items: string[] }) {
  if (items.length === 0) return null;
  return (
    <div className="mb-3">
      <p className="text-xs font-medium text-gray-500 mb-1">{title}</p>
      <div className="flex flex-wrap gap-1">
        {items.map((item) => (
          <Badge key={item} variant="info">
            {item}
          </Badge>
        ))}
      </div>
    </div>
  );
}

export default function ComparePage() {
  const { data, loading, error, refetch } = useFetch<KGraphData>("/data/knowledge_graph.json", {
    parser: parseGraphData,
  });

  const [conceptA, setConceptA] = useState("");
  const [conceptB, setConceptB] = useState("");
  const [result, setResult] = useState<ReturnType<typeof compareConcepts> | null>(null);

  const conceptNames = useMemo(() => {
    if (!data) return [];
    return [...new Set(data.nodes.filter((n) => n.type === "concept").map((n) => n.name || n.id))].sort();
  }, [data]);

  const handleCompare = () => {
    if (!data || !conceptA || !conceptB) return;
    setResult(compareConcepts(data, conceptA, conceptB));
  };

  if (loading) {
    return (
      <main className="min-h-screen bg-gray-50 p-8">
        <h1 className="text-3xl font-bold mb-6">Compare Concepts</h1>
        <LoadingSkeleton rows={5} />
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold mb-2">Compare Concepts</h1>
        <p className="text-gray-600 mb-8">
          Select two concepts to see their shared and unique papers, frameworks, and relationships.
        </p>

        {error && (
          <div className="mb-6">
            <ErrorBanner message={error} onRetry={refetch} />
          </div>
        )}

        <Card title="Select Concepts" className="mb-8">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
            <ConceptSelector
              label="Concept A"
              concepts={conceptNames}
              value={conceptA}
              onChange={setConceptA}
            />
            <ConceptSelector
              label="Concept B"
              concepts={conceptNames}
              value={conceptB}
              onChange={setConceptB}
            />
          </div>
          <Button onClick={handleCompare} disabled={!conceptA || !conceptB}>
            Compare
          </Button>
        </Card>

        {result && (
          <>
            {/* Side by side cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
              <Card title={result.conceptA.name}>
                <SectionList title="Papers" items={result.conceptA.papers} />
                <SectionList title="Frameworks" items={result.conceptA.frameworks} />
                {result.conceptA.relations.length > 0 && (
                  <div>
                    <p className="text-xs font-medium text-gray-500 mb-1">Relationships</p>
                    <ul className="text-xs text-gray-600 space-y-1">
                      {result.conceptA.relations.slice(0, 10).map((r, i) => (
                        <li key={i} className="truncate">{r}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </Card>

              <Card title={result.conceptB.name}>
                <SectionList title="Papers" items={result.conceptB.papers} />
                <SectionList title="Frameworks" items={result.conceptB.frameworks} />
                {result.conceptB.relations.length > 0 && (
                  <div>
                    <p className="text-xs font-medium text-gray-500 mb-1">Relationships</p>
                    <ul className="text-xs text-gray-600 space-y-1">
                      {result.conceptB.relations.slice(0, 10).map((r, i) => (
                        <li key={i} className="truncate">{r}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </Card>
            </div>

            {/* Common */}
            <Card title="Common" className="mb-6">
              <SectionList title="Shared Papers" items={result.common.papers} />
              <SectionList title="Shared Frameworks" items={result.common.frameworks} />
              <SectionList title="Shared Relationships" items={result.common.relations} />
              {result.common.papers.length === 0 &&
                result.common.frameworks.length === 0 &&
                result.common.relations.length === 0 && (
                  <p className="text-sm text-gray-400">No common items found.</p>
                )}
            </Card>

            {/* Unique to A */}
            <Card title={`Unique to ${result.conceptA.name}`} className="mb-6">
              <SectionList title="Papers" items={result.uniqueToA.papers} />
              <SectionList title="Frameworks" items={result.uniqueToA.frameworks} />
              {result.uniqueToA.papers.length === 0 && result.uniqueToA.frameworks.length === 0 && (
                <p className="text-sm text-gray-400">No unique items.</p>
              )}
            </Card>

            {/* Unique to B */}
            <Card title={`Unique to ${result.conceptB.name}`} className="mb-6">
              <SectionList title="Papers" items={result.uniqueToB.papers} />
              <SectionList title="Frameworks" items={result.uniqueToB.frameworks} />
              {result.uniqueToB.papers.length === 0 && result.uniqueToB.frameworks.length === 0 && (
                <p className="text-sm text-gray-400">No unique items.</p>
              )}
            </Card>
          </>
        )}
      </div>
    </main>
  );
}
