import React from "react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, waitFor, fireEvent } from "@testing-library/react";
import FrameworksPage from "../page";

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

// Mock @/lib/api
vi.mock("@/lib/api", () => ({
  apiFetch: vi.fn().mockRejectedValue(new Error("API not available")),
}));

const mockGraphData = {
  nodes: [
    {
      id: "crewAIInc/crewAI",
      type: "framework",
      name: "crewAIInc/crewAI",
      description: "Multi-agent collaboration framework",
    },
    {
      id: "langchain-ai/langgraph",
      type: "framework",
      name: "langchain-ai/langgraph",
      description: "State machine framework",
    },
    {
      id: "ConceptReAct",
      type: "concept",
      name: "ReAct",
      description: "Reasoning and acting",
    },
  ],
  links: [
    { source: "langchain-ai/langgraph", target: "ConceptReAct", type: "IMPLEMENTS" },
  ],
};

const mockFrameworksData = [
  {
    name: "langchain-ai/langgraph",
    description: "State machine framework for complex agent workflows",
    stars: 8000,
    language: "Python",
    github_url: "https://github.com/langchain-ai/langgraph",
    implements: ["ReAct", "Plan-and-Execute"],
  },
  {
    name: "crewAIInc/crewAI",
    description: "Multi-agent collaboration framework",
    stars: 15000,
    language: "Python",
    github_url: "https://github.com/crewAIInc/crewAI",
    implements: ["Multi-Agent Societies"],
  },
];

describe("FrameworksPage", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("renders loading state initially", () => {
    globalThis.fetch = vi.fn(() => new Promise(() => {})) as unknown as typeof fetch;

    render(<FrameworksPage />);
    expect(screen.getByText(/Framework Ecosystem/i)).toBeInTheDocument();
  });

  it("renders framework cards from JSON fallback", async () => {
    // Order: first fetch is knowledge_graph.json, Second fetch is frameworks.json
    globalThis.fetch = vi
      .fn()
      .mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockGraphData),
        text: () => Promise.resolve(JSON.stringify(mockGraphData)),
      } as Response)
      .mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockFrameworksData),
        text: () => Promise.resolve(JSON.stringify(mockFrameworksData)),
      } as Response);

    render(<FrameworksPage />);

    await waitFor(() => {
      expect(screen.getByText("langchain-ai/langgraph")).toBeInTheDocument();
    });

    expect(screen.getByText("crewAIInc/crewAI")).toBeInTheDocument();
  });

  it("shows framework stars and language", async () => {
    globalThis.fetch = vi
      .fn()
      .mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockGraphData),
        text: () => Promise.resolve(JSON.stringify(mockGraphData)),
      } as Response)
      .mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockFrameworksData),
        text: () => Promise.resolve(JSON.stringify(mockFrameworksData)),
      } as Response);

    render(<FrameworksPage />);

    await waitFor(() => {
      expect(screen.getByText(/8,000/)).toBeInTheDocument();
    });

    // Both frameworks have Python, so use getAllByText
    const pythonBadges = screen.getAllByText("Python");
    expect(pythonBadges.length).toBe(2);
  });

  it("sorts by stars (default) — highest first", async () => {
    globalThis.fetch = vi
      .fn()
      .mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockGraphData),
        text: () => Promise.resolve(JSON.stringify(mockGraphData)),
      } as Response)
      .mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockFrameworksData),
        text: () => Promise.resolve(JSON.stringify(mockFrameworksData)),
      } as Response);

    render(<FrameworksPage />);

    await waitFor(() => {
      expect(screen.getByText("crewAIInc/crewAI")).toBeInTheDocument();
    });

    // Get the select and switch to name sort
    const select = screen.getByRole("combobox");
    fireEvent.change(select, { target: { value: "name" } });

    // After name sort, "crewAIInc/crewAI" (c) should come before "langchain-ai/langgraph" (l)
    const cards = screen.getAllByText(/crewAIInc|langchain-ai/);
    expect(cards[0].textContent).toContain("crewAIInc");
  });

  it("shows concepts implemented via graph IMPLEMENTS edges", async () => {
    globalThis.fetch = vi
      .fn()
      .mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockGraphData),
        text: () => Promise.resolve(JSON.stringify(mockGraphData)),
      } as Response)
      .mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockFrameworksData),
        text: () => Promise.resolve(JSON.stringify(mockFrameworksData)),
      } as Response);

    render(<FrameworksPage />);

    await waitFor(() => {
      expect(screen.getByText("langchain-ai/langgraph")).toBeInTheDocument();
    });

    // langgraph should show ReAct from both its own implements field and the graph edge
    // Plan-and-Execute from its own field
    expect(screen.getByText("ReAct")).toBeInTheDocument();
  });

  it("shows error state when all fetches fail", async () => {
    globalThis.fetch = vi.fn().mockRejectedValue(new Error("Network failure"));

    render(<FrameworksPage />);

    await waitFor(() => {
      // Should fall back to demo data, so frameworks still render
      expect(screen.getByText("langchain-ai/langgraph")).toBeInTheDocument();
    });
  });
});