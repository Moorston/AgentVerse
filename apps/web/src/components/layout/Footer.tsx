export function Footer() {
  return (
    <footer className="border-t py-6 px-8 text-center text-sm text-gray-500">
      <div className="flex items-center justify-center gap-4">
        <span>AgentVerse</span>
        <span>·</span>
        <a href="/docs" className="hover:text-blue-600 transition">API Docs</a>
        <span>·</span>
        <a href="https://github.com/your-org/agentverse" className="hover:text-blue-600 transition">GitHub</a>
      </div>
      <p className="mt-2 text-xs text-gray-400">
        The Open Knowledge Graph for AI Agents
      </p>
    </footer>
  );
}