"use client";

interface ErrorBannerProps {
  message: string;
  onRetry?: () => void;
  className?: string;
}

export function ErrorBanner({ message, onRetry, className = "" }: ErrorBannerProps) {
  return (
    <div
      className={`p-4 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm flex items-start gap-3 ${className}`}
    >
      <div className="shrink-0 mt-0.5">
        <svg
          className="w-5 h-5"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
          xmlns="http://www.w3.org/2000/svg"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
          />
        </svg>
      </div>
      <div className="flex-1">
        <p>{message}</p>
        {onRetry && (
          <button
            onClick={onRetry}
            className="mt-2 px-3 py-1 bg-red-600 text-white rounded text-xs hover:bg-red-700 transition"
          >
            Retry
          </button>
        )}
      </div>
    </div>
  );
}