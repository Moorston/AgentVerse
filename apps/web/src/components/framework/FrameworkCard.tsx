import { Card } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { FrameworkRecommendation } from "@/lib/recommend";

interface FrameworkData {
  name: string;
  description: string;
  stars: number;
  language?: string;
  github_url?: string;
  updated_at?: string;
  implements: string[];
}

interface FrameworkCardProps {
  framework: FrameworkData;
  onClick: () => void;
  recommendations?: FrameworkRecommendation[];
}

export function FrameworkCard({ framework, onClick, recommendations }: FrameworkCardProps) {
  return (
    <Card title={framework.name} onClick={onClick}>
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          {framework.language && <Badge>{framework.language}</Badge>}
        </div>
        <div className="flex items-center gap-2">
          {framework.stars > 0 && (
            <span className="text-sm text-gray-500">
              ⭐ {framework.stars.toLocaleString()}
            </span>
          )}
        </div>
      </div>

      {framework.updated_at && (
        <p className="text-xs text-gray-400 mb-2">
          Last updated:{" "}
          {new Date(framework.updated_at).toLocaleDateString("en-US", {
            year: "numeric",
            month: "short",
            day: "numeric",
          })}
        </p>
      )}

      {framework.description && (
        <p className="text-gray-600 text-sm mb-4">{framework.description}</p>
      )}

      {framework.github_url && (
        <a
          href={framework.github_url}
          target="_blank"
          rel="noopener noreferrer"
          className="text-xs text-blue-500 hover:underline block mb-3"
          onClick={(e) => e.stopPropagation()}
        >
          {framework.github_url}
        </a>
      )}

      {framework.implements.length > 0 && (
        <div className="pt-3 border-t border-gray-100">
          <p className="text-xs font-medium text-gray-500 mb-2">
            Concepts implemented:
          </p>
          <div className="flex flex-wrap gap-1">
            {framework.implements.map((impl) => (
              <Badge key={impl} variant="info">
                {impl}
              </Badge>
            ))}
          </div>
        </div>
      )}

      {recommendations && recommendations.length > 0 && (
        <p className="text-xs text-gray-400 mt-2">
          Similar: {recommendations.slice(0, 2).map(r => r.name.split("/").pop()).join(", ")}
        </p>
      )}
    </Card>
  );
}
