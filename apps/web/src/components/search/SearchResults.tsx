import { Badge } from "@/components/ui/Badge";
import type { SearchResult } from "@/lib/search";

interface SearchResultsProps {
  results: SearchResult[];
  loading: boolean;
  error: string;
  query: string;
}

export function SearchResults({ results, loading, error, query }: SearchResultsProps) {
  if (loading) {
    return (
      <div className="space-y-4">
        {[1, 2, 3].map((i) => (
          <div key={i} className="animate-pulse border rounded-lg p-4 bg-white">
            <div className="h-4 bg-gray-200 rounded w-1/3 mb-3" />
            <div className="h-3 bg-gray-100 rounded w-2/3" />
          </div>
        ))}
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {results.map((r, i) => (
        <div key={i} className="border rounded-lg p-4 bg-white hover:shadow-md transition">
          <div className="flex items-center gap-2 mb-2">
            <Badge
              variant={
                r.type === "concept"
                  ? "info"
                  : r.type === "paper"
                    ? "success"
                    : r.type === "framework"
                      ? "warning"
                      : "default"
              }
            >
              {r.type}
            </Badge>
            <span className="text-xs text-gray-400">score: {r.score.toFixed(2)}</span>
            <span className="text-xs px-1.5 py-0.5 bg-gray-50 rounded text-gray-400">
              {r.match === "exact_name"
                ? "exact name"
                : r.match === "neighbor"
                  ? "neighbor"
                  : "description"}
            </span>
          </div>
          <h3 className="text-lg font-semibold mb-1">{r.name}</h3>
          <p className="text-gray-600 text-sm">{r.description}</p>
        </div>
      ))}
      {results.length === 0 && query && !error && (
        <p className="text-gray-500">No results found for &quot;{query}&quot;</p>
      )}
    </div>
  );
}
