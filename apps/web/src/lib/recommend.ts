export interface FrameworkRecommendation {
  name: string;
  score: number;
  reason: string;
  sharedConcepts: string[];
}

export function recommendFrameworks(
  graphData: { nodes: any[]; links: any[] },
  currentFramework: string,
  topK: number = 5
): FrameworkRecommendation[] {
  // Find concepts implemented by currentFramework via IMPLEMENTS edges
  // Find other frameworks that implement the same concepts
  // Score by number of shared concepts
  // Return top K recommendations sorted by score descending

  const nodes = graphData.nodes || [];
  const links = graphData.links || graphData.edges || [];

  // Find the current framework node
  const currentNode = nodes.find(
    (n: any) => n.name === currentFramework || n.id === currentFramework
  );
  if (!currentNode) return [];

  // Find concepts implemented by currentFramework
  const currentConcepts = new Set<string>();
  for (const link of links) {
    if (link.type === "IMPLEMENTS" && (link.source === currentNode.id || link.source === currentFramework)) {
      const conceptNode = nodes.find((n: any) => n.id === link.target);
      if (conceptNode) {
        currentConcepts.add(conceptNode.name || conceptNode.id);
      }
    }
  }

  if (currentConcepts.size === 0) return [];

  // Find other frameworks
  const frameworkNodes = nodes.filter(
    (n: any) =>
      (n.type === "framework" || n.type === "Framework") &&
      n.id !== currentNode.id
  );

  const recommendations: FrameworkRecommendation[] = [];

  for (const fw of frameworkNodes) {
    // Find concepts this framework implements
    const fwConcepts = new Set<string>();
    for (const link of links) {
      if (link.type === "IMPLEMENTS" && link.source === fw.id) {
        const conceptNode = nodes.find((n: any) => n.id === link.target);
        if (conceptNode) {
          fwConcepts.add(conceptNode.name || conceptNode.id);
        }
      }
    }

    // Find shared concepts
    const shared: string[] = [];
    for (const concept of currentConcepts) {
      if (fwConcepts.has(concept)) {
        shared.push(concept);
      }
    }

    if (shared.length > 0) {
      recommendations.push({
        name: fw.name || fw.id,
        score: shared.length,
        reason: `Shares ${shared.length} concept${shared.length !== 1 ? "s" : ""}`,
        sharedConcepts: shared,
      });
    }
  }

  // Sort by score descending
  recommendations.sort((a, b) => b.score - a.score);
  return recommendations.slice(0, topK);
}
