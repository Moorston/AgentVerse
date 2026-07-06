import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";

interface FrameworkData {
  name: string;
  description: string;
  stars: number;
  language?: string;
  github_url?: string;
  updated_at?: string;
  implements: string[];
}

interface FrameworkModalProps {
  framework: FrameworkData;
  onClose: () => void;
}

export function FrameworkModal({ framework, onClose }: FrameworkModalProps) {
  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4"
      onClick={onClose}
    >
      <div
        className="bg-white rounded-xl max-w-lg w-full p-6 shadow-xl"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-bold">
            {framework.name.split("/").pop() || framework.name}
          </h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 text-xl leading-none"
          >
            ✕
          </button>
        </div>

        <p className="text-sm text-gray-500 mb-1">{framework.name}</p>

        {framework.description && (
          <p className="text-gray-600 text-sm mb-4">{framework.description}</p>
        )}

        <div className="grid grid-cols-2 gap-4 mb-4">
          {framework.language && (
            <div>
              <p className="text-xs text-gray-400 font-medium">Language</p>
              <Badge>{framework.language}</Badge>
            </div>
          )}
          {framework.stars > 0 && (
            <div>
              <p className="text-xs text-gray-400 font-medium">GitHub Stars</p>
              <p className="text-sm font-semibold">
                ⭐ {framework.stars.toLocaleString()}
              </p>
            </div>
          )}
          {framework.updated_at && (
            <div>
              <p className="text-xs text-gray-400 font-medium">Last Updated</p>
              <p className="text-sm">
                {new Date(framework.updated_at).toLocaleDateString("en-US", {
                  year: "numeric",
                  month: "long",
                  day: "numeric",
                })}
              </p>
            </div>
          )}
        </div>

        {framework.github_url && (
          <a
            href={framework.github_url}
            target="_blank"
            rel="noopener noreferrer"
            className="text-sm text-blue-500 hover:underline block mb-4"
          >
            View on GitHub &rarr;
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

        <div className="mt-4 pt-3 border-t border-gray-100 flex justify-end">
          <Button variant="secondary" onClick={onClose}>
            Close
          </Button>
        </div>
      </div>
    </div>
  );
}
