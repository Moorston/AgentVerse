"use client";

import { useEffect, useState, useCallback, useRef } from "react";

interface UseFetchResult<T> {
  data: T | null;
  loading: boolean;
  error: string;
  refetch: () => void;
}

export function useFetch<T = unknown>(
  url: string,
  options?: {
    parser?: (json: unknown) => T;
  },
): UseFetchResult<T> {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const cancelledRef = useRef(false);

  const fetchData = useCallback(async () => {
    cancelledRef.current = false;
    setLoading(true);
    setError("");

    try {
      const response = await fetch(url);

      if (cancelledRef.current) return;

      if (!response.ok) {
        setError(`Request failed: ${response.status} ${response.statusText}`);
        setLoading(false);
        return;
      }

      const text = await response.text();
      if (cancelledRef.current) return;

      let json: unknown;
      try {
        json = JSON.parse(text);
      } catch {
        setError("Failed to parse response as JSON.");
        setLoading(false);
        return;
      }

      if (options?.parser) {
        setData(options.parser(json));
      } else {
        setData(json as T);
      }
    } catch (err) {
      if (!cancelledRef.current) {
        setError(err instanceof TypeError ? "Network error: could not reach server." : String(err));
      }
    } finally {
      if (!cancelledRef.current) {
        setLoading(false);
      }
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [url]);

  useEffect(() => {
    cancelledRef.current = false;
    fetchData();
    return () => {
      cancelledRef.current = true;
    };
  }, [fetchData]);

  const refetch = useCallback(() => {
    fetchData();
  }, [fetchData]);

  return { data, loading, error, refetch };
}