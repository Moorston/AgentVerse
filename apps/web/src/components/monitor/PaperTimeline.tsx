import { Badge } from "@/components/ui/Badge";

interface GraphNode {
  id: string;
  type: string;
  name: string;
  published_date?: string;
}

interface PaperTimelineProps {
  nodes: GraphNode[];
}

export function PaperTimeline({ nodes }: PaperTimelineProps) {
  const papers = nodes
    .filter((n) => n.type === "paper" && n.published_date)
    .sort((a, b) => {
      const dateA = new Date(a.published_date!).getTime();
      const dateB = new Date(b.published_date!).getTime();
      return dateB - dateA;
    });

  if (papers.length === 0) {
    return <p className="text-sm text-gray-400">No paper dates available for timeline.</p>;
  }

  return (
    <div className="relative pl-6">
      {/* Vertical line */}
      <div className="absolute left-2 top-0 bottom-0 w-0.5 bg-gray-200" />

      <div className="space-y-4">
        {papers.map((paper) => (
          <div key={paper.id} className="relative">
            {/* Dot on the timeline */}
            <div className="absolute -left-4 top-1.5 w-2.5 h-2.5 rounded-full bg-blue-500 border-2 border-white" />

            <div className="ml-2">
              <Badge variant="info">{paper.published_date}</Badge>
              <p className="text-sm font-medium mt-1">{paper.name}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
