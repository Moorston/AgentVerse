interface GraphNode {
  id: string;
  type: string;
  name: string;
}

interface NodeTypeChartProps {
  nodes: GraphNode[];
}

const TYPE_COLORS: Record<string, string> = {
  concept: "bg-blue-500",
  paper: "bg-green-500",
  framework: "bg-purple-500",
  dataset: "bg-orange-500",
  method: "bg-pink-500",
};

function getTypeColor(type: string): string {
  return TYPE_COLORS[type] || "bg-gray-400";
}

export function NodeTypeChart({ nodes }: NodeTypeChartProps) {
  const dist: Record<string, number> = {};
  for (const n of nodes) {
    dist[n.type] = (dist[n.type] || 0) + 1;
  }

  const entries = Object.entries(dist).sort((a, b) => b[1] - a[1]);
  const total = nodes.length;

  if (total === 0) {
    return <p className="text-sm text-gray-400">No node data available.</p>;
  }

  return (
    <div className="space-y-3">
      {entries.map(([type, count]) => {
        const pct = ((count / total) * 100).toFixed(1);
        return (
          <div key={type}>
            <div className="flex justify-between text-sm mb-1">
              <span className="font-medium capitalize">{type}</span>
              <span className="text-gray-500">
                {count} <span className="text-xs">({pct}%)</span>
              </span>
            </div>
            <div className="w-full bg-gray-100 rounded-full h-2">
              <div
                className={`${getTypeColor(type)} h-2 rounded-full transition-all`}
                style={{ width: `${pct}%` }}
              />
            </div>
          </div>
        );
      })}
    </div>
  );
}
