"use client";

import { useEffect, useRef, useCallback } from "react";
import cytoscape from "cytoscape";
import type { GraphData } from "@/types/graph";

interface GraphCanvasProps {
  data: GraphData;
  onNodeClick?: (nodeId: string) => void;
  onNodeDoubleClick?: (nodeId: string) => void;
  filterType?: string[];
  edgeFilter?: string[];
  highlightNode?: string;
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

export function GraphCanvas({
  data,
  onNodeClick,
  onNodeDoubleClick,
  filterType,
  edgeFilter,
  highlightNode,
  className,
}: GraphCanvasProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const cyRef = useRef<cytoscape.Core | null>(null);

  const getNodeColor = useCallback((types: string[]): string => {
    for (const t of types) {
      if (NODE_COLORS[t]) return NODE_COLORS[t];
    }
    return "#6b7280";
  }, []);

  // ── Initialise Cytoscape instance ─────────────────────────────
  useEffect(() => {
    if (!containerRef.current) return;

    const elements: cytoscape.ElementDefinition[] = [];

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

    cyRef.current = cy;

    return () => {
      cy.destroy();
      cyRef.current = null;
    };
  }, [data, getNodeColor]);

  // ── Single-tap / double-tap detection ─────────────────────────
  useEffect(() => {
    const cy = cyRef.current;
    if (!cy) return;

    let lastTapTime = 0;
    let singleTapTimer: ReturnType<typeof setTimeout> | null = null;

    const onTapNode = (event: cytoscape.EventObject) => {
      const nodeId = event.target.id();
      const now = Date.now();

      if (now - lastTapTime < 300) {
        // Double-tap detected
        if (singleTapTimer !== null) {
          clearTimeout(singleTapTimer);
          singleTapTimer = null;
        }
        onNodeDoubleClick?.(nodeId);
        lastTapTime = 0;
      } else {
        lastTapTime = now;
        singleTapTimer = setTimeout(() => {
          onNodeClick?.(nodeId);
          singleTapTimer = null;
        }, 300);
      }
    };

    cy.on("tap", "node", onTapNode);

    return () => {
      cy.off("tap", "node", onTapNode);
      if (singleTapTimer !== null) {
        clearTimeout(singleTapTimer);
      }
    };
  }, [onNodeClick, onNodeDoubleClick]);

  // ── Filter nodes by type ───────────────────────────────────────
  useEffect(() => {
    const cy = cyRef.current;
    if (!cy) return;

    if (!filterType || filterType.length === 0) {
      cy.nodes().show();
      cy.edges().show();
    } else {
      cy.nodes().forEach((node) => {
        const nodeType = node.data("type");
        if (filterType.includes(nodeType)) {
          node.show();
        } else {
          node.hide();
        }
      });
      // Only show edges connecting two visible nodes
      cy.edges().forEach((edge) => {
        if (edge.source().visible() && edge.target().visible()) {
          edge.show();
        } else {
          edge.hide();
        }
      });
    }
  }, [filterType]);

  // ── Filter edges by relationship type ──────────────────────────
  useEffect(() => {
    const cy = cyRef.current;
    if (!cy) return;

    if (!edgeFilter || edgeFilter.length === 0) {
      cy.edges().forEach((edge) => {
        edge.style({ opacity: 1 });
      });
    } else {
      cy.edges().forEach((edge) => {
        const edgeType = edge.data("label");
        if (edgeFilter.includes(edgeType)) {
          edge.style({ opacity: 1 });
        } else {
          edge.style({ opacity: 0 });
        }
      });
    }
  }, [edgeFilter]);

  // ── Highlight node and its 1-hop neighbours ────────────────────
  useEffect(() => {
    const cy = cyRef.current;
    if (!cy) return;

    // Reset to defaults
    cy.nodes().style({
      opacity: 1,
      "border-width": 2,
      "border-color": "#fff",
    });
    cy.edges().style({
      opacity: 1,
      width: 2,
    });

    if (!highlightNode) return;

    const targetNode = cy.getElementById(highlightNode);
    if (targetNode.length === 0) return;

    const neighbors = targetNode.neighborhood().nodes();
    const allRelated = targetNode.add(neighbors);

    // Dim everything outside the 1-hop neighbourhood
    cy.nodes().not(allRelated).style({ opacity: 0.15 });
    cy.edges().forEach((edge) => {
      const src = edge.source();
      const tgt = edge.target();
      if (!allRelated.contains(src) || !allRelated.contains(tgt)) {
        edge.style({ opacity: 0.1 });
      }
    });

    // Highlight the target node (gold border)
    targetNode.style({
      "border-width": 4,
      "border-color": "#ffd700",
    });

    // Highlight 1-hop neighbours (orange border)
    neighbors.style({
      "border-width": 3,
      "border-color": "#ffa500",
    });
  }, [highlightNode]);

  return (
    <div
      ref={containerRef}
      className={className}
      style={{ width: "100%", height: "100%", minHeight: 400 }}
    />
  );
}