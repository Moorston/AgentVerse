"use client";

import { useCallback } from "react";

interface GraphControlsProps {
  onSearch?: (query: string) => void;
  onFilter?: (types: string[]) => void;
  onEdgeFilter?: (types: string[]) => void;
  onZoomIn?: () => void;
  onZoomOut?: () => void;
  onFit?: () => void;
  activeFilter?: string[];
  activeEdgeFilter?: string[];
  highlightNode?: string;
  onHighlight?: (nodeId: string | undefined) => void;
}

const NODE_TYPES = [
  { label: "Paper", value: "Paper" },
  { label: "Concept", value: "Concept" },
  { label: "Framework", value: "Framework" },
  { label: "MemoryFramework", value: "MemoryFramework" },
  { label: "MemoryType", value: "MemoryType" },
];

const EDGE_TYPES = [
  { label: "Proposes", value: "PROPOSES" },
  { label: "Implements", value: "IMPLEMENTS" },
  { label: "Evolves To", value: "EVOLVES_TO" },
  { label: "Extends", value: "EXTENDS" },
  { label: "Used In", value: "USED_IN" },
  { label: "Related To", value: "RELATED_TO" },
];

export function GraphControls({
  onSearch,
  onFilter,
  onEdgeFilter,
  onZoomIn,
  onZoomOut,
  onFit,
  activeFilter = [],
  activeEdgeFilter = [],
  highlightNode,
  onHighlight,
}: GraphControlsProps) {
  const handleSearch = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      onSearch?.(e.target.value);
    },
    [onSearch],
  );

  const toggleType = useCallback(
    (type: string) => {
      if (!onFilter) return;
      const isSelected = activeFilter.includes(type);
      if (isSelected) {
        onFilter(activeFilter.filter((t) => t !== type));
      } else {
        onFilter([...activeFilter, type]);
      }
    },
    [activeFilter, onFilter],
  );

  const toggleEdgeType = useCallback(
    (type: string) => {
      if (!onEdgeFilter) return;
      const isSelected = activeEdgeFilter.includes(type);
      if (isSelected) {
        onEdgeFilter(activeEdgeFilter.filter((t) => t !== type));
      } else {
        onEdgeFilter([...activeEdgeFilter, type]);
      }
    },
    [activeEdgeFilter, onEdgeFilter],
  );

  const handleReset = useCallback(() => {
    onFilter?.([]);
    onEdgeFilter?.([]);
    onHighlight?.(undefined);
  }, [onFilter, onEdgeFilter, onHighlight]);

  const handleHighlightChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      onHighlight?.(e.target.value || undefined);
    },
    [onHighlight],
  );

  return (
    <div className="flex flex-col gap-3 p-4 border-r h-full">
      {/* Search */}
      <div>
        <label className="text-xs font-medium text-gray-500 mb-1 block">
          Search
        </label>
        <input
          type="text"
          placeholder="Search concepts..."
          onChange={handleSearch}
          className="w-full px-3 py-2 border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>

      {/* Type Filter — Multi-select */}
      <div>
        <label className="text-xs font-medium text-gray-500 mb-1 block">
          Filter by Type
        </label>
        <div className="flex flex-col gap-1">
          {NODE_TYPES.map((t) => (
            <label
              key={t.value}
              className={`flex items-center gap-2 px-2 py-1 text-xs rounded cursor-pointer ${
                activeFilter.includes(t.value)
                  ? "bg-blue-100 text-blue-800"
                  : "text-gray-700 hover:bg-gray-100"
              }`}
            >
              <input
                type="checkbox"
                checked={activeFilter.includes(t.value)}
                onChange={() => toggleType(t.value)}
                className="accent-blue-600"
              />
              {t.label}
            </label>
          ))}
        </div>
      </div>

      {/* Relation Filter — Multi-select */}
      <div>
        <label className="text-xs font-medium text-gray-500 mb-1 block">
          Filter by Relation
        </label>
        <div className="flex flex-col gap-1">
          {EDGE_TYPES.map((t) => (
            <label
              key={t.value}
              className={`flex items-center gap-2 px-2 py-1 text-xs rounded cursor-pointer ${
                activeEdgeFilter.includes(t.value)
                  ? "bg-blue-100 text-blue-800"
                  : "text-gray-700 hover:bg-gray-100"
              }`}
            >
              <input
                type="checkbox"
                checked={activeEdgeFilter.includes(t.value)}
                onChange={() => toggleEdgeType(t.value)}
                className="accent-blue-600"
              />
              {t.label}
            </label>
          ))}
        </div>
      </div>

      {/* Highlight Node */}
      <div>
        <label className="text-xs font-medium text-gray-500 mb-1 block">
          Highlight Node
        </label>
        <input
          type="text"
          placeholder="Node ID to highlight..."
          value={highlightNode || ""}
          onChange={handleHighlightChange}
          className="w-full px-3 py-2 border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>

      {/* Zoom Controls */}
      <div>
        <label className="text-xs font-medium text-gray-500 mb-1 block">
          View
        </label>
        <div className="flex gap-1">
          <button
            onClick={onZoomIn}
            className="px-3 py-1 text-sm border rounded hover:bg-gray-50"
          >
            +
          </button>
          <button
            onClick={onZoomOut}
            className="px-3 py-1 text-sm border rounded hover:bg-gray-50"
          >
            -
          </button>
          <button
            onClick={onFit}
            className="px-3 py-1 text-sm border rounded hover:bg-gray-50"
          >
            Fit
          </button>
        </div>
      </div>

      {/* Reset */}
      <button
        onClick={handleReset}
        className="w-full px-3 py-2 text-sm border rounded hover:bg-gray-50 text-gray-600"
      >
        Reset All Filters
      </button>

      {/* Legend */}
      <div className="mt-auto">
        <label className="text-xs font-medium text-gray-500 mb-1 block">
          Legend
        </label>
        <div className="flex flex-col gap-1">
          {NODE_TYPES.map((t) => (
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