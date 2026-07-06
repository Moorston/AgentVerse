import type { KGraphData, KGraphNode } from "@/lib/types/graph";

export interface ComparisonResult {
  conceptA: { name: string; papers: string[]; frameworks: string[]; relations: string[] };
  conceptB: { name: string; papers: string[]; frameworks: string[]; relations: string[] };
  common: { papers: string[]; frameworks: string[]; relations: string[] };
  uniqueToA: { papers: string[]; frameworks: string[]; relations: string[] };
  uniqueToB: { papers: string[]; frameworks: string[]; relations: string[] };
}

function resolveNode(nodes: KGraphNode[], id: string): string {
  const node = nodes.find((n) => n.id === id);
  return node?.name || id;
}

function getLinkedNames(
  graphData: KGraphData,
  conceptId: string,
  edgeType: string,
  nodeType: string,
): string[] {
  return graphData.links
    .filter((e) => {
      if (edgeType === "PROPOSES") {
        return e.type === edgeType && e.target === conceptId;
      }
      return e.type === edgeType && (e.source === conceptId || e.target === conceptId);
    })
    .map((e) => {
      const otherId = e.source === conceptId ? e.target : e.source;
      const otherNode = graphData.nodes.find((n) => n.id === otherId);
      return otherNode?.name || otherId;
    })
    .filter((name, i, arr) => arr.indexOf(name) === i);
}

function getRelationStrings(graphData: KGraphData, conceptId: string): string[] {
  return graphData.links
    .filter((e) => e.source === conceptId || e.target === conceptId)
    .map((e) => {
      const sourceName = resolveNode(graphData.nodes, e.source);
      const targetName = resolveNode(graphData.nodes, e.target);
      return `${sourceName} --${e.type}--> ${targetName}`;
    });
}

function intersect(a: string[], b: string[]): string[] {
  const setB = new Set(b);
  return a.filter((item) => setB.has(item));
}

function diff(from: string[], exclude: string[]): string[] {
  const excluded = new Set(exclude);
  return from.filter((item) => !excluded.has(item));
}

export function compareConcepts(
  graphData: KGraphData,
  conceptA: string,
  conceptB: string,
): ComparisonResult {
  const nodeA = graphData.nodes.find(
    (n) => n.name === conceptA || n.id === conceptA || n.id.toLowerCase() === conceptA.toLowerCase(),
  );
  const nodeB = graphData.nodes.find(
    (n) => n.name === conceptB || n.id === conceptB || n.id.toLowerCase() === conceptB.toLowerCase(),
  );

  const idA = nodeA?.id || conceptA;
  const idB = nodeB?.id || conceptB;

  const papersA = getLinkedNames(graphData, idA, "PROPOSES", "paper");
  const papersB = getLinkedNames(graphData, idB, "PROPOSES", "paper");

  const implementsA = getLinkedNames(graphData, idA, "IMPLEMENTS", "framework");
  const supportsA = getLinkedNames(graphData, idA, "SUPPORTS", "framework");
  const frameworksA = [...implementsA, ...supportsA].filter((v, i, a) => a.indexOf(v) === i);

  const implementsB = getLinkedNames(graphData, idB, "IMPLEMENTS", "framework");
  const supportsB = getLinkedNames(graphData, idB, "SUPPORTS", "framework");
  const frameworksB = [...implementsB, ...supportsB].filter((v, i, a) => a.indexOf(v) === i);

  const relationsA = getRelationStrings(graphData, idA);
  const relationsB = getRelationStrings(graphData, idB);

  return {
    conceptA: { name: nodeA?.name || conceptA, papers: papersA, frameworks: frameworksA, relations: relationsA },
    conceptB: { name: nodeB?.name || conceptB, papers: papersB, frameworks: frameworksB, relations: relationsB },
    common: {
      papers: intersect(papersA, papersB),
      frameworks: intersect(frameworksA, frameworksB),
      relations: intersect(relationsA, relationsB),
    },
    uniqueToA: {
      papers: diff(papersA, papersB),
      frameworks: diff(frameworksA, frameworksB),
      relations: diff(relationsA, relationsB),
    },
    uniqueToB: {
      papers: diff(papersB, papersA),
      frameworks: diff(frameworksB, frameworksA),
      relations: diff(relationsB, relationsA),
    },
  };
}
