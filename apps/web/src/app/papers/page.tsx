"use client";

import { useState, useMemo, useCallback, useRef, useEffect } from "react";
import { Card } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { LoadingSkeleton } from "@/components/ui/Loading";
import { ErrorBanner } from "@/components/ui/ErrorBanner";
import { useFetch } from "@/hooks/useFetch";

interface PaperNode {
  id: string;
  type: string;
  name: string;
  description?: string;
  authors?: string[];
  published_date?: string;
  categories?: string[];
  sources?: string[];
  arxiv_id?: string;
}

interface KGraphLink {
  source: string;
  target: string;
  type: string;
}

interface KGraphData {
  nodes: PaperNode[];
  links: KGraphLink[];
}

interface PaperFromFile {
  name: string;
  description?: string;
  authors?: string[];
  published_date?: string;
  arxiv_id?: string;
  citation_count?: number;
}

interface PapersFileData {
  papers: PaperFromFile[];
}

type PaperInfo = PaperNode & { citation_count?: number; concepts: string[]; expanded: boolean };

function parseGraphData(json: unknown): KGraphData {
  const raw = json as Record<string, unknown>;
  return {
    nodes: (raw.nodes as PaperNode[]) || [],
    links: (raw.links || raw.edges || []) as KGraphLink[],
  };
}

function parsePapersData(json: unknown): PapersFileData {
  const raw = json as PaperFromFile[] | PapersFileData;
  return {
    papers: Array.isArray(raw) ? raw : ((raw as PapersFileData).papers || []),
  };
}

function mergePapers(graphData: KGraphData, papersData: PapersFileData): PaperInfo[] {
  const graphPaperNodes = graphData.nodes.filter((n) => n.type === "paper");

  // For each paper, find concepts it proposes via PROPOSES edges
  const paperConceptMap = new Map<string, string[]>();
  for (const link of graphData.links) {
    if (link.type === "PROPOSES") {
      const existing = paperConceptMap.get(link.source) || [];
      const conceptNode = graphData.nodes.find((n) => n.id === link.target);
      const conceptName = conceptNode?.name || link.target;
      existing.push(conceptName);
      paperConceptMap.set(link.source, existing);
    }
  }

  // Merge papers from both sources
  const merged: PaperInfo[] = graphPaperNodes.map((node) => {
    const fromFile = papersData.papers.find(
      (p) => p.name === node.name || p.arxiv_id === node.arxiv_id,
    );
    return {
      ...node,
      citation_count: fromFile?.citation_count ?? 0,
      concepts: paperConceptMap.get(node.id) || [],
      expanded: false,
    };
  });

  // If no graph papers, fall back to papers.json entries
  if (merged.length === 0) {
    for (const p of papersData.papers) {
      merged.push({
        id: p.name,
        type: "paper",
        name: p.name,
        description: p.description,
        authors: p.authors,
        published_date: p.published_date,
        citation_count: p.citation_count ?? 0,
        concepts: [],
        expanded: false,
      });
    }
  }

  // Sort by published_date descending
  merged.sort((a, b) => {
    const dateA = a.published_date ? new Date(a.published_date).getTime() : 0;
    const dateB = b.published_date ? new Date(b.published_date).getTime() : 0;
    return dateB - dateA;
  });

  return merged;
}

function PaperCard({ paper, index, expanded, onToggle }: { paper: PaperInfo; index: number; expanded: boolean; onToggle: (index: number) => void }) {
  return (
    <Card title={paper.name} className="cursor-pointer" onClick={() => onToggle(index)}>
      <div className="flex flex-wrap items-center gap-2 mb-2">
        {paper.authors && paper.authors.length > 0 && (
          <span className="text-xs text-gray-500">
            {paper.authors.slice(0, 3).join(", ")}
            {paper.authors.length > 3 ? ` +${paper.authors.length - 3} more` : ""}
          </span>
        )}
        {paper.published_date && <Badge variant="info">{paper.published_date}</Badge>}
        {paper.categories && paper.categories.map((cat) => <Badge key={cat}>{cat}</Badge>)}
        {paper.citation_count !== undefined && paper.citation_count > 0 && (
          <Badge variant="success">{paper.citation_count} citations</Badge>
        )}
      </div>
      {paper.description && (
        <p className="text-gray-600 text-sm mb-2">
          {paper.description.length > 200 ? paper.description.slice(0, 200) + "..." : paper.description}
        </p>
      )}
      {expanded && (
        <div className="mt-3 pt-3 border-t border-gray-100">
          {paper.concepts.length > 0 ? (
            <>
              <p className="text-xs font-medium text-gray-500 mb-2">Concepts proposed by this paper:</p>
              <div className="flex flex-wrap gap-2">
                {paper.concepts.map((concept) => (
                  <Badge key={concept} variant="success">{concept}</Badge>
                ))}
              </div>
            </>
          ) : (
            <p className="text-xs text-gray-400">No concepts extracted for this paper.</p>
          )}
        </div>
      )}
    </Card>
  );
}

