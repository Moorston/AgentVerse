export interface KGraphNode {
  id: string;
  type: string;
  name: string;
  description?: string;
  category?: string;
  sources?: string[];
  authors?: string[];
  published_date?: string;
}

export interface KGraphLink {
  source: string;
  target: string;
  type: string;
}

export interface KGraphData {
  nodes: KGraphNode[];
  links: KGraphLink[];
}

export function parseGraphData(json: unknown): KGraphData {
  const raw = json as Record<string, unknown>;
  return {
    nodes: (raw.nodes as KGraphNode[]) || [],
    links: (raw.links || raw.edges || []) as KGraphLink[],
  };
}
