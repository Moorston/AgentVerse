import { Card } from "@/components/ui/Card";
import Link from "next/link";

interface Paper {
  id: string;
  name: string;
  date?: string;
  authors?: string[];
}

interface ConceptPapersProps {
  papers: Paper[];
}

export function ConceptPapers({ papers }: ConceptPapersProps) {
  return (
    <Card title={`Papers Proposing This Concept (${papers.length})`}>
      {papers.length === 0 ? (
        <p className="text-sm text-gray-400">No papers propose this concept.</p>
      ) : (
        <ul className="space-y-2">
          {papers.map((paper) => (
            <li
              key={paper.id}
              className="text-sm border-b border-gray-100 pb-2 last:border-0"
            >
              <Link
                href={`/papers`}
                className="text-blue-600 hover:underline font-medium"
              >
                {paper.name}
              </Link>
              {paper.authors && paper.authors.length > 0 && (
                <p className="text-gray-500 text-xs mt-0.5">
                  {paper.authors.slice(0, 3).join(", ")}
                  {paper.authors.length > 3 ? " et al." : ""}
                </p>
              )}
            </li>
          ))}
        </ul>
      )}
    </Card>
  );
}
