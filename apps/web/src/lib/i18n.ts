export const UI_TEXT = {
  // Navigation
  home: "Home",
  graph: "Graph",
  search: "Search",
  papers: "Papers",
  frameworks: "Frameworks",
  timeline: "Timeline",
  monitor: "Monitor",
  compare: "Compare",
  roadmap: "Roadmap",

  // Common
  loading: "Loading...",
  error: "An error occurred",
  retry: "Retry",
  noResults: "No results found",
  searchPlaceholder: "Search concepts...",

  // Graph
  filterByType: "Filter by Type",
  filterByRelation: "Filter by Relation",
  all: "All",
  graphExplorer: "Graph Explorer",
  nodes: "nodes",
  edges: "edges",

  // Concept
  relatedPapers: "Related Papers",
  relatedFrameworks: "Related Frameworks",
  pathTo: "Path to...",
  conceptDetail: "Concept Detail",
  conceptNotFound: "Concept Not Found",
  noConceptMatching: (name: string) => `No concept matching "${name}" was found.`,
  backToSearch: "Back to Search",
  papersProposing: (count: number) => `Papers Proposing This Concept (${count})`,
  noPapersPropose: "No papers propose this concept.",
  frameworks: "Frameworks",
  noFrameworks: "No frameworks implement or support this concept.",
  localSubgraph: "Local Subgraph",
  subgraphDescription: (name: string) => `1-hop neighborhood of ${name}. Click a node to navigate.`,
  pathDiscovery: "Path Discovery",
  pathDescription: (name: string) => `Find the shortest path between ${name} and another concept.`,

  // Search
  graphRagSearch: "GraphRAG Search",
  searchConceptsFrameworksPapers: "Search concepts, frameworks, papers...",
  searching: "Searching...",
  noLocalMatches: "No local matches found.",
  apiSearch: "API Search",
  localSearch: "Local Search",
  searchTips: "Search Tips",
  trendingConcepts: "Trending Concepts",
  topConceptsByPaperCount: "Top concepts by paper count",

  // Monitor
  systemMonitor: "System Monitor",
  systemStatus: "System Status",
  realtimeHealth: "Real-time system health and statistics",
  nodeTypes: "Node Types",
  edgeTypes: "Edge Types",
  paperTimeline: "Paper Timeline",
  loadingStats: "Loading stats...",
  knowledgeGraph: "Knowledge Graph",
  cacheStatistics: "Cache Statistics",
  dataExport: "Data Export",
  apiDocs: "API Docs",

  // Papers
  paperBrowser: "Paper Browser",
  researchPapersDescription: (count: number) => `Research papers and the concepts they propose (${count} papers)`,
  noPapersFound: "No papers found.",

  // Frameworks
  frameworkEcosystem: "Framework Ecosystem",
} as const;
