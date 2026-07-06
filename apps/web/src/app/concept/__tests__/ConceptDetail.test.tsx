import React from "react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import ConceptDetailPage from "../[name]/page";

// Mock next/navigation
vi.mock("next/navigation", () => ({
  useParams: vi.fn(),
  useRouter: vi.fn(),
}));

// Mock next/link
vi.mock("next/link", () => ({
  default: ({
    children,
    href,
    className,
  }: {
    children: React.ReactNode;
    href: string;
    className?: string;
  }) => (
    <a href={href} className={className}>
      {children}
    </a>
  ),
}));

// Mock Minigraph (uses cytoscape which requires canvas)
vi.mock("@/components/graph/Minigraph", () => ({
  Minigraph: ({ centerNodeId, className }: { centerNodeId?: string; className?: string }) => (
    <div data-testid="minigraph" data-center={centerNodeId} className={className} />
  ),
}));

import { useParams } from "next/navigation";

const mockGraphData = {
  nodes: [
    {
      id: "MultiAgentSystems",
      type: "concept",
      name: "Multi-Agent Systems",
      description: "Systems with multiple autonomous agents",
      category: "architecture",
      sources: ["arxiv_extraction"],
    },
    {
      id: "AgenticRAG",
      type: "concept",
      name: "Agentic RAG",
      description: "Retrieval augmented generation with agent capabilities",
      category: "technique",
      sources: ["arxiv_extraction"],
    },
    {
      id: "PaperOneTitle",
      type: "paper",
      name: "Paper One Title",
      description: "A paper about multi-agent systems",
      authors: ["Alice", "Bob"],
      published_date: "2025-01-01",
    },
  ],
  links: [
    { source: "PaperOneTitle", target: "MultiAgentSystems", type: "PROPOSES" },
    { source: "SomeFramework", target: "MultiAgentSystems", type: "IMPLEMENTS" },
  ],
};

describe("ConceptDetailPage", () => {
  beforeEach(() => {
    vi.clearAllMocks();

    // Mock fetch to return knowledge_graph.json
    globalThis.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve(mockGraphData),
      text: () => Promise.resolve(JSON.stringify(mockGraphData)),
    } as Response);

    // Default param: existing concept
    (useParams as ReturnType<typeof vi.fn>).mockReturnValue({
      name: "Multi-Agent Systems",
    });
  });

  it("renders loading state initially", () => {
    render(<ConceptDetailPage />);
    expect(screen.getByText(/Concept Detail/i)).toBeInTheDocument();
  });

  it("renders concept name when data loads", async () => {
    render(<ConceptDetailPage />);

    await waitFor(() => {
      // Name appears in breadcrumb, header, and table — use heading
      expect(screen.getByRole("heading", { level: 1, name: "Multi-Agent Systems" })).toBeInTheDocument();
    });
  });

  it("renders concept description", async () => {
    render(<ConceptDetailPage />);

    await waitFor(() => {
      expect(
        screen.getByText("Systems with multiple autonomous agents"),
      ).toBeInTheDocument();
    });
  });

  it("renders concept type badge", async () => {
    render(<ConceptDetailPage />);

    await waitFor(() => {
      expect(screen.getByText("concept")).toBeInTheDocument();
    });
  });

  it("lists papers proposing this concept", async () => {
    render(<ConceptDetailPage />);

    await waitFor(() => {
      // Paper name appears in proposing papers list and may appear in table
      const paperLinks = screen.getAllByText("Paper One Title");
      expect(paperLinks.length).toBeGreaterThanOrEqual(1);
    });
  });

  it("shows not-found state for unknown concept", async () => {
    (useParams as ReturnType<typeof vi.fn>).mockReturnValue({
      name: "NonExistentConcept",
    });

    render(<ConceptDetailPage />);

    await waitFor(() => {
      expect(screen.getByText(/Concept Not Found/i)).toBeInTheDocument();
      expect(
        screen.getByText(/No concept matching .NonExistentConcept. was found/i),
      ).toBeInTheDocument();
    });
  });

  it("shows error state when fetch fails", async () => {
    globalThis.fetch = vi.fn().mockRejectedValue(new Error("Network failure"));

    render(<ConceptDetailPage />);

    await waitFor(() => {
      // useFetch converts non-TypeError to String(err), so "Error: Network failure"
      expect(
        screen.getByText(/Error: Network failure/i),
      ).toBeInTheDocument();
    });
  });
});