// Simple virtual scrolling for long lists
function VirtualPaperList({
  papers,
  expandedIndex,
  onToggle
}: {
  papers: PaperInfo[];
  expandedIndex: number | null;
  onToggle: (index: number) => void;
}) {
  const ITEM_HEIGHT = 120; // estimated height per card
  const BUFFER = 5;
  const containerRef = useRef<HTMLDivElement>(null);
  const [scrollTop, setScrollTop] = useState(0);

  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;
    const onScroll = () => setScrollTop(container.scrollTop);
    container.addEventListener("scroll", onScroll, { passive: true });
    return () => container.removeEventListener("scroll", onScroll);
  }, []);

  if (papers.length <= 50) {
    // Don't use virtual scrolling for small lists
    return (
      <div className="space-y-4">
        {papers.map((paper, index) => (
          <PaperCard key={paper.id} paper={paper} index={index} expanded={expandedIndex === index} onToggle={onToggle} />
        ))}
      </div>
    );
  }

  const totalHeight = papers.length * ITEM_HEIGHT;
  const startIndex = Math.max(0, Math.floor(scrollTop / ITEM_HEIGHT) - BUFFER);
  const visibleCount = Math.ceil(600 / ITEM_HEIGHT) + BUFFER * 2;
  const endIndex = Math.min(papers.length, startIndex + visibleCount);
  const visiblePapers = papers.slice(startIndex, endIndex);

  return (
    <div ref={containerRef} style={{ height: 600, overflow: "auto" }} className="border rounded-lg">
      <div style={{ height: totalHeight, position: "relative" }}>
        <div style={{ position: "absolute", top: startIndex * ITEM_HEIGHT, width: "100%" }}>
          <div className="space-y-4 p-4">
            {visiblePapers.map((paper, i) => {
              const actualIndex = startIndex + i;
              return (
                <PaperCard key={paper.id} paper={paper} index={actualIndex} expanded={expandedIndex === actualIndex} onToggle={onToggle} />
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
}

export default function PapersPage() {
  const [expandedIndex, setExpandedIndex] = useState<number | null>(null);

  const graph = useFetch<KGraphData>("/data/knowledge_graph.json", { parser: parseGraphData });
  const papersFile = useFetch<PapersFileData>("/data/papers.json", { parser: parsePapersData });

  const loading = graph.loading || papersFile.loading;
  const error = graph.error || papersFile.error;

  const papers = useMemo(() => {
    if (!graph.data || !papersFile.data) return [];
    return mergePapers(graph.data, papersFile.data);
  }, [graph.data, papersFile.data]);

  const toggleExpand = useCallback((index: number) => {
    setExpandedIndex((prev) => (prev === index ? null : index));
  }, []);

  if (loading) {
    return (
      <main className="min-h-screen bg-gray-50 p-8">
        <h1 className="text-3xl font-bold mb-6">Papers</h1>
        <LoadingSkeleton rows={6} />
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold mb-2">Paper Browser</h1>
        <p className="text-gray-600 mb-8">
          Research papers and the concepts they propose ({papers.length} papers)
        </p>

        {error && (
          <div className="mb-6">
            <ErrorBanner
              message={error}
              onRetry={() => {
                graph.refetch();
                papersFile.refetch();
              }}
            />
          </div>
        )}

        <VirtualPaperList papers={papers} expandedIndex={expandedIndex} onToggle={toggleExpand} />

        {papers.length === 0 && !error && (
          <p className="text-gray-500">No papers found.</p>
        )}
      </div>
    </main>
  );
}