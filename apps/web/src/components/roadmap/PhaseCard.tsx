import { Card } from "@/components/ui/Card";
import { ModuleItem, type ModuleStatus } from "./ModuleItem";

interface Module {
  name: string;
  status: ModuleStatus;
  description: string;
}

interface Phase {
  name: string;
  description: string;
  modules: Module[];
}

interface PhaseCardProps {
  phase: Phase;
}

export function PhaseCard({ phase }: PhaseCardProps) {
  return (
    <Card title={phase.name} className="mb-6">
      <p className="text-sm text-gray-500 mb-4">{phase.description}</p>
      <div className="divide-y divide-gray-100">
        {phase.modules.map((mod) => (
          <ModuleItem
            key={mod.name}
            name={mod.name}
            status={mod.status}
            description={mod.description}
          />
        ))}
      </div>
    </Card>
  );
}
