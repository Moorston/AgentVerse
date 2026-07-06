import { Card } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import Link from "next/link";

interface Concept {
  name: string;
  category?: string;
}

interface PaperConceptsProps {
  concepts: Concept[];
  loading: boolean;
}

export function PaperConcepts({ concepts, loading }: PaperConceptsProps) {
  if (loading) {
    return (
      <Card title="Concepts">
        <div className="space-y-2 animate-pulse">
          {[1, 2, 3].map((i) => (
            <div key={i} className="h-4 bg-gray-200 rounded w-2/3" />
          ))}
        </div>
      </Card>
    );
  }

  return (
    <Card title={`Concepts (${concepts.length})`}>
      {concepts.length === 0 ? (
        <p className="text-sm text-gray-400">No concepts extracted from this paper.</p>
      ) : (
        <ul className="space-y-2">
          {concepts.map((concept) => (
            <li
              key={concept.name}
              className="flex items-center justify-between text-sm border-b border-gray-100 pb-2 last:border-0"
            >
              <Link
                href={`/concept/${encodeURIComponent(concept.name)}`}
                className="text-blue-600 hover:underline font-medium"
              >
                {concept.name}
              </Link>
              {concept.category && (
                <Badge>{concept.category}</Badge>
              )}
            </li>
          ))}
        </ul>
      )}
    </Card>
  );
}
