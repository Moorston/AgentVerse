import { Badge } from "@/components/ui/Badge";

export type ModuleStatus = "completed" | "in_progress" | "planned";

interface ModuleItemProps {
  name: string;
  status: ModuleStatus;
  description: string;
}

const STATUS_CONFIG: Record<ModuleStatus, { icon: string; label: string; variant: "success" | "warning" | "default" }> = {
  completed: { icon: "✅", label: "Completed", variant: "success" },
  in_progress: { icon: "🔄", label: "In Progress", variant: "warning" },
  planned: { icon: "⬜", label: "Planned", variant: "default" },
};

export function ModuleItem({ name, status, description }: ModuleItemProps) {
  const config = STATUS_CONFIG[status];

  return (
    <div className="flex items-start gap-3 py-3 border-b border-gray-100 last:border-b-0">
      <span className="text-sm mt-0.5 flex-shrink-0" title={config.label}>
        {config.icon}
      </span>
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2 mb-1">
          <span className="font-medium text-sm text-gray-900">{name}</span>
          <Badge variant={config.variant}>{config.label}</Badge>
        </div>
        <p className="text-xs text-gray-500 leading-relaxed">{description}</p>
      </div>
    </div>
  );
}
