import { useEffect, useState, useMemo } from "react";
import { apiFetch } from "@/lib/api";
import { DEMO_FRAMEWORKS } from "@/lib/data/demo-frameworks";

export interface Framework {
  name: string;
  description: string;
  stars: number;
  language?: string;
  github_url?: string;
  implements: string[];
  updated_at?: string;
}

interface KGraphNode {
  id: string;
  name: string;
  type: string;
  updated_at?: string;
}

interface KGraphLink {
  source: string;
  target: string;
  type: string;
}

export function useFrameworks() {
  const [frameworks, setFrameworks] = useState<Framework[]>([]);
  const [loading, setLoading] = useState(true);
  const [graphConcepts, setGraphConcepts] = useState<Map<string, string[]>>(new Map());
  const [graphUpdatedAt, setGraphUpdatedAt] = useState<Map<string, string>>(new Map());

  useEffect(() => {
    let cancelled = false;
    async function load() {
      const graphPromise = fetch("/data/knowledge_graph.json")
        .then(async (res) => {
          if (res.ok) {
            const json = await res.json();
            const links: KGraphLink[] = json.links || json.edges || [];
            const nodes: KGraphNode[] = json.nodes || [];
            const implMap = new Map<string, string[]>();
            const updatedAtMap = new Map<string, string>();

            const frameworkIds = new Set(
              nodes.filter((n) => n.type === "framework").map((n) => n.id),
            );

            for (const node of nodes) {
              if (node.type === "framework" && node.updated_at) {
                updatedAtMap.set(node.name, node.updated_at);
              }
            }

            for (const link of links) {
              if (link.type !== "IMPLEMENTS") continue;
              const conceptNode = nodes.find((n) => n.id === link.target);
              const conceptName = conceptNode?.name || link.target;

              if (frameworkIds.has(link.source)) {
                const existing = implMap.get(link.source) || [];
                existing.push(conceptName);
                implMap.set(link.source, existing);
              } else if (frameworkIds.has(link.target)) {
                const fwId = link.target;
                const conceptNode2 = nodes.find((n) => n.id === link.source);
                const conceptName2 = conceptNode2?.name || link.source;
                const existing = implMap.get(fwId) || [];
                existing.push(conceptName2);
                implMap.set(fwId, existing);
              }
            }

            return { implMap, updatedAtMap };
          }
          return { implMap: new Map<string, string[]>(), updatedAtMap: new Map<string, string>() };
        })
        .catch(() => ({
          implMap: new Map<string, string[]>(),
          updatedAtMap: new Map<string, string>(),
        }));

      let fwData: Framework[] = [];
      try {
        const data = await apiFetch<Framework[]>("/api/v1/frameworks/?size=50");
        if (!cancelled) fwData = data;
      } catch {
        // Fall through
      }

      if (fwData.length === 0 && !cancelled) {
        try {
          const res = await fetch("/data/frameworks.json");
          if (res.ok) {
            const data = await res.json();
            fwData = Array.isArray(data) ? data : data.frameworks || [];
          }
        } catch {
          // Final fallback
        }
      }

      if (!cancelled) {
        if (fwData.length === 0) fwData = [...DEMO_FRAMEWORKS];
        setFrameworks(fwData);

        const { implMap, updatedAtMap } = await graphPromise;
        if (implMap.size > 0) setGraphConcepts(implMap);
        if (updatedAtMap.size > 0) setGraphUpdatedAt(updatedAtMap);
        setLoading(false);
      }
    }
    load();
    return () => { cancelled = true; };
  }, []);

  const mergedFrameworks = useMemo(() => {
    return frameworks.map((fw) => {
      const graphImpl = graphConcepts.get(fw.name) || [];
      const combined = [...new Set([...fw.implements, ...graphImpl])];
      return {
        ...fw,
        implements: combined,
        updated_at: graphUpdatedAt.get(fw.name) || fw.updated_at,
      };
    });
  }, [frameworks, graphConcepts, graphUpdatedAt]);

  return { frameworks: mergedFrameworks, loading };
}
