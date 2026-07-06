import { useMemo } from "react";
import { Card } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";

interface FrameworkData {
  name: string;
  description: string;
  stars: number;
  language?: string;
  updated_at?: string;
  implements: string[];
}

interface SimilarFrameworksProps {
  frameworks: FrameworkData[];
  onFrameworkClick: (fw: FrameworkData) => void;
}

export function SimilarFrameworks({ frameworks, onFrameworkClick }: SimilarFrameworksProps) {
  const pairs = useMemo(() => {
    const result: { source: FrameworkData; target: FrameworkData; shared: string[] }[] = [];
    for (let i = 0; i < frameworks.length; i++) {
      for (let j = i + 1; j < frameworks.length; j++) {
        const a = frameworks[i];
        const b = frameworks[j];
        const aSet = new Set(a.implements);
        const shared = b.implements.filter((impl) => aSet.has(impl));
        if (shared.length >= 2) {
          result.push({ source: a, target: b, shared });
        }
      }
    }
    return result;
  }, [frameworks]);

  if (pairs.length === 0) return null;

  return (
    <div className="mt-12">
      <h2 className="text-xl font-semibold mb-4">Similar Frameworks</h2>
      <p className="text-sm text-gray-500 mb-4">
        Frameworks sharing 2+ concepts
      </p>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {pairs.slice(0, 8).map((pair, i) => (
          <Card key={i} title="">
            <div className="flex items-center justify-between gap-4 text-sm">
              <span
                className="font-medium text-blue-700 cursor-pointer hover:underline"
                onClick={() => onFrameworkClick(pair.source)}
              >
                {pair.source.name.split("/").pop() || pair.source.name}
              </span>
              <div className="flex flex-wrap gap-1 justify-center">
                {pair.shared.map((s) => (
                  <Badge key={s} variant="info" className="text-[10px]">
                    {s}
                  </Badge>
                ))}
              </div>
              <span
                className="font-medium text-blue-700 cursor-pointer hover:underline"
                onClick={() => onFrameworkClick(pair.target)}
              >
                {pair.target.name.split("/").pop() || pair.target.name}
              </span>
            </div>
          </Card>
        ))}
      </div>
    </div>
  );
}
