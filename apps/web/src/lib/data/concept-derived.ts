import type { KGraphNode, KGraphData } from "@/lib/types/graph";

export interface ConceptDerivedData {
  proposingPapers: KGraphNode[];
  frameworks: { id: string; name: string; relation: "IMPLEMENTS" | "SUPPORTS" }[];
  allRelations: { source: string; target: string; type: string }[];
  subgraphNodes: { id: string; type: string; name: string; description: string; category: string }[];
  subgraphEdges: { source: string; target: string; type: string }[];
}

export function buildConceptDerived(data: KGraphData, conceptId: string): ConceptDerivedData {
  const resolveNode = (id: string) => data.nodes.find((n) => n.id === id);
  const allRelations = data.links.filter(
    (e) => e.source === conceptId || e.target === conceptId,
  );

  const neighborIds = new Set<string>([conceptId]);
  for (const rel of allRelations) {
    if (rel.source === conceptId) neighborIds.add(rel.target);
    if (rel.target === conceptId) neighborIds.add(rel.source);
  }

  const subgraphNodes = Array.from(neighborIds)
    .map(resolveNode)
    .filter((n): n is KGraphNode => n !== undefined)
    .map((n) => ({ id: n.id, type: n.type, name: n.name || n.id, description: n.description || "", category: n.category || "" }));

  const subgraphEdges = allRelations
    .filter((e) => neighborIds.has(e.source) && neighborIds.has(e.target))
    .map((e) => ({ source: e.source, target: e.target, type: e.type }));

  const proposingPapers = data.links
    .filter((e) => e.type === "PROPOSES" && e.target === conceptId)
    .map((e) => resolveNode(e.source))
    .filter((n): n is KGraphNode => n !== undefined && n.type === "paper");

  const implementingFrameworks = data.links
    .filter((e) => e.type === "IMPLEMENTS" && e.target === conceptId)
    .map((e) => resolveNode(e.source))
    .filter((n): n is KGraphNode => n !== undefined && n.type === "framework")
    .map((n) => ({ id: n.id, name: n.name, relation: "IMPLEMENTS" as const }));

  const supportingFrameworks = data.links
    .filter((e) => e.type === "SUPPORTS" && e.target === conceptId)
    .map((e) => resolveNode(e.source))
    .filter((n): n is KGraphNode => n !== undefined && n.type === "framework")
    .map((n) => ({ id: n.id, name: n.name, relation: "SUPPORTS" as const }));

  return {
    proposingPapers,
    frameworks: [...implementingFrameworks, ...supportingFrameworks],
    allRelations,
    subgraphNodes,
    subgraphEdges,
  };
}
