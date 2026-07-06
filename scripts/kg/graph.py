"""In-memory knowledge graph data structure."""

import re
from typing import Any


class KnowledgeGraph:
    """In-memory knowledge graph with nodes and edges."""

    def __init__(self) -> None:
        self.nodes: dict[str, dict[str, Any]] = {}  # id -> node
        self.edges: list[dict[str, Any]] = []

    def add_node(self, node_id: str, **props: Any) -> None:
        """Add or merge a node."""
        if node_id in self.nodes:
            # Merge: update sources, keep richer description
            existing = self.nodes[node_id]
            new_sources = set(existing.get("sources", [])) | set(props.get("sources", []))
            existing["sources"] = sorted(new_sources)
            if props.get("description") and len(props.get("description", "")) > len(existing.get("description", "")):
                existing["description"] = props["description"]
            for k, v in props.items():
                if k not in existing or not existing[k]:
                    existing[k] = v
        else:
            self.nodes[node_id] = {"id": node_id, **props}

    def add_edge(self, source: str, target: str, edge_type: str, **props: Any) -> None:
        """Add an edge if it doesn't already exist."""
        for e in self.edges:
            if e["source"] == source and e["target"] == target and e["type"] == edge_type:
                return
        self.edges.append({"source": source, "target": target, "type": edge_type, **props})

    def to_d3(self) -> dict[str, Any]:
        """Export as D3.js force-directed graph format."""
        return {
            "nodes": list(self.nodes.values()),
            "links": [
                {"source": e["source"], "target": e["target"], "type": e["type"],
                 **{k: v for k, v in e.items() if k not in ("source", "target", "type")}}
                for e in self.edges
            ],
        }

    def stats(self) -> dict[str, int]:
        """Return graph statistics."""
        type_counts: dict[str, int] = {}
        for n in self.nodes.values():
            t = n.get("type", "unknown")
            type_counts[t] = type_counts.get(t, 0) + 1
        edge_type_counts: dict[str, int] = {}
        for e in self.edges:
            t = e.get("type", "unknown")
            edge_type_counts[t] = edge_type_counts.get(t, 0) + 1
        return {
            "total_nodes": len(self.nodes),
            "total_edges": len(self.edges),
            "node_types": type_counts,
            "edge_types": edge_type_counts,
        }


def normalize_name(name: str) -> str:
    """Normalize a concept name to PascalCase key."""
    name = name.strip()
    # Remove special chars, keep alphanumeric and spaces
    name = re.sub(r"[^a-zA-Z0-9\s]", "", name)
    words = name.split()
    if not words:
        return name
    # If already PascalCase-ish, return as-is
    if len(words) == 1 and words[0][0].isupper():
        return words[0]
    return "".join(w.capitalize() for w in words)
