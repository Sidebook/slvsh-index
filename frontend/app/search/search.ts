import { useState, useEffect } from "react";
import { SearchResponse } from "../types/trick";
import { useDebouncedCallback } from "use-debounce";

export const useTrickSearch = (
  who: string,
  what: string,
  allowAdditions: boolean
) => {
  const [isLoading, setIsLoading] = useState(false);
  const [loadState, setLoadState] = useState<{
    pages: {
      [page: number]: SearchResponse;
    };
    error?: string;
    totalCount?: number;
    hasMore: boolean;
    nextPage: number;
  }>({
    pages: {},
    hasMore: true,
    nextPage: 0,
  });

  const loadNextPage = useDebouncedCallback(async () => {
    if (isLoading) return;
    setIsLoading(true);

    try {
      const currentState = loadState;
      if (!currentState.hasMore) {
        setIsLoading(false);
        return;
      }

      const page = currentState.nextPage;
      const params = new URLSearchParams({
        trick_query: what,
        title_query: who,
        page: page.toString(),
        page_size: "100",
        allow_additions: allowAdditions.toString(),
      });
      const url = `${process.env.NEXT_PUBLIC_API_URL}/api/search?${params}`;

      const resp = await fetch(url);
      const data: SearchResponse = await resp.json();

      setLoadState((prev) => {
        const newPages = {
          ...prev.pages,
          [page]: data,
        };
        const nextPage = Object.keys(newPages).length;
        const newState = {
          ...prev,
          pages: newPages,
          nextPage: nextPage,
          totalCount: data.count,
          hasMore: nextPage <= data.max_page,
        };
        return newState;
      });
    } catch (err) {
      setLoadState((prev) => ({
        ...prev,
        error: err instanceof Error ? err.message : "Unknown error",
      }));
    } finally {
      setIsLoading(false);
    }
  }, 50);

  useEffect(() => {
    setLoadState({
      pages: {},
      hasMore: true,
      nextPage: 0,
    });
    loadNextPage();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [what, who, allowAdditions]);

  return {
    tricks: Object.values(loadState.pages)
      .map((page) => page.results)
      .flat(),
    loadNextPage,
    totalCount: loadState.totalCount,
    isLoading: isLoading,
    error: loadState.error,
    hasMore: loadState.hasMore,
  };
};
