import { Badge } from "@/components/ui/Badge";

interface ConceptHeaderProps {
  name: string;
  type?: string;
  description?: string;
  category?: string;
  paperCount: number;
  sources?: string[];
}

export function ConceptHeader({ name, type, description, category, paperCount, sources }: ConceptHeaderProps) {
  return (
    <div className="mb-8">
      <div className="flex items-center gap-3 mb-2 flex-wrap">
        <h1 className="text-3xl font-bold">{name}</h1>
        {type && <Badge variant="info">{type}</Badge>}
        {category && <Badge>{category}</Badge>}
        {paperCount > 0 && (
          <Badge variant="success">
            {paperCount} paper{paperCount !== 1 ? "s" : ""}
          </Badge>
        )}
      </div>
      <p className="text-gray-600 text-lg mb-4">
        {description || "No description available."}
      </p>
      {sources && sources.length > 0 && (
        <div className="flex items-center gap-2 text-sm text-gray-500">
          <span>Sources:</span>
          {sources.map((s) => (
            <Badge key={s}>{s}</Badge>
          ))}
        </div>
      )}
    </div>
  );
}
