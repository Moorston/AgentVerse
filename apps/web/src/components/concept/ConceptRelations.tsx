import { Card } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";

interface RelationEdge {
  source: string;
  target: string;
  type: string;
}

interface RelationNode {
  id: string;
  name: string;
  type: string;
}

interface ConceptRelationsProps {
  relations: RelationEdge[];
  nodes: RelationNode[];
  conceptType: string;
}

export function ConceptRelations({ relations, nodes, conceptType }: ConceptRelationsProps) {
  const resolveNode = (id: string) => nodes.find((n) => n.id === id);

  return (
    <Card title={`All Relationships (${relations.length})`}>
      {relations.length === 0 ? (
        <p className="text-sm text-gray-400">No relationships found.</p>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b text-left text-gray-500">
                <th className="pb-2 pr-4">Source</th>
                <th className="pb-2 pr-4">Type</th>
                <th className="pb-2">Target</th>
              </tr>
            </thead>
            <tbody>
              {relations.map((rel, i) => {
                const source = resolveNode(rel.source);
                const target = resolveNode(rel.target);
                return (
                  <tr key={i} className="border-b border-gray-100 last:border-0">
                    <td className="py-2 pr-4">
                      <span className="font-medium">{source?.name || rel.source}</span>
                      {source && source.type !== conceptType && (
                        <Badge className="ml-2">{source.type}</Badge>
                      )}
                    </td>
                    <td className="py-2 pr-4">
                      <Badge
                        variant={
                          rel.type === "PROPOSES" ? "success"
                            : rel.type === "IMPLEMENTS" ? "info"
                              : rel.type === "SUPPORTS" ? "warning"
                                : "default"
                        }
                      >
                        {rel.type}
                      </Badge>
                    </td>
                    <td className="py-2">
                      <span className="font-medium">{target?.name || rel.target}</span>
                      {target && target.type !== conceptType && (
                        <Badge className="ml-2">{target.type}</Badge>
                      )}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </Card>
  );
}
