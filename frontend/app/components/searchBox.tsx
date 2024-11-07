"use client";

import { useRouter, useSearchParams } from "next/navigation";
import { Suspense, useEffect, useState } from "react";

interface Props {
  className?: string;
}

const SearchBoxInner: React.FC<Props> = ({ className }) => {
  const searchParams = useSearchParams();
  const router = useRouter();
  const [what, setWhat] = useState(searchParams.get("what") ?? "");
  const [who, setWho] = useState(searchParams.get("who") ?? "");
  const [suggestions, setSuggestions] = useState<
    { trick: string; count: number }[]
  >([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [commonTricks, setCommonTricks] = useState<
    { trick: string; count: number }[]
  >([]);

  useEffect(() => {
    fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/common_tricks`)
      .then((res) => res.json())
      .then((data) => setCommonTricks(data));
  }, []);

  useEffect(() => {
    setSuggestions(
      commonTricks.filter((trick) =>
        trick.trick.toLowerCase().includes(what.toLowerCase())
      )
    );
  }, [commonTricks, what]);

  return (
    <form
      onSubmit={(e) => {
        e.preventDefault();
        setShowSuggestions(false);
        router.push(`/search?what=${what}&who=${who}`);
      }}
      className={`flex flex-col sm:flex-row gap-4 ${className}`}
    >
      <div className="flex flex-1 flex-row gap-4">
        <div className="relative w-full">
          <input
            type="text"
            placeholder="What"
            className="md:text-lg w-full px-4 py-2 bg-[#171717] border border-[#a0a0a0] rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 text-white placeholder:text-gray-400"
            value={what}
            onChange={(e) => {
              setWhat(e.target.value);
              setShowSuggestions(true);
            }}
            onFocus={() => setShowSuggestions(true)}
            onBlur={() => setShowSuggestions(false)}
          />
          {what.length > 0 && showSuggestions && suggestions.length > 0 && (
            <div className="absolute w-full mt-1 bg-[#303030] border border-[#505050] rounded-md shadow-lg max-h-60 overflow-y-auto">
              <div className="p-2">
                <div className="space-y-1">
                  {suggestions.map((suggestion) => (
                    <button
                      key={suggestion.trick}
                      className="block w-full text-left px-2 py-1 text-white text-sm md:text-base hover:bg-[#404040] rounded"
                      onMouseDown={(e) => {
                        e.preventDefault();
                        setWhat(suggestion.trick);
                        setShowSuggestions(false);
                        router.push(
                          `/search?what=${suggestion.trick}&who=${who}`
                        );
                      }}
                    >
                      {suggestion.trick}{" "}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>
        <div className="relative w-full">
          <input
            type="text"
            placeholder="Who"
            className="md:text-lg w-full px-4 py-2 bg-[#171717] border border-[#a0a0a0] rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 text-white placeholder:text-gray-400"
            value={who}
            onChange={(e) => setWho(e.target.value)}
          />
        </div>
      </div>
      <button
        type="submit"
        className="flex-0 bg-white text-black px-4 py-2 rounded-md"
      >
        Search
      </button>
    </form>
  );
};

const SearchBox: React.FC<Props> = ({ className }) => {
  return (
    <Suspense>
      <SearchBoxInner className={className} />
    </Suspense>
  );
};

export default SearchBox;
