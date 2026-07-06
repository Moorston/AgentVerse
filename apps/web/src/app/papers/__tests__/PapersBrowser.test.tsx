import React from "react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, waitFor, fireEvent } from "@testing-library/react";
import PapersPage from "../page";

// Mock next/navigation for Next.js internals
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

const mockGraphData = {
  nodes: [
    {
      id: "MultiAgentSurvey",
      type: "paper",
      name: "Multi-Agent Survey",
      description: "A comprehensive survey of multi-agent systems",
      authors: ["Alice", "Bob", "Charlie", "Diana"],
      published_date: "2025-06-01",
      categories: ["cs.AI"],
    },
    {
      id: "AgenticRAGPaper",
      type: "paper",
      name: "Agentic RAG: A New Paradigm",
      description: "Introducing agentic RAG architecture",
      authors: ["Eve"],
      published_date: "2025-04-15",
      categories: ["cs.CL"],
    },
    {
      id: "ConceptReAct",
      type: "concept",
      name: "ReAct",
      description: "Reasoning and acting paradigm",
      category: "technique",
    },
    {
      id: "ConceptToolUse",
      type: "concept",
      name: "Tool Use",
      description: "Using external tools",
      category: "technique",
    },
  ],
  links: [
    { source: "MultiAgentSurvey", target: "ConceptReAct", type: "PROPOSES" },
    { source: "AgenticRAGPaper", target: "ConceptToolUse", type: "PROPOSES" },
  ],
};

const mockPapersData = [
  {
    name: "Multi-Agent Survey",
    authors: ["Alice", "Bob", "Charlie", "Diana"],
    published_date: "2025-06-01",
    arxiv_id: "2506.00001",
    citation_count: 42,
  },
  {
    name: "Agentic RAG: A New Paradigm",
    authors: ["Eve"],
    published_date: "2025-04-15",
    arxiv_id: "2504.00001",
    citation_count: 10,
  },
];

describe("PapersPage", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("renders loading state initially", () => {
    // Deferred promise so loading persists
    globalThis.fetch = vi.fn(() => new Promise(() => {})) as unknown as typeof fetch;

    render(<PapersPage />);
    expect(screen.getByText(/Papers/i)).toBeInTheDocument();
  });

  it("renders paper list when data loads", async () => {
    // First call: knowledge_graph.json, Second call: papers.json
    globalThis.fetch = vi
      .fn()
      .mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockGraphData),
        text: () => Promise.resolve(JSON.stringify(mockGraphData)),
      } as Response)
      .mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockPapersData),
        text: () => Promise.resolve(JSON.stringify(mockPapersData)),
      } as Response);

    render(<PapersPage />);

    await waitFor(() => {
      expect(screen.getByText("Multi-Agent Survey")).toBeInTheDocument();
    });

    expect(screen.getByText("Agentic RAG: A New Paradigm")).toBeInTheDocument();
  });

  it("shows paper metadata (authors, date, citations)", async () => {
    globalThis.fetch = vi
      .fn()
      .mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockGraphData),
        text: () => Promise.resolve(JSON.stringify(mockGraphData)),
      } as Response)
      .mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockPapersData),
        text: () => Promise.resolve(JSON.stringify(mockPapersData)),
      } as Response);

    render(<PapersPage />);

    await waitFor(() => {
      expect(screen.getByText(/Alice, Bob, Charlie \+1 more/)).toBeInTheDocument();
    });

    expect(screen.getByText("2025-04-15")).toBeInTheDocument();
    expect(screen.getByText(/42 citations/)).toBeInTheDocument();
  });

  it("expands concept section on click", async () => {
    globalThis.fetch = vi
      .fn()
      .mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockGraphData),
        text: () => Promise.resolve(JSON.stringify(mockGraphData)),
      } as Response)
      .mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockPapersData),
        text: () => Promise.resolve(JSON.stringify(mockPapersData)),
      } as Response);

    render(<PapersPage />);

    // Wait for paper cards to render, then click first one
    await waitFor(() => {
      expect(screen.getByText("Multi-Agent Survey")).toBeInTheDocument();
    });

    // Click the first card to expand
    const card = screen.getByText("Multi-Agent Survey").closest("[role='button']") || screen.getByText("Multi-Agent Survey");
    fireEvent.click(card);

    await waitFor(() => {
      expect(screen.getByText("ReAct")).toBeInTheDocument();
    });
  });

  it("shows error state when fetch fails", async () => {
    globalThis.fetch = vi.fn().mockRejectedValue(new Error("Network failure"));

    render(<PapersPage />);

    await waitFor(() => {
      // useFetch converts non-TypeError to String(err)
      expect(
        screen.getByText(/Error: Network failure/i),
      ).toBeInTheDocument();
    });
  });

  it("shows empty state when no papers", async () => {
    const emptyGraph = { nodes: [], links: [] };
    globalThis.fetch = vi
      .fn()
      .mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(emptyGraph),
        text: () => Promise.resolve(JSON.stringify(emptyGraph)),
      } as Response)
      .mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve([]),
        text: () => Promise.resolve(JSON.stringify([])),
      } as Response);

    render(<PapersPage />);

    await waitFor(() => {
      expect(screen.getByText("No papers found.")).toBeInTheDocument();
    });
  });
});