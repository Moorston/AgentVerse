"use client";

import Link from "next/link";

const NAV_ITEMS = [
  { label: "Home", href: "/", icon: "🏠" },
  { label: "Graph", href: "/graph", icon: "🔮" },
  { label: "Search", href: "/search", icon: "🔍" },
  { label: "Papers", href: "/papers", icon: "📄" },
  { label: "Frameworks", href: "/frameworks", icon: "🧩" },
  { label: "Compare", href: "/compare", icon: "⚖️" },
  { label: "Timeline", href: "/timeline", icon: "📈" },
  { label: "Roadmap", href: "/roadmap", icon: "🗺️" },
  { label: "Monitor", href: "/monitor", icon: "📊" },
];

export function Sidebar() {
  return (
    <aside className="w-56 border-r bg-gray-50 flex flex-col h-screen sticky top-0">
      <div className="p-4 border-b">
        <Link href="/" className="text-xl font-bold text-blue-600">
          AgentVerse
        </Link>
        <p className="text-xs text-gray-400 mt-1">Knowledge Graph</p>
      </div>
      <nav className="flex-1 p-2">
        {NAV_ITEMS.map((item) => (
          <Link
            key={item.href}
            href={item.href}
            className="flex items-center gap-3 px-3 py-2 rounded-lg text-sm hover:bg-gray-100 transition"
          >
            <span>{item.icon}</span>
            <span>{item.label}</span>
          </Link>
        ))}
      </nav>
      <div className="p-4 border-t text-xs text-gray-400">
        v0.1.0
      </div>
    </aside>
  );
}