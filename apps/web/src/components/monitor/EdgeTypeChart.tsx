interface GraphLink {
  source: string;
  target: string;
  type: string;
}

interface EdgeTypeChartProps {
  links: GraphLink[];
}

const EDGE_COLORS: Record<string, string> = {
  PROPOSES: "bg-green-500",
  IMPLEMENTS: "bg-blue-500",
  SUPPORTS: "bg-yellow-500",
  RELATED_TO: "bg-purple-500",
  USES: "bg-orange-500",
};

function getEdgeColor(type: string): string {
  return EDGE_COLORS[type] || "bg-gray-400";
}

export function EdgeTypeChart({ links }: EdgeTypeChartProps) {
  const dist: Record<string, number> = {};
  for (const l of links) {
    dist[l.type] = (dist[l.type] || 0) + 1;
  }

  const entries = Object.entries(dist).sort((a, b) => b[1] - a[1]);
  const total = links.length;

  if (total === 0) {
    return <p className="text-sm text-gray-400">No edge data available.</p>;
  }

  return (
    <div className="space-y-3">
      {entries.map(([type, count]) => {
        const pct = ((count / total) * 100).toFixed(1);
        return (
          <div key={type}>
            <div className="flex justify-between text-sm mb-1">
              <span className="font-medium">{type}</span>
              <span className="text-gray-500">
                {count} <span className="text-xs">({pct}%)</span>
              </span>
            </div>
            <div className="w-full bg-gray-100 rounded-full h-2">
              <div
                className={`${getEdgeColor(type)} h-2 rounded-full transition-all`}
                style={{ width: `${pct}%` }}
              />
            </div>
          </div>
        );
      })}
    </div>
  );
}
