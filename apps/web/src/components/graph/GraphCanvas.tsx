"use client";

import { useEffect, useRef, useCallback } from "react";
import cytoscape from "cytoscape";
import type { GraphData } from "@/types/graph";

interface GraphCanvasProps {
  data: GraphData;
  onNodeClick?: (nodeId: string) => void;
  className?: string;
}

const NODE_COLORS: Record<string, string> = {
  Concept: "#3b82f6",
  Agent: "#8b5cf6",
  Framework: "#10b981",
  Paper: "#f59e0b",
  Protocol: "#ef4444",
  MemoryFramework: "#ec4899",
  MemoryType: "#06b6d4",
  Product: "#84cc16",
  News: "#6366f1",
  Pattern: "#f97316",
};

export function GraphCanvas({ data, onNodeClick, className }: GraphCanvasProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const cyRef = useRef<cytoscape.Core | null>(null);

  const getNodeColor = useCallback((types: string[]): string => {
    for (const t of types) {
      if (NODE_COLORS[t]) return NODE_COLORS[t];
    }
    return "#6b7280";
  }, []);

  useEffect(() => {
    if (!containerRef.current) return;

    const elements: cytoscape.ElementDefinition[] = [];

    // Add nodes
    for (const node of data.nodes) {
      elements.push({
        group: "nodes",
        data: {
          id: node.id,
          label: node.label,
          type: node.type,
          ...node.properties,
        },
      });
    }

    // Add edges
    for (const edge of data.edges) {
      elements.push({
        group: "edges",
        data: {
          id: edge.id,
          source: edge.source,
          target: edge.target,
          label: edge.type,
          ...edge.properties,
        },
      });
    }

    const cy = cytoscape({
      container: containerRef.current,
      elements,
      style: [
        {
          selector: "node",
          style: {
            label: "data(label)",
            "background-color": (ele: cytoscape.NodeSingular) =>
              getNodeColor(ele.data("type") ? [ele.data("type")] : []),
            color: "#fff",
            "text-valign": "center",
            "text-halign": "center",
            "font-size": "10px",
            width: 40,
            height: 40,
            "border-width": 2,
            "border-color": "#fff",
          } as cytoscape.Css.Node,
        },
        {
          selector: "edge",
          style: {
            label: "data(label)",
            width: 2,
            "line-color": "#94a3b8",
            "target-arrow-color": "#94a3b8",
            "target-arrow-shape": "triangle",
            "curve-style": "bezier",
            "font-size": "8px",
            color: "#64748b",
            "text-rotation": "autorotate",
          } as cytoscape.Css.Edge,
        },
      ],
      layout: {
        name: "dagre",
        rankDir: "TB",
        nodeSep: 50,
        rankSep: 80,
      } as cytoscape.LayoutOptions,
      minZoom: 0.2,
      maxZoom: 3,
    });

    // Handle node click
    cy.on("tap", "node", (event) => {
      const nodeId = event.target.id();
      onNodeClick?.(nodeId);
    });

    cyRef.current = cy;

    return () => {
      cy.destroy();
      cyRef.current = null;
    };
  }, [data, getNodeColor, onNodeClick]);

  return (
    <div
      ref={containerRef}
      className={className}
      style={{ width: "100%", height: "100%", minHeight: 400 }}
    />
  );
}