import { useState, useEffect, useCallback, useRef } from "react";
import type { SearchResult as GSearchResult } from "@/lib/search";
import { MemoryGraphRAG } from "@/lib/search";

interface KGraphNode {
  id: string;
  label?: string;
  name?: string;
  type: string;
  description?: string;
  category?: string;
  properties?: Record<string, unknown>;
}

interface KGraphLink {
  source: string;
  target: string;
  type: string;
}

export function useGraphSearch() {
  const [graphNodes, setGraphNodes] = useState<KGraphNode[]>([]);
  const ragRef = useRef<MemoryGraphRAG | null>(null);
  const [trending, setTrending] = useState<{ name: string; count: number }[]>([]);

  useEffect(() => {
    let cancelled = false;
    async function loadGraph() {
      try {
        const res = await fetch("/data/knowledge_graph.json");
        if (res.ok && !cancelled) {
          const json = await res.json();
          const nodes: KGraphNode[] = json.nodes || [];
          const links: KGraphLink[] = json.links || json.edges || [];
          setGraphNodes(nodes);

          const mnodes = nodes.map((n) => ({
            id: n.id,
            type: n.type,
            name: n.name || n.label || n.id,
            description: n.description || (n.properties?.description as string) || "",
            category: n.category || "",
          }));
          const medges = links.map((l) => ({
            source: l.source,
            target: l.target,
            type: l.type,
          }));
          ragRef.current = new MemoryGraphRAG({ nodes: mnodes, links: medges });

          const conceptProposeCount = new Map<string, number>();
          for (const link of links) {
            if (link.type === "PROPOSES") {
              const conceptNode = nodes.find(
                (n) => n.id === link.target && (n.type === "concept" || n.type === "memory_type"),
              );
              if (conceptNode) {
                const name = conceptNode.name || conceptNode.label || conceptNode.id;
                conceptProposeCount.set(name, (conceptProposeCount.get(name) || 0) + 1);
              }
            }
          }
          const trendingList = Array.from(conceptProposeCount.entries())
            .map(([name, count]) => ({ name, count }))
            .sort((a, b) => b.count - a.count)
            .slice(0, 10);
          if (!cancelled) setTrending(trendingList);
        }
      } catch {
        // Client-side search will just not be available
      }
    }
    loadGraph();
    return () => { cancelled = true; };
  }, []);

  const searchLocal = useCallback(
    (q: string): GSearchResult[] => {
      if (!ragRef.current) {
        const lower = q.toLowerCase();
        const terms = lower.split(/\s+/).filter(Boolean);
        return graphNodes
          .map((node) => {
            const name = (node.name || node.label || node.id || "").toLowerCase();
            const desc = (node.description || (node.properties?.description as string) || "").toLowerCase();
            const text = `${name} ${desc}`;
            let matched = false;
            let score = 0;
            for (const term of terms) {
              if (text.includes(term)) {
                matched = true;
                if (name.includes(term)) score += 3;
                if (desc.includes(term)) score += 1;
              }
            }
            return matched
              ? {
                  name: node.name || node.label || node.id,
                  description: node.description || (node.properties?.description as string) || "",
                  type: node.type || "Unknown",
                  score,
                  match: name.includes(lower) ? "exact_name" : "description",
                }
              : null;
          })
          .filter((r): r is GSearchResult => r !== null)
          .sort((a, b) => b.score - a.score)
          .slice(0, 20);
      }
      return ragRef.current.search(q, 20);
    },
    [graphNodes],
  );

  return { searchLocal, trending };
}
