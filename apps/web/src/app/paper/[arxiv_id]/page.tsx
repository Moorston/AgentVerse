"use client";

import { useMemo } from "react";
import { useParams } from "next/navigation";
import { LoadingSkeleton } from "@/components/ui/Loading";
import { ErrorBanner } from "@/components/ui/ErrorBanner";
import { useFetch } from "@/hooks/useFetch";
import { PaperHeader } from "@/components/paper/PaperHeader";
import { PaperConcepts } from "@/components/paper/PaperConcepts";
import { parseGraphData } from "@/lib/types/graph";
import type { KGraphData, KGraphNode, KGraphLink } from "@/lib/types/graph";
import { Card } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import Link from "next/link";

interface PaperFromFile {
  name: string;
  description?: string;
  authors?: string[];
  published_date?: string;
  arxiv_id?: string;
  categories?: string[];
  citation_count?: number;
}

interface PapersFileData {
  papers: PaperFromFile[];
}

function parsePapersData(json: unknown): PapersFileData {
  const raw = json as PaperFromFile[] | PapersFileData;
  return {
    papers: Array.isArray(raw) ? raw : ((raw as PapersFileData).papers || []),
  };
}

function findPaperConcepts(graphData: KGraphData, paperId: string): { name: string; category?: string }[] {
  const concepts: { name: string; category?: string }[] = [];
  for (const link of graphData.links) {
    if (link.type === "PROPOSES" && link.source === paperId) {
      const conceptNode = graphData.nodes.find((n) => n.id === link.target);
      if (conceptNode) {
        concepts.push({ name: conceptNode.name || conceptNode.id, category: conceptNode.category });
      }
    }
  }
  return concepts;
}

function findRelatedEdges(graphData: KGraphData, paperId: string): KGraphLink[] {
  return graphData.links.filter((e) => e.source === paperId || e.target === paperId);
}

function resolveNodeName(nodes: KGraphNode[], id: string): string {
  const node = nodes.find((n) => n.id === id);
  return node?.name || id;
}

export default function PaperDetailPage() {
  const params = useParams();
  const arxivId = typeof params.arxiv_id === "string" ? decodeURIComponent(params.arxiv_id) : "";

  const graph = useFetch<KGraphData>("/data/knowledge_graph.json", { parser: parseGraphData });
  const papersFile = useFetch<PapersFileData>("/data/papers.json", { parser: parsePapersData });

  const loading = graph.loading || papersFile.loading;
  const error = graph.error || papersFile.error;

  const paperNode = useMemo(() => {
    if (!graph.data) return undefined;
    return graph.data.nodes.find(
      (n) =>
        n.type === "paper" &&
        (n.arxiv_id === arxivId ||
          n.id === arxivId ||
          n.id.toLowerCase() === arxivId.toLowerCase()),
    );
  }, [graph.data, arxivId]);

  const paperFromFile = useMemo(() => {
    if (!papersFile.data) return undefined;
    return papersFile.data.papers.find(
      (p) => p.arxiv_id === arxivId || p.name === arxivId,
    );
  }, [papersFile.data, arxivId]);

  const concepts = useMemo(() => {
    if (!graph.data || !paperNode) return [];
    return findPaperConcepts(graph.data, paperNode.id);
  }, [graph.data, paperNode]);

  const relatedEdges = useMemo(() => {
    if (!graph.data || !paperNode) return [];
    return findRelatedEdges(graph.data, paperNode.id);
  }, [graph.data, paperNode]);

  if (loading) {
    return (
      <main className="min-h-screen bg-gray-50 p-8">
        <h1 className="text-3xl font-bold mb-6">Paper Detail</h1>
        <LoadingSkeleton rows={5} />
      </main>
    );
  }

  if (error) {
    return (
      <main className="min-h-screen bg-gray-50 p-8">
        <h1 className="text-3xl font-bold mb-6">Paper Detail</h1>
        <ErrorBanner
          message={error}
          onRetry={() => {
            graph.refetch();
            papersFile.refetch();
          }}
        />
      </main>
    );
  }

  if (!graph.data || !paperNode) {
    return (
      <main className="min-h-screen bg-gray-50 p-8">
        <h1 className="text-3xl font-bold mb-6">Paper Not Found</h1>
        <p className="text-gray-500">
          No paper matching &ldquo;{arxivId}&rdquo; was found.
        </p>
        <Link
          href="/papers"
          className="mt-4 inline-block text-blue-600 hover:underline text-sm"
        >
          Back to Papers
        </Link>
      </main>
    );
  }

  const name = paperNode.name;
  const authors = paperNode.authors || paperFromFile?.authors;
  const date = paperNode.published_date || paperFromFile?.published_date;
  const abstract = paperNode.description || paperFromFile?.description;
  const categories = paperNode.categories || paperFromFile?.categories;

  return (
    <main className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-4xl mx-auto">
        <div className="text-sm text-gray-500 mb-4">
          <Link href="/papers" className="hover:text-blue-600">
            Papers
          </Link>
          <span className="mx-2">/</span>
          <span className="text-gray-800 font-medium">{name}</span>
        </div>

        <PaperHeader
          name={name}
          authors={authors}
          date={date}
          arxivId={paperNode.arxiv_id || arxivId}
          abstract={abstract}
          categories={categories}
        />

        <PaperConcepts concepts={concepts} loading={false} />

        {relatedEdges.length > 0 && (
          <Card title={`Related Edges (${relatedEdges.length})`} className="mt-6">
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b text-left text-gray-500">
                    <th className="pb-2 pr-4">Source</th>
                    <th className="pb-2 pr-4">Type</th>
                    <th className="pb-2">Target</th>
                  </tr>
                </thead>
                <tbody>
                  {relatedEdges.map((edge, i) => (
                    <tr
                      key={i}
                      className="border-b border-gray-100 last:border-0"
                    >
                      <td className="py-2 pr-4">
                        <span className="font-medium">
                          {resolveNodeName(graph.data!.nodes, edge.source)}
                        </span>
                      </td>
                      <td className="py-2 pr-4">
                        <Badge
                          variant={
                            edge.type === "PROPOSES"
                              ? "success"
                              : edge.type === "IMPLEMENTS"
                                ? "info"
                                : edge.type === "SUPPORTS"
                                  ? "warning"
                                  : "default"
                          }
                        >
                          {edge.type}
                        </Badge>
                      </td>
                      <td className="py-2">
                        <span className="font-medium">
                          {resolveNodeName(graph.data!.nodes, edge.target)}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </Card>
        )}
      </div>
    </main>
  );
}
