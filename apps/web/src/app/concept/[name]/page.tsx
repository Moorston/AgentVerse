"use client";

import { useMemo } from "react";
import { useParams, useRouter } from "next/navigation";
import { LoadingSkeleton } from "@/components/ui/Loading";
import { ErrorBanner } from "@/components/ui/ErrorBanner";
import { useFetch } from "@/hooks/useFetch";
import { ConceptHeader } from "@/components/concept/ConceptHeader";
import { ConceptPapers } from "@/components/concept/ConceptPapers";
import { ConceptFrameworks } from "@/components/concept/ConceptFrameworks";
import { ConceptRelations } from "@/components/concept/ConceptRelations";
import { ConceptPath } from "@/components/concept/ConceptPath";
import { Minigraph } from "@/components/graph/Minigraph";
import { parseGraphData } from "@/lib/types/graph";
import { buildConceptDerived } from "@/lib/data/concept-derived";
import type { KGraphData } from "@/lib/types/graph";
import Link from "next/link";
import { UI_TEXT } from "@/lib/i18n";

export default function ConceptDetailPage() {
  const params = useParams();
  const router = useRouter();
  const nameParam = typeof params.name === "string" ? decodeURIComponent(params.name) : "";

  const { data, loading, error, refetch } = useFetch<KGraphData>(
    "/data/knowledge_graph.json",
    { parser: parseGraphData },
  );

  const conceptNode = useMemo(() => {
    if (!data) return undefined;
    return data.nodes.find(
      (n) => n.name === nameParam || n.id === nameParam || n.id.toLowerCase() === nameParam.toLowerCase(),
    );
  }, [data, nameParam]);

  const derived = useMemo(() => {
    if (!data || !conceptNode) return null;
    return buildConceptDerived(data, conceptNode.id);
  }, [data, conceptNode]);

  if (loading) return <main className="min-h-screen bg-gray-50 p-8"><h1 className="text-3xl font-bold mb-6">{UI_TEXT.conceptDetail}</h1><LoadingSkeleton rows={5} /></main>;
  if (error) return <main className="min-h-screen bg-gray-50 p-8"><h1 className="text-3xl font-bold mb-6">{UI_TEXT.conceptDetail}</h1><ErrorBanner message={error} onRetry={refetch} /></main>;
  if (!data) return <main className="min-h-screen bg-gray-50 p-8"><h1 className="text-3xl font-bold mb-6">{UI_TEXT.conceptDetail}</h1><p className="text-gray-500">No data available.</p></main>;
  if (!conceptNode) {
    return (
      <main className="min-h-screen bg-gray-50 p-8">
        <h1 className="text-3xl font-bold mb-6">{UI_TEXT.conceptNotFound}</h1>
        <p className="text-gray-500">{UI_TEXT.noConceptMatching(nameParam)}</p>
        <Link href="/search" className="mt-4 inline-block text-blue-600 hover:underline text-sm">{UI_TEXT.backToSearch}</Link>
      </main>
    );
  }

  const { proposingPapers, frameworks, allRelations, subgraphNodes, subgraphEdges } = derived!;

  return (
    <main className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-4xl mx-auto">
        <div className="text-sm text-gray-500 mb-4">
          <Link href="/search" className="hover:text-blue-600">Search</Link>
          <span className="mx-2">/</span>
          <span className="text-gray-800 font-medium">{conceptNode.name}</span>
        </div>

        <ConceptHeader name={conceptNode.name} type={conceptNode.type} description={conceptNode.description} category={conceptNode.category} paperCount={proposingPapers.length} sources={conceptNode.sources} />

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          <ConceptPapers papers={proposingPapers} />
          <ConceptFrameworks frameworks={frameworks} />
        </div>

        <ConceptRelations relations={allRelations} nodes={data.nodes} conceptType={conceptNode.type} />

        {subgraphNodes.length > 1 && (
          <div className="mb-8">
            <h2 className="text-xl font-semibold mb-3">{UI_TEXT.localSubgraph}</h2>
            <p className="text-xs text-gray-400 mb-3">{UI_TEXT.subgraphDescription(conceptNode.name)}</p>
            <Minigraph
              nodes={subgraphNodes}
              edges={subgraphEdges}
              centerNodeId={conceptNode.id}
              onNodeClick={(nodeId) => {
                const node = data.nodes.find((n) => n.id === nodeId);
                if (node) router.push(`/concept/${encodeURIComponent(node.name || node.id)}`);
              }}
            />
          </div>
        )}

        <ConceptPath graphNodes={data.nodes} graphLinks={data.links} conceptNodeId={conceptNode.id} conceptName={conceptNode.name} />
      </div>
    </main>
  );
}
