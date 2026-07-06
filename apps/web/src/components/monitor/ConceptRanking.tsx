import { Badge } from "@/components/ui/Badge";

interface GraphNode {
  id: string;
  type: string;
  name: string;
  category?: string;
}

interface GraphLink {
  source: string;
  target: string;
  type: string;
}

interface ConceptRankingProps {
  nodes: GraphNode[];
  links: GraphLink[];
}

interface RankedConcept {
  name: string;
  paperCount: number;
  category?: string;
}

export function ConceptRanking({ nodes, links }: ConceptRankingProps) {
  // Count PROPOSES edges per concept
  const conceptPaperCounts = new Map<string, number>();

  for (const link of links) {
    if (link.type === "PROPOSES") {
      const current = conceptPaperCounts.get(link.target) || 0;
      conceptPaperCounts.set(link.target, current + 1);
    }
  }

  // Build ranked list
  const ranked: RankedConcept[] = [];
  for (const [conceptId, paperCount] of conceptPaperCounts) {
    const node = nodes.find((n) => n.id === conceptId);
    if (node) {
      ranked.push({
        name: node.name || node.id,
        paperCount,
        category: node.category,
      });
    }
  }

  ranked.sort((a, b) => b.paperCount - a.paperCount);
  const top10 = ranked.slice(0, 10);

  if (top10.length === 0) {
    return <p className="text-sm text-gray-400">No concept ranking data available.</p>;
  }

  return (
    <ol className="space-y-2">
      {top10.map((concept, index) => (
        <li
          key={concept.name}
          className="flex items-center justify-between text-sm border-b border-gray-100 pb-2 last:border-0"
        >
          <div className="flex items-center gap-2">
            <span className="text-gray-400 text-xs w-5 text-right font-mono">{index + 1}.</span>
            <span className="font-medium">{concept.name}</span>
            {concept.category && <Badge>{concept.category}</Badge>}
          </div>
          <Badge variant="success">
            {concept.paperCount} paper{concept.paperCount !== 1 ? "s" : ""}
          </Badge>
        </li>
      ))}
    </ol>
  );
}
