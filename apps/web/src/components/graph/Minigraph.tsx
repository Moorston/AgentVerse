"use client";

import { useEffect, useRef } from "react";
import cytoscape from "cytoscape";
import type { GraphNode } from "@/lib/search";
import type { GraphEdge } from "@/lib/search";

interface MinigraphProps {
  nodes: GraphNode[];
  edges: GraphEdge[];
  centerNodeId?: string;
  onNodeClick?: (nodeId: string) => void;
  className?: string;
}

const NODE_COLORS: Record<string, string> = {
  concept: "#3b82f6",
  paper: "#f59e0b",
  framework: "#10b981",
  memory_framework: "#ec4899",
  memory_type: "#06b6d4",
  protocol: "#8b5cf6",
  agent: "#ef4444",
};

export function Minigraph({
  nodes,
  edges,
  centerNodeId,
  onNodeClick,
  className = "",
}: MinigraphProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const cyRef = useRef<cytoscape.Core | null>(null);

  useEffect(() => {
    if (!containerRef.current || nodes.length === 0) return;

    const elements: cytoscape.ElementDefinition[] = [];

    for (const node of nodes) {
      elements.push({
        group: "nodes",
        data: {
          id: node.id,
          label: node.name || node.id,
          type: node.type,
        },
      });
    }

    for (const edge of edges) {
      elements.push({
        group: "edges",
        data: {
          id: `${edge.source}-${edge.target}`,
          source: edge.source,
          target: edge.target,
          label: edge.type,
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
            "background-color": (ele: cytoscape.NodeSingular) => {
              const t = ele.data("type");
              return NODE_COLORS[t] || "#6b7280";
            },
            color: "#fff",
            "text-valign": "center",
            "text-halign": "center",
            "font-size": "9px",
            width: 30,
            height: 30,
            "border-width": 2,
            "border-color": "#fff",
          } as cytoscape.Css.Node,
        },
        {
          selector: "edge",
          style: {
            label: "data(label)",
            width: 1.5,
            "line-color": "#94a3b8",
            "target-arrow-color": "#94a3b8",
            "target-arrow-shape": "triangle",
            "curve-style": "bezier",
            "font-size": "7px",
            color: "#64748b",
            "text-rotation": "autorotate",
          } as cytoscape.Css.Edge,
        },
        {
          selector: "node.highlighted",
          style: {
            "border-width": 4,
            "border-color": "#ffd700",
          } as cytoscape.Css.Node,
        },
      ],
      layout: {
        name: "breadthfirst",
        directed: true,
        spacingFactor: 1.2,
      } as cytoscape.LayoutOptions,
      minZoom: 0.3,
      maxZoom: 2,
      userZoomingEnabled: true,
      userPanningEnabled: true,
    });

    cyRef.current = cy;

    // Highlight center node if specified
    if (centerNodeId) {
      const centerEl = cy.getElementById(centerNodeId);
      if (centerEl.length > 0) {
        centerEl.addClass("highlighted");
      }
    }

    // Fit to view
    cy.fit(undefined, 40);

    // Click handler
    const onClick = (event: cytoscape.EventObject) => {
      const nodeId = event.target.id();
      onNodeClick?.(nodeId);
    };
    cy.on("tap", "node", onClick);

    return () => {
      cy.destroy();
      cyRef.current = null;
    };
  }, [nodes, edges, centerNodeId, onNodeClick]);

  if (nodes.length === 0) {
    return (
      <div className="flex items-center justify-center h-48 bg-gray-50 rounded-lg border border-dashed border-gray-300 text-sm text-gray-400">
        No subgraph data available
      </div>
    );
  }

  return (
    <div
      ref={containerRef}
      className={`border rounded-lg bg-white ${className}`}
      style={{ width: "100%", height: 300, minHeight: 300 }}
    />
  );
}