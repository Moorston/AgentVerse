import React from "react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, waitFor, fireEvent } from "@testing-library/react";
import SearchPage from "../page";

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

// Mock @/lib/search (MemoryGraphRAG)
vi.mock("@/lib/search", () => ({
  MemoryGraphRAG: vi.fn().mockImplementation(() => ({
    search: vi.fn().mockReturnValue([]),
  })),
}));

const mockGraphData = {
  nodes: [
    {
      id: "MultiAgentSystems",
      label: "Multi-Agent Systems",
      type: "concept",
      description: "Systems with multiple autonomous agents",
      properties: {},
    },
    {
      id: "ReAct",
      label: "ReAct",
      type: "concept",
      description: "Reasoning and acting paradigm",
      properties: {},
    },
    {
      id: "crewAIInc/crewAI",
      label: "crewAIInc/crewAI",
      type: "framework",
      description: "Multi-agent collaboration framework",
      properties: {},
    },
  ],
  links: [],
};

describe("SearchPage", () => {
  beforeEach(() => {
    vi.clearAllMocks();

    // Mock initial graph data load
    globalThis.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve(mockGraphData),
    } as Response);
  });

  it("renders search input and tab buttons", async () => {
    render(<SearchPage />);

    await waitFor(() => {
      expect(
        screen.getByPlaceholderText("Search concepts, frameworks, papers..."),
      ).toBeInTheDocument();
    });

    // Tab buttons
    expect(screen.getByText("API Search")).toBeInTheDocument();
    expect(screen.getByText("Local Search")).toBeInTheDocument();

    // Search button (there are 3 buttons, use getAllByRole)
    const searchButtons = screen.getAllByText("Search");
    expect(searchButtons.length).toBeGreaterThanOrEqual(1);
  });

  it("searches and displays results via API", async () => {
    // Override fetch for the search endpoint
    globalThis.fetch = vi
      .fn()
      .mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockGraphData),
      } as Response)
      .mockResolvedValueOnce({
        ok: true,
        json: () =>
          Promise.resolve({
            results: [
              {
                name: "Multi-Agent Systems",
                description: "Systems with multiple autonomous agents",
                type: "concept",
                score: 3,
                match: "name",
              },
              {
                name: "ReAct",
                description: "Reasoning and acting paradigm",
                type: "concept",
                score: 1,
                match: "description",
              },
            ],
          }),
      } as Response);

    render(<SearchPage />);

    // Wait for graph data to load, then type a query and search
    await waitFor(() => {
      expect(
        screen.getByPlaceholderText("Search concepts, frameworks, papers..."),
      ).toBeInTheDocument();
    });

    const input = screen.getByPlaceholderText("Search concepts, frameworks, papers...");
    fireEvent.change(input, { target: { value: "multi-agent" } });

    // Click the "Search" button (the last one, which is the submit button)
    const searchButtons = screen.getAllByText("Search");
    const submitButton = searchButtons[searchButtons.length - 1];
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText("Multi-Agent Systems")).toBeInTheDocument();
    });
  });

  it("uses local search mode when tab is clicked", async () => {
    render(<SearchPage />);

    await waitFor(() => {
      expect(
        screen.getByPlaceholderText("Search concepts, frameworks, papers..."),
      ).toBeInTheDocument();
    });

    // Switch to Local Search mode
    fireEvent.click(screen.getByText("Local Search"));

    const input = screen.getByPlaceholderText("Search concepts, frameworks, papers...");
    fireEvent.change(input, { target: { value: "multi-agent" } });

    // Click the submit button
    const searchButtons = screen.getAllByText("Search");
    const submitButton = searchButtons[searchButtons.length - 1];
    fireEvent.click(submitButton);

    // In local mode, MemoryGraphRAG returns empty, so we should see the error
    await waitFor(() => {
      expect(screen.getByText(/No local matches found/i)).toBeInTheDocument();
    });
  });

  it("shows no results message when nothing matches via API", async () => {
    globalThis.fetch = vi
      .fn()
      .mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockGraphData),
      } as Response)
      .mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({ results: [] }),
      } as Response);

    render(<SearchPage />);

    await waitFor(() => {
      expect(
        screen.getByPlaceholderText("Search concepts, frameworks, papers..."),
      ).toBeInTheDocument();
    });

    const input = screen.getByPlaceholderText("Search concepts, frameworks, papers...");
    fireEvent.change(input, { target: { value: "zzz_nonexistent" } });

    const searchButtons = screen.getAllByText("Search");
    const submitButton = searchButtons[searchButtons.length - 1];
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(
        screen.getByText(/No results found for.*zzz_nonexistent/i),
      ).toBeInTheDocument();
    });
  });

  it("disables search button while loading", async () => {
    // Use a deferred promise to keep loading state
    let resolveFetch: (value: unknown) => void;
    const deferredFetch = new Promise((resolve) => {
      resolveFetch = resolve;
    });

    // First mock resolves for graph data, second stays pending
    globalThis.fetch = vi
      .fn()
      .mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockGraphData),
      } as Response)
      .mockReturnValueOnce(deferredFetch);

    render(<SearchPage />);

    await waitFor(() => {
      expect(
        screen.getByPlaceholderText("Search concepts, frameworks, papers..."),
      ).toBeInTheDocument();
    });

    const input = screen.getByPlaceholderText("Search concepts, frameworks, papers...");
    fireEvent.change(input, { target: { value: "test" } });

    // Find the submit button (the last "Search" text)
    const searchButtons = screen.getAllByText("Search");
    const submitButton = searchButtons[searchButtons.length - 1];
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(submitButton).toBeDisabled();
    });

    // Resolve to clean up
    resolveFetch!({ ok: true, json: () => Promise.resolve({ results: [] }) });
  });

  it("renders trending concepts and search tips in sidebar", async () => {
    // Graph data with PROPOSES edges to show trending
    const graphDataWithEdges = {
      nodes: [
        ...mockGraphData.nodes,
        { id: "Paper1", label: "Paper 1", type: "paper", properties: {} },
      ],
      links: [
        { source: "Paper1", target: "MultiAgentSystems", type: "PROPOSES" },
      ],
    };

    globalThis.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve(graphDataWithEdges),
    } as Response);

    render(<SearchPage />);

    await waitFor(() => {
      expect(screen.getByText("Search Tips")).toBeInTheDocument();
    });

    // Trending should show Multi-Agent Systems with 1 paper
    expect(screen.getByText(/1 papers?/)).toBeInTheDocument();
  });
});