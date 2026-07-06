export interface GraphNode {
  id: string;
  type: string;
  name: string;
  description?: string;
  category?: string;
  [key: string]: unknown;
}

export interface GraphEdge {
  source: string;
  target: string;
  type: string;
  evidence?: string;
}

export interface SearchResult {
  name: string;
  description: string;
  type: string;
  score: number;
  match: string; // "exact_name" | "description" | "neighbor"
}

export class MemoryGraphRAG {
  private nodes: Map<string, GraphNode>;
  private edges: GraphEdge[];
  private adjacency: Map<string, string[]>;

  constructor(data: { nodes: GraphNode[]; links: GraphEdge[] }) {
    this.nodes = new Map();
    this.edges = data.links || [];
    this.adjacency = new Map();

    // Build node index
    for (const node of data.nodes) {
      this.nodes.set(node.id, node);
    }

    // Build adjacency list (bidirectional for neighbor traversal and BFS)
    for (const link of this.edges) {
      const src = link.source;
      const tgt = link.target;

      if (!this.adjacency.has(src)) this.adjacency.set(src, []);
      if (!this.adjacency.has(tgt)) this.adjacency.set(tgt, []);

      if (!this.adjacency.get(src)!.includes(tgt)) {
        this.adjacency.get(src)!.push(tgt);
      }
      if (!this.adjacency.get(tgt)!.includes(src)) {
        this.adjacency.get(tgt)!.push(src);
      }
    }
  }

  search(query: string, topK: number = 10): SearchResult[] {
    const lower = query.toLowerCase().trim();
    if (!lower) return [];

    const terms = lower.split(/\s+/).filter(Boolean);
    if (terms.length === 0) return [];

    const scored: SearchResult[] = [];
    const exactMatchIds = new Set<string>();

    // Phase 1: Score all nodes by name and description
    for (const [, node] of this.nodes) {
      const name = (node.name || "").toLowerCase();
      const desc = (node.description || "").toLowerCase();
      const category = (node.category || "").toLowerCase();

      let totalScore = 0;
      let matched = false;
      let bestMatch = "";

      for (const term of terms) {
        if (name.includes(term)) {
          totalScore += 3;
          matched = true;
          bestMatch = "exact_name";
          exactMatchIds.add(node.id);
        }
        if (desc.includes(term)) {
          totalScore += 1;
          matched = true;
          if (bestMatch !== "exact_name") bestMatch = "description";
        }
        if (category.includes(term)) {
          totalScore += 0.5;
          matched = true;
          if (!bestMatch) bestMatch = "description";
        }
      }

      if (matched) {
        scored.push({
          name: node.name || node.id,
          description: node.description || "",
          type: node.type || "Unknown",
          score: totalScore,
          match: bestMatch,
        });
      }
    }

    // Phase 2: Add neighbors of exact-matched nodes (score 0.5)
    const existingNames = new Set(scored.map((s) => s.name));
    for (const id of exactMatchIds) {
      const neighbors = this.adjacency.get(id) || [];
      for (const nId of neighbors) {
        const node = this.nodes.get(nId);
        if (node && !existingNames.has(node.name || node.id)) {
          scored.push({
            name: node.name || node.id,
            description: node.description || "",
            type: node.type || "Unknown",
            score: 0.5,
            match: "neighbor",
          });
          existingNames.add(node.name || node.id);
        }
      }
    }

    // Sort by score descending, then alphabetically
    scored.sort((a, b) => b.score - a.score || a.name.localeCompare(b.name));
    return scored.slice(0, topK);
  }

  findPath(source: string, target: string): GraphEdge[] {
    if (source === target) return [];

    // BFS shortest path
    const visited = new Set<string>();
    const parent = new Map<string, { node: string; edge: GraphEdge } | null>();

    const queue: string[] = [source];
    visited.add(source);
    parent.set(source, null);

    while (queue.length > 0) {
      const current = queue.shift()!;
      if (current === target) break;

      const neighbors = this.adjacency.get(current) || [];
      for (const next of neighbors) {
        if (!visited.has(next)) {
          visited.add(next);
          // Find the edge that connects current to next
          const edge = this.edges.find(
            (e) =>
              (e.source === current && e.target === next) ||
              (e.target === current && e.source === next),
          );
          parent.set(next, {
            node: current,
            edge: edge || { source: current, target: next, type: "UNKNOWN" },
          });
          queue.push(next);
        }
      }
    }

    // Reconstruct path
    if (!parent.has(target)) return []; // No path found

    const path: GraphEdge[] = [];
    let current: string | null = target;
    while (current && parent.get(current)) {
      const entry: { node: string; edge: GraphEdge } = parent.get(current)!;
      path.unshift(entry.edge);
      current = entry.node;
    }

    return path;
  }

  getNode(id: string): GraphNode | undefined {
    return this.nodes.get(id);
  }

  getAllNodes(): GraphNode[] {
    return Array.from(this.nodes.values());
  }
}