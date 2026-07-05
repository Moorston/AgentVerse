"use client";

import { useCallback } from "react";

interface GraphControlsProps {
  onSearch?: (query: string) => void;
  onFilter?: (type: string) => void;
  onZoomIn?: () => void;
  onZoomOut?: () => void;
  onFit?: () => void;
  activeFilter?: string;
}

const NODE_TYPES = [
  { label: "All", value: "" },
  { label: "Concept", value: "Concept" },
  { label: "Framework", value: "Framework" },
  { label: "Paper", value: "Paper" },
  { label: "Agent", value: "Agent" },
  { label: "Memory", value: "MemoryFramework" },
  { label: "Pattern", value: "Pattern" },
];

export function GraphControls({
  onSearch,
  onFilter,
  onZoomIn,
  onZoomOut,
  onFit,
  activeFilter = "",
}: GraphControlsProps) {
  const handleSearch = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      onSearch?.(e.target.value);
    },
    [onSearch],
  );

  return (
    <div className="flex flex-col gap-3 p-4 border-r h-full">
      {/* Search */}
      <div>
        <label className="text-xs font-medium text-gray-500 mb-1 block">Search</label>
        <input
          type="text"
          placeholder="Search concepts..."
          onChange={handleSearch}
          className="w-full px-3 py-2 border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>

      {/* Type Filter */}
      <div>
        <label className="text-xs font-medium text-gray-500 mb-1 block">Filter by Type</label>
        <div className="flex flex-wrap gap-1">
          {NODE_TYPES.map((t) => (
            <button
              key={t.value}
              onClick={() => onFilter?.(t.value)}
              className={`px-2 py-1 text-xs rounded ${
                activeFilter === t.value
                  ? "bg-blue-600 text-white"
                  : "bg-gray-100 text-gray-700 hover:bg-gray-200"
              }`}
            >
              {t.label}
            </button>
          ))}
        </div>
      </div>

      {/* Zoom Controls */}
      <div>
        <label className="text-xs font-medium text-gray-500 mb-1 block">View</label>
        <div className="flex gap-1">
          <button onClick={onZoomIn} className="px-3 py-1 text-sm border rounded hover:bg-gray-50">
            +
          </button>
          <button onClick={onZoomOut} className="px-3 py-1 text-sm border rounded hover:bg-gray-50">
            -
          </button>
          <button onClick={onFit} className="px-3 py-1 text-sm border rounded hover:bg-gray-50">
            Fit
          </button>
        </div>
      </div>

      {/* Legend */}
      <div className="mt-auto">
        <label className="text-xs font-medium text-gray-500 mb-1 block">Legend</label>
        <div className="flex flex-col gap-1">
          {NODE_TYPES.filter((t) => t.value).map((t) => (
            <div key={t.value} className="flex items-center gap-2 text-xs">
              <span className="w-3 h-3 rounded-full bg-blue-500" />
              <span>{t.label}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}