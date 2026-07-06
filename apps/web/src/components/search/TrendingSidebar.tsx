import { Card } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";

interface TrendingItem {
  name: string;
  count: number;
}

interface TrendingSidebarProps {
  trending: TrendingItem[];
}

export function TrendingSidebar({ trending }: TrendingSidebarProps) {
  return (
    <aside className="w-72 shrink-0">
      {trending.length > 0 && (
        <Card title="Trending Concepts" className="mb-6">
          <p className="text-xs text-gray-400 mb-3">
            Top concepts by paper count
          </p>
          <ol className="space-y-2">
            {trending.map((item, i) => (
              <li key={item.name} className="flex items-center justify-between text-sm">
                <span className="flex items-center gap-2">
                  <span className="text-xs font-medium text-gray-400 w-4 text-right">
                    {i + 1}.
                  </span>
                  <span className="font-medium">{item.name}</span>
                </span>
                <Badge variant="info">{item.count} papers</Badge>
              </li>
            ))}
          </ol>
        </Card>
      )}

      <Card title="Search Tips" className="mb-6">
        <ul className="text-xs text-gray-500 space-y-1.5">
          <li>Try searching by concept name for exact matches</li>
          <li>Use partial words for description matches</li>
          <li>Switch to Local Search for offline RAG scoring</li>
          <li>Neighbor results show related concepts</li>
        </ul>
      </Card>
    </aside>
  );
}
