import { Badge } from "@/components/ui/Badge";
import Link from "next/link";

interface PaperHeaderProps {
  name: string;
  authors?: string[];
  date?: string;
  arxivId?: string;
  abstract?: string;
  categories?: string[];
}

export function PaperHeader({ name, authors, date, arxivId, abstract, categories }: PaperHeaderProps) {
  return (
    <div className="mb-8">
      <h1 className="text-3xl font-bold mb-3">{name}</h1>

      {authors && authors.length > 0 && (
        <p className="text-gray-600 mb-2">
          {authors.join(", ")}
        </p>
      )}

      <div className="flex flex-wrap items-center gap-2 mb-4">
        {date && <Badge variant="info">{date}</Badge>}
        {arxivId && (
          <Link
            href={`https://arxiv.org/abs/${arxivId}`}
            target="_blank"
            rel="noopener noreferrer"
            className="text-sm text-blue-600 hover:underline"
          >
            arXiv: {arxivId}
          </Link>
        )}
        {categories &&
          categories.map((cat) => (
            <Badge key={cat}>{cat}</Badge>
          ))}
      </div>

      {abstract && (
        <p className="text-gray-600 text-base leading-relaxed">
          {abstract}
        </p>
      )}
    </div>
  );
}
