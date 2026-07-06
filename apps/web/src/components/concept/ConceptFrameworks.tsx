import { Card } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";

interface Framework {
  id: string;
  name: string;
  relation: "IMPLEMENTS" | "SUPPORTS";
}

interface ConceptFrameworksProps {
  frameworks: Framework[];
}

export function ConceptFrameworks({ frameworks }: ConceptFrameworksProps) {
  const implementing = frameworks.filter((fw) => fw.relation === "IMPLEMENTS");
  const supporting = frameworks.filter((fw) => fw.relation === "SUPPORTS");

  return (
    <Card title={`Frameworks (${frameworks.length})`}>
      {frameworks.length === 0 ? (
        <p className="text-sm text-gray-400">
          No frameworks implement or support this concept.
        </p>
      ) : (
        <div className="space-y-3">
          {implementing.map((fw) => (
            <div key={fw.id} className="flex items-center justify-between text-sm">
              <span className="font-medium">{fw.name}</span>
              <Badge variant="success">IMPLEMENTS</Badge>
            </div>
          ))}
          {supporting.map((fw) => (
            <div key={fw.id} className="flex items-center justify-between text-sm">
              <span className="font-medium">{fw.name}</span>
              <Badge variant="warning">SUPPORTS</Badge>
            </div>
          ))}
        </div>
      )}
    </Card>
  );
}
