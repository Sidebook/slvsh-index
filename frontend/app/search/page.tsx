"use client";

import { useRouter, useSearchParams } from "next/navigation";
import { Suspense, useCallback, useRef } from "react";
import SearchBox from "../components/searchBox";
import TrickView from "../components/TrickView";
import MatchView from "../components/MatchView";
import { Trick } from "../types/trick";
import { useTrickSearch } from "./search";

const SearchPageInner: React.FC = () => {
  const router = useRouter();
  const searchParams = useSearchParams();
  const what = searchParams.get("what") ?? "";
  const who = searchParams.get("who") ?? "";
  const allowAdditions = searchParams.get("allow_additions") !== "false";

  const { tricks, totalCount, loadNextPage, error, isLoading, hasMore } =
    useTrickSearch(who, what, allowAdditions);

  const observer = useRef<IntersectionObserver | null>(null);
  const lastTrickElementRef = useCallback(
    (node: HTMLDivElement | null) => {
      if (observer.current) observer.current.disconnect();
      observer.current = new IntersectionObserver((entries) => {
        if (entries[0].isIntersecting && hasMore) {
          loadNextPage();
        }
      });
      if (node) observer.current.observe(node);
    },
    [hasMore, loadNextPage]
  );

  const groupedByTitle: Record<string, Trick[]> = tricks.reduce(
    (acc, trick) => {
      if (!acc[trick.title]) {
        acc[trick.title] = [];
      }
      acc[trick.title].push(trick);
      return acc;
    },
    {} as Record<string, Trick[]>
  );

  let formattedQuery = [what, who]
    .filter(Boolean)
    .map((q) => `"${q}"`)
    .join(" and ");

  if (!allowAdditions) {
    formattedQuery += " (no additions)";
  }

  return (
    <div className="flex flex-col max-w-4xl mx-auto w-full px-4 items-stretch pb-8">
      <h1 className="text-2xl font-bold my-4">
        <a href="/" className="text-white no-underline text-[2rem]">
          SLVSH INDEX
        </a>
      </h1>

      <SearchBox className="mb-4" />
      {error && (
        <p className="text-center text-red-500 my-4">Something went wrong!</p>
      )}
      <div className="space-y-4 mt-4">
        <div className="flex justify-between">
          <p>
            <span className="hidden sm:inline">
              Found <span className="font-bold">{totalCount ?? "-"}</span>{" "}
              results matching {formattedQuery}
            </span>
            <span className="sm:hidden">
              <span className="font-bold">{totalCount ?? "-"}</span> results
            </span>
          </p>
          <p>
            <label className="flex items-center space-x-2 text-sm">
              <input
                type="checkbox"
                className="bg-[#333333] accent-[#333333]"
                checked={!allowAdditions}
                onChange={(e) => {
                  const next = !e.target.checked;
                  router.push(
                    `/search?what=${what}&who=${who}&allow_additions=${next}`
                  );
                }}
              />
              <span>No additional grab/axis/etc.</span>
            </label>
          </p>
        </div>
        {tricks.length > 0 &&
          Object.entries(groupedByTitle).map(
            ([title, tricks], index, array) => (
              <div
                key={tricks[0].video_id}
                className="rounded-lg shadow bg-[#303030]"
                ref={index === array.length - 1 ? lastTrickElementRef : null}
              >
                <div className="p-4">
                  <MatchView
                    title={title}
                    upload_date={tricks[0].upload_date}
                    video_id={tricks[0].video_id}
                    who={who}
                  />
                </div>
                <hr className="mx-4 border-[#707070]" />
                <div className="p-4 gap-2 flex flex-col">
                  {tricks.map((trick) => (
                    <TrickView
                      key={`${tricks[0].video_id} ${trick.start}`}
                      trick={trick}
                      what={what}
                    />
                  ))}
                </div>
              </div>
            )
          )}
      </div>
      {totalCount === 0 && (
        <div className="h-[50vh] flex flex-col justify-center">
          <div className="flex justify-center">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
              strokeWidth={1.5}
              stroke="currentColor"
              className="w-16 h-16 text-gray-400"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="m21 21-5.197-5.197m0 0A7.5 7.5 0 1 0 5.196 5.196a7.5 7.5 0 0 0 10.607 10.607Z"
              />
            </svg>
          </div>
          <p className="text-lg text-gray-300 p-8 text-center">
            No results found for {formattedQuery}
          </p>
        </div>
      )}
      {isLoading && (
        <div className="flex justify-center items-center p-4">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-300"></div>
        </div>
      )}
      {totalCount !== undefined && totalCount > 100 && !hasMore && (
        <div className="text-center p-4">
          <p className="text-gray-300">—— End of results ——</p>
        </div>
      )}
    </div>
  );
};

const SearchPage: React.FC = () => {
  return (
    <Suspense>
      <SearchPageInner />
    </Suspense>
  );
};

export default SearchPage;
