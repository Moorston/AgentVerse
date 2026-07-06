import "@testing-library/jest-dom";
import React from "react";

// Make React available globally for vitest + jsdom environment
// This is needed because Next.js uses "jsx: preserve" in tsconfig
// and relies on its own JSX transform, but vitest needs React in scope
(globalThis as Record<string, unknown>).React = React;