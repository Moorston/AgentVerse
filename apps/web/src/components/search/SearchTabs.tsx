interface SearchTabsProps {
  activeTab: "api" | "local";
  onTabChange: (tab: "api" | "local") => void;
  strategy: string;
  onStrategyChange: (strategy: string) => void;
  loading: boolean;
}

export function SearchTabs({ activeTab, onTabChange, strategy, onStrategyChange, loading }: SearchTabsProps) {
  return (
    <>
      <div className="flex gap-1 mb-6 border-b border-gray-200">
        {(["api", "local"] as const).map((tab) => (
          <button
            key={tab}
            onClick={() => onTabChange(tab)}
            className={`px-4 py-2 text-sm font-medium border-b-2 transition ${
              activeTab === tab
                ? "border-blue-600 text-blue-600"
                : "border-transparent text-gray-500 hover:text-gray-700"
            }`}
          >
            {tab === "api" ? "API Search" : "Local Search"}
          </button>
        ))}
      </div>

      <div className="flex gap-4 mb-8">
        {activeTab === "api" && (
          <select
            value={strategy}
            onChange={(e) => onStrategyChange(e.target.value)}
            className="px-4 py-3 border rounded-lg"
            disabled={loading}
          >
            <option value="graph">Graph Search</option>
            <option value="vector">Vector Search</option>
            <option value="hybrid">Hybrid</option>
          </select>
        )}
      </div>
    </>
  );
}
