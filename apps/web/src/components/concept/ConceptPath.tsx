import { useState, useRef, useMemo, useCallback } from "react";
import { Card } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { MemoryGraphRAG } from "@/lib/search";
import type { GraphEdge } from "@/lib/search";

interface PathNode {
  id: string;
  name: string;
  type: string;
  description?: string;
  category?: string;
}

interface PathLink {
  source: string;
  target: string;
  type: string;
}

interface ConceptPathProps {
  graphNodes: PathNode[];
  graphLinks: PathLink[];
  conceptNodeId: string;
  conceptName: string;
}

export function ConceptPath({ graphNodes, graphLinks, conceptNodeId, conceptName }: ConceptPathProps) {
  const [pathTarget, setPathTarget] = useState("");
  const [pathEdges, setPathEdges] = useState<GraphEdge[]>([]);
  const [pathError, setPathError] = useState("");
  const ragRef = useRef<MemoryGraphRAG | null>(null);

  useMemo(() => {
    const mnodes = graphNodes.map((n) => ({
      id: n.id,
      type: n.type,
      name: n.name || n.id,
      description: n.description || "",
      category: n.category || "",
    }));
    const medges = graphLinks.map((l) => ({
      source: l.source,
      target: l.target,
      type: l.type,
    }));
    ragRef.current = new MemoryGraphRAG({ nodes: mnodes, links: medges });
  }, [graphNodes, graphLinks]);

  const handleFindPath = useCallback(() => {
    if (!ragRef.current || !pathTarget.trim()) return;
    setPathError("");

    const targetNode = graphNodes.find(
      (n) =>
        n.name.toLowerCase() === pathTarget.trim().toLowerCase() ||
        n.id.toLowerCase() === pathTarget.trim().toLowerCase(),
    );
    if (!targetNode) {
      setPathError(`No concept found matching "${pathTarget.trim()}"`);
      setPathEdges([]);
      return;
    }

    const edges = ragRef.current.findPath(conceptNodeId, targetNode.id);
    setPathEdges(edges);
    if (edges.length === 0) {
      setPathError(`No path found between "${conceptName}" and "${targetNode.name}"`);
    }
  }, [conceptNodeId, conceptName, graphNodes, pathTarget]);

  const resolveNodeName = useCallback(
    (id: string) => graphNodes.find((n) => n.id === id)?.name || id,
    [graphNodes],
  );

  return (
    <Card title="Path Discovery">
      <p className="text-sm text-gray-500 mb-3">
        Find the shortest path between <strong>{conceptName}</strong> and another concept.
      </p>
      <div className="flex gap-2 mb-3">
        <input
          type="text"
          value={pathTarget}
          onChange={(e) => setPathTarget(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter") handleFindPath();
          }}
          placeholder="Enter target concept name..."
          className="flex-1 px-3 py-2 border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
        <button
          onClick={handleFindPath}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm hover:bg-blue-700 transition"
        >
          Find Path
        </button>
      </div>

      {pathError && (
        <div className="mb-3 p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-xs">
          {pathError}
        </div>
      )}

      {pathEdges.length > 0 && (
        <div className="bg-gray-50 rounded-lg p-4">
          <p className="text-xs font-medium text-gray-500 mb-2">Path:</p>
          <div className="flex flex-wrap items-center gap-1 text-sm">
            <span className="font-semibold text-blue-700">{conceptName}</span>
            {pathEdges.map((edge, i) => (
              <span key={i} className="flex items-center gap-1">
                <span className="text-gray-400 mx-1">&rarr;</span>
                <Badge
                  variant={
                    edge.type === "PROPOSES"
                      ? "success"
                      : edge.type === "IMPLEMENTS"
                        ? "info"
                        : edge.type === "SUPPORTS"
                          ? "warning"
                          : edge.type === "EXTENDS"
                            ? "info"
                            : "default"
                  }
                >
                  {edge.type}
                </Badge>
                <span className="text-gray-400 mx-1">&rarr;</span>
                <span className="font-semibold text-blue-700">
                  {resolveNodeName(edge.target)}
                </span>
              </span>
            ))}
          </div>
        </div>
      )}
    </Card>
  );
}
