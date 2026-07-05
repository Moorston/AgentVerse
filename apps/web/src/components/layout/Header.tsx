"use client";

export function Header() {
  return (
    <header className="border-b px-6 py-3 flex items-center justify-between">
      <a href="/" className="text-xl font-bold">AgentVerse</a>
      <nav className="flex gap-4">
        <a href="/graph" className="text-sm hover:text-blue-600 transition">Graph</a>
      </nav>
    </header>
  );
